import unicodedata
from .screen_util import CursorSaver, getwch, goto, get_cursor_position, get_real_length
import sys


def clear_input(start_pos: tuple, length: int) -> None:
    """
    清除指定位置开始的输入区域。

    参数:
    start_pos (tuple): 起始位置，格式为 (y, x)。
    length (int): 要清除的字符长度。
    """
    goto(*start_pos)
    for _ in range(length):
        sys.stdout.write(" ")

    sys.stdout.flush()


def input(
    prompt: str = "", pos=None, key_callbacks: dict = {}, max_length: int = -1
) -> str:
    """
    自定义输入函数，支持自定义提示、位置、按键回调以及最大输入长度。

    参数:
    prompt (str): 输入提示信息。
    pos (tuple, 可选): 输入起始位置，格式为 (行, 列)。
    key_callbacks (dict, 可选): 按键回调字典，键为按键字符，值为回调函数。
    max_length (int, 可选): 最大输入长度，-1 表示无限制。

    返回:
    str: 用户输入的字符串。
    """
    user_input = []
    cursor_saver = CursorSaver()
    cursor_saver.save()

    if pos is not None:
        goto(*pos)

    _start_pos = get_cursor_position()
    sys.stdout.write(prompt)
    sys.stdout.flush()

    while True:
        char = getwch()
        key_callbacks.get(char, lambda: None)()
        if char in ("\r", "\n"):
            break
        elif char == "\b":
            if user_input:
                last_char = user_input.pop()
                width = unicodedata.east_asian_width(last_char)
                if width in "WF":
                    sys.stdout.write("\b \b \b\b")
                else:
                    sys.stdout.write("\b \b")
                sys.stdout.flush()
        else:
            user_input.append(char)
            sys.stdout.write(char)
            sys.stdout.flush()
            if max_length != -1 and len(user_input) >= max_length:
                break
    result = "".join(user_input)
    clear_input(_start_pos, get_real_length(prompt + result))
    cursor_saver.load()

    return result


# 示例使用
if __name__ == "__main__":
    key_callbacks = {}

    user_input = input(
        "请输入内容：", key_callbacks=key_callbacks, max_length=160, pos=(10, 5)
    )
    print(f" 您输入的内容是：{repr(user_input)}")
