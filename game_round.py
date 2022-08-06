"""Module to handle a single game round."""

from __future__ import annotations

from dice import DiceSet


class Round:
    """Class modeling a single game round."""
    def __init__(self, picked_faces: Optional[List[int]] = None) -> None:
        self.roll = None
        self.picked = DiceSet(picked_faces)
    
    def pick(face: int) -> Round:
        """Pick a set of dice with the given face from the current roll.
        
        A new Round object is returned, which allows searching and backtracking.
        """
        if self.roll is None:
            raise ValueError("Current roll is not set. Set the roll before picking dice.")
        if face not in self.roll:
            raise InvalidPickError(f"Cannot pick '{face}' dice: they are not in the current roll.")
        if face in self.picked:
            raise InvalidPickError(f"Cannot pick '{face}' dice: they were already picked before.")
        
        count = self.roll.compact[face]
        picked = self.picked + [face] * count
        return Round(picked)
    
    def score(self) -> int:
        """Compute the score of the dice picked this round."""
        return self.picked.score()
    
    def simulate(self) -> Dict[int, Tuple[float, float, int, int]]:
        """Simulate the next rolls and picks.
        
        Returns: 
            A dictionary mapping each possible pick of the next roll to a tuple containing the 
            probability of loosing, the expected score, the minimum score and the maximum score.
        """
        results = {}
        this_roll_count = len(self.roll)
        for face in self.roll.compact:
            try:
                next = self.pick(face)
            except InvalidPickError:
                continue

            next_roll_count = this_roll_count - (len(next.picked) - len(self.picked))
            if next_roll_count == 0:
                # end of round
                prob = float(next.is_complete())
                score = next.score()
                results[face] = (prob, score, score, score)
            else:
                # generate all rolls and simulate picks
                # TODO
        
        return results


            

class InvalidPickError(Exception):
    """Exception for an invalid pick of dice."""