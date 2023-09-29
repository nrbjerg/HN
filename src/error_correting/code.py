#!/usr/bin/env python3
import galois as gl
from functools import cached_property
import numpy as np
import math

Word = gl.FieldArray

def gauss_elimination(A):
    row, col = A.shape
    if row == 0 or col == 0:
        return A
    for i in range(min(row, col)):
        max_element = abs(A[i, i])
        max_row = i
        for k in range(i+1, row):
            if abs(A[k, i]) > max_element:
                max_element = abs(A[k, i])
                max_row = k
        A[[i, max_row]] = A[[max_row, i]]
        for k in range(i+1, row):
            factor = A[k, i]/A[i, i]
            A[k, :] -= factor * A[i, :]
    return A


class Code:

    @property
    def k(self) -> int:
        """The dimension of the reed solomon code."""
        return self.G.shape[0]

    @property
    def n(self) -> int:
        """The length of the reed solomon code."""
        return self.G.shape[1]

    @property
    def d(self) -> int:
        """The minimum distance of the reed solomon code."""
        return self.n - self.k + 1  # Reed solomon codes are MDS.

    @property
    def t(self) -> int:
        """The error decoding redius."""
        return int(math.floor((self.d - 1) / 2))

    @cached_property
    def H(self) -> gl.FieldArray:
        """A parity check matrix for the code"""
        echellon = gauss_elimination(self.G)
        return np.concatenate(echellon[self.k:].T, np.identity(self.k))
