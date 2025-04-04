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

class Board:
    def __init__(self, size: int = 10):
        self.size = size
        self.grid = [['~' for _ in range(size)] for _ in range(size)]
        self.ships = []
        self.hit_cells = set()
        self.miss_cells = set()
    
    def place_ship(self, ship: Ship) -> bool:
        for x, y in ship.positions:
            if not (0 <= x < self.size and 0 <= y < self.size):
                return False
            if self.grid[x][y] != '~':
                return False
        
        for x, y in ship.positions:
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.size and 0 <= ny < self.size:
                        if self.grid[nx][ny] != '~':
                            return False
        
        for x, y in ship.positions:
            self.grid[x][y] = '■'
        
        self.ships.append(ship)
        return True

    def receive_attack(self, x: int, y: int) -> Tuple[bool, Optional[Ship]]:
        if not (0 <= x < self.size and 0 <= y < self.size):
            return False, None
        
        if self.grid[x][y] == 'X' or self.grid[x][y] == '○':
            return False, None
        
        hit_ship = None
        for ship in self.ships:
            if ship.hit((x, y)):
                hit_ship = ship
                break
        
        if hit_ship:
            self.grid[x][y] = 'X'
            self.hit_cells.add((x, y))
            return True, hit_ship
        else:
            self.grid[x][y] = '○'
            self.miss_cells.add((x, y))
            return False, None