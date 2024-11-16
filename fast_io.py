"""原作者:量子态发圈
链接:https://www.acwing.com/blog/content/29692/
来源:AcWing
改进:KrisTHL181

该功能不适合日用.
"""

import os
import sys
from io import BytesIO, IOBase

_str = str


def str(string=b""):
    return string if type(string) is bytes else _str(string).encode()


BUFSIZE = 8192


class FastIO(IOBase):
    newlines = 0

    def __init__(self, file):
        self._fd = file.fileno()
        self.buffer = BytesIO()
        self.writable = "x" in file.mode or "r" not in file.mode
        self.write = self.buffer.write if self.writable else None
        self.size = max(os.fstat(self._fd).st_size, BUFSIZE)

    def read(self):
        while True:
            b = os.read(self._fd, self.size)
            if not b:
                break
            self.buffer.seek(0, 2), self.buffer.write(b), self.buffer.seek(
                self.buffer.tell()
            )
        self.newlines = 0
        return self.buffer.read()

    def readline(self):
        while self.newlines == 0:
            b = os.read(self._fd, self.size)
            self.newlines = b.count(b"\n") + (not b)
            self.buffer.seek(0, 2), self.buffer.write(b), self.buffer.seek(
                self.buffer.tell()
            )
        self.newlines -= 1
        return self.buffer.readline()

    def flush(self):
        if self.writable:
            os.write(self._fd, self.buffer.getvalue())
            self.buffer.truncate(0), self.buffer.seek(0)


class IOWrapper(IOBase):
    def __init__(self, file):
        self.buffer = FastIO(file)
        self.flush = self.buffer.flush
        self.writable = self.buffer.writable
        self.write = lambda s: self.buffer.write(s.encode("ascii"))
        self.read = lambda: self.buffer.read().decode("ascii")
        self.readline = lambda: self.buffer.readline().decode("ascii")


def input():
    return sys.stdin.readline().rstrip("\r\n")


if __name__ == "__main__":
    print(
        "sys.stdin = IOWrapper(sys.stdin)\nsys.stdout = IOWrapper(sys.stdout)\nsys.stderr = IOWrapper(sys.stderr)"
    )
