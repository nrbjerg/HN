#!/usr/bin/env python3
import galois as gl
import numpy as np

def compute_masking_score(mat: gl.FieldArray) -> int:
    """Computes the masking score of the matrix."""
    height, width = mat.shape
    score = 0

    # Top row & bottom row
    for i in range(width):
        if i == 0:
            score += np.sum(mat[:1, :i + 1] == mat[0, i])
            score += np.sum(mat[-2:, :i + 1] == mat[-1, i])
        elif i == width - 1:
            score += np.sum(mat[:1, i - 1:] == mat[0, i])
            score += np.sum(mat[-2:, i - 1:] == mat[-1, i])
        else:
            score += np.sum(mat[:1, i - 1: i + 1] == mat[0, i])
            score += np.sum(mat[-2:, i - 1: i + 1] == mat[-1, i])

    # Left and right most columns
    for i in range(1, height - 1):
        score += np.sum(mat[i - 1: i + 1, :1] == mat[i, 0])
        score += np.sum(mat[i - 1: i + 1, -2:] == mat[i, -1])

    # Middle
    for i in range(1, height - 1):
        for j in range(1, width - 1):
            score += np.sum(mat[i - 1: i + 1, j - 1: j + 1] == mat[i, j])

    return score

def compute_mask (mat: gl.FieldArray) -> int:
    pass
