import galois as gl
import numpy as np
from colorama import Back, Style

def number_of_symbols_in_HN_code (size: int) -> int:
    """Computes the expected number of symbols in a HN code."""
    return size ** 2 - 2 * (8 * 10) + (6 * 8) + 2 * (size - 16)

def generate_matrix(data: gl.FieldArray, error_correction_level: int, mask_index: int, encoding: int, base: int = 8, size: int = 24) -> gl.FieldArray:
    """Creates a matrix representation of the HN code, given  the data array."""
    # 1. Check that we have recived the correct number of symbols
    number_of_symbols = number_of_symbols_in_HN_code(size)
    if data.shape[0] != number_of_symbols:
        raise ValueError(f"Expected data array to have size {number_of_symbols} but got {data.shape[0]}")

    gf = gl.GF(base)
    matrix = gf.Ones((size + 2, size + 2))

    # 2. Add locators to matrix
    large_locator = gf.Zeros((7, 7)) - gf(np.pad(gf.Ones((5, 5)), 1)) + gf(np.pad(gf.Ones((3, 3)), 2))
    small_locator = gf.Zeros((5, 5)) - gf(np.pad(gf.Ones((3, 3)), 1)) + gf(np.pad(gf.Ones((1, 1)), 2))

    matrix[1:8, 1:8] = large_locator # NOTE: Remember that we have padding around the edge of the code.
    matrix[1:8, -8:-1] = large_locator
    matrix[-6:-1, 1:6] = small_locator

    # 3. Add timing information
    timing_pattern = gf([2 for _ in range(size - 16)]) # [(idx + 1) % 2 for idx in range(size - 16)])
    matrix[6, 9:-9] = timing_pattern
    matrix[11:-7, 6] = timing_pattern

    # 4. Add calibration symbols:
    colors = gf([3, 3, 3])# [2, 3, 5])
    matrix[-4:-1, 7] = colors
    matrix[9, 2:5] = colors
    matrix[9, -5:-2] = colors

    # 5. Add extra information
    matrix[9, 1], matrix[9, 8] = encoding, encoding
    matrix[9, -9] = encoding

    mask_symbols = (mask_index // base, mask_index % base) # TODO: use this
    matrix[9, 7], matrix[9, 6] = mask_index, mask_index
    matrix[9, -8], matrix[9, -7] = mask_index, mask_index
    matrix[-5, 7], matrix[-6, 7] = mask_index, mask_index

    matrix[9, 5] = error_correction_level
    matrix[9, -6] = error_correction_level
    matrix[9, -2] = error_correction_level

    return repr_matrix(matrix)

def repr_matrix(mat: gl.FieldArray) -> str:
    """Allows us to print a QR style code to the terminal."""
    color_mapping = {0: Style.RESET_ALL + "  ", 1: Back.WHITE + "  ", 2: Back.RED + "  ", 3: Back.GREEN + "  ", 4: Back.BLUE + "  ", 5: Back.MAGENTA + "  ", 6: Back.YELLOW + "  "}
    rows = ["".join((color_mapping[int(cell)] for cell in row)) for row in mat]
    buffer = "\n " + f"{Style.RESET_ALL}\n ".join(rows) + f"{Style.RESET_ALL}\n"

    return buffer


if __name__ == "__main__":
    print(generate_matrix(np.array([0 for _ in range(number_of_symbols_in_HN_code(24))]), 4, 5, 6))
