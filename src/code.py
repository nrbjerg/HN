#!/usr/bin/env python3
import galois as gl
import numpy as np
from helpers import convert_int_to_symbols, repr_matrix

class Code:
    """Constructs a HN code."""

    @staticmethod
    def number_of_symbols(size: int) -> int:
        """The number of symbols avalible for use in a HN code of the given size."""
        size_of_small_locator = 6 * 8
        size_of_big_locator = 8 * 8
        size_of_timing_strip = size - 6 - 8
        return size ** 2 - size_of_big_locator - 2 * size_of_small_locator - 8 * size_of_timing_strip

    def __init__(self, data: gl.FieldArray, gf: gl.GF, error_correction_level: int, mask: int, encoding: int, size: int = 23):
        """Initializese a HN code with the given parameters."""
        if data.shape[0] != self.number_of_symbols(size):
            raise ValueError(f"Expected data array to have size {self.number_of_symbols(size)} but got {data.shape[0]}")

        self.gf = gf
        self.data = data
        self.error_correction_level = error_correction_level
        self.mask = mask
        self.encoding = encoding
        self.size = size

        self.matrix = self.gf.Ones((self.size + 2, self.size + 2))
        self.add_locator_and_timing_pattern()
        self.add_parameters_and_calibration_colors()
        self.add_data()

    def add_locator_and_timing_pattern(self) -> None:
        """Create a matrix with the locator and timing patterns."""
        # 1. Add locators to matrix
        large_locator = self.gf.Zeros((7, 7)) - self.gf(np.pad(self.gf.Ones((5, 5)), 1)) + self.gf(np.pad(self.gf.Ones((3, 3)), 2))
        small_locator = self.gf.Zeros((5, 5)) - self.gf(np.pad(self.gf.Ones((3, 3)), 1)) + self.gf(np.pad(self.gf.Ones((1, 1)), 2))

        # NOTE: Remember that we have padding around the edge of the code.
        self.matrix[1:8, 1:8] = large_locator
        self.matrix[1:6, -6:-1] = small_locator
        self.matrix[-6:-1, 1:6] = small_locator

        # 2. Add timing information
        timing_pattern = self.gf([idx % 2 for idx in range(self.size - 8 - 6)])
        self.matrix[7, 9:-7] = timing_pattern
        self.matrix[9:-7, 7] = timing_pattern

    def add_parameters_and_calibration_colors(self) -> None:
        """Add parameters and calibration colors to the matrix."""
        # 1. Add calibration symbols:
        rgb = self.gf([2, 3, 5])
        for pos in [((7, 7, 7), (-4, -3, -2)), ((6, 6, 6), (12, 13, 14)), ((12, 13, 14), (6, 6, 6)), ((-4, -3, -2), (7, 7, 7))]:
            self.matrix[pos] = rgb

        # 2. Add error correction symbols
        for pos in [(9, 6), (-8, 6), (6, 15)]:
            self.matrix[pos] = self.error_correction_level

        # 3. Add masking symbols
        masking_symbols = convert_int_to_symbols(self.mask, self.gf, length = 2)
        for pos in [((6, 6), (-8, -9)), ((10, 11), (6, 6)), ((-5, -6), (7, 7))]:
            self.matrix[pos] = masking_symbols

        # 4. Add encoding symbols
        encoding_symbols = convert_int_to_symbols(self.encoding, self.gf, length = 2)
        for pos in [((6, 6), (10, 11)), ((7, 7), (-5, -6)), ((-9, -10), (6, 6))]:
            self.matrix[pos] = encoding_symbols

    def add_data(self) -> None:
        """Add the data to the matrix."""
        a, b, c = np.split(self.data, [15 * 15, 15 * 15 + 4 * 9])
        self.matrix[-16:-1, -16:-1] = np.reshape(a, (15, 15))
        self.matrix[-16:-7, 1:5] = np.reshape(b, (9, 4))
        self.matrix[1:5, -16:-7] = np.reshape(c, (9, 4)).T

    def __repr__(self) -> str:
        """Convert the HN code to a matrix of pixels."""
        return repr_matrix(self.matrix)


if __name__ == "__main__":
    gf = gl.GF(8)
    code = Code(gf.Random(shape=(Code.number_of_symbols(23),)), gf, error_correction_level=2, mask = 4, encoding = 2)
    print(code)
