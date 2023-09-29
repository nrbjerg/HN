#!/usr/bin/env python3
import galois as gl
import numpy as np
from error_correting.code import Word, Code
from typing import Iterable, List
from itertools import combinations_with_replacement

def find_zero_indicies (xs: Iterable[Word]) -> List[int]:
    """Find the indicies with all zeros"""
    zeros = [i for i in range(len(xs))]
    for x in xs:
        for idx in zeros:
            if x[idx] != 0:
                zeros.remove(idx)

    return zeros

class ReedSolomonCode(Code):
    """A reed solomon code is a cyclic code (meaning it's good for burst errors)."""

    def __init__(self, q: int, k: int, n: int, compute_error_correcting_pair: bool = False):
        """Construct a generator matrix of a reed solomon code."""
        if k > n or n > q:
            raise ValueError(f"Expeceted 1 <= k <= n <= q, but got: k = {k}, n = {n} and q = {q}")

        self.gf = gl.GF(q)
        self.G = self.gf([[p ** i for p in range(k)] for i in range(n)])
        if compute_error_correcting_pair:
            self.A = ReedSolomonCode(q, (self.t + 1), n)
            self.B_dual = ReedSolomonCode(q, (k + self.t), n)

    def encode(self, message: Word) -> Word:
        """Encode a word using the generator matrix."""
        return message.T @ self.gen

    def decode(self, recived: Word) -> Word:
        """Decode the recived word. Usign error correcting pairs."""
        # 1. Check if the recived vector is already in the code.
        if not np.any(self.H @ recived):
            return recived

        # 1. Compute M_ecp
        m_ecp = [a for a in self.A.generate_codewords() if (not np.any(self.B_dual.H @ (a * recived)))]

        # 2. Find Z(M_ecp)
        zero_positions = find_zero_indicies(m_ecp)

        #  3. Find error
        He = self.H[zero_positions] # FIXME: This is generally not square
        error = np.linalg.solve(He, self.H @ recived)

        # 4. Remoce error
        for i, j in enumerate(zero_positions):
            recived[j] -= error[i]

        return recived

    def generate_codewords(self) -> Iterable[Word]:
        """Construct a iterator over all of the codewords in self."""
        for word in combinations_with_replacement(self.gf.elements, self.k):
            yield self.gf(word).T @ self.G
