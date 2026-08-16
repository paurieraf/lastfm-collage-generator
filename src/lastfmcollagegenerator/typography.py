from typing import Any, Optional, Tuple
from PIL import ImageFont


def wrap_text_to_width(
    font: Any,
    text: str,
    max_width: int,
    max_lines: Optional[int] = None,
) -> str:
    """Wrap text to fit within a given pixel width using word boundaries.

    Falls back to character-level splitting for words wider than max_width.
    """
    if not text:
        return ""

    words = text.split()
    if not words:
        return text

    lines = []
    current_line = ""

    for word in words:
        candidate = f"{current_line} {word}".strip()
        candidate_w = font.getlength(candidate)

        if candidate_w <= max_width:
            current_line = candidate
        else:
            if current_line:
                lines.append(current_line)
                current_line = ""

            # Check if the single word is wider than max_width
            word_w = font.getlength(word)
            if word_w > max_width:
                # Split the long word character by character
                chunk = ""
                for char in word:
                    test_chunk = chunk + char
                    if font.getlength(test_chunk) <= max_width:
                        chunk = test_chunk
                    else:
                        if chunk:
                            lines.append(chunk)
                        chunk = char
                current_line = chunk
            else:
                current_line = word

    if current_line:
        lines.append(current_line)

    if max_lines is not None and len(lines) > max_lines:
        lines = lines[:max_lines]
        if lines:
            last = lines[-1]
            while last and font.getlength(f"{last}...") > max_width:
                last = last[:-1]
            lines[-1] = f"{last}..."

    return "\n".join(lines)


def get_auto_scaled_font(
    font_path: str,
    base_font_size: int,
    text: str,
    max_width: int,
    max_height: int,
    line_spacing: int = 2,
    min_font_size: int = 7,
) -> Tuple[Any, str]:
    """Dynamically downscale font size until wrapped text fits within max dimensions."""
    current_size = max(min_font_size, base_font_size)
    best_font: Any = ImageFont.load_default()
    best_text: str = ""

    while current_size >= min_font_size:
        try:
            font: Any = ImageFont.truetype(font_path, current_size)
        except OSError:
            # Fallback if custom path fails
            default_font = ImageFont.load_default()
            wrapped = wrap_text_to_width(default_font, text, max_width)
            return default_font, wrapped

        wrapped = wrap_text_to_width(font, text, max_width)
        lines = wrapped.split("\n")
        line_count = len(lines)
        total_height = (line_count * current_size) + ((line_count - 1) * line_spacing)

        best_font = font
        best_text = wrapped

        if total_height <= max_height:
            break

        current_size -= 1

    return best_font, best_text
