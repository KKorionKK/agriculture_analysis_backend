from dataclasses import dataclass, field
import numpy as np

from typing import Tuple

from worker.analysis.model import NDVIResult


@dataclass
class File:
    path: str
    name: str


@dataclass
class SavedFiles:
    ndvi: File
    problems: File


@dataclass
class UploadedFiles:
    ndvi: str | None
    problems: str | None


@dataclass
class CropHealthStats:
    total_pixels: float
    vegetation_pixels: float
    problem_pixels: float
    vegetation_coverage: float
    mean_ndvi: float


@dataclass
class CropHealthData:
    stats: CropHealthStats
    problem_mask: np.array
    affected_percentage: float
    green_mask: np.array
    ndvi_map: np.array

    def as_result(
        self, ndvi_map: str, problems_map: str, coordinates: Tuple[float, float]
    ):
        return NDVIResult(
            mean_ndvi=self.stats.mean_ndvi,
            affected_percentage=round(self.affected_percentage, 2),
            plants_percentage=round(self.stats.vegetation_coverage, 2),
            ndvi_map=ndvi_map,
            problems_map=problems_map,
            coordinates=coordinates,
        )
