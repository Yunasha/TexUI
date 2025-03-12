from dataclasses import dataclass


@dataclass
class Position:
    """
    Logic operation done by ...
    """

    x: int
    y: int

    def __post_init__(self):
        # Ensure x and y are integers
        if not isinstance(self.x, int) or not isinstance(self.y, int):
            raise TypeError("x and y must be whole numbers (integers).")

    def __add__(self, other):
        if isinstance(other, Position):
            return Position(self.x + other.x, self.y + other.y)
        raise TypeError("Operand must be of type Position.")

    def __sub__(self, other):
        if isinstance(other, Position):
            return Position(self.x - other.x, self.y - other.y)
        raise TypeError("Operand must be of type Position.")

    def __mul__(self, scalar):
        if isinstance(scalar, int):
            return Position(self.x * scalar, self.y * scalar)
        raise TypeError("Operand must be an integer.")

    def __truediv__(self, scalar):
        if isinstance(scalar, int) and scalar != 0:
            return Position(self.x // scalar, self.y // scalar)
        elif scalar == 0:
            raise ValueError("Cannot divide by zero.")
        raise TypeError("Operand must be a non-zero integer.")

    def __eq__(self, other):
        return isinstance(other, Position) and all(
            (self.x == other.x, self.y == other.y)
        )

    # compare the area size
    def __lt__(self, other):
        if isinstance(other, Position):
            # return (self.x, self.y) < (other.x, other.y)
            return all((self.x < other.x, self.y < other.y))
        return NotImplemented

    def __le__(self, other):
        if isinstance(other, Position):
            # return (self.x, self.y) <= (other.x, other.y)
            return all((self.x <= other.x, self.y <= other.y))
        return NotImplemented

    def __gt__(self, other):
        if isinstance(other, Position):
            # return (self.x, self.y) > (other.x, other.y)
            return all((self.x > other.x, self.y > other.y))
        return NotImplemented

    def __ge__(self, other):
        if isinstance(other, Position):
            # return (self.x, self.y) >= (other.x, other.y)
            return all((self.x >= other.x, self.y >= other.y))
        return NotImplemented

    def __abs__(self):
        # Returns the Euclidean distance from the origin (0, 0)
        return (self.x**2 + self.y**2) ** 0.5

    def __repr__(self):
        # Detailed output for debugging
        return f"Position(x={self.x}, y={self.y})"

    def __str__(self):
        return f"Position({self.x}, {self.y})"


class Character:
    def __init__(self, char):
        if not isinstance(char, str) or len(char) != 1:
            raise ValueError(
                f"Invalid Character of {char!r}. Expected string with length of one."
            )
        self.char = char

    def __str__(self):
        return self.char

    def __repr__(self):
        return f"Character({self.char!r})"

    def is_upper(self):
        return self.char.isupper()

    def is_lower(self):
        return self.char.islower()

    def to_upper(self):
        self.char = self.char.upper()
        return self.char

    def to_lower(self):
        self.char = self.char.lower()
        return self.char

    def is_digit(self):
        return self.char.isdigit()

    def is_alpha(self):
        return self.char.isalpha()

    def get_ascii(self):
        return ord(self.char)
