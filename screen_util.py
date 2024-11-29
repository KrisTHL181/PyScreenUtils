"""控制台输出工具. 风格为(y, x)而非(x, y)."""

import ctypes
import sys
import os
import unicodedata


class CursorSaver:
    def __init__(self) -> None:
        self.position = get_cursor_position()

    def save(self) -> None:
        self.position = get_cursor_position()

    def write(self, data: tuple) -> None:
        self.position = (data[0], data[1])

    def load(self) -> None:
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
        console_handle = ctypes.windll.kernel32.GetStdHandle(-11)

        csbi = CONSOLE_SCREEN_BUFFER_INFO()
        ctypes.windll.kernel32.GetConsoleScreenBufferInfo(
            console_handle,
            ctypes.byref(csbi),
        )

        return csbi.dwCursorPosition.Y, csbi.dwCursorPosition.X

    def goto(y, x):
        console_handle = ctypes.windll.kernel32.GetStdHandle(-11)

        coord = COORD(x, y)
        ctypes.windll.kernel32.SetConsoleCursorPosition(console_handle, coord)

    def getch() -> str:
        ch = msvcrt.getch()
        return ch if isinstance(ch, str) else ch.decode("utf-8")

    def getwch() -> str:
        ch = msvcrt.getwch()
        return ch if isinstance(ch, str) else ch.decode("utf-8")

    def enable_term_color() -> int:
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
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    def getwch() -> str:
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.buffer.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch.decode("utf-8")

    def get_cursor_position():
        return curses.getyx()

    def goto(y, x):
        curses.setsyx(y, x)

    def enable_term_color() -> int:
        return 0


def get_real_length(char: str) -> int:
    length = 0
    for last_char in char:
        if unicodedata.east_asian_width(last_char) in "WF":
            length += 2
        else:
            length += 1
    return length


def clear():
    sys.stderr.write("\033c")
    sys.stderr.flush()


def get_term_size() -> tuple:
    return os.get_terminal_size()[::-1]


def __hex_to_rgb(hex_color: str) -> tuple:
    hex_color = hex_color.lstrip("#")

    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)

    return r, g, b


def print_rgb_color(color: str | tuple[int, int, int], text: str):
    """
    在终端中打印指定RGB颜色的文本。

    :param r: 红色分量 (0-255)
    :param g: 绿色分量 (0-255)
    :param b: 蓝色分量 (0-255)
    :param text: 要打印的文本
    """
    rgb_escape = f"\033[38;2;{';'.join(map(str, color)) if isinstance(color, tuple) else ';'.join(map(str, __hex_to_rgb(color)))}m"
    reset_escape = "\033[0m"

    sys.stdout.write(f"{rgb_escape}{text}{reset_escape}")
    sys.stdout.flush()


if __name__ == "__main__":
    import time
    import colorsys

    def hsv_to_rgb(h, s, v):
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return int(r * 255), int(g * 255), int(b * 255)

    # 清屏
    clear()

    # 初始化光标保存器
    cursor_saver = CursorSaver()

    # 移动光标到(5, 10)位置并打印一些文本
    goto(5, 10)
    print("Hello, World!")

    # 保存当前光标位置
    cursor_saver.save()

    # 移动光标到(10, 5)位置并打印一些文本
    goto(10, 5)
    print("Moved Cursor")

    # 暂停1秒以便观察
    time.sleep(1)

    # 恢复光标到之前保存的位置
    cursor_saver.load()

    # 打印一些文本以确认光标位置恢复
    print("Cursor Restored!")

    h = 0
    while h <= 1:
        rgb = hsv_to_rgb(h, 1.0, 1.0)
        hex_color = "#{:02x}{:02x}{:02x}".format(rgb[0], rgb[1], rgb[2])
        for char in "RGB Color Demo|":
            print_rgb_color(rgb, char)
        h += 0.003

    getwch()
