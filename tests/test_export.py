import os
import tempfile
import pytest
from PIL import Image

from lastfmcollagegenerator import (
    CollageGenerator,
    export_image,
    infer_format,
    SUPPORTED_EXPORT_FORMATS,
)


def test_infer_format():
    assert infer_format("test.png") == "PNG"
    assert infer_format("test.PNG") == "PNG"
    assert infer_format("test.jpg") == "JPEG"
    assert infer_format("test.JPG") == "JPEG"
    assert infer_format("test.jpeg") == "JPEG"
    assert infer_format("test.webp") == "WEBP"
    assert infer_format("test.WEBP") == "WEBP"
    assert infer_format("test.unknown") == "PNG"
    assert infer_format("test") == "PNG"


def test_export_image_png():
    with tempfile.TemporaryDirectory() as tmpdir:
        out_file = os.path.join(tmpdir, "collage.png")
        img = Image.new("RGBA", (100, 100), (255, 0, 0, 128))
        res = export_image(img, out_file)
        assert res == out_file
        assert os.path.exists(out_file)

        saved = Image.open(out_file)
        assert saved.format == "PNG"
        assert saved.size == (100, 100)


def test_export_image_webp():
    with tempfile.TemporaryDirectory() as tmpdir:
        out_file = os.path.join(tmpdir, "collage.webp")
        img = Image.new("RGBA", (100, 100), (0, 255, 0, 200))
        res = export_image(img, out_file, quality=90)
        assert res == out_file
        assert os.path.exists(out_file)

        saved = Image.open(out_file)
        assert saved.format == "WEBP"
        assert saved.size == (100, 100)


def test_export_image_jpeg_rgba_flattening():
    with tempfile.TemporaryDirectory() as tmpdir:
        out_file = os.path.join(tmpdir, "collage.jpg")
        # RGBA image with translucent pixels
        img = Image.new("RGBA", (100, 100), (255, 255, 255, 128))
        res = export_image(img, out_file, quality=85)
        assert res == out_file
        assert os.path.exists(out_file)

        saved = Image.open(out_file)
        assert saved.format == "JPEG"
        assert saved.mode == "RGB"
        assert saved.size == (100, 100)


def test_export_image_jpeg_p_mode_and_rgb_mode():
    with tempfile.TemporaryDirectory() as tmpdir:
        # P mode
        out_file_p = os.path.join(tmpdir, "collage_p.jpeg")
        img_p = Image.new("P", (50, 50))
        export_image(img_p, out_file_p)
        saved_p = Image.open(out_file_p)
        assert saved_p.format == "JPEG"
        assert saved_p.mode == "RGB"

        # RGB mode directly
        out_file_rgb = os.path.join(tmpdir, "collage_rgb.jpg")
        img_rgb = Image.new("RGB", (50, 50), (10, 20, 30))
        export_image(img_rgb, out_file_rgb)
        saved_rgb = Image.open(out_file_rgb)
        assert saved_rgb.format == "JPEG"
        assert saved_rgb.mode == "RGB"


def test_export_image_creates_parent_directories():
    with tempfile.TemporaryDirectory() as tmpdir:
        out_file = os.path.join(tmpdir, "nested", "sub", "collage.webp")
        img = Image.new("RGB", (50, 50), (0, 0, 0))
        export_image(img, out_file)
        assert os.path.exists(out_file)


def test_export_image_explicit_format_override():
    with tempfile.TemporaryDirectory() as tmpdir:
        out_file = os.path.join(tmpdir, "image_without_ext")
        img = Image.new("RGB", (50, 50), (100, 100, 100))
        export_image(img, out_file, format="webp")
        saved = Image.open(out_file)
        assert saved.format == "WEBP"


def test_export_image_via_facade():
    with tempfile.TemporaryDirectory() as tmpdir:
        out_file = os.path.join(tmpdir, "facade_collage.jpg")
        img = Image.new("RGBA", (100, 100), (50, 50, 50, 255))
        res = CollageGenerator.export_image(img, out_file)
        assert res == out_file
        assert os.path.exists(out_file)
        saved = Image.open(out_file)
        assert saved.format == "JPEG"


def test_export_image_validation_errors():
    img = Image.new("RGB", (10, 10))

    # Invalid image type
    with pytest.raises(TypeError, match="image must be a PIL.Image.Image"):
        export_image("not_an_image", "out.png")  # type: ignore

    # Invalid output_path
    with pytest.raises(ValueError, match="output_path must be a non-empty string"):
        export_image(img, "")
    with pytest.raises(ValueError, match="output_path must be a non-empty string"):
        export_image(img, "   ")
    with pytest.raises(ValueError, match="output_path must be a non-empty string"):
        export_image(img, None)  # type: ignore

    # Invalid quality
    with pytest.raises(ValueError, match="quality must be an integer between 1 and 100"):
        export_image(img, "out.jpg", quality=0)
    with pytest.raises(ValueError, match="quality must be an integer between 1 and 100"):
        export_image(img, "out.jpg", quality=101)
    with pytest.raises(ValueError, match="quality must be an integer between 1 and 100"):
        export_image(img, "out.jpg", quality="high")  # type: ignore

    # Invalid format type
    with pytest.raises(TypeError, match="format must be a string or None"):
        export_image(img, "out.png", format=123)  # type: ignore

    # Unsupported format
    with pytest.raises(ValueError, match="Unsupported export format"):
        export_image(img, "out.gif", format="GIF")
