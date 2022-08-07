"""Module to handle dice and dice sets.

A Pickomino die has 6 faces: numbers 1-5 and a worm.
Its outcome is represented as an int 0-5, with 0 representing a worm and 1-5 ints mapped directly to 
the corresponding face number.
The value of a number face corresponds to that number; the value of a worm face is 5.

Dice are indistinguishable: different rolls with the same faces on different dice are equivalent.
"""

from __future__ import annotations

from collections import Counter
import math
from typing import Dict, Iterator, List, Optional, Sequence, Union

WORM = 0
WORM_VAL = 5
FACES = [WORM, 1, 2, 3, 4, 5]

class DiceSet:
    """Class modeling a set of n identical dice.
    
    Parameters: 
        faces: Faces present in this set.
    """
    def __init__(self, faces: Optional[Union[int, List[int]]] = None) -> None:
        if faces is None:
            self.faces = []
        elif not isinstance(faces, Sequence):
            self.faces = [faces]
        else:
            self.faces = faces
    
    def __repr__(self) -> str:
        faces_str = ", ".join(map(str, self.faces))
        return f"<DiceSet ({faces_str})>"

    def __add__(self, new_faces: Union[int, List[int]]) -> DiceSet:
        """Implement the + operation to create a new DiceSet with additional faces."""
        if not isinstance(new_faces, Sequence):
            new_faces = [new_faces]

        faces = sorted(self.faces + new_faces)
        return DiceSet(faces)
    
    def __contains__(self, face: int) -> bool:
        """Implement the `in` operator."""
        return face in self.faces

    def __len__(self) -> int:
        """Return the number of dice in the set."""
        return len(self.faces)
    
    @property
    def compact(self) -> Dict[int, int]:
        """Return a compact representation of the dice set.

        Returns:
            A dictionary mapping the faces and their number of occurences in the dice set.
        
        Example: 
            Roll([1, 1, 1, 2, 5, 5]).compact
            >>> {1: 3, 2: 1, 5: 2}
        """
        return Counter(self.faces)

    def combinations(self) -> int:
        """Compute the number of combinations of dice that would yield this dice set."""
        ndice = len(self.faces)
        combs = 1
        # the faces have no influence on the number of combinations: only the numbers of groups and 
        # faces per group
        for count in self.compact.values():
            combs *= math.comb(ndice, count)
            ndice -= count
        
        return combs
    
    def score(self) -> int:
        """Compute the score of this dice set"""
        return sum(face_score(face) for face in self.faces)

    def is_complete(self) -> bool:
        """Return whether this dice set is complete, i.e. contains at least a WORM face."""
        return WORM in self.faces


def face_score(face: int) -> int:
    """Return the score of a face."""
    if face == WORM:
        return WORM_VAL

    return face

def all_rolls(n: int, faces: List[int] = FACES) -> Iterator[DiceSet]:
    """Generate all possible rolls of `n` dice with the given `faces`. 
    
    The dice outcomes are ordered from lowest to highest to prevent overcounting equivalent rolls.

    Returns:
        An iterator over all possible rolls.
    """
    if n > 0:
        for i, face in enumerate(faces):
            for roll in all_rolls(n - 1, faces[i:]):
                yield roll + face
    else:
        yield DiceSet()
