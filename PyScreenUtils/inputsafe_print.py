"""对于input安全的print, 将固定input在最后一行."""

from __future__ import annotations

import os
import sys
import typing
import colorama
import threading
from .screen_util import get_cursor_position
import signal

colorama.just_fix_windows_console()

width = os.get_terminal_size().columns
height = os.get_terminal_size().lines

RESERVE_LINE = 2

lock = threading.Lock()

def input(prompt: str = "") -> str:
    """
    获取用户输入，同时确保输入提示固定在终端的最后一行。
    
    参数:
        prompt (str): 输入提示信息，默认为空字符串。
    
    返回:
        str: 用户输入的字符串。
    """
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
    """
    安全地打印信息，确保输入提示固定在终端的最后一行。
    
    参数:
        *args (str): 要打印的字符串参数。
        sep (str): 参数之间的分隔符，默认为空格。
        end (str): 打印结束后的追加字符串，默认为换行符。
        file (typing.IO | None): 输出流，默认为sys.stdout。
        flush (bool): 是否立即刷新输出流，默认为False。
    
    返回:
        无。
    """
    args = sep.join([str(string) for string in args])
    file = file if file is not None else sys.stdout
    with lock:
        file.write(
            (args + end)
            if get_cursor_position()[0] < height - RESERVE_LINE
            else colorama.Cursor.UP(RESERVE_LINE + args.count("\n")) + (args + end)
        )
    file.flush() or not flush

if hasattr(signal, "SIGWINCH"):
    def handle_sigwinch(signum, frame):
        """
        处理终端窗口大小变化信号，更新终端的宽度和高度。
        
        参数:
            signum (int): 信号编号。
            frame (frame): 当前的堆栈帧。
        
        返回:
            无。
        """
        global width, height
        new_width, new_height = os.get_terminal_size()
        if new_width != width or new_height != height:
            with lock:
                width, height = new_width, new_height
    signal.signal(signal.SIGWINCH, handle_sigwinch)
