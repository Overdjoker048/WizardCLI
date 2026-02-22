from typing import Optional, Union
from re import compile as recompile, split, sub
from functools import lru_cache
from PIL import Image
from shutil import get_terminal_size



def gradiant(
    text: str,
    start: Union[tuple, str, list, int],
    end: Union[tuple, str, list, int],
    sep: Optional[str] = ""
) -> str:
    """Create text with color gradient effect while preserving existing styles.

    Arguments:
        text (str): Text to apply gradient to.
        start (Union[tuple, str, list]): Starting color in RGB tuple or hex format.
        end (Union[tuple, str, list]): Ending color in RGB tuple or hex format.
        sep (str, optional): Separator for splitting text into segments.

    Return:
        str: Text with color gradient applied, preserving styles.
    """
    def parse_color(c):
        if isinstance(c, (list, tuple)) and len(c) == 3:
            return c
        elif isinstance(c, int):
            return ((c >> 16) & 255, (c >> 8) & 255, c & 255)
        elif isinstance(c, str):
            return tuple(int(c[i:i+2], 16) for i in (0, 2, 4))
        ValueError(f"Invalid color: {c}")

    ANSI_PATTERN = recompile(r"\x1b\[[0-9;]*m")
    start_rgb = parse_color(start)
    end_rgb = parse_color(end)

    def apply_gradient(segment: str, start_offset: float = 0.0, global_len: Optional[int] = None, global_pos: int = 0) -> str:
        parts = split(r"(\x1b\[[0-9;]*m)", segment)
        clean_len = sum(len(p) for i, p in enumerate(parts) if i % 2 == 0)
        denom = max(1, (global_len if global_len is not None else clean_len) - 1)

        out = []
        visible_idx = 0
        for i, p in enumerate(parts):
            if i % 2 == 1:
                out.append(p)
            else:
                for ch in p:
                    idx = global_pos + visible_idx
                    if idx == denom:
                        out.append(f"\033[38;2;{end_rgb[0]};{end_rgb[1]};{end_rgb[2]}m{ch}")
                    else:
                        f = (idx / denom) + start_offset
                        out.append(f"\033[38;2;{int(start_rgb[0] + (end_rgb[0] - start_rgb[0]) * f)};{int(start_rgb[1] + (end_rgb[1] - start_rgb[1]) * f)};{int(start_rgb[2] + (end_rgb[2] - start_rgb[2]) * f)}m{ch}")
                    visible_idx += 1
        return "".join(out)

    if sep:
        segments = text.split(sep)
        total_len = sum(len(sub(ANSI_PATTERN, "", seg)) for seg in segments)
        pos = 0
        colored_segments = []
        for seg in segments:
            colored_segments.append(apply_gradient(seg, 0.0, global_len=total_len, global_pos=pos))
            pos += len(sub(ANSI_PATTERN, "", seg))
        return sep.join(colored_segments) + "\033[0m"
    else:
        return apply_gradient(text) + "\033[0m"


def fg(color: Optional[Union[tuple, str, list, int]] = None) -> str:
    """
    Returns the ANSI escape code for forground text color.

    Arguments:
        color (Union[tuple, str, list, int], optional): Color in RGB tuple, hex string, or integer format. Defaults to None.

    Return:
        str: ANSI fg text string.

    Example of use:
        >>> import WizardCLI
        >>> print(WizardCLI.fg("FF0000") + "Red background" + WizardCLI.rst())
        >>> print(WizardCLI.fg((255, 0, 0)) + "Red background" + WizardCLI.rst())
        >>> print(WizardCLI.fg(0xFF0000) + "Red background" + WizardCLI.rst())
    """
    if color is None:
        return ""
    if isinstance(color, int):
        return f"\033[38;2;{(color >> 16) & 255};{(color >> 8) & 255};{color & 255}m"
    elif isinstance(color, str):
        return f"\033[38;2;{int(color[0:2], 16)};{int(color[2:4], 16)};{int(color[4:6], 16)}m"
    elif isinstance(color, (list, tuple)) and len(color) == 3:
        return f"\033[38;2;{color[0]};{color[1]};{color[2]}m"
    raise TypeError("Invalid color format. Expected tuple, list, string, or int string.")


def bg(color: Optional[Union[tuple, str, list, int]] = None) -> str:
    """
    Returns the ANSI escape code for background text color.

    Parameters:
        color (Union[tuple, str, list, int], optional): RGB color value as tuple, hex string, or integer. Defaults to None.

    Return:
        str: ANSI escape code for background color formatting

    Example of use:
        >>> import WizardCLI
        >>> print(WizardCLI.bg("FF0000") + "Red background" + WizardCLI.rst())
        >>> print(WizardCLI.bg((255, 0, 0)) + "Red background" + WizardCLI.rst())
        >>> print(WizardCLI.bg(0xFF0000) + "Red background" + WizardCLI.rst())
    """
    if color is None:
        return ""
    if isinstance(color, int):
        return f"\033[48;2;{(color>>16)&255};{(color>>8)&255};{color&255}m"
    elif isinstance(color, str):
        return f"\033[48;2;{int(color[0:2],16)};{int(color[2:4],16)};{int(color[4:6],16)}m"
    elif isinstance(color, (list, tuple)) and len(color) == 3:
        return f"\033[48;2;{color[0]};{color[1]};{color[2]}m"
    raise TypeError("Invalid color format. Expected tuple, list, string, or int string.")


def rst() -> str:
    """Returns the ANSI escape code to reset text formatting to default.

    This function is used to reset any applied text formatting, such as colors, bold, italic, underline, etc., back to the terminal's default state.

    Return:
        str: ANSI escape code to reset text formatting.

    Example of use:
        >>> import WizardCLI
        >>> print(WizardCLI.rst() + "Default text")
    """
    return "\033[0m"


def bld() -> str:
    """Returns the ANSI escape code for bold text formatting.

    This function is used to apply bold styling to text in the terminal.

    Return:
        str: ANSI escape code for bold text.

    Example of use:
        >>> import WizardCLI
        >>> print(WizardCLI.bld() + "Bold text" + WizardCLI.rst())
    """
    return "\033[1m"


def itl() -> str:
    """Returns the ANSI escape code for italic text formatting.

    This function is used to apply italic styling to text in the terminal. Note that not all terminals support italic text.

    Return:
        str: ANSI escape code for italic text.

    Example of use:
        >>> import WizardCLI
        >>> print(WizardCLI.itl() + "Italic text" + WizardCLI.rst())
    """
    return "\033[3m"


def und() -> str:
    """Returns the ANSI escape code for underlined text formatting.

    This function is used to underline text in the terminal.

    Return:
        str: ANSI escape code for underlined text.

    Example of use:
        >>> import WizardCLI
        >>> print(WizardCLI.und() + "Underlined text" + WizardCLI.rst())
    """
    return "\033[4m"


def rev() -> str:
    """Returns the ANSI escape code for reversed text color formatting.

    This function is used to swap the foreground and background colors of text in the terminal.

    Return:
        str: ANSI escape code for reversed text color.

    Example of use:
        >>> import WizardCLI
        >>> print(WizardCLI.rev() + "Reversed text" + WizardCLI.rst())
    """
    return "\033[7m"


def strk() -> str:
    """Returns the ANSI escape code for strikethrough text formatting.

    This function is used to apply a strikethrough effect to text in the terminal. Note that not all terminals support strikethrough text.

    Return:
        str: ANSI escape code for strikethrough text.

    Example of use:
        >>> import WizardCLI
        >>> print(WizardCLI.strk() + "Strikethrough text" + WizardCLI.rst())
    """
    return "\033[9m"


@lru_cache(maxsize=256)
def __RGBA(path: str, width: int, height: int) -> str:
    """Converts an image to colored ASCII with alpha channel management."""
    result = []
    last_color = None
    append = result.append
    for r, g, b, a in Image.open(path).resize((width, height), Image.Resampling.BILINEAR).getdata():
        if a < 51:
            append(" ")
        elif a < 102:
            if last_color == (r, g, b):
                append("░")
            else:
                append(f"\033[38;2;{r};{g};{b}m░")
                last_color = (r, g, b)
        elif a < 153:
            if last_color == (r, g, b):
                append("▒")
            else:
                append(f"\033[38;2;{r};{g};{b}m▒")
                last_color = (r, g, b)
        elif a < 204:
            if last_color == (r, g, b):
                append("▓")
            else:
                append(f"\033[38;2;{r};{g};{b}m▓")
                last_color = (r, g, b)
        else:
            if last_color == (r, g, b):
                append("█")
            else:
                append(f"\033[38;2;{r};{g};{b}m█")
                last_color = (r, g, b)
    lines = ["".join(result[i:i+width]).rstrip(" ") for i in range(0, len(result), width)]
    return "".join(("\n".join(lines), "\033[0m"))

@lru_cache(maxsize=128)
def __RGB(path: str, width: int, height: int, mode: bool = True) -> str:
    """Converts an image to colored ASCII without alpha channel management."""
    result = []
    last_color = None
    append = result.append
    if mode:
            pixels = Image.open(path).resize((width, height), Image.Resampling.BILINEAR).getdata()
    else:
        pixels = Image.open(path).convert("RGB").resize((width, height), Image.Resampling.BILINEAR).getdata()
    for r, g, b in pixels:
        if last_color == (r, g, b):
            append("█")
        else:
            append(f"\033[38;2;{r};{g};{b}m█")
            last_color = (r, g, b)
    lines = ["".join(result[i:i+width]) for i in range(0, len(result), width)]
    return "".join(("\n".join(lines), "\033[0m"))

@lru_cache(maxsize=32)
def __P(path: str, width: int, height: int) -> str:
    """Converts an image to colored ASCII with transparency handling."""
    result = []
    last_color = None
    append = result.append
    for r, g, b, a in Image.open(path).convert("RGBA").resize((width, height), Image.Resampling.BILINEAR).getdata():
        if not a:
            append(" ")
        if last_color == (r, g, b):
            append("█")
        else:
            append(f"\033[38;2;{r};{g};{b}m█")
            last_color = (r, g, b)
    lines = ["".join(result[i:i+width]).rstrip(" ") for i in range(0, len(result), width)]
    return "".join(("\n".join(lines), "\033[0m"))

def strimg(path: str, width: Optional[int] = None, height: Optional[int] = None, termadj: Optional[bool] = False) -> str:
    """
        Converts an image into a colored text representation faithful to the original image.

        Parameters:
            path (str): Path to the image file.
            width (Optional[int]): Desired output width. If None, calculated automatically.
            height (Optional[int]): Desired output height. If None, calculated automatically.
            termadj (Optional[bool]): If True, constrains output size to terminal dimensions.

        Returns:
            str: Colored text representation of the image.

        Example of use:
            result = strimg("image.png", width=80, termadj=True)
    """
    try:
        img = Image.open(path)
    except FileNotFoundError:
        raise FileNotFoundError(f"Image file '{path}' not found.")
    term_width, term_height = get_terminal_size(fallback=(80, 24))
    img_ratio = (img.width / img.height) * 1.8

    if width is None and height is None:
        if img_ratio < 1:
            width = term_width
            height = width / img_ratio
        elif img_ratio > 1:
            height = term_height
            width = height * img_ratio
        else:
            width = term_width
            height = term_height * 1.8
    elif width is None:
        width = height * img_ratio
    elif height is None:
        height = width / img_ratio
    else:
        if width / height > img_ratio:
            height = width / img_ratio
        else:
            width = height * img_ratio

    if termadj:
        if width > term_width:
            if img_ratio < 1:
                width = term_width
                height = width / img_ratio
            else:
                height = term_height
                width = height * img_ratio
        if height > term_height:
            if img_ratio < 1:
                height = term_height
                width = height * img_ratio
            else:
                width = term_width
                height = width / img_ratio
    width = round(width)
    height = round(height)
    if img.mode == "RGBA":
        return __RGBA(path, width, height)
    elif img.mode == "P":
        return __P(path, width, height)
    elif img.mode == "RGB":
        return __RGB(path, width, height, True)
    else:
        return __RGB(path, width, height, False)

del lru_cache