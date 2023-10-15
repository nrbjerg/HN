from __future__ import annotations
import os
import galois as gl
import numpy as np
from math import ceil
from typing import Any, List, Dict, Tuple
from itertools import combinations_with_replacement
from collections import ChainMap

Symbol = List[Any]


class Huffman:
    """Huffman coding for compression."""

    # We use binary compression, the compressed bits are later converted to base 8
    def __init__(self, source: List[Any], alphabeth: List[Any], symbol_length: int, base: int = 2):
        """Intialize the hufffman code, given the alphabeth and symbol length."""
        # 1. Construct frequency map by iterating over each symbol of the given length

        frequencies = {"".join(sym): 0.0 for sym in combinations_with_replacement(alphabeth, symbol_length)}
        n = ceil(len(source) / symbol_length)
        for (idx, sym) in enumerate([source[i : i + symbol_length] for i in range(len(source) - symbol_length + 1)]):
            if idx % symbol_length != 0:  # Skip symbols which aren't disjoint.
                continue

            frequencies[str(sym)] = frequencies.get(sym, 0) + 1 / n

        # 2. Construct the code book
        symbols_ordered_by_frequency = sorted(frequencies.items(), key = lambda item: item[1], reverse=True)
        self.symbol_length = symbol_length
        self.base = base
        self.gf = gl.GF(base)
        self.code_book = self._construct_huffman_codebook(symbols_ordered_by_frequency)
        # self.reversed_code_book = {val: sym for (sym, val) in self.code_book.items()}

    def _construct_huffman_codebook(self, symbols_ordered_by_frequency: List[Tuple[Symbol, float]], path: List[int] = []) -> Dict[Symbol, gl.FieldArray]:
        """Construct a huffman code book given the information provided."""
        # Termination criteria:
        if len(symbols_ordered_by_frequency) == 1:
            return {sym: self.gf(path) for (sym, _) in symbols_ordered_by_frequency}

        elif len(symbols_ordered_by_frequency) <= self.base:
            return  {sym: self.gf([*path, idx]) for idx, (sym, _) in enumerate(symbols_ordered_by_frequency)}

        total_freq = sum(map(lambda tup: tup[1], symbols_ordered_by_frequency))
        cutoff_indicies = self._cuttof_indicies([freq for (_, freq) in symbols_ordered_by_frequency], total_freq)
        split_symbols_ordered_by_frequency = [symbols_ordered_by_frequency[start : end] for (start, end) in zip(cutoff_indicies[:-1], cutoff_indicies[1:])]
        code_books = [self._construct_huffman_codebook(sym_and_freq, path = [*path, idx]) for idx, sym_and_freq in enumerate(split_symbols_ordered_by_frequency)]

        return dict(ChainMap(*list(filter(lambda code_book: code_book is not None, code_books))))

    def _cuttof_indicies(self, freqs: List[float], total_freq: float) -> Tuple[int]:
        """Compute the cuttoff indicies given the list of frequenciese and the total frequency."""
        cutoffs = [0]
        for idx in range(self.base):
            cutoffs.append(cutoffs[-1] + 1)
            while sum(freqs[cutoffs[idx]:cutoffs[idx + 1]]) < (total_freq / self.base) and cutoffs[-1] < len(freqs):
                cutoffs[-1] += 1

            #cutoffs[-1] -= # for some reason it overshoots

        return cutoffs

    def compress(self, message: List[Any]) -> gl.FieldArray:
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

    def decompress(self, recived_message: gl.FieldArray) -> List[Any]:
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

if __name__ == "__main__":
    print("Compressing Romeo & Juliet script. (Consisting only of ascii characters)")
    ascii = "".join(chr(i) for i in range(128))
    with open(os.path.join(os.getcwd(), 'misc', 'romeo_and_juliet.txt'), "r") as file:
        source = file.read()
    huffman = Huffman(source, source, 1, base=2)
    compressed = huffman.compress(source)
    print(f" - Compressed size: {len(compressed)} [symbols], Original size: {len(source) * 8} [bits]")
    print(f" - Size ratio: {round(len(compressed) / (len(source) * 8) * 10000) / 100}% (NOTE: Only works if base=2)")
