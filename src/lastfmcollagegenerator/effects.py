from typing import List, Optional, Tuple, Union

try:
    from typing import Protocol
except ImportError:  # pragma: no cover
    from typing_extensions import Protocol

from PIL import Image, ImageOps, ImageStat

from lastfmcollagegenerator.theme import Theme, parse_color


class ImageFilter(Protocol):
    """Protocol for image filters in the visual effect pipeline."""

    def apply(self, image: Image.Image) -> Image.Image:
        """Apply transformation to the input image and return the processed image."""
        ...


class VisualEffectPipeline:
    """Sequential pipeline for applying multiple image filters."""

    def __init__(self, filters: Optional[List[ImageFilter]] = None) -> None:
        self.filters: List[ImageFilter] = list(filters) if filters else []

    def add_filter(self, filter_: ImageFilter) -> "VisualEffectPipeline":
        """Add a filter to the end of the pipeline."""
        self.filters.append(filter_)
        return self

    def apply(self, image: Image.Image) -> Image.Image:
        """Apply all filters in sequence to the provided image."""
        result = image
        for f in self.filters:
            result = f.apply(result)
        return result


class DuotoneFilter:
    """Duotone filter that maps grayscale luminance to a gradient between two colors."""

    def __init__(
        self,
        black_color: Union[str, Tuple[int, ...]] = (0, 0, 0),
        white_color: Union[str, Tuple[int, ...]] = (255, 255, 255),
    ) -> None:
        parsed_black = parse_color(black_color, default_alpha=255)
        parsed_white = parse_color(white_color, default_alpha=255)
        self.black: Tuple[int, int, int] = (
            int(parsed_black[0]),
            int(parsed_black[1]),
            int(parsed_black[2]),
        )
        self.white: Tuple[int, int, int] = (
            int(parsed_white[0]),
            int(parsed_white[1]),
            int(parsed_white[2]),
        )

    def apply(self, image: Image.Image) -> Image.Image:
        """Apply duotone color mapping preserving alpha if present."""
        has_alpha = image.mode in ("RGBA", "LA") or (
            image.mode == "P" and "transparency" in image.info
        )
        alpha = None
        if has_alpha:
            converted = image.convert("RGBA")
            alpha = converted.split()[3]
            rgb_image = converted.convert("RGB")
        else:
            rgb_image = image.convert("RGB")

        grayscale = ImageOps.grayscale(rgb_image)
        colorized = ImageOps.colorize(grayscale, black=self.black, white=self.white)

        if alpha is not None:
            colorized = colorized.convert("RGBA")
            colorized.putalpha(alpha)
            return colorized
        return colorized


class ColorExtractor:
    """Extract dominant and vibrant color palettes from images."""

    @staticmethod
    def extract_dominant_color(image: Image.Image) -> Tuple[int, int, int]:
        """Extract the most prominent dominant RGB color from an image."""
        thumb = image.copy().convert("RGB")
        thumb.thumbnail((50, 50))
        # Quantize down to 16 colors to group similar shades
        quantized = thumb.quantize(colors=16, method=Image.Quantize.MEDIANCUT)
        palette = quantized.getpalette()
        if not palette:
            stat = ImageStat.Stat(thumb)
            return (int(stat.mean[0]), int(stat.mean[1]), int(stat.mean[2]))

        # Count frequencies of color indices
        color_counts = quantized.getcolors(maxcolors=2500)
        if not color_counts:
            stat = ImageStat.Stat(thumb)
            return (int(stat.mean[0]), int(stat.mean[1]), int(stat.mean[2]))

        color_counts.sort(key=lambda x: x[0], reverse=True)
        top_index = color_counts[0][1]
        r = palette[top_index * 3]
        g = palette[top_index * 3 + 1]
        b = palette[top_index * 3 + 2]
        return (int(r), int(g), int(b))

    @staticmethod
    def extract_palette(
        image: Image.Image, count: int = 5
    ) -> List[Tuple[int, int, int]]:
        """Extract a list of top distinct RGB colors from an image."""
        thumb = image.copy().convert("RGB")
        thumb.thumbnail((50, 50))
        quantized = thumb.quantize(
            colors=max(16, count), method=Image.Quantize.MEDIANCUT
        )
        palette = quantized.getpalette()
        if not palette:
            stat = ImageStat.Stat(thumb)
            return [(int(stat.mean[0]), int(stat.mean[1]), int(stat.mean[2]))]

        color_counts = quantized.getcolors(maxcolors=2500)
        if not color_counts:
            stat = ImageStat.Stat(thumb)
            return [(int(stat.mean[0]), int(stat.mean[1]), int(stat.mean[2]))]

        color_counts.sort(key=lambda x: x[0], reverse=True)
        results: List[Tuple[int, int, int]] = []
        for _, idx in color_counts[:count]:
            r = palette[idx * 3]
            g = palette[idx * 3 + 1]
            b = palette[idx * 3 + 2]
            results.append((int(r), int(g), int(b)))
        return results

    @classmethod
    def generate_adaptive_theme(
        cls, image: Image.Image, name: str = "adaptive"
    ) -> Theme:
        """Dynamically construct a Theme derived from image artwork."""
        palette = cls.extract_palette(image, count=3)
        primary = palette[0] if palette else (30, 30, 30)
        secondary = palette[1] if len(palette) > 1 else primary

        # Calculate luminance of dominant color: L = 0.299*R + 0.587*G + 0.114*B
        luminance = 0.299 * primary[0] + 0.587 * primary[1] + 0.114 * primary[2]

        if luminance > 130:
            # Light background -> dark text
            text_color = (15, 15, 15)
            overlay_bg = (primary[0], primary[1], primary[2], 195)
            accent_color = (secondary[0], secondary[1], secondary[2], 230)
        else:
            # Dark background -> light text
            text_color = (250, 250, 250)
            overlay_bg = (primary[0], primary[1], primary[2], 180)
            accent_color = (secondary[0], secondary[1], secondary[2], 220)

        return Theme(
            name=name,
            overlay_bg=overlay_bg,
            text_color=text_color,
            accent_color=accent_color,
        )
