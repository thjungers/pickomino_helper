"""Module to handle a full game."""

from random import randrange

from game_round import Round

TILE_SCORES = {
    21: 1,
    22: 1,
    23: 1,
    24: 1,
    25: 2,
    26: 2,
    27: 2,
    28: 2,
    29: 3,
    30: 3,
    31: 3,
    32: 3,
    33: 4,
    34: 4,
    35: 4,
    36: 4,
}
NDICE = 8

class Game: 
    """Class modeling a full game."""
    def __init__(self, player_names: List[str]) -> None:
        self.players = [Player(self, name) for name in player_names]
        self.free_tiles = list(TILE_SCORES.keys())
        self.current_player_idx = 0

    def player_index(self, player_name: str) -> int:
        """Get the index of a player in self.players by its name."""
        for i, player in enumerate(self.players):
            if player.name == player_name:
                return i
        
        raise ValueError(f"{player_name} is not in list of players.")
    
    def start(self, player_name: Optional[str] = None) -> None:
        """Set the start player and start a new round.
        
        If no player name is provided, a random player is selected.
        """
        if player_name is None:
            self.current_player_idx = randrange(len(self.players))
        else:
            # move back by 1: the next call of self.next_round() will do +=1
            self.current_player_idx = self.player_index(player_name) - 1
    
    def valid_score(self, score: int) -> bool:
        """Determine if a tile can be picked with the given score, either picked from the free tiles 
        of stolen from a player.
        
        A free tile can be picked if its value is less or equal to the score. A player tile can be 
        stolen if its value is equal to the score and it is the last tile collected by that player.
        """
        if score >= min(self.free_tiles):
            return True
        for player in self.players:
            try:
                if score == player.tiles[-1]:
                    return True
            except IndexError:
                continue
        return False
    
    @property
    def current_player(self) -> Player:
        """Provide the current player."""
        return self.players[self.current_player_idx]
    
    def next_round(self) -> Round:
        """Move to the next player and return the Round object."""
        self.current_player_idx += 1
        self.current_player_idx %= len(self.players)
        return Round(self)


class Player:
    """Class modeling a player."""
    def __init__(self, game: Game, name: str) -> None:
        self.game = game
        self.name = name
        self.tiles = []

    def score(self) -> int:
        return sum(TILE_SCORES[tile] for tile in self.tiles)
    
    def pick_tile(self, tile: int, score: int) -> None:
        """Pick a tile from the free tiles."""
        if tile not in self.game.free_tiles:
            raise TilePickError(f"Tile {tile} is not free.")
        if tile > score:
            raise TilePickError(f"Tile {tile} cannot be picked with a score of {score}.")
        
        self.tiles.append(tile)
        self.game.free_tiles.remove(tile)
    
    def steal_tile(self, tile: int, score: int) -> None:
        """Steal a tile from a player."""
        if tile != score:
            raise TilePickError(f"Tile {tile} cannot be stolen with a score of {score}.")
        if tile in self.tiles:
            raise TilePickError(f"Tile {tile} cannot be stolen from yourself.")
        if tile in self.game.free_tiles:
            raise TilePickError(f"Tile {tile} cannot be stolen: it is still free.")
        
        for player in self.game.players:
            try:
                if tile == player.tiles[-1]:
                    player.tiles.pop()
                    self.tiles.append(tile)
                    return
            except IndexError:
                continue
        
        raise TilePickError(f"Tile {tile} cannot be stolen from any player: it is not visible.")

class TilePickError(Exception):
    """Exception raised when a tile cannot be picked."""