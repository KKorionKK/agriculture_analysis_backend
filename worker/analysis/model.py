from dataclasses import dataclass, field
from typing import Tuple
import dataclasses


@dataclass
class NDVIResult:
    mean_ndvi: float
    affected_percentage: float
    plants_percentage: float
    ndvi_map: str
    problems_map: str
    coordinates: Tuple[float, float] | None

    def as_dict(self):
        return dataclasses.asdict(self)


@dataclass
class NeuralResult:
    shapes: list[list[float]]
    labels: list[str]
    input_img: str
    coordinates: Tuple[float, float] | None
