#!/usr/bin/env python3
import numpy as np
from numpy.typing import ArrayLike
from colorama import Back, Style
import math

def convert_int_to_bit_string(n: int, maximum: int) -> ArrayLike:
    """Takes an int and converts it to a bit string of lengh log_2(maximum)."""
    length = int(math.ceil(np.log2(maximum)))
    bit_string = np.zeros(length)
    for idx in range(length):
        bit_string[idx] = (n & 2 ** idx) >> idx

    return bit_string


class QRCode:

    def __init__(self, data: str, k: int = 21, error_correction_level: int = 0, mask: int = 2):
        """Construct a QR code (version 1)."""
        #self.matrix = np.random.randint(0, 2, size=(k, k))
        self.matrix = np.ones(shape=(k, k)) * 2

        # 1. Add locators & seperators
        locator = np.zeros(shape=(7, 7)) + np.pad(np.ones(shape=(5, 5)), pad_width=1) - np.pad(np.ones(shape=(3, 3)), pad_width=2)
        self.matrix[:7, :7] = locator
        self.matrix[7, :7] = np.ones(shape=(1, 7))
        self.matrix[:8, 7] = np.ones(shape=(1, 8))

        self.matrix[k - 7:, :7] = locator
        self.matrix[k - 8, :7] = np.ones(shape=(1, 7))
        self.matrix[-8:, 7] = np.ones(shape=(1, 8))

        self.matrix[:7, k - 7:] = locator
        self.matrix[:7, k - 8] = np.ones(shape=(1, 7))
        self.matrix[7, -8:] = np.ones(shape=(1, 8))

        # 2. Add timing pattern
        self.matrix[6, 8:-8] = [(i + 1) % 2 for i in range(9, k - 7)]
        self.matrix[8:-8, 6] = [(i + 1) % 2 for i in range(9, k - 7)]

        # 3. Add error correction information
        self.matrix[8, 0:2] = convert_int_to_bit_string(error_correction_level, 4)
        self.matrix[-2:, 8] = convert_int_to_bit_string(error_correction_level, 4)

        # 4. Add masking information
        self.matrix[8, 2:5] = convert_int_to_bit_string(mask, 8)
        self.matrix[-5:-2, 8] = convert_int_to_bit_string(mask, 8)

    def __repr__(self) -> str:
        """Allows us to print a QR code to the terminal."""
        #return str(self.matrix)
        aux = lambda cell: Back.WHITE + "  " if cell == 1 else Style.RESET_ALL + "  "
        rows = ["".join((aux(cell)) for cell in row) for row in self.matrix]
        buffer = "\n " + f"{Style.RESET_ALL}\n ".join(rows) + f"{Style.RESET_ALL}\n"

        return buffer



if __name__ == "__main__":
    qr = QRCode("")
    print(qr)
