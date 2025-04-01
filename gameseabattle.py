import random
from typing import List, Tuple, Optional, Dict
import time
import json
import os
from datetime import datetime

class Ship:
    def __init__(self, size: int, positions: List[Tuple[int, int]]):
        self.size = size
        self.positions = positions
        self.hits = set()
        self.name = self.get_ship_name(size)
    
    def is_sunk(self) -> bool:
        return len(self.hits) == self.size
    
    def hit(self, position: Tuple[int, int]) -> bool:
        if position in self.positions:
            self.hits.add(position)
            return True
        return False
    
    @staticmethod
    def get_ship_name(size: int) -> str:
        names = {
            1: "Катер",
            2: "Эсминец",
            3: "Крейсер",
            4: "Линкор",
            5: "Авианосец"
        }
        return names.get(size, "Корабль")
