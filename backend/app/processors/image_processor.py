"""
Image evidence processor.

Extracts EXIF metadata from uploaded images — creation time, camera/device
info, and GPS coordinates if present.
"""
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from io import BytesIO
from typing import Dict, Any


def extract_image_metadata(file_bytes: bytes) -> Dict[str, Any]:
    metadata: Dict[str, Any] = {}
    try:
        img = Image.open(BytesIO(file_bytes))
        metadata["format"] = img.format
        metadata["size"] = img.size

        exif_data = img._getexif() if hasattr(img, "_getexif") else None
        if not exif_data:
            return metadata

        for tag_id, value in exif_data.items():
            tag = TAGS.get(tag_id, tag_id)
            if tag == "GPSInfo":
                metadata["gps"] = _parse_gps(value)
            elif tag in ("DateTimeOriginal", "DateTime", "Make", "Model"):
                metadata[tag] = str(value)

    except Exception as e:
        metadata["extraction_error"] = str(e)

    return metadata


def _parse_gps(gps_info: dict) -> Dict[str, Any]:
    parsed = {}
    for key, val in gps_info.items():
        tag = GPSTAGS.get(key, key)
        parsed[tag] = str(val)
    return parsed
