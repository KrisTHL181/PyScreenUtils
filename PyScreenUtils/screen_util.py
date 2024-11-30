"""控制台输出工具. 风格为(y, x)而非(x, y)."""

import ctypes
import sys
import os
import unicodedata


class CursorSaver:
    def __init__(self) -> None:
        """
        初始化光标保存器, 并保存当前光标位置.
        """
        self.position = get_cursor_position()

    def save(self) -> None:
        """
        保存当前光标位置.
        """
        self.position = get_cursor_position()

    def write(self, data: tuple) -> None:
        """
        设置光标位置.
        
        参数:
            data (tuple): 光标的新位置, 格式为(y, x).
        """
        self.position = (data[0], data[1])

    def load(self) -> None:
        """
        将光标恢复到保存的位置.
        """
        return goto(*self.position)


if os.name == "nt":
    import msvcrt

    class COORD(ctypes.Structure):
        _fields_ = [("X", ctypes.c_short), ("Y", ctypes.c_short)]

    class SMALL_RECT(ctypes.Structure):
        _fields_ = [
            ("Left", ctypes.c_short),
            ("Top", ctypes.c_short),
            ("Right", ctypes.c_short),
            ("Bottom", ctypes.c_short),
        ]

    class CONSOLE_SCREEN_BUFFER_INFO(ctypes.Structure):
        _fields_ = [
            ("dwSize", COORD),
            ("dwCursorPosition", COORD),
            ("wAttributes", ctypes.c_short),
            ("srWindow", SMALL_RECT),
            ("dwMaximumWindowSize", COORD),
        ]

    def get_cursor_position():
        """
        获取当前光标位置.
        
        返回:
            tuple: 光标位置, 格式为(y, x).
        """
        console_handle = ctypes.windll.kernel32.GetStdHandle(-11)

        csbi = CONSOLE_SCREEN_BUFFER_INFO()
        ctypes.windll.kernel32.GetConsoleScreenBufferInfo(
            console_handle,
            ctypes.byref(csbi),
        )

        return csbi.dwCursorPosition.Y, csbi.dwCursorPosition.X

    def goto(y, x):
        """
        将光标移动到指定位置.
        
        参数:
            y (int): 目标位置的行号.
            x (int): 目标位置的列号.
        """
        console_handle = ctypes.windll.kernel32.GetStdHandle(-11)

        coord = COORD(x, y)
        ctypes.windll.kernel32.SetConsoleCursorPosition(console_handle, coord)

    def getch() -> str:
        """
        获取一个字符输入, 不等待回车.
        
        返回:
            str: 用户输入的字符.
        """
        ch = msvcrt.getch()
        return ch if isinstance(ch, str) else ch.decode("utf-8")

    def getwch() -> str:
        """
        获取一个宽字符输入, 不等待回车.
        
        返回:
            str: 用户输入的宽字符.
        """
        ch = msvcrt.getwch()
        return ch if isinstance(ch, str) else ch.decode("utf-8")

    def enable_term_color() -> int:
        """
        启用终端颜色支持.
        
        返回:
            int: 0表示成功, 其他值表示错误代码.
        """
        h_out = ctypes.windll.kernel32.GetStdHandle(-11)
        if h_out == ctypes.c_void_p(-1).value:
            return ctypes.get_last_error()

        dw_mode = ctypes.c_ulong()
        if not ctypes.windll.kernel32.GetConsoleMode(h_out, ctypes.byref(dw_mode)):
            return ctypes.get_last_error()

        dw_mode.value |= 4
        if not ctypes.windll.kernel32.SetConsoleMode(h_out, dw_mode):
            return ctypes.get_last_error()
        return 0

else:
    import curses
    import tty
    import termios

    def getch() -> str:
        """
        获取一个字符输入, 不等待回车.
        
        返回:
            str: 用户输入的字符.
        """
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    def getwch() -> str:
        """
        获取一个宽字符输入, 不等待回车.
        
        返回:
            str: 用户输入的宽字符.
        """
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.buffer.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch.decode("utf-8")

    def get_cursor_position():
        """
        获取当前光标位置.
        
        返回:
            tuple: 光标位置, 格式为(y, x).
        """
        return curses.getyx()

    def goto(y, x):
        """
        将光标移动到指定位置.
        
        参数:
            y (int): 目标位置的行号.
            x (int): 目标位置的列号.
        """
        curses.setsyx(y, x)

    def enable_term_color() -> int:
        """
        启用终端颜色支持.
        
        返回:
            int: 总是返回0, 在unix系统下我们无法直接开启tty的颜色支持.
        """
        return 0


def get_real_length(char: str) -> int:
    """
    获取字符串的实际显示长度, 考虑宽字符.
    
    参数:
        char (str): 要计算长度的字符串.
    
    返回:
        int: 字符串的实际显示长度.
    """
    length = 0
    for last_char in char:
        if unicodedata.east_asian_width(last_char) in "WF":
            length += 2
        else:
            length += 1
    return length


def clear():
    """
    清除终端屏幕.
    """
    sys.stderr.write("\033c")
    sys.stderr.flush()


def get_term_size() -> tuple:
    """
    获取终端的尺寸.
    
    返回:
        tuple: 终端的尺寸, 格式为(width, height).
    """
    return os.get_terminal_size()[::-1]


def __hex_to_rgb(hex_color: str) -> tuple:
    """
    将十六进制颜色代码转换为RGB颜色值.

    参数:
        hex_color (str): 十六进制颜色代码, 例如"#ff5733".

    返回:
        tuple: RGB颜色值, 格式为(r, g, b).
    """
    hex_color = hex_color.lstrip("#")

    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)

    return r, g, b


def print_rgb_color(color: str | tuple[int, int, int], text: str):
    """
    在终端中打印指定RGB颜色的文本.

    参数:
        color (str | tuple): RGB颜色值或十六进制颜色代码.
        text (str): 要打印的文本.
    """
    rgb_escape = f"\033[38;2;{';'.join(map(str, color)) if isinstance(color, tuple) else ';'.join(map(str, __hex_to_rgb(color)))}m"
    reset_escape = "\033[0m"

    sys.stdout.write(f"{rgb_escape}{text}{reset_escape}")
    sys.stdout.flush()


if __name__ == "__main__":
    import time
    import colorsys

    def hsv_to_rgb(h, s, v):
        """
        将HSV颜色值转换为RGB颜色值.
        
        参数:
            h (float): 色调 (0.0-1.0)
            s (float): 饱和度 (0.0-1.0)
            v (float): 明度 (0.0-1.0)
        
        返回:
            tuple: RGB颜色值, 格式为(r, g, b).
        """
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return int(r * 255), int(g * 255), int(b * 255)

    cursor_saver = CursorSaver()

    goto(5, 10)
    print("Hello, World!")

    cursor_saver.save()

    goto(10, 5)
    print("Moved Cursor")

    time.sleep(1)

    cursor_saver.load()

    print("Cursor Restored!")

    h = 0
    while h <= 1:
        rgb = hsv_to_rgb(h, 1.0, 1.0)
        hex_color = "#{:02x}{:02x}{:02x}".format(rgb[0], rgb[1], rgb[2])
        for char in "RGB Color Demo|":
            print_rgb_color(rgb, char)
        h += 0.003

    getwch()
