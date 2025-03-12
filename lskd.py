"""
### Local Scope Keyboard Detector
Sugar syntaxed version of Microsoft Visual C Runtime (msvcrt) Library with a bit more feature
"""

import msvcrt
import ctypes
from ctypes import wintypes

user32 = ctypes.WinDLL("user32", use_last_error=True)
user32.GetKeyState.restype = wintypes.SHORT
user32.GetKeyState.argtypes = [wintypes.INT]

__SHIFT = 0x10
__CONTROL = 0x11
__MENU = 0x12
__APP_HANDLE = user32.GetForegroundWindow()


class __Modifier:
    global user32

    def __init__(self, shift, control, menu, app_handle):
        self.__SHIFT = shift
        self.__CONTROL = control
        self.__MENU = menu
        self.__APP_HANDLE = app_handle

    def get(self, type: str = "") -> tuple[bool, bool, bool]:
        """
        shift, control, alt. \n
        capture certain modifier key by calling the name in the parameter.
        """

        # record only when runner window is focused
        if not user32.GetForegroundWindow() == self.__APP_HANDLE:
            return False, False, False

        if type == "shift":
            return user32.GetKeyState(self.__SHIFT) & 0x8000 != 0
        elif type == "control":
            return user32.GetKeyState(self.__CONTROL) & 0x8000 != 0
        elif type == "alt":
            return user32.GetKeyState(self.__MENU) & 0x8000 != 0
        else:
            return (
                user32.GetKeyState(self.__SHIFT) & 0x8000 != 0,
                user32.GetKeyState(self.__CONTROL) & 0x8000 != 0,
                user32.GetKeyState(self.__MENU) & 0x8000 != 0,
            )


class __Char:
    def get(self, wide: bool = False) -> bytes | str:
        if any(modifier.get()):
            return None
        return msvcrt.getwch() if wide else msvcrt.getch()

    def put(self, char: str | bytes | bytearray, wide=False) -> None:
        msvcrt.putwch(char) if wide else msvcrt.putch(char)

    def push(self, char: str | bytes | bytearray, wide: bool = False) -> None:
        msvcrt.ungetwch(char) if wide else msvcrt.ungetch(char)


char = __Char()
modifier = __Modifier(__SHIFT, __CONTROL, __MENU, __APP_HANDLE)
sequence_code = (b"\xe0", b"\x00")
special_key = (b"\x1b", b"\x08", b"\t", b"\r")


def on_press() -> None:
    return msvcrt.kbhit() or any(modifier.get())


# clutterfuck of something that i've forgot
def __internal_translate(char, special=False):
    if char == None:
        return None

    try:
        if not special:
            return {
                b"\x1b": "ESC",
                b"\x08": "BACKSPACE",
                b"\t": "TAB",
                b"\r": "ENTER",
                b" ": "SPACE",
            }[char]
        elif special:
            return {
                b"H": "UP",
                b"P": "DOWN",
                b"K": "LEFT",
                b"M": "RIGHT",
                b"R": "INSERT",
                b"S": "DELETE",
                b"G": "HOME",
                b"O": "END",
                b"I": "PG_UP",
                b"Q": "PG_DOWN",
                b";": "F1",
                b"<": "F2",
                b"=": "F3",
                b">": "F4",
                b"?": "F5",
                b"@": "F6",
                b"A": "F7",
                b"B": "F8",
                b"C": "F9",
                b"D": "F10",
                b"\x85": "F11", # reserved. might not be recordable
                b"\x86": "F12",
            }[char]

    except KeyError:
        return char.decode()


def translate(key_content, last_key) -> str | None:
    """
    translate raw bytes Sequence into a more readable form
    """
    if last_key in sequence_code:
        key_content = __internal_translate(key_content, last_key)
    elif not key_content in sequence_code:
        key_content = __internal_translate(key_content)
    return key_content
