from __future__ import annotations

import json
import os
from dataclasses import dataclass


@dataclass
class BoundingBox:
    min_x: float
    min_y: float
    min_z: float
    max_x: float
    max_y: float
    max_z: float

    @property
    def width(self) -> float:
        return self.max_x - self.min_x

    @property
    def depth(self) -> float:
        return self.max_y - self.min_y

    @property
    def height(self) -> float:
        return self.max_z - self.min_z

    def to_dict(self) -> dict:
        return {
            "min": {"x": round(self.min_x, 3), "y": round(self.min_y, 3), "z": round(self.min_z, 3)},
            "max": {"x": round(self.max_x, 3), "y": round(self.max_y, 3), "z": round(self.max_z, 3)},
            "size": {
                "width": round(self.width, 3),
                "depth": round(self.depth, 3),
                "height": round(self.height, 3),
            },
        }


def measure_stl(path: str) -> dict:
    """Parse an STL file and return bounding box, triangle count, and volume estimate."""
    if not os.path.isfile(path):
        return {"error": f"File not found: {path}"}

    try:
        from stl import mesh as stl_mesh
    except ImportError:
        return {"error": "numpy-stl not installed"}

    try:
        m = stl_mesh.Mesh.from_file(path)
    except Exception as e:
        return {"error": f"Failed to parse STL: {e}"}

    bbox = BoundingBox(
        min_x=float(m.min_[0]),
        min_y=float(m.min_[1]),
        min_z=float(m.min_[2]),
        max_x=float(m.max_[0]),
        max_y=float(m.max_[1]),
        max_z=float(m.max_[2]),
    )

    volume = float(m.get_mass_properties()[0]) if hasattr(m, "get_mass_properties") else None

    return {
        "file": path,
        "triangles": len(m.vectors),
        "bounding_box": bbox.to_dict(),
        "volume_mm3": round(volume, 3) if volume is not None else None,
    }
