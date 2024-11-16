"""对于input安全的print, 将固定input在最后一行."""

from __future__ import annotations

import os
import sys
import typing
import colorama
import threading
from screen_util import get_cursor_position
import signal

width = os.get_terminal_size().columns
height = os.get_terminal_size().lines

RESERVE_LINE = 2


lock = threading.Lock()


def handle_sigwinch(signum, frame):
    global width, height
    new_width, new_height = os.get_terminal_size()
    if new_width != width or new_height != height:
        with lock:
            width, height = new_width, new_height


def input(prompt: str = "") -> str:
    with lock:
        sys.stdout.write(colorama.Cursor.POS(0, height) + prompt)
        sys.stdout.flush()
    result = sys.stdin.readline().strip()
    return result


def print(
    *args: str,
    sep: str = " ",
    end: str = "\n",
    file: typing.IO | None = None,
    flush: bool = False,
) -> None:
    args = sep.join([str(string) for string in args])
    file = file if file is not None else sys.stdout
    with lock:
        file.write(
            (args + end)
            if get_cursor_position()[0] < height - RESERVE_LINE
            else colorama.Cursor.UP(RESERVE_LINE + args.count("\n")) + (args + end)
        )
        file.flush() or not flush


signal.signal(signal.SIGWINCH, handle_sigwinch)
