# import os
#
# import exif
# from PIL import Image
# import cv2
# from pathlib import Path
# import numpy as np
# import os
# from typing import List, Tuple
#
#
# class PanoramicMaker:
#     def __init__(self):
#         pass
#
#     def extract_geo_data(self, image_path):
#         """Извлечение координат и фокусного расстояния из метаданных"""
#         with open(image_path, 'rb') as img_file:
#             image = exif.Image(img_file)
#
#         # Извлечение GPS координат
#         if hasattr(image, 'gps_latitude') and hasattr(image, 'gps_longitude'):
#             latitude = self.convert_gps_coordinates(
#                 image.gps_latitude,
#                 image.gps_latitude_ref
#             )
#             longitude = self.convert_gps_coordinates(
#                 image.gps_longitude,
#                 image.gps_longitude_ref
#             )
#
#         # Извлечение фокусного расстояния
#         focal_length = image.get('focal_length', None)
#
#         return latitude, longitude, focal_length
#
#     def convert_gps_coordinates(self, coordinates, ref):
#         """Конвертация GPS координат"""
#         degrees = coordinates[0]
#         minutes = coordinates[1]
#         seconds = coordinates[2]
#
#         coordinate = degrees + (minutes / 60.0) + (seconds / 3600.0)
#         return -coordinate if ref in ['S', 'W'] else coordinate
#
#     def get_image_paths(self, dir: str):
#         raws = os.listdir(dir)
#         files = []
#         c = 0
#         for raw in raws:
#             if raw.split('.')[-1] == 'JPG':
#                 if c >= 20:
#                     return files
#                 c += 1
#                 files.append(os.path.join(dir, raw))
#
#         return files
#
#     def images(self, paths):
#         for path in paths:
#             yield cv2.imread(path)
#
#     def stich_images(self, dir: str):
#         image_paths = self.get_image_paths(dir)
#         meta = [self.extract_geo_data(path) for path in image_paths]
#
#         images = [cv2.imread(path) for path in image_paths]
#
#         result = self.stitch_geo_images(images, meta)
#
#         # Сохранение результата
#         cv2.imwrite('geo_panorama.jpg', result)
#
