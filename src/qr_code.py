#!/usr/bin/env python3
import numpy as np
from colorama import Back, Style

class QRCode:

    def __init__(self, data: str, k: int = 21):
        """Construct a QR code (version 1)."""
        self.matrix = np.random.randint(0, 2, size=(k, k))

    def __repr__(self) -> str:
        """Allows us to print a QR code to the terminal."""
        aux = lambda cell: Back.WHITE + "  " if cell == 1 else Style.RESET_ALL + "  "
        rows = ["".join((aux(cell)) for cell in row) for row in self.matrix]
        buffer = "\n " + f"{Style.RESET_ALL}\n ".join(rows) + f"{Style.RESET_ALL}\n"

        return buffer



if __name__ == "__main__":
    qr = QRCode("")
    print(qr)
