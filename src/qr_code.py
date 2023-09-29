#!/usr/bin/env python3
import numpy as np
from numpy.typing import ArrayLike
from colorama import Back, Style
import math

def convert_int_to_symbol_string(n: int, maximum: int, base: int = 2) -> ArrayLike:
    """Takes an int and converts it to a, symbol string of the current base, of lengh ceil(log_base(maximum))
       if no base is supplied the base will be two (meaning it will construct a bitstring.)"""
    length = int(math.ceil(math.log(maximum, base)))
    symbol_string = np.zeros(length)
    for idx in range(length - 1, -1, -1):
        symbol_string[idx] = n // (base ** idx)
        n = n % base ** idx

    return symbol_string


def construct_locator_with_information(error_correction_level: int,  mask: int, locator_size: int):
    """Constructs each locator and adds the information"""
    if locator_size < 5:
        raise ValueError(f"Expected locator size to be >= 5, got {locator_size}")

    locator_with_information = np.ones(shape=(locator_size + 2, locator_size + 1))
    locator = np.zeros(shape=(locator_size, locator_size)) + \
              np.pad(np.ones(shape=(locator_size - 2, locator_size - 2)), pad_width=1) - \
              np.pad(np.ones(shape=(locator_size - 4, locator_size- 4)), pad_width=2)
    locator_with_information[:locator_size, :locator_size] = locator

    # Error and masking information
    locator_with_information[locator_size + 1, 0] = error_correction_level # NOTE: is encoded using two bits
    locator_with_information[locator_size + 1, 1:3] = convert_int_to_symbol_string(mask, 7 ** 2,  base = 7)
    locator_with_information[locator_size + 1, 3:5] = convert_int_to_symbol_string(0, 4, base = 7) # could include information about the version

    return locator_with_information

class QRCode:

    def __init__(self, data: str, k: int = 20, error_correction_level: int = 2, mask: int = 1, base: int = 7, locator_size: int = 5):
        """Construct a QR code (version 1)."""
        self.matrix = np.random.randint(0, base, size=(k, k))
        #self.matrix = np.ones(shape=(k, k)) * 2

        # 1. Add locators & seperators
        locator_with_information = construct_locator_with_information(error_correction_level, mask, locator_size)

        self.matrix[:locator_size + 2, :locator_size + 1] = locator_with_information
        self.matrix[-(locator_size + 1):, :(locator_size + 2)] = np.rot90(locator_with_information)
        self.matrix[:locator_size + 1, -(locator_size + 2):] = np.rot90(locator_with_information, k = 3)

        # 2. Add timing pattern
        timing_patterns = [i % 2 for i in range(locator_size + 2, k - (locator_size + 1))]
        cyclic_pattern = [i % base for i in range(locator_size + 2, k - (locator_size + 1))]
        self.matrix[locator_size - 1, locator_size + 1:-(locator_size + 2)] = timing_patterns
        self.matrix[locator_size - 2, locator_size + 1:-(locator_size + 2)] = cyclic_pattern
        self.matrix[locator_size - 3, locator_size + 1:-(locator_size + 2)] = timing_patterns
        self.matrix[(locator_size + 2):-(locator_size + 1), locator_size - 1] = timing_patterns
        self.matrix[(locator_size + 2):-(locator_size + 1), locator_size - 2] = cyclic_pattern
        self.matrix[(locator_size + 2):-(locator_size + 1), locator_size - 3] = timing_patterns

    def __repr__(self) -> str:
        """Allows us to print a QR code to the terminal."""
        return repr_matrix(self.matrix)

def repr_matrix(mat: ArrayLike) -> str:
    """Allows us to print a QR style code to the terminal."""
    color_mapping = {0: Style.RESET_ALL + "  ", 1: Back.WHITE + "  ", 2: Back.RED + "  ", 3: Back.GREEN + "  ", 4: Back.BLUE + "  ", 5: Back.MAGENTA + "  ", 6: Back.YELLOW + "  "}
    rows = ["".join((color_mapping[cell] for cell in row)) for row in mat]
    buffer = "\n " + f"{Style.RESET_ALL}\n ".join(rows) + f"{Style.RESET_ALL}\n"

    return buffer


if __name__ == "__main__":
    qr = QRCode("")
    print(qr)
