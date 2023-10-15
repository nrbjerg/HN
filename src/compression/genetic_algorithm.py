#!/usr/bin/env python3
from src.compression.huffman import Huffman, Symbol
from math import ceil
import numpy as np
import json
import galois as gl
from typing import List



class Genetic_Algorithm:
    """A genetic algorithm for optimizing the code books for huffman"""

    def __init__ (self, symbol_length: int, number_of_agents: int, permutation_prob: float, base: int = 8):
        """"Initialize a list of agents (code_books). That will later be optimized"""
        self.symbol_length = symbol_length
        self.permuation_prob = permutation_prob
        self.code_books = [{} for _ in range(number_of_agents)]
        self.scores = [np.inf for _ in range(number_of_agents)]

    def compute_offspring(self, uncompressed_size: int) -> None:
        """Computes the new agents based on the scores."""
        # NOTE: might need to be reversed.
        against_identity = [(uncompressed_size - score) / uncompressed_size for score in self.scores]
        total_against_identity = sum(against_identity)
        probs = [rel_score  / total_against_identity for rel_score in against_identity]
        offspring = []
        for _ in range(len(self.code_books)):
            x, y = np.random.choice(self.code_books, probs, replace=False)
            offspring.append()

        self.code_books = offspring


    def recompute_scores(self, message: List[Symbol]) -> None:
        """Check how well each code_book performs for compression."""
        for idx, code_book in enumerate(self.code_books):
            huffman = Huffman(code_book, symbol_length=self.symbol_length, will_be_decompressed=False)
            self.scores[idx] = huffman.compress(message).shape[0]

    def run(self, message: List[Symbol], alphabeth: List[Symbol], encoding: str, max_iter: int = 2):
        """Run the genetic algorithm and return the best code_book as a json file."""
        # Perform the iterations.
        uncompressed_size = len(message) * (ceil(len(alphabeth) / self.base))
        for iter in range(1, max_iter + 1):
            print(f"Now at iteration: {iter}")
            self.recompute_scores(message)
            new_best = min(self.scores)
            print(f"  Best size: {new_best} [symbols]")
            print(f"   - Compared to original: {new_best / uncompressed_size * 100} %")
            self.compute_of_spring()

        # Store the best code_book as a json file.
        self.recompute_scores(message)
        max_idx = self.scores.index(min(self.scores))
        best_code_book = self.code_boks[max_idx]
        final_best = min(self.scores)
        print(f"Final best size: {final_best} [symbols]")
        print(f" - Compared to orignial: {final_best / uncompressed_size * 100} %")
        with open(f"{encoding}.json", "w+") as file:
            obj = {"base": self.base, "code_book": {key: list(val) for (key, val) in best_code_book.items()}}
            json.dump(obj, file)
