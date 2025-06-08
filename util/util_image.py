import base64
import datetime
import os
from pathlib import Path

from PIL import Image

from entity import ImageFileInfo


def format_file_size(size_bytes: int) -> str:
    """Convert bytes to human-readable format (GB/MB/KB/B)"""
    for unit, threshold in [("GB", 1 << 30), ("MB", 1 << 20), ("KB", 1 << 10)]:
        if size_bytes >= threshold:
            return f"{size_bytes / threshold:.2f} {unit}"
    return f"{size_bytes} B"


def format_timestamp(unix_timestamp: float) -> str:
    """Format UNIX timestamp to yyyy-MM-dd HH:mm:ss.SSS"""
    dt = datetime.datetime.fromtimestamp(unix_timestamp)
    milliseconds = int(dt.microsecond / 1000)
    return dt.strftime(f"%Y-%m-%d %H:%M:%S.{milliseconds:03d}")


# noinspection PyBroadException
def get_image_properties(file_path: str) -> dict:
    """Extract image properties using Pillow"""
    try:
        with Image.open(file_path) as img:
            return {
                "format": img.format,
                "dimensions": img.size,
                "color_mode": img.mode
            }
    except Exception:
        return {}


def analyze_image_file(file_path: str | os.PathLike) -> ImageFileInfo:
    """Analyze image file and return structured ImageFileInfo"""
    path = Path(file_path)
    if not path.exists():
        return ImageFileInfo(
            path=str(path.absolute()),
            size="0 B",
            created_time="",
            modified_time="",
            is_valid=False
        )

    # File metadata
    file_stat = path.stat()
    img_props = get_image_properties(file_path)

    return ImageFileInfo(
        path=str(path.absolute()),
        size=format_file_size(file_stat.st_size),
        created_time=format_timestamp(file_stat.st_ctime),
        modified_time=format_timestamp(file_stat.st_mtime),
        image_format=img_props.get("format"),
        dimensions=img_props.get("dimensions"),
        color_mode=img_props.get("color_mode"),
        is_valid=bool(img_props)
    )


def encode_image(image_url: str) -> str:
    """
    Encode image to base64

    Args:
        image_url: image file url

    Returns:
        base64 encoded image
    """
    with open(image_url, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def media_type(image_url: str) -> str:
    """
    Get image media type

    Args:
        image_url: image file url

    Returns:
        image media type
    """
    match analyze_image_file(image_url).image_format.lower():
        case "jpg" | "jpeg":
            _type = "image/jpeg"
        case "png":
            _type = "image/png"
        case "gif":
            _type = "image/gif"
        case "webp":
            _type = "image/webp"
        case _:
            raise ValueError(f"Unsupported image format for chat: {analyze_image_file(image_url).image_format}")
    return _type
