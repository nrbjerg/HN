import galois as gl
import numpy as np
from colorama import Back, Style
from typing import Iterable, Tuple
import math

def convert_int_to_symbols (n: int, gf: gl.GF, length: int) -> gl.FieldArray:
    """Convert n to a set of symbols."""
    if n > gf.order ** length:
        raise ValueError(f"Cannot convert {n} to {length} symbols of GF({gf.properties.order})")

    res = n
    symbols = [0 for _ in range(length)]
    for idx in range(length, 1, -1):
        symbols[idx - 2] = math.floor(n / (gf.order ** idx))
        res = n % (gf.order ** idx)
        if res == 0:
            break

    symbols[-1] = res

    vals = [int(c) for c in str(int(str(n), base=gf.order))]
    print(vals)
    return gf(vals)

def window(data: gl.FieldArray, window_size: int) -> Iterable[Tuple[int]]:
    """A generator yielding disjoint windows of the data array."""
    for idx in range(data.shape[0] // window_size):
        yield tuple(data[idx * window_size : (idx + 1) * window_size])

def number_of_symbols_in_HN_code (size: int) -> int:
    """Computes the expected number of symbols in a HN code."""
    size_of_small_locator = 6 * 8
    size_of_big_locator = 8 * 8
    strip_size = size - 6 - 8
    return size ** 2 - size_of_big_locator - 2 * size_of_small_locator - 8 * (strip_size)

def setup_locator_and_timing_pattern(gf: gl.GF, size: int) -> gl.FieldArray:
    """Create a matrix with the locator and timing patterns."""
    # 1. Construct matrix
    matrix = gf.Ones((size + 2, size + 2))

    # 2. Add locators to matrix
    large_locator = gf.Zeros((7, 7)) - gf(np.pad(gf.Ones((5, 5)), 1)) + gf(np.pad(gf.Ones((3, 3)), 2))
    small_locator = gf.Zeros((5, 5)) - gf(np.pad(gf.Ones((3, 3)), 1)) + gf(np.pad(gf.Ones((1, 1)), 2))

    matrix[1:8, 1:8] = large_locator # NOTE: Remember that we have padding around the edge of the code.
    matrix[1:6, -6:-1] = small_locator
    matrix[-6:-1, 1:6] = small_locator

    # 3. Add timing information
    timing_pattern = gf([idx % 2 for idx in range(size - 8 - 6)])
    matrix[7, 9:-7] = timing_pattern
    matrix[9:-7, 7] = timing_pattern

    return matrix

def add_parameters_and_calibration_colors(gf: gl.GF, matrix: gl.FieldArray, error_correction_level: int, mask: int, encoding: int) -> gl.FieldArray:
    """Adds parameters and calibration colors to the matrix"""
    # 4. Add calibration symbols:
    rgb = gf([2, 3, 5])
    for pos in [((7, 7, 7), (-4, -3, -2)), ((6, 6, 6), (12, 13, 14)), ((12, 13, 14), (6, 6, 6)), ((-4, -3, -2), (7, 7, 7))]:
        matrix[pos] = rgb

    for pos in [(9, 6), (-8, 6), (6, 15)]:
        matrix[pos] = error_correction_level

    masking_symbols = convert_int_to_symbols(mask, gf, length = 2)
    for pos in [((6, 6), (-8, -9)), ((10, 11), (6, 6)), ((-5, -6), (7, 7))]:
        matrix[pos] = masking_symbols

    encoding_symbols = convert_int_to_symbols(encoding, gf, length = 2)
    for pos in [((6, 6), (10, 11)), ((7, 7), (-5, -6)), ((-9, -10), (6, 6))]:
        matrix[pos] = encoding_symbols

    return matrix


def add_data (gf: gl.GF, matrix: gl.FieldArray, data: gl.FieldArray) -> gl.FieldArray:
    """adds the given data to the """
    print(data.shape)
    a, b, c = np.split(data, [15 * 15, 15 * 15 + 4 * 9])
    print(a.shape, b.shape, c.shape, matrix[-18:-8, 1:5].shape)
    matrix[-16:-1, -16:-1] = np.reshape(a, (15, 15))
    matrix[-16:-7, 1:5] = np.reshape(b, (9, 4))
    matrix[1:5, -16:-7] = np.reshape(c, (9, 4)).T
    return matrix


def generate_matrix(data: gl.FieldArray, gf: gl.GF, error_correction_level: int, mask: int, encoding: int, size: int = 23) -> gl.FieldArray:
    """Create a matrix representation of the HN code, given the data array."""
    # 1. Check that we have recived the correct number of symbols
    number_of_symbols = number_of_symbols_in_HN_code(size)
    if data.shape[0] != number_of_symbols:
        raise ValueError(f"Expected data array to have size {number_of_symbols} but got {data.shape[0]}")

    matrix = setup_locator_and_timing_pattern(gf, size)
    matrix = add_parameters_and_calibration_colors(gf, matrix, error_correction_level, mask, encoding)
    matrix = add_data(gf, matrix, data)
    return repr_matrix(matrix)

def repr_matrix(mat: gl.FieldArray) -> str:
    """Allows us to print a QR style code to the terminal."""
    color_mapping = {0: Style.RESET_ALL + "  ", 1: Back.WHITE + "  ", 2: Back.RED + "  ", 3: Back.GREEN + "  ", 4: Back.YELLOW + "  ", 5: Back.BLUE + "  ", 6: Back.MAGENTA + "  ", 7: Back.CYAN + "  "}
    rows = ["".join((color_mapping[int(cell)] for cell in row)) for row in mat]
    buffer = "\n " + f"{Style.RESET_ALL}\n ".join(rows) + f"{Style.RESET_ALL}\n"

    return buffer


if __name__ == "__main__":
    gf = gl.GF(8)
    print(convert_int_to_symbols(12, gf, 2))
    print(generate_matrix(gf.Random(shape=(number_of_symbols_in_HN_code(23),)), gf, encoding = 6, error_correction_level = 4, mask = 7))
