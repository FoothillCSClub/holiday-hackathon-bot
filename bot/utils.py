from typing import Tuple

from PIL import ImageFont


# TODO: move to utility cog for reloading?
def get_max_str(font: ImageFont, text: str, max_size: int) -> Tuple[str, float]:
    """Get max string that fits a width."""
    cur_text = ""
    cur_len = 0

    for char in text:
        length = font.getlength(char)

        if cur_len + length <= max_size:
            cur_text += char
            cur_len += length
        else:
            break

    if len(text) > len(cur_text) and len(cur_text):
        cur_text = cur_text[:-2] + "..."

    return cur_text, cur_len
