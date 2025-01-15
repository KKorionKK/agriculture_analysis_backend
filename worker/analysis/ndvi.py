import os

import numpy as np
import cv2
from scipy import ndimage
import matplotlib.pyplot as plt
from logging import Logger
import io
from worker.utils.media import MediaController
from typing import Tuple
from worker.utils.database import SyncPostgreSQLController
from worker.models.analyze_request import AnalyzeRequest
from sqlalchemy import update
from worker.utils.enumerations import DataStatus


from worker.models.dto import (
    CropHealthStats,
    CropHealthData,
    File,
    SavedFiles,
    UploadedFiles,
)

from sqlalchemy.orm import session
from worker.models.ndvi_result import NDVIResult as DBResult

from .model import NDVIResult


class NDVIAnalyzer:
    """
    Производит анализ на основе NDVI. Поддерживает как и множественное, так и одиночное преобразование.

    """

    def __init__(self, logger: Logger, db: SyncPostgreSQLController, current_hash: str):
        self.media = MediaController()
        self.logger: Logger = logger
        self.current_hash = current_hash
        self.db = db

        self.rgb_raw = []
        self.nir_raw = []

    def preprocess_images(self, rgb_image, nir_image):
        """
        Приводит RGB и NIR изображения к одинаковому размеру и формату

        Параметры:
        rgb_image: RGB изображение
        nir_image: NIR изображение (одноканальное)

        Возвращает:
        - обработанное RGB изображение
        - обработанное NIR изображение
        """
        # Определяем целевой размер (используем размер RGB изображения)
        target_height, target_width = rgb_image.shape[:2]

        # Изменяем размер NIR изображения
        nir_resized = cv2.resize(nir_image, (target_width, target_height))
        nir_resized = cv2.rotate(nir_resized, 180) # TODO: delete in production

        # Убеждаемся, что NIR - одноканальное изображение
        if len(nir_resized.shape) > 2:
            nir_resized = cv2.cvtColor(nir_resized, cv2.COLOR_BGR2GRAY)

        return rgb_image, nir_resized

    def analyze_crop_health(self, rgb_image, nir_image) -> CropHealthData:
        """
        Анализирует состояние посевов на основе RGB и NIR изображений
        с расчетом процента поражения
        """
        # Предварительная обработка изображений
        rgb_processed, nir_processed = self.preprocess_images(rgb_image, nir_image)

        # Конвертируем RGB в HSV для лучшего выделения растительности
        hsv = cv2.cvtColor(rgb_processed, cv2.COLOR_RGB2HSV)

        # Выделяем зеленые области (растительность)
        green_mask = cv2.inRange(hsv, np.array([35, 25, 25]), np.array([85, 255, 255]))

        # Рассчитываем NDVI
        red = rgb_processed[:, :, 0].astype(float)
        nir = nir_processed.astype(float)

        # Избегаем деления на ноль
        ndvi = np.zeros(red.shape)
        mask = (nir + red) != 0
        ndvi[mask] = (nir[mask] - red[mask]) / (nir[mask] + red[mask])

        # Выделяем проблемные зоны только там, где есть растительность
        problem_areas = np.zeros(ndvi.shape, dtype=np.uint8)
        vegetation_mask = green_mask > 0  # Маска где есть растительность

        # Определяем проблемные зоны только на участках с растительностью
        problem_areas[(ndvi < 0.3) & vegetation_mask] = 255

        # Удаляем шум и мелкие области
        problem_areas = ndimage.binary_opening(problem_areas, structure=np.ones((3, 3)))

        # Подсчитываем процент пораженной площади ТОЛЬКО от площади растительности
        total_vegetation_pixels = np.sum(vegetation_mask)
        if total_vegetation_pixels > 0:
            problem_pixels = np.sum(problem_areas > 0)
            problem_percentage = (problem_pixels / total_vegetation_pixels) * 100
        else:
            problem_percentage = 0

        # Добавляем дополнительную статистику
        stats = CropHealthStats(
            total_pixels=rgb_processed.shape[0] * rgb_processed.shape[1],
            vegetation_pixels=total_vegetation_pixels,
            problem_pixels=np.sum(problem_areas > 0),
            vegetation_coverage=(
                total_vegetation_pixels
                / (rgb_processed.shape[0] * rgb_processed.shape[1])
            )
            * 100,
            mean_ndvi=np.mean(ndvi[vegetation_mask]) if np.any(vegetation_mask) else 0,
        )

        return CropHealthData(
            stats=stats,
            ndvi_map=ndvi,
            problem_mask=problem_areas,
            affected_percentage=problem_percentage,
            green_mask=green_mask,
        )

    def print_analysis_stats(self, results):
        """
        Выводит подробную статистику анализа
        """
        stats = results["stats"]
        print("\nПодробная статистика анализа:")
        print(f"Общая площадь изображения: {stats['total_pixels']} пикселей")
        print(f"Площадь растительности: {stats['vegetation_pixels']} пикселей")
        print(f"Покрытие растительностью: {stats['vegetation_coverage']:.1f}%")
        print(f"Проблемные участки: {stats['problem_pixels']} пикселей")
        print(
            f"Процент поражения: {results['affected_percentage']:.1f}% от площади растительности"
        )
        print(f"Средний NDVI: {stats['mean_ndvi']:.3f}")

    def plot_analysis_results(self, rgb_image, analysis_results, figsize=(15, 10)):
        """
        Создает комплексную визуализацию результатов анализа состояния посевов

        Параметры:
        rgb_image: исходное RGB изображение
        analysis_results: словарь с результатами анализа
        figsize: размер итоговой фигуры
        """
        # Создаем фигуру с подграфиками
        fig, axes = plt.subplots(2, 2, figsize=figsize)
        fig.suptitle("Анализ состояния посевов", fontsize=16)

        # 1. Исходное RGB изображение
        axes[0, 0].imshow(rgb_image)
        axes[0, 0].set_title("RGB изображение")
        axes[0, 0].axis("off")

        # 2. Карта NDVI
        ndvi_plot = axes[0, 1].imshow(
            analysis_results["ndvi_map"], cmap="RdYlGn", vmin=-1, vmax=1
        )
        axes[0, 1].set_title("Карта NDVI")
        axes[0, 1].axis("off")
        plt.colorbar(ndvi_plot, ax=axes[0, 1], label="NDVI")

        # 3. Маска растительности
        axes[1, 0].imshow(analysis_results["green_mask"], cmap="gray")
        axes[1, 0].set_title("Маска растительности")
        axes[1, 0].axis("off")

        # 4. Проблемные зоны
        problem_viz = rgb_image.copy()
        problem_viz[analysis_results["problem_mask"] > 0] = [255, 0, 0]
        axes[1, 1].imshow(problem_viz)
        axes[1, 1].set_title(
            f'Проблемные зоны\n(поражено {analysis_results["affected_percentage"]:.1f}%)'
        )
        axes[1, 1].axis("off")

        # Добавляем пространство между подграфиками
        plt.tight_layout(pad=3.0)

        return fig

    def save_analysis_visualizations(
        self, rgb_image, analysis_results: CropHealthData, output_path, dpi=300, img_name: str = None
    ) -> SavedFiles:
        """
        Сохраняет визуализации анализа состояния посевов в отдельные файлы

        Параметры:
        rgb_image: исходное RGB изображение
        analysis_results: словарь с результатами анализа
        output_path: путь для сохранения файлов
        dpi: разрешение сохраняемых изображений
        """

        ndvi_name = f"{output_path}/{self.current_hash}_{img_name}_rgb_ndvi_overlay.png"
        problems_name = (
            f"{output_path}/{self.current_hash}_{img_name}_rgb_problems_overlay.png"
        )

        # 1. RGB с наложением NDVI маски и колорбаром
        plt.figure(figsize=(10, 8))

        # Создаем наложение NDVI на RGB
        ndvi_overlay = plt.imshow(rgb_image)
        ndvi_mask = plt.imshow(
            analysis_results.ndvi_map,
            cmap="RdYlGn",
            alpha=0.5,  # Прозрачность наложения
            vmin=-1,
            vmax=1,
        )

        # Добавляем колорбар
        colorbar = plt.colorbar(ndvi_mask)
        colorbar.set_label("NDVI")

        plt.title("RGB с наложением NDVI")
        plt.axis("off")

        # Сохраняем первую визуализацию
        plt.savefig(ndvi_name, dpi=dpi, bbox_inches="tight", pad_inches=0.1)
        plt.close()

        # 2. RGB с наложением масок растительности и поражений
        plt.figure(figsize=(10, 8))

        # Уменьшаем яркость RGB изображения на 50%
        darkened_rgb = rgb_image.astype(float) * 0.5
        darkened_rgb = np.clip(darkened_rgb, 0, 255).astype(np.uint8)

        # Показываем затемненное RGB изображение
        plt.imshow(darkened_rgb)

        # Создаем маску растительности (зеленый цвет)
        vegetation_overlay = np.zeros((*rgb_image.shape[:2], 4))  # RGBA
        vegetation_overlay[analysis_results.green_mask > 0] = [
            0,
            0,
            1,
            1,
        ]  # Зеленый с альфа=0.3

        # Создаем маску поражений (красный цвет)
        problem_overlay = np.zeros((*rgb_image.shape[:2], 4))  # RGBA
        problem_overlay[analysis_results.problem_mask > 0] = [
            1,
            0,
            0,
            1,
        ]  # Красный с альфа=0.3

        # Накладываем маски
        plt.imshow(vegetation_overlay)
        plt.imshow(problem_overlay)

        # Добавляем легенду
        from matplotlib.patches import Patch

        legend_elements = [
            Patch(facecolor="blue", alpha=1, label="Растительность"),
            Patch(facecolor="red", alpha=1, label="Поражения"),
        ]
        plt.legend(handles=legend_elements, loc="upper right", bbox_to_anchor=(1, 1))

        plt.title("RGB с масками растительности и поражений")
        plt.axis("off")

        # Сохраняем вторую визуализацию
        plt.savefig(problems_name, dpi=dpi, bbox_inches="tight", pad_inches=0.1)
        plt.close()

        return SavedFiles(
            ndvi=File(ndvi_name, "rgb_ndvi_overlay"),
            problems=File(problems_name, "rgb_problems_overlay"),
        )

    def save_data(self, data_array: list[NDVIResult], request: AnalyzeRequest):
        model = DBResult.as_db_instances(data_array, request)
        with self.db() as session:
            session.add(model)
            session.flush([model])

            session.execute(update(AnalyzeRequest)
                            .where(AnalyzeRequest.id == request.id)
                            .values(ndvi_result_id=model.id, ndvi_status=DataStatus.ready))
            session.flush([model, request])
            session.commit()

    def get_ordered_lists(self, path: str):
        nir_path = path + '/nir'
        rgb_path = path + '/rgb'
        if not os.path.exists(nir_path) or not os.path.exists(rgb_path):
            raise Exception('Not found nir or rgb dirs')

        nirs = []
        rgbs = []
        for file in os.listdir(nir_path):
            if file.endswith('.JPG') or file.endswith('.tif'):
                nirs.append(nir_path + '/' + file)
        for file in os.listdir(rgb_path):
            if file.endswith('.JPG'):
                rgbs.append(rgb_path + '/' + file)

        return nirs, rgbs

    def analyze(self, path: str, request: AnalyzeRequest, current_path: str) -> None:
        data_array: list[NDVIResult] = []

        self.rgb_raw, self.nir_raw = self.get_ordered_lists(path)
        for i in range(len(self.rgb_raw)):
            rgb_img = cv2.imread(self.rgb_raw[i])
            nir_img = cv2.imread(self.nir_raw[i], cv2.IMREAD_GRAYSCALE)

            rgb_img = cv2.cvtColor(rgb_img, cv2.COLOR_BGR2RGB)

            self.logger.info("Started analyzing data")
            results = self.analyze_crop_health(rgb_img, nir_img)

            img_name = self.rgb_raw[i].split("/")[-1].split(".")[0]
            files = self.save_analysis_visualizations(
                rgb_img, results, current_path + "/results/", img_name=img_name
            )
            print(files)
            hrefs = self.upload_visuals(files, img_name)
            data = results.as_result(hrefs.ndvi, hrefs.problems, (111, 111))
            data_array.append(data)

        self.save_data(data_array, request)

    def delete_temp_files(self, files: SavedFiles):
        os.remove(files.ndvi.path)
        os.remove(files.problems.path)

    def upload_visuals(self, files: SavedFiles, img_name: str) -> UploadedFiles:
        uploaded = UploadedFiles(None, None)
        with open(files.ndvi.path, "rb") as f:
            buffer = io.BytesIO(f.read())

            extension = files.ndvi.path.split(".")[-1]
            href = self.media.upload(
                buffer, extension, img_name + "_" + files.ndvi.name
            )
            uploaded.ndvi = href

        with open(files.problems.path, "rb") as f:
            buffer = io.BytesIO(f.read())

            extension = files.problems.path.split(".")[-1]
            href = self.media.upload(
                buffer, extension, img_name + "_" + files.problems.name
            )
            uploaded.problems = href
        self.delete_temp_files(files)
        return uploaded

    def debug_analyze(self, rgb, nir):
        rgb_path = "/Users/kkorionkk/Downloads/archive (1)/rgb-images/IX-01-07922_0011_0093.JPG"
        nir_path = "/Users/kkorionkk/Downloads/archive (1)/multispectral-images/NIR/IMG_210204_095452_0093_NIR.tif"

        rgb_img = cv2.imread(rgb_path)
        nir_img = cv2.imread(nir_path, cv2.IMREAD_GRAYSCALE)

        rgb_img = cv2.cvtColor(rgb_img, cv2.COLOR_BGR2RGB)
        self.logger.info("Started analyzing data")
        results = self.analyze_crop_health(rgb_img, nir_img)

        print("Создаем визуализацию...")
        img_name = rgb_path.split("/")[-1].split(".")[0]
        ndvi, problems = self.save_analysis_visualizations(
            rgb_img, results, os.getcwd() + "/results/", img_name=img_name
        )
        self.upload_visuals([ndvi, problems], img_name)


# def main():
#     """
#     Основная функция для запуска анализа
#     """
#     # Загружаем изображения
#     rgb_path = '/Users/kkorionkk/Downloads/archive (1)/rgb-images/IX-01-07922_0011_0093.JPG'  # Укажите путь к вашему RGB изображению
#     nir_path = '/Users/kkorionkk/Downloads/archive (1)/multispectral-images/NIR/IMG_210204_095452_0093_NIR.tif'  # Укажите путь к вашему NIR изображению
#
#     # Читаем изображения
#     rgb_img = cv2.imread(rgb_path)
#     if rgb_img is None:
#         raise ValueError(f"Не удалось загрузить RGB изображение: {rgb_path}")
#     rgb_img = cv2.cvtColor(rgb_img, cv2.COLOR_BGR2RGB)
#
#     nir_img = cv2.imread(nir_path, cv2.IMREAD_GRAYSCALE)
#     if nir_img is None:
#         raise ValueError(f"Не удалось загрузить NIR изображение: {nir_path}")
#
#     # Проводим анализ
#     print("Анализируем изображения...")
#     results = analyze_crop_health(rgb_img, nir_img)
#     print_analysis_stats(results)
#
#     # Создаем визуализацию
#     print("Создаем визуализацию...")
#     fig = plot_analysis_results(rgb_img, results)
#
#     # Сохраняем результат
#     output_path = 'результаты_анализа.png'
#     plt.savefig(output_path, dpi=300, bbox_inches='tight')
#     print(f"Результаты сохранены в: {output_path}")
#
#     # Показываем результат
#     plt.show()
#
#     # Выводим статистику
#     print(f"\nСтатистика анализа:")
#     print(f"Процент пораженной площади: {results['affected_percentage']:.1f}%")
#     print(f"Средний NDVI: {np.mean(results['ndvi_map']):.3f}")
