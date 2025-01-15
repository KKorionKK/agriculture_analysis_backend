import os
import exif
import geopandas as gpd
from shapely.geometry import Point
import numpy as np
import pandas as pd
import laspy
import cv2
import open3d as o3d

def convert_gps_to_decimal(gps_coords):
    """
    Конвертирует GPS координаты из формата (градусы, минуты, секунды) в десятичные градусы
    """
    degrees, minutes, seconds = gps_coords

    # Преобразование в десятичные градусы
    decimal_degrees = degrees + minutes / 60 + seconds / 3600

    return decimal_degrees

def extract_image_metadata(image_path):
    # Извлечение метаданных геолокации из изображения
    with open(image_path, 'rb') as img_file:
        image = exif.Image(img_file)

    # Получение GPS-координат
    # Получение GPS координат в формате (градусы, минуты, секунды)
    latitude_dms = image.get('gps_latitude', None)
    longitude_dms = image.get('gps_longitude', None)

    # Преобразование в десятичные градусы
    latitude = convert_gps_to_decimal(latitude_dms) if latitude_dms else None
    longitude = convert_gps_to_decimal(longitude_dms) if longitude_dms else None

    return {
        'latitude': latitude,
        'longitude': longitude,
        'camera_model': image.get('model', 'Unknown'),
        'timestamp': image.get('datetime', None)
    }


def create_point_cloud_with_metadata(image_paths):
    # Сначала создадим обычный pandas DataFrame
    data = []

    for img_path in image_paths:
        metadata = extract_image_metadata(img_path)

        if metadata['latitude'] is not None and metadata['longitude'] is not None:
            data.append({
                'latitude': metadata['latitude'],
                'longitude': metadata['longitude'],
                'camera_model': metadata['camera_model'],
                'timestamp': metadata['timestamp']
            })

    if not data:
        return None

    # Создаем pandas DataFrame
    df = pd.DataFrame(data)

    # Создаем список геометрических объектов
    geometry = [Point(xy) for xy in zip(df['longitude'], df['latitude'])]

    # Создаем GeoDataFrame
    gdf = gpd.GeoDataFrame(
        df,
        geometry=geometry,
        crs="EPSG:4326"  # Явно указываем строкой
    )

    # Проверяем и трансформируем CRS если нужно
    if gdf.crs is None:
        gdf.set_crs("EPSG:4326", inplace=True)

    # Убеждаемся что CRS установлен правильно
    print(f"CRS before saving: {gdf.crs}")

    # Сохраняем в различных форматах для тестирования
    # GeoPackage
    gdf.to_file('point_cloud.gpkg', driver='GPKG', engine='fiona')

    # GeoJSON (как альтернатива)
    gdf.to_file('point_cloud.geojson', driver='GeoJSON', engine='fiona')

    # Shapefile (как еще одна альтернатива)
    gdf.to_file('point_cloud.shp', engine='fiona')

    return gdf


def test():
    dirpath = '/Users/kkorionkk/Курсач/Тестовые данные/архив/rgb'
    paths = os.listdir(dirpath)
    paths = [dirpath + '/' + path for path in paths]
    point_cloud = create_point_cloud_with_metadata(paths)


def create_point_cloud(image_path):
    # Читаем изображение и создаем облако точек через Open3D
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    height, width = gray.shape
    x, y = np.meshgrid(np.arange(width), np.arange(height))

    points = np.zeros((height * width, 3))
    points[:, 0] = x.flatten()
    points[:, 1] = y.flatten()
    points[:, 2] = gray.flatten() / 255.0

    colors = img.reshape(-1, 3) / 255.0

    # Создаем Open3D облако точек
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)
    pcd.colors = o3d.utility.Vector3dVector(colors)

    # Сохраняем в PLY
    o3d.io.write_point_cloud("point_cloud.ply", pcd)

    # Конвертируем в LAZ
    points = np.asarray(pcd.points)
    colors = np.asarray(pcd.colors)

    header = laspy.LasHeader(point_format=2, version="1.2")
    las = laspy.LasData(header)

    las.x = points[:, 0]
    las.y = points[:, 1]
    las.z = points[:, 2]
    las.red = (colors[:, 0] * 65535).astype(np.uint16)
    las.green = (colors[:, 1] * 65535).astype(np.uint16)
    las.blue = (colors[:, 2] * 65535).astype(np.uint16)

    las.write("point_cloud.laz", do_compress=True)

    return pcd



def test3d():
    dirpath = '/Users/kkorionkk/Курсач/Тестовые данные/архив/rgb'
    paths = os.listdir(dirpath)
    paths = [dirpath + '/' + path for path in paths]
    point_cloud = create_point_cloud(paths[0])

#
# # Пример использования
# image_paths = ['image1.jpg', 'image2.jpg', 'image3.jpg']
# point_cloud = create_point_cloud_with_metadata(image_paths)