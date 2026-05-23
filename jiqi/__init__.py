# 军旗人机对战 — Chinese Army Chess (Jinqi)
# Version: 1.0.0

__version__ = "1.0.0"

from jiqi.piece import Piece, PieceType
from jiqi.board import Board
from jiqi.rules import RuleEngine
from jiqi.player import GameSetup, AIPlayer, HumanPlayer
from jiqi.game import Game
from jiqi.ui import TerminalUI

__all__ = [
    "Piece",
    "PieceType",
    "Board",
    "RuleEngine",
    "GameSetup",
    "AIPlayer",
    "HumanPlayer",
    "Game",
    "TerminalUI",
]
