#!/usr/bin/env python3
import galois as gl
import math
from colorama import Back, Style


def convert_int_to_symbols(n: int, gf: gl.GF, length: int) -> gl.FieldArray:
    """Convert n to a set of symbols."""
    if n > gf.order ** length:
        raise ValueError(f"Cannot convert {n} to {length} symbols of GF({gf.properties.order})")

    res = n
    symbols = [0 for _ in range(length)]
    for idx in range(length, 0, -1):
        symbols[idx - 1] = math.floor(n / (gf.order ** idx))
        res = n % (gf.order ** idx)
        if res == 0:
            break

    symbols[-1] = res

    return gf(symbols)


def repr_matrix(mat: gl.FieldArray) -> str:
    """Return a matrix of pixels (QR style) to the terminal."""
    color_mapping = {0: Style.RESET_ALL + "  ", 1: Back.WHITE + "  ", 2: Back.RED + "  ", 3: Back.GREEN + "  ", 4: Back.YELLOW + "  ", 5: Back.BLUE + "  ", 6: Back.MAGENTA + "  ", 7: Back.CYAN + "  "}
    rows = ["".join((color_mapping[int(cell)] for cell in row)) for row in mat]
    buffer = "\n " + f"{Style.RESET_ALL}\n ".join(rows) + f"{Style.RESET_ALL}\n"

    return buffer
