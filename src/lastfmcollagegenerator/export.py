"""Export utilities for composite collage images."""

import os
from typing import Optional, Tuple, Union
from PIL import Image

SUPPORTED_EXPORT_FORMATS = ("PNG", "JPEG", "WEBP")

EXTENSION_TO_FORMAT = {
    ".png": "PNG",
    ".jpg": "JPEG",
    ".jpeg": "JPEG",
    ".webp": "WEBP",
}


def infer_format(output_path: str) -> str:
    """Infer image format from file path extension.

    Defaults to PNG if extension is unrecognized or missing.
    """
    ext = os.path.splitext(output_path)[1].lower()
    return EXTENSION_TO_FORMAT.get(ext, "PNG")


def export_image(
    image: Image.Image,
    output_path: str,
    format: Optional[str] = None,
    quality: int = 85,
    background_color: Union[str, Tuple[int, int, int]] = (0, 0, 0),
    optimize: bool = True,
) -> str:
    """Export a PIL Image to disk with safe format handling and optimization.

    Args:
        image: PIL Image instance to export.
        output_path: Target filesystem path.
        format: Explicit image format ("PNG", "JPEG", "WEBP"). If None, inferred
            from output_path extension.
        quality: Compression quality for lossy formats (JPEG/WebP). Default 85.
        background_color: Background color for flattening RGBA when exporting to JPEG.
            Default is solid black (0, 0, 0).
        optimize: Whether to enable encoder optimization. Default True.

    Returns:
        The normalized output path where the file was saved.

    Raises:
        ValueError: If format is unsupported, output_path is empty, or quality
            is out of range.
        TypeError: If parameters have invalid types.
    """
    if not isinstance(image, Image.Image):
        raise TypeError("image must be a PIL.Image.Image instance.")
    if not isinstance(output_path, str) or not output_path.strip():
        raise ValueError("output_path must be a non-empty string.")
    if type(quality) is not int or not (1 <= quality <= 100):
        raise ValueError("quality must be an integer between 1 and 100.")
    if format is not None and not isinstance(format, str):
        raise TypeError("format must be a string or None.")

    target_format = format.upper() if format else infer_format(output_path)

    if target_format == "JPG":
        target_format = "JPEG"

    if target_format not in SUPPORTED_EXPORT_FORMATS:
        raise ValueError(
            f"Unsupported export format: '{target_format}'. "
            f"Supported formats: {SUPPORTED_EXPORT_FORMATS}"
        )

    parent_dir = os.path.dirname(output_path)
    if parent_dir and not os.path.exists(parent_dir):
        os.makedirs(parent_dir, exist_ok=True)

    img_to_save = image

    # Safe alpha channel handling for formats that do not support transparency (JPEG)
    if target_format == "JPEG":
        if img_to_save.mode in ("RGBA", "LA", "P"):
            if img_to_save.mode == "P":
                img_to_save = img_to_save.convert("RGBA")
            bg = Image.new("RGB", img_to_save.size, background_color)
            if img_to_save.mode == "RGBA":
                bg.paste(img_to_save, mask=img_to_save.split()[3])
            else:
                bg.paste(img_to_save)
            img_to_save = bg
        elif img_to_save.mode != "RGB":
            img_to_save = img_to_save.convert("RGB")

    save_kwargs = {}
    if target_format in ("JPEG", "WEBP"):
        save_kwargs["quality"] = quality
        save_kwargs["optimize"] = optimize
    elif target_format == "PNG":
        save_kwargs["optimize"] = optimize

    img_to_save.save(output_path, format=target_format, **save_kwargs)
    return output_path
