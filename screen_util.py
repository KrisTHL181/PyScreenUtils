import ctypes
import sys
import os

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

else:
    import curses
    import sys
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
        return ch if isinstance(ch, str) else ch.decode("utf-8")

    def get_cursor_position():
        return curses.getyx()

    def goto(y, x):
        curses.setsyx(y, x)


# 示例使用
if __name__ == "__main__":
    if os.name == "nt":
        print("检测到NT类系统.")
        print("当前光标位置:", get_cursor_position())
        goto(5, 10)
        print("移动后的光标位置:", get_cursor_position())
    else:
        # 初始化curses
        stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        stdscr.keypad(True)

        try:
            print("当前光标位置:", get_cursor_position())
            goto(5, 10)
            stdscr.addstr(5, 10, "移动后的光标位置")
            stdscr.refresh()
            stdscr.getch()
        finally:
            # 恢复终端设置
            curses.nocbreak()
            stdscr.keypad(False)
            curses.echo()
            curses.endwin()
