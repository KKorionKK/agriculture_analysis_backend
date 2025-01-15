import cv2
import numpy as np
import os
from exif import Image


def read_image_with_metadata(image_path):
    # Чтение изображения и его метаданных
    img = cv2.imread(image_path)
    with open(image_path, 'rb') as img_file:
        metadata = Image(img_file)
    return img, metadata


def stitch_images(image_paths):
    # Читаем изображения
    images = []
    for path in image_paths:
        img = cv2.imread(path)
        # Уменьшаем размер для улучшения производительности
        img = cv2.resize(img, (1024, 768), fx=0.5, fy=0.5)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
        images.append(img)

    # Создаем объект stitcher с параметрами
    stitcher = cv2.Stitcher.create()
    stitcher.setPanoConfidenceThresh(0.1)  # Снижаем порог уверенности

    # Пробуем разные режимы
    try:
        status, result = stitcher.stitch(images)
        if status == cv2.Stitcher_OK:
            return result

        # Пробуем режим SCANS если обычный не сработал
        stitcher = cv2.Stitcher.create(cv2.Stitcher_SCANS)
        status, result = stitcher.stitch(images)
        if status == cv2.Stitcher_OK:
            return result
    except Exception as e:
        print(f"Error: {e}")

    return None


# Использование
image_folder = "/Users/kkorionkk/Курсач/Тестовые данные/архив/rgb"
image_paths = [os.path.join(image_folder, f) for f in os.listdir(image_folder) if f.endswith(('.JPG', '.jpeg', '.png'))]
result = stitch_images(image_paths)

if result is not None:
    cv2.imwrite("stitched_field.jpg", result)