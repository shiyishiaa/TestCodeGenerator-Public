from typing import Tuple, Optional

from pydantic import BaseModel


class ImageFileInfo(BaseModel):
    path: str
    size: str
    created_time: str
    modified_time: str
    image_format: Optional[str] = None
    dimensions: Optional[Tuple[int, int]] = None
    color_mode: Optional[str] = None
    is_valid: bool = False
