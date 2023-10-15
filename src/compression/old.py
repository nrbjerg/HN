#!/usr/bin/env python3
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
import galois as gl
from typing import Dict, Any, List

Symbol = Any

@dataclass()
class HuffmanNode:
    """Stores the information needed for huffman"""
    sym: Symbol | None
    freq: float
    children: [HuffmanNode]

    @property()
    def total_frequency (self) -> float:
        """Compute the total frequency of the branch"""
        return self.freq + sum(child.total_frequency for child in self.children)



class Compression:
    """A class for compression algorithms."""

    def __init__(self, code_book: Dict[Symbol, gl.FieldArray], symbol_length: int, will_be_decompressed: bool = True):
        """Constructs a codebook given a dictionary of frequencies"""
        self.symbol_length = symbol_length
        self.code_book = code_book
        if will_be_decompressed:
            self.reversed_code_book = {val: key for (key, val) in self.code_book.items()}

    def compress(self, message: List[Symbol]) -> gl.FieldArray:
        """Compress the message and return it as a galois array."""
        buffer = []

        # Iterate through each block of NON OVERLAPPING information of the message (of synmbol length)
        for (start_idx, sym) in enumerate([message[i:i + self.symbol_length] for i in range(len(message) - self.symbol_length + 1)]):
            if start_idx % self.symbol_length != 0:
                continue

            if sym in self.code_book.keys():
                buffer.append(self.code_book[sym])
            else:
                raise ValueError(f"Got the symbol {sym}, but it was not found in the code book!")

        return np.concatenate(buffer)

    def decompress(self, recived_message: gl.FieldArray) -> List[Symbol]:
        """Decompresses the recived message."""
        buffer = []
        start, end = 0, 1
        while end != recived_message.shape[0]:
            if recived_message[start : end] in self.reversed_code_book.keys():
                buffer.append(self.reversed_code_book[recived_message[start : end]])
                start = end

            end += 1

        if start != end:
            raise ValueError("Couldn't decompress the recived message.")

        return buffer
