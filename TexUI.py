"""
Let's create TUI with ease! (POSIX-compliant system only)
"""

from __future__   import annotations
from os           import system, name, path
from sys          import path as sys_path

sys_path.append(path.dirname(path.realpath(__file__)))

from shutil       import get_terminal_size
from TexUI_module.\
datatype_extend   import *
from TexUI_module import helper_function
from typing       import Iterable, Literal, Tuple
from collections  import deque
from textwrap     import wrap as smart_wrap


class __Handler:
    def __init__(self):
        pass

    def is_valid_position(self, position: Position, max_size: Tuple[int, int]) -> bool:
        return (position.x >= 0 and position.y >= 0) and (  # no negative
            position.x < max_size[0] and position.y < max_size[1]
        )  # smaller or equal than terminal | fence-post warning: position < terminal_size


handler = __Handler()


def move_cursor(x: int, y: int) -> None:
    """
    Moves the cursor to a specified coordinate in the terminal.
    The top left corner of the terminal is considered as the origin (0, 0).
    """
    if not handler.is_valid_position(Position(x, y), get_terminal_size()):
        raise ValueError(
            f"Invalid position. Position must be within the terminal size ({x}, {y}) vs {
            get_terminal_size().columns}x{get_terminal_size().lines}."
        )

    print(f"\033[{y + 1};{x + 1}H", end="")


def clear_terminal() -> None:
    system("cls" if name == "nt" else "clear")


class Display:

    def __init__(
        self,
        width: int | Literal["full"] = "full",
        height: int | Literal["full"] = "full",
        default_fill=" ",
        no_terminal_bound: bool = False,
    ) -> None:
        """
        A Display that can be drawn on.

        ### Parametres
        - `width`: the width of the screen. Must be less or equal than terminal width. Use 'full' to set it to biggest it can go
        - `height`: the height of the screen. Must be less or equal than terminal height
        minus one (accounting newline after flushing). Use 'full' to set it to biggest it can go
        - `default_fill`: A character that is used as a background of the screen
        - `no_terminal_bound`: Allow display sizes to be greater than the terminal itself
        """

        # prepare
        global handler
        self.default_fill = default_fill
        self.terminal_width = get_terminal_size().columns
        self.terminal_height = (
            get_terminal_size().lines - 1
        )  # account for newline when done printing

        if isinstance(width, str) or width is None:
            if width != "full" or width is None:
                raise ValueError(
                    f"Invalid width value of {width!r}. Expected 'full' or integer."
                )

        if isinstance(height, str) or width is None:
            if height != "full" or width is None:
                raise ValueError(
                    f"Invalid height value of {height!r}. Expected 'full' or integer."
                )

        self.width = width if isinstance(width, int) else self.terminal_width
        self.height = height if isinstance(height, int) else self.terminal_height

        # validate
        if not handler.is_valid_position(
            Position(self.width, self.height),
            (
                get_terminal_size()[0] + 1,
                get_terminal_size()[1],
            ),  # bypass for when screen size == terminal size
        ) and any((not no_terminal_bound, self.width < 0 or self.height < 0)):
            raise ValueError(
                f"Invalid screen size of {self.width}x{self.height}. \
Expected integer above zero and within terminal size: {self.terminal_width}x{self.terminal_height}.\n\
Set no_terminal_bound to be True if you want to make display bigger than the terminal size."
            )

        Character(default_fill)

        self.content = [[default_fill] * self.width for _ in range(self.height)]

    def __str__(self):
        return f"Display object: {self.width}x{self.height} ({ \
        self.width * self.height}) | default fill: {self.default_fill}"

    def __contains__(self, item):
        for row in self.content:
            if item in row:
                return True
        return False

    def clear(self, reset: Literal["screen", "all"] = "screen"):
        """
        Clears the display, and or the terminal also
        """

        if reset in ["screen", "all"]:
            self.content = [
                [self.default_fill] * self.width for _ in range(self.height)
            ]
            if reset == "all":
                system("cls" if name == "nt" else "clear")
        else:
            raise ValueError(
                f"Invalid reset value of {reset!r}. Expected 'screen' or 'all'."
            )

    def flush(self, x: int | None = None, y: int | None = None) -> None:
        """
        Flushes the current state of the display into the terminal at position (x, y).
        """
        if not (x is None or isinstance(x, int)) or not (
            y is None or isinstance(y, int)
        ):
            raise ValueError(
                f"Invalid position. Expected integer or None, got {x!r} and {y!r}."
            )

        out = self.content[:]

        # Adjust y-position by moving cursor or trimming content
        if y is not None:
            if y >= 0:
                move_cursor(0, y)
            else:
                move_cursor(0, 0)
                out = out[abs(y) :]  # Trim top rows if y is negative

        # Process and format all rows before printing
        formatted_rows = []
        for row in out:
            row_str = "".join(row)

            if x is not None:
                if x < 0:
                    row_str = row_str[abs(x) :]  # Trim left side if x is negative
                if x + self.width > self.terminal_width:
                    row_str = row_str[
                        : self.terminal_width - x
                    ]  # Trim right side if exceeding terminal width
                formatted_rows.append(
                    f"\033[{max(0, min(x, self.terminal_width - 1)) - 1}C" + row_str
                )
            else:
                formatted_rows.append(row_str[: self.terminal_width])

        print("\n".join(formatted_rows))

    def get_char(self, x: int, y: int) -> Character:
        """
        Returns a character on x, y.

        ### Parametres
        `x`: x-coordinate of the character.
        `y`: y-coordinate of the character.

        ### Return
        Return a character (not a Character object. Just a string with lenght of one)
        """

        if not handler.is_valid_position(Position(x, y), (self.width, self.height)):
            raise ValueError(
                f"Invalid position. Position must be within the screen size ({x}, {y}) vs {self.width}x{self.height}."
            )

        return self.content[y][x]

    def draw_char(
        self,
        x: int,
        y: int,
        character: Character,
        mask_limit_character: Character | str = "",
    ) -> None:
        """
        Draws a character into the screen.

        ### Parametres
        - `x`: x-coordinate of the screen where the character will be drawn on.
        - `y`: y-coordinate of the screen where the character will be drawn on.
        - `character`: The character that will be drawn into.
        - `mask_limit_character`: At what the character only can be drawn on. Default is an empty string.

        """

        Character(character)

        if mask_limit_character != "":
            if not isinstance(mask_limit_character, str):
                raise ValueError(
                    f"Invalid mask_limit_text value of {mask_limit_character!r}. Expected string or character."
                )
            elif not mask_limit_character.isprintable():
                raise ValueError(
                    f"Invalid text_mask value of {mask_limit_character!r}. Expected non sequence code string or character."
                )

        if self.get_char(x, y) in mask_limit_character or mask_limit_character == "":
            self.content[y][x] = character

    def draw_line(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        character: Character | str | Iterable[str],
        mask_limit_character: Character | str | Iterable[str] = "",
    ):
        """
        Draws line from x1, y1 to x2, y2 using Bresenham's Line Algorithm.

        ### Parametres
        - `x1`: x-coordinate of first corner.
        - `y1`: y-coordinate of first corner.
        - `x2`: x-coordinate of second corner.
        - `y2`: y-coordinate of second corner.
        - `character`: What character the line will be made of. If iterable is given, then it'll be used as pattern.
        - `mask_limit_character`: At what the line only can be drawn on. Default is an empty string.
        """
        if character != "":
            if not isinstance(character, str):
                raise ValueError(
                    f"Invalid text_mask value of {character!r}. Expected string or character."
                )
            elif not character.isprintable():
                raise ValueError(
                    f"Invalid text_mask value of {character!r}. Expected non sequence code string or character."
                )

        if mask_limit_character != "":
            if not isinstance(mask_limit_character, str):
                raise ValueError(
                    f"Invalid mask_limit_text value of {mask_limit_character!r}. Expected string or character."
                )
            elif not mask_limit_character.isprintable():
                raise ValueError(
                    f"Invalid text_mask value of {mask_limit_character!r}. Expected non sequence code string or character."
                )

        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy

        c = 0
        while True:
            try:
                if (
                    self.get_char(x1, y1) in mask_limit_character
                ) or mask_limit_character == "":
                    self.content[y1][x1] = character[c % len(character)]
            except (IndexError, ValueError):
                pass

            # fence-post warning: x, y < display size
            # x, y   : 0, 1, 2 <- +1 then x > width ?
            # screen : 1, 2, 3
            if (x1 == x2 and y1 == y2) or (x1 + 1 > self.width or y1 + 1 > self.height):
                break

            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x1 += sx
            if e2 < dx:
                err += dx
                y1 += sy

            c += 1

    def draw_str(
        self,
        x: int,
        y: int,
        text: str | list[str],
        max_width: int | str = 0,
        max_line: int = 0,
        edge_of_screen: Literal["default", "newline", "preserve"] = "default",
        text_mask: Character | str = "",
        mask_limit_text: Character | str = "",
        foward: dict = {},
        ellipsis: dict = {},
        indent: int = 0,
        calc_only: bool = False,
    ) -> dict:
        """
        Draws a string or a list of string to the screen.

        ### Parametres
        - `x`: x-coordinate of the screen where the string will be drawn into.
        - `y`: y-coordinate of the screen where the string will be drawn into.
        - `text`: The content that will be drawn. Can take multiline string and a list of string.
        - `max_width` Limit on how long the string can be before getting drawn onto new line. can take 2 different input:
            - `integer`: Cut the text after the limit is reached.
            - `preserve-<int>`: Cut the text after the limit is reached while also trying to preserve the word in text
        - `edge_of_screen`: Behavior on when the text is outside the display screen.
            - `default`: Will stop drawing if on outside.
            - `newline`: Countinue drawing on new line.
            - `preserve`: Countinue drawing on new line while also preserving the word.
        - `text_mask`: What character should be skipped on drawing. Default is an empty string.
        - `mask_limit_text`: At what the string only can be drawn on. Default is an empty string.
        - `foward`: Direction the string will be drawn to. A dict with content of
        `{'action': bool, *'preserve': bool, *'anchour': Literal['left', 'right']}`. *optional
        - `max_line`: How much line of string it allowed to be drawn. The default is 0 (draw all).
        - `ellipsis`: A dict determining the behaviour of ellipsis. Containing
        `{'symbol': Character, 'count': int >= 0, *'at': Literal['all', 'max line', 'screen edge']}`. *optional
            - `all`: Draw if any of the below is true
            - `max line`: Only draw on the end of line.
            - `screen edge`: Only draw if the text intersect the bottom of the screen.
        - `indent`: Amount of space added before every line. Only work if anchoured on left. See `foward`.
        - `calc_only`: Disable drawing onto screen, and only return result of the method.

        ### Return
        Return a dictonary which consist of 4 integer that corespond to left, top, right, bottom side of bordering text,
        and a list containing the processed text (excluding masking)

        ### Behavior
        Any control characters will be removed from the string. \n
        The text will be splited on `\\n`.\n
        the text will be splitted on new line and then splitted again using warp.
        Indent is added after the text is cleaned
        """

        """
        helper function ----------------------------------------------------------------------------------------------
        """

        # max width --------------------------------------------------------------------------------------------------
        def apply_max_width(text: list, width: int, preserve: bool):
            text = (
                [smart_wrap(line, width) for line in text]  # smart warp
                if preserve
                else [  # basic cut
                    helper_function.chunk_split(line, width) for line in text
                ]
            )

            # smart warp turn empty string into empty list. change it back to str
            text = [word if word != [] else [""] for word in text]

            text = helper_function.flatten_list(text)
            return text

        def apply_ellipsis(line: str, symbol: str, count: int):
            if count > len(line):
                return symbol * len(line)
            else:
                return line[:-count] + symbol * count

        def apply_advance_ellipsis():
            if not foward["action"] and foward["preserve"]:
                text[-1] = (
                    ellipsis["symbol"] * ellipsis["count"]
                    + text[-1][ellipsis["count"] :]
                    if len(text[-1]) >= ellipsis["count"]
                    else ellipsis["symbol"] * len(text[-1])
                )
            else:
                text[-1] = apply_ellipsis(
                    text[-1], ellipsis["symbol"], ellipsis["count"]
                )

            # print("a", text, len(text[-1]) ,"<=", ellipsis["count"])

        """
        validation ---------------------------------------------------------------------------------------------------
        """
        # coordinate -------------------------------------------------------------------------------------------------
        if (
            not handler.is_valid_position(Position(x, y), (self.width, self.height))
            and x >= 0  # allow x and y to be above and left of screen
            and y >= 0
        ):
            raise ValueError(
                f"Invalid position. Position must be within the screen size ({x}, {y}) vs {self.width}x{self.height}."
            )

        # text -------------------------------------------------------------------------------------------------------

        # turn str into list for easier processing
        text = [text] if isinstance(text, str) else text

        # if isinstance(text, list):
        if text != helper_function.flatten_list(text):
            raise ValueError(
                f"""Invalid text. Expected list[str], got {helper_function.deep_typeof(text)}: {text!r}.
If your text somehow is a nested list, then maybe it's the time to rethink your choice."""
            )

        else:
            for thing in text:
                if not isinstance(thing, str):
                    raise ValueError(
                        f"Invalid text. Expected list[str], got {helper_function.deep_typeof(text)}."
                    )

        # max width --------------------------------------------------------------------------------------------------
        preserve_width = False

        # Check if max_width is an integer
        if isinstance(max_width, int):
            pass
        # Check if max_width is a valid string with "preserve-<width>"
        elif isinstance(max_width, str) and max_width.startswith("preserve-"):
            try:
                max_width = int(max_width.removeprefix("preserve-"))
                preserve_width = True
            except ValueError:
                raise ValueError(
                    f"Invalid max_width value of {max_width!r}. Expected integer or a string of 'preserve-<width>'."
                )
        # Raise an error if max_width is of an invalid type or format
        else:
            raise ValueError(
                f"Invalid max_width value of {max_width!r}. Expected integer or a string of 'preserve-<width>'."
            )

        # edge of screen ---------------------------------------------------------------------------------------------
        if not edge_of_screen in ["default", "newline", "preserve"]:
            raise ValueError(
                f"Invalid edge_of_screen value of {edge_of_screen!r}. Expected 'default', 'newline', or 'preserve'."
            )

        # max line ---------------------------------------------------------------------------------------------------
        if isinstance(max_line, int):
            if max_line < 0:
                raise ValueError(
                    f"Invalid max_line value of {max_line!r}. Expected positive integer"
                )
        else:
            raise ValueError(
                f"Invalid max_line. Expected integer, got {type(max_line)!r}."
            )

        # foward -----------------------------------------------------------------------------------------------------

        # reverse_action = ""
        if foward != {}:
            if not isinstance(foward, dict):
                raise ValueError(
                    f"Invalid foward. Expected dict, got {helper_function.deep_typeof(foward)!r}."
                )
            else:
                for key, value in foward.items():
                    if not isinstance(key, str):
                        raise ValueError(
                            f"Invalid key in foward. Expected str, got {type(foward)!r}."
                        )

                    if key not in ["action", "preserve", "anchour"]:
                        raise ValueError(
                            f"Invalid key in foward. Expected 'action', 'preserve', or 'anchour'. got {foward!r}."
                        )

                    if key == "action":
                        if not isinstance(value, bool):
                            raise ValueError(
                                f"Invalid 'action' value in foward. Expected bool, got {value!r}."
                            )

                    elif key == "preserve":
                        if not isinstance(value, bool):
                            raise ValueError(
                                f"Invalid 'preserve' value in foward. Expected bool, got {value!r}."
                            )

                    elif key == "anchour":
                        if not isinstance(value, str):
                            raise ValueError(
                                f"Invalid 'anchour' value in foward. Expected 'left' or 'right', got {value!r}."
                            )
                        elif not value in ["left", "right"]:
                            raise ValueError(
                                f"Invalid 'anchour' value in foward. Expected 'left' or 'right', got {value!r}."
                            )

                if not "action" in [key for key, _ in foward.items()]:
                    raise ValueError(
                        f"Parameter foward expected 1 key, with key of 'action' and type value of bool"
                    )

        foward.setdefault("action", True)
        foward.setdefault("preserve", False)
        foward.setdefault("anchour", "left")

        # ellipsis ---------------------------------------------------------------------------------------------------

        if ellipsis != {}:
            if not isinstance(ellipsis, dict):
                raise ValueError(
                    f"Invalid ellipsis. Expected dict, got {helper_function.deep_typeof(ellipsis)!r}."
                )
            else:
                for key, value in ellipsis.items():
                    if not isinstance(key, str):
                        raise ValueError(
                            f"Invalid key in ellipsis. Expected str, got {type(key)!r}."
                        )

                    if key not in ["symbol", "count", "at"]:
                        raise ValueError(
                            f"Invalid key in ellipsis. Expected 'symbol', 'count', or 'at'. got {ellipsis!r}."
                        )

                    if key == "symbol":
                        Character(value)

                        if not value.isprintable():
                            raise ValueError(
                                f"Invalid 'symbol' value in ellipsis. Expected printable character, got {value!r}."
                            )

                    elif key == "count":
                        if not isinstance(value, int):
                            raise ValueError(
                                f"Invalid 'count' value in ellipsis. Expected non-negative int, got {value!r}."
                            )
                        elif value <= 0:
                            raise ValueError(
                                f"Invalid 'count' value in ellipsis. Expected non-negative int, got {value!r}."
                            )

                    elif key == "at":
                        if not isinstance(value, str):
                            raise ValueError(
                                f"Invalid 'at' value in ellipsis. Expected str, got {value!r}."
                            )
                        elif not value in ["all", "max line", "screen edge"]:
                            raise ValueError(
                                f"Invalid 'at' value in ellipsis. Expected 'all', 'max line', or 'screen edge', got {value!r}."
                            )

            ellipsis.setdefault("at", "all")

        # masking ----------------------------------------------------------------------------------------------------

        if text_mask != "":
            if not isinstance(text_mask, str):
                raise ValueError(
                    f"Invalid text_mask value of {text_mask!r}. Expected string or character."
                )
            elif not text_mask.isprintable():
                raise ValueError(
                    f"Invalid text_mask value of {text_mask!r}. Expected non sequence code string or character."
                )

        if mask_limit_text != "":
            if not isinstance(mask_limit_text, str):
                raise ValueError(
                    f"Invalid mask_limit_text value of {mask_limit_text!r}. Expected string or character."
                )
            elif not mask_limit_text.isprintable():
                raise ValueError(
                    f"Invalid text_mask value of {mask_limit_text!r}. Expected non sequence code string or character."
                )

        # indent -----------------------------------------------------------------------------------------------------
        if indent != 0:
            if not isinstance(indent, int):
                raise ValueError(
                    f"Invalid indent value of {indent!r}. Expected int, got {type(indent)!r}."
                )
            elif indent < 0:
                raise ValueError(
                    f"Invalid indent value of {indent!r}. Expected non-negative int, got {indent!r}."
                )

        """
        processing ---------------------------------------------------------------------------------------------------
        """
        # cleaning ---------------------------------------------------------------------------------------------------

        text = helper_function.flatten_list([line.split("\n") for line in text])
        text = ["".join([char for char in line if char.isprintable()]) for line in text]

        # indent -----------------------------------------------------------------------------------------------------
        if indent:
            text = [
                (
                    (" " * indent) + line
                    if foward["anchour"] == "left" and line != ""
                    else line
                )
                for line in text
            ]

        # max width --------------------------------------------------------------------------------------------------
        if max_width:
            text = apply_max_width(text, max_width, preserve_width)

        # edge of screen ---------------------------------------------------------------------------------------------
        if edge_of_screen != "default":
            write_space = self.width - x
            if edge_of_screen == "newline":
                text = apply_max_width(text, write_space, False)
            else:
                text = apply_max_width(text, write_space, True)

        # max line ---------------------------------------------------------------------------------------------------
        old_text = text
        if max_line:
            text = text[:max_line]

        # foward -----------------------------------------------------------------------------------------------------

        viewed_text = text
        # print(foward)
        if foward != {}:
            if not foward["action"]:
                # text reversed
                if foward["preserve"]:
                    text = [line[::-1] for line in text]
                else:
                    viewed_text = [line[::-1] for line in viewed_text]

        # ellipsis ---------------------------------------------------------------------------------------------------
        if ellipsis != {}:
            # print(text)
            if ellipsis["at"] in ["all", "max line"] and len(text) < len(old_text):
                apply_advance_ellipsis()

            elif (
                ellipsis["at"] in ["all", "screen edge"] and y + len(text) > self.height
            ):
                # write ellipsis on the line where it touches the edge
                last_line_index = len(text) - (y + len(text) - self.height)
                text = text[:last_line_index]

                apply_advance_ellipsis()

        """
        printing -----------------------------------------------------------------------------------------------------
        """

        row_offset = 0
        max_line_length = len(max(text, key=len))
        result = {
            "edge": [
                (
                    x - 1
                    if foward["action"] or foward["anchour"] == "right"
                    else x - max_line_length
                ),  # Left edge
                y - 1,  # Top edge
                (
                    x + max_line_length
                    if foward["action"] or foward["anchour"] == "right"
                    else x + 1
                ),  # Right edge
                y + len(text),  # Bottom edge
            ],
            "text": viewed_text,
        }

        if calc_only:
            return result

        for line in text:

            column_offset = 0
            for char in line:
                if char in text_mask and text_mask != "":
                    column_offset += 1
                    continue

                if not self.get_char(x, y) in mask_limit_text and mask_limit_text != "":
                    column_offset += 1
                    continue

                if x + column_offset >= self.width:
                    break

                if y + row_offset >= self.height:
                    break

                if foward["action"]:
                    if foward["anchour"] == "left":
                        self.content[y + row_offset][x + column_offset] = char

                    else:
                        right_space = max_line_length - len(line)
                        self.content[y + row_offset][
                            x + column_offset + right_space
                        ] = char

                else:
                    if foward["anchour"] == "left":
                        if x - column_offset < 0:
                            column_offset += 1
                            continue
                        self.content[y + row_offset][x - column_offset] = char

                    else:
                        right_space = max_line_length - 1
                        if x - column_offset + right_space < 0:
                            column_offset += 1
                            continue
                        self.content[y + row_offset][
                            x - column_offset + right_space
                        ] = char

                column_offset += 1

            row_offset += 1

        return result

    def draw_box(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        style: Character | str | Iterable[str],
        mask_limit_line: Character | str | Iterable[str] = "",
    ) -> None:
        """
        Draws box from x1, y1 to x2, y2.

        ### Parametres
        - `x1`: x-coordinate of first corner.
        - `y1`: y-coordinate of first corner.
        - `x2`: x-coordinate of second corner.
        - `y2`: y-coordinate of second corner.
        - `style`: Styling the border will use.
            - style length of 1: all border.
            - style length of 2: horizontal and vertical (horizontal will fill the corner).
            - style length of 3: number 2 + corner.
            - style length of 4: top, down, left, right.
            - style length of 5: number 4 + corner.
            - style length of 8: number 4 + TL, TR, Bl, BR.
        - `mask_limit_line`: At what the box only can be drawn on. Default is an empty string.
        """

        if not isinstance(x1, int):
            raise ValueError(f"Invalid x1 value of {x1!r}. Must be an Integer.")

        if not isinstance(x2, int):
            raise ValueError(f"Invalid x1 value of {x2!r}. Must be an Integer.")

        if not isinstance(y1, int):
            raise ValueError(f"Invalid x1 value of {y1!r}. Must be an Integer.")

        if not isinstance(y2, int):
            raise ValueError(f"Invalid x1 value of {y2!r}. Must be an Integer.")

        try:
            if isinstance(style, str) and len(style) == 1:
                Character(style)
            if not len(style) in [1, 2, 3, 4, 5, 8]:
                raise ValueError
        except ValueError:
            raise ValueError(
                f"Invalid style value of {style!r}. Expected 1, 2, 3, 4, 5, or 8 characters."
            )

        # Mapping of positions to characters
        style_map = {
            "T": "",
            "B": "",
            "L": "",
            "R": "",
            "TL": "",
            "TR": "",
            "BL": "",
            "BR": "",
        }

        # Update style_map based on length of `style`
        if len(style) == 1:
            # All borders and corners use the same character
            style_map = {k: style for k in style_map}
        elif len(style) == 2:
            style_map.update(
                {
                    "T": style[0],
                    "B": style[0],
                    "L": style[1],
                    "R": style[1],
                    "TL": style[0],
                    "TR": style[0],
                    "BL": style[0],
                    "BR": style[0],
                }
            )
        elif len(style) == 3:
            style_map.update(
                {
                    "T": style[0],
                    "B": style[0],
                    "L": style[1],
                    "R": style[1],
                    "TL": style[2],
                    "TR": style[2],
                    "BL": style[2],
                    "BR": style[2],
                }
            )
        elif len(style) == 4:
            style_map.update(
                {
                    "T": style[0],
                    "B": style[1],
                    "L": style[2],
                    "R": style[3],
                    "TL": style[0],
                    "TR": style[0],
                    "BL": style[1],
                    "BR": style[1],
                }
            )
        elif len(style) == 5:
            style_map.update(
                {
                    "T": style[0],
                    "B": style[1],
                    "L": style[2],
                    "R": style[3],
                    "TL": style[4],
                    "TR": style[4],
                    "BL": style[4],
                    "BR": style[4],
                }
            )
        elif len(style) == 8:
            style_map.update(
                {
                    "T": style[0],
                    "B": style[1],
                    "L": style[2],
                    "R": style[3],
                    "TL": style[4],
                    "TR": style[5],
                    "BL": style[6],
                    "BR": style[7],
                }
            )
        else:
            raise ValueError(
                f"Invalid style value of {style!r}. Expected 1, 2, 3, 4, 5, or 8 characters."
            )

        self.draw_line(
            x1, y1, x2, y1, style_map["T"], mask_limit_character=mask_limit_line
        )  # Top
        self.draw_line(
            x1, y2, x2, y2, style_map["B"], mask_limit_character=mask_limit_line
        )  # Bottom
        self.draw_line(
            x1, y1, x1, y2, style_map["L"], mask_limit_character=mask_limit_line
        )  # Left
        self.draw_line(
            x2, y1, x2, y2, style_map["R"], mask_limit_character=mask_limit_line
        )  # Right

        corners = {"TL": (x1, y1), "BL": (x1, y2), "TR": (x2, y1), "BR": (x2, y2)}

        for corner, pos in corners.items():
            try:
                self.draw_char(
                    pos[0],
                    pos[1],
                    style_map[corner],
                    mask_limit_character=mask_limit_line + style,
                )
            except ValueError:
                pass

    def export_display(self, x1: int, y1: int, x2: int, y2: int) -> Display:
        """
        Returns a chunk of screen's content as a Display object from the specified position.

        ### Parametres
        - `x1`: x-coordinate of first corner.
        - `y1`: y-coordinate of first corner.
        - `x2`: x-coordinate of second corner.
        - `y2`: y-coordinate of second corner.

        ### Return
        Return a Display object.
        """
        # Ensure x1, y1 are the top-left corner and x2, y2 are the bottom-right corner
        if x1 > x2:
            x1, x2 = x2, x1
        if y1 > y2:
            y1, y2 = y2, y1

        # Check that both positions are within the screen boundaries
        if not handler.is_valid_position(Position(x1, y1), (self.width, self.height)):
            raise ValueError(
                f"Invalid position. Position must be within the screen size ({x1}, {y1}) vs {self.width}x{self.height}."
            )
        if not handler.is_valid_position(Position(x2, y2), (self.width, self.height)):
            raise ValueError(
                f"Invalid position. Position must be within the screen size ({x2}, {y2}) vs {self.width}x{self.height}."
            )

        # Initialize a new Display for the cloned area
        out = []
        display = Display()
        for yy in range(y1, y2 + 1):
            row = []
            for xx in range(x1, x2 + 1):
                row.append(
                    self.get_char(xx, yy)
                )  # Use get_char to fetch the character at each position
            out.append(row)

        # Set the content, width, and height of the cloned display
        display.content = out
        display.width = len(out[0]) if out else 0
        display.height = len(out)

        return display

    def merge_display(
        self,
        x: int,
        y: int,
        display: Display,
        display_mask: Character | str | Iterable[str] = "",
        mask_limit_display: Character | str | Iterable[str] = "",
    ):
        """
        Merges content of a Display to this content at specified x, y coordinate.

        ### Parametres
        - `x`: x position on where the content of the Display will be drawn into.
        - `y`: y position on where the content of the Display will be drawn into.
        - `display`: Display object to be merged.
        - `display_mask`: What character should be skipped on drawing. Default is an empty string.
        - `mask_limit_display`: At what the content can be drawn on. Default is an empty string.
        """
        if (
            not handler.is_valid_position(Position(x, y), (self.width, self.height))
            and x >= 0  # bypass minimun x and y requerment
            and y >= 0
        ):
            raise ValueError(
                f"Invalid position. Position must be within the screen size ({x}, {y}) vs {self.width}x{self.height}."
            )

        if not isinstance(display, Display):
            raise ValueError(
                f"Invalid display. Expected Display, got {type(display)!r}."
            )

        if display_mask != "":
            if not isinstance(display_mask, str):
                raise ValueError(
                    f"Invalid display_mask value of {display_mask!r}. Expected string or character."
                )
            elif not display_mask.isprintable():
                raise ValueError(
                    f"Invalid display_mask value of {display_mask!r}. Expected non sequence code string or character."
                )

        if mask_limit_display != "":
            if not isinstance(mask_limit_display, str):
                raise ValueError(
                    f"Invalid mask_limit_display value of {mask_limit_display!r}. Expected string or character."
                )
            elif not mask_limit_display.isprintable():
                raise ValueError(
                    f"Invalid mask_limit_display value of {mask_limit_display!r}. Expected non sequence code string or character."
                )

        for y_index, row in enumerate(display.content):
            try:
                self.draw_str(
                    x,
                    y + y_index,
                    "".join(row),
                    text_mask=display_mask,
                    mask_limit_text=mask_limit_display,
                )
            except ValueError:
                break

    def fill(
        self,
        x: int,
        y: int,
        character: Character,
        ignore: Character | str | Iterable[str] = "",
        neighbour: Literal[Literal[4] | Literal[8]] = 4,
    ):
        """
        floods fill using Breadth-First Search algorithm

        ### Parametres
        - `x`: x position on where the content of the Display will be drawn into.
        - `y`: y position on where the content of the Display will be drawn into.
        - `character`: Character used as filling.
        - `ignore`: What character should be also overidden when filling. Default is an empty string (only the character on x, y).
        - `neighbour`: How many neighbours need to be checked.
            - 4: Only the side.
            - 8: All the side including the corner.
        """

        Character(character)

        if ignore != "":
            if not isinstance(ignore, str):
                raise ValueError(
                    f"Invalid ignore value of {ignore!r}. Expected string or character."
                )
            elif not ignore.isprintable():
                raise ValueError(
                    f"Invalid ignore value of {ignore!r}. Expected non sequence code string or character."
                )

        if not neighbour in [4, 8]:
            raise ValueError(
                f"Invalid neighbour value of {neighbour!r}. Expected 4 or 8."
            )

        target = "".join([self.content[y][x], ignore])
        if character in target:
            return  # No action if the cell is already the target character

        queue = deque([(y, x)])

        # 4-directional neighbors (up, down, left, right)
        directions = (
            [(-1, 0), (1, 0), (0, -1), (0, 1)]
            if neighbour == 4
            else [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, 1), (1, 1), (-1, -1), (1, -1)]
        )

        while queue:
            cy, cx = queue.popleft()

            # Fill the cell with the new character
            self.content[cy][cx] = character

            # Check all 4 neighbors
            for dy, dx in directions:
                ny, nx = cy + dy, cx + dx

                # Check if the neighboring cell is within bounds and has the original character
                if (
                    0 <= ny < len(self.content)
                    and 0 <= nx < len(self.content[0])
                    and self.content[ny][nx] in target
                ):

                    # Mark the cell with the new character immediately to prevent re-adding it
                    self.content[ny][nx] = character
                    queue.append((ny, nx))
