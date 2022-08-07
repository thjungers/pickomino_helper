"""Module to handle a single game round (roll + pick)."""

from __future__ import annotations

from dataclasses import dataclass

from dice import all_rolls, DiceSet
from game import Game


class Round:
    """Class modeling a single game round (roll + pick)."""
    def __init__(self, game: Game, picked_set: Optional[DiceSet] = None) -> None:
        self.game = game
        self.roll = None
        self.picked = picked_set or DiceSet()
    
    def pick(self, face: int) -> Round:
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
        return Round(self.game, picked)
    
    def score(self) -> int:
        """Compute the score of the dice picked this round."""
        return self.picked.score()
    
    def simulate(self) -> Dict[int, SimResult]:
        """Simulate the next rolls and picks.
        
        Returns: 
            A dictionary mapping each possible pick of the next roll to a SimResult object, 
            containing the probability of a valid roll, the expected score, the minimum score and 
            the maximum score.
        """
        # results dictionary {picked_face: SimResult}
        results = {}
        this_roll_count = len(self.roll)
        for face in self.roll.compact:
            try:
                next = self.pick(face)
            except InvalidPickError:
                continue

            next_roll_count = this_roll_count - (len(next.picked) - len(self.picked))
            if next_roll_count == 0:
                # end: all dice were picked
                prob = float(next.picked.is_complete() or self.game.valid_score(next.picked.score()))
                score = next.score()
                results[face] = SimResult(prob, score, score, score)
            else:
                # generate all rolls and simulate picks
                # TODO 
                roll_sims = []
                for roll in all_rolls(next_roll_count):
                    next.roll = roll
                    sim_res = next.simulate()
                    combs = roll.combinations()
                    for result in sim_res.values():
                        # skip zero-valid-probability results
                        if result.prob <= 0:
                            continue
                        roll_sims.append((result, combs))
                
                ## agregate roll simulations:
                # probability: sum of rolled probabilities, weighted by number of combinationss, 
                # divided by total number of rolls;
                # scores: avg, min, max of scores, weighted by number of combinations.
                try:
                    results[face] = SimResult(
                        sum(roll_res.prob * roll_combs for roll_res, roll_combs in roll_sims) / \
                            (6 ** next_roll_count),
                        sum(roll_res.avg_score * roll_combs for roll_res, roll_combs in roll_sims) / \
                            sum(roll_combs for roll_res, roll_combs in roll_sims),
                        min(roll_res.min_score for roll_res, _ in roll_sims),
                        max(roll_res.max_score for roll_res, _ in roll_sims)
                    )
                except ZeroDivisionError:
                    # no valid roll in roll_sims
                    continue
        
        return results

@dataclass
class SimResult:
    """Contain the results of a simulation for a given pick."""
    prob: float
    avg_score: float
    min_score: int
    max_score: int

    def __repr__(self) -> str:
        return (
            f"<SimResult: {self.prob:.2%} valid, "
            f"{self.avg_score:.2f} ({self.min_score}-{self.max_score})>"
        )

class InvalidPickError(Exception):
    """Exception for an invalid pick of dice."""