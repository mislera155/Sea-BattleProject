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
    
    def all_ships_sunk(self) -> bool:
        return all(ship.is_sunk() for ship in self.ships)
    
    def display(self, show_ships: bool = False) -> None:
        print("   " + " ".join(f"{i:2}" for i in range(self.size)))
        for i in range(self.size):
            row = []
            for j in range(self.size):
                cell = self.grid[i][j]
                if not show_ships and cell == '■':
                    row.append(' ~')
                else:
                    row.append(f" {cell}")
            print(f"{i:2}" + "".join(row))
    
    def get_ship_at_position(self, x: int, y: int) -> Optional[Ship]:
        for ship in self.ships:
            if (x, y) in ship.positions:
                return ship
        return None

class Player:
    def __init__(self, name: str):
        self.name = name
        self.board = Board()
        self.enemy_board = Board()
        self.score = 0
        self.shots = 0
        self.hits = 0
        self.misses = 0
        self.ships_sunk = 0
    
    def place_ships(self) -> None:
        ship_sizes = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]
        print(f"\n{self.name}, доступные корабли:")
        for size in ship_sizes:
            print(f"- {Ship.get_ship_name(size)} (размер: {size})")
        
        for size in ship_sizes:
            placed = False
            while not placed:
                print(f"\n{self.name}, разместите {Ship.get_ship_name(size)} (размер: {size})")
                self.board.display(show_ships=True)
                
                try:
                    x, y = map(int, input("Введите начальные координаты (строка столбец): ").split())
                    orientation = input("Выберите ориентацию (г - горизонтально, в - вертикально): ").lower()
                    
                    positions = []
                    if orientation == 'г':
                        for i in range(size):
                            positions.append((x, y + i))
                    elif orientation == 'в':
                        for i in range(size):
                            positions.append((x + i, y))
                    else:
                        print("Неверная ориентация. Используйте 'г' или 'в'.")
                        continue
                    
                    ship = Ship(size, positions)
                    if self.board.place_ship(ship):
                        placed = True
                    else:
                        print("Невозможно разместить корабль в этом месте. Попробуйте снова.")
                except ValueError:
                    print("Неверный ввод. Введите координаты как два числа через пробел.")
        
        print(f"\n{self.name}, все корабли размещены!")
        self.board.display(show_ships=True)
        input("Нажмите Enter чтобы продолжить...")
        
    def make_move(self, opponent: 'Player') -> bool:
        print(f"\nХод игрока {self.name}")
        print("Ваше поле:")
        self.board.display(show_ships=True)
        print("\nПоле противника:")
        opponent.board.display(show_ships=False)
        
        # Показать статистику
        print(f"\nСтатистика {self.name}:")
        print(f"Выстрелы: {self.shots} | Попадания: {self.hits} | Промахи: {self.misses}")
        print(f"Точность: {self.get_accuracy():.1f}% | Потоплено кораблей: {self.ships_sunk}")
        
        while True:
            try:
                coords = input("Введите координаты для выстрела (строка столбец) или 'q' для выхода: ")
                if coords.lower() == 'q':
                    print("Игра прервана.")
                    exit()
                
                x, y = map(int, coords.split())
                hit, ship = opponent.board.receive_attack(x, y)
                self.shots += 1
                
                if hit:
                    self.hits += 1
                    print("Попадание!")
                    if ship.is_sunk():
                        self.ships_sunk += 1
                        print(f"{ship.name} размером {ship.size} потоплен!")
                        # Награда за потопление корабля
                        self.score += ship.size * 10
                    else:
                        # Награда за попадание
                        self.score += 5
                    return True
                else:
                    self.misses += 1
                    print("Промах!")
                    return False
            except ValueError:
                print("Неверный ввод. Введите координаты как два числа через пробел.")