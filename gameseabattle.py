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

    def get_accuracy(self) -> float:
        if self.shots == 0:
            return 0.0
        return (self.hits / self.shots) * 100
    
    def save_stats(self, filename: str = "battleship_stats.json") -> None:
        stats = {
            "player": self.name,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "shots": self.shots,
            "hits": self.hits,
            "misses": self.misses,
            "accuracy": self.get_accuracy(),
            "ships_sunk": self.ships_sunk,
            "score": self.score
        }
        
        all_stats = []
        if os.path.exists(filename):
            with open(filename, "r") as f:
                try:
                    all_stats = json.load(f)
                except json.JSONDecodeError:
                    all_stats = []
        
        all_stats.append(stats)
        
        with open(filename, "w") as f:
            json.dump(all_stats, f, indent=2)
        
        print(f"\nСтатистика игры сохранена в файл {filename}")

class AIPlayer(Player):
    DIFFICULTY_LEVELS = {
        "easy": {"delay": 2.0, "randomness": 0.7},
        "medium": {"delay": 1.0, "randomness": 0.4},
        "hard": {"delay": 0.5, "randomness": 0.1}
    }
    
    def __init__(self, difficulty: str = "medium"):
        super().__init__("Компьютер")
        self.last_hits = []
        self.directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        self.current_direction = None
        self.first_hit = None
        self.difficulty = difficulty if difficulty in self.DIFFICULTY_LEVELS else "medium"
        self.available_shots = [(x, y) for x in range(10) for y in range(10)]
        random.shuffle(self.available_shots)
    
    def place_ships(self) -> None:
        ship_sizes = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]
        for size in ship_sizes:
            placed = False
            attempts = 0
            
            while not placed and attempts < 100:
                x = random.randint(0, self.board.size - 1)
                y = random.randint(0, self.board.size - 1)
                orientation = random.choice(['г', 'в'])
                
                positions = []
                if orientation == 'г':
                    for i in range(size):
                        positions.append((x, y + i))
                else:
                    for i in range(size):
                        positions.append((x + i, y))
                
                ship = Ship(size, positions)
                if self.board.place_ship(ship):
                    placed = True
                else:
                    attempts += 1
            
            if not placed:
                print(f"Компьютер не смог разместить корабль размером {size} после 100 попыток.")
    
    def make_move(self, opponent: Player) -> bool:
        print(f"\nХод компьютера {self.name} (уровень: {self.difficulty})")
        time.sleep(self.DIFFICULTY_LEVELS[self.difficulty]["delay"])

        if self.last_hits and random.random() > self.DIFFICULTY_LEVELS[self.difficulty]["randomness"]:
            if not self.current_direction:
                if not self.first_hit:
                    self.first_hit = self.last_hits[0]
                
                for dx, dy in self.directions:
                    x, y = self.first_hit
                    x += dx
                    y += dy
                    if 0 <= x < self.board.size and 0 <= y < self.board.size:
                        if opponent.board.grid[x][y] not in ['X', '○'] and (x, y) in self.available_shots:
                            self.available_shots.remove((x, y))
                            print(f"Компьютер стреляет в {x} {y}")
                            hit, ship = opponent.board.receive_attack(x, y)
                            self.shots += 1
                            
                            if hit:
                                self.hits += 1
                                self.last_hits.append((x, y))
                                self.current_direction = (dx, dy)
                                print("Попадание!")
                                if ship.is_sunk():
                                    self.ships_sunk += 1
                                    self.score += ship.size * 10
                                    print(f"{ship.name} размером {ship.size} потоплен!")
                                    self.last_hits = []
                                    self.current_direction = None
                                    self.first_hit = None
                                    self.remove_adjacent_cells(ship, opponent)
                                else:
                                    self.score += 5
                                return True
                            else:
                                self.misses += 1
                                print("Промах!")
                                return False
            else:
                last_x, last_y = self.last_hits[-1]
                dx, dy = self.current_direction
                x = last_x + dx
                y = last_y + dy
                
                if 0 <= x < self.board.size and 0 <= y < self.board.size:
                    if opponent.board.grid[x][y] not in ['X', '○'] and (x, y) in self.available_shots:
                        self.available_shots.remove((x, y))
                        print(f"Компьютер стреляет в {x} {y}")
                        hit, ship = opponent.board.receive_attack(x, y)
                        self.shots += 1
                        
                        if hit:
                            self.hits += 1
                            self.last_hits.append((x, y))
                            print("Попадание!")
                            if ship.is_sunk():
                                self.ships_sunk += 1
                                self.score += ship.size * 10
                                print(f"{ship.name} размером {ship.size} потоплен!")
                                self.last_hits = []
                                self.current_direction = None
                                self.first_hit = None
                                self.remove_adjacent_cells(ship, opponent)
                            else:
                                self.score += 5
                            return True
                        else:
                            self.misses += 1
                            print("Промах!")
                            self.current_direction = (-dx, -dy)
                            return False
                else:
                    self.current_direction = (-dx, -dy)
                    return self.make_move(opponent)
                
        while self.available_shots:
            x, y = self.available_shots.pop()
            if opponent.board.grid[x][y] not in ['X', '○']:
                print(f"Компьютер стреляет в {x} {y}")
                hit, ship = opponent.board.receive_attack(x, y)
                self.shots += 1
                
                if hit:
                    self.hits += 1
                    self.last_hits.append((x, y))
                    print("Попадание!")
                    if ship.is_sunk():
                        self.ships_sunk += 1
                        self.score += ship.size * 10
                        print(f"{ship.name} размером {ship.size} потоплен!")
                        self.last_hits = []
                        self.remove_adjacent_cells(ship, opponent)
                    else:
                        self.score += 5
                    return True
                else:
                    self.misses += 1
                    print("Промах!")
                    return False
        
        print("Компьютер не нашел доступных клеток для выстрела!")
        return False
    
    def remove_adjacent_cells(self, ship: Ship, opponent: Player) -> None:
        """Удаляет соседние клетки потопленного корабля из доступных для выстрелов"""
        for x, y in ship.positions:
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.board.size and 0 <= ny < self.board.size:
                        if (nx, ny) in self.available_shots:
                            self.available_shots.remove((nx, ny))

class Game:
    def __init__(self):
        print("Добро пожаловать в игру 'Морской бой'!")
        print("="*40)
        self.show_menu()
    
    def show_menu(self) -> None:
        while True:
            print("\nГлавное меню:")
            print("1. Играть против компьютера")
            print("2. Играть против другого игрока")
            print("3. Просмотреть статистику")
            print("4. Выход")
            
            choice = input("Выберите опцию: ")
            
            if choice == '1':
                self.setup_game_vs_ai()
                break
            elif choice == '2':
                self.setup_game_vs_player()
                break
            elif choice == '3':
                self.show_stats()
            elif choice == '4':
                print("До свидания!")
                exit()
            else:
                print("Неверный выбор. Попробуйте снова.")
    
    def setup_game_vs_ai(self) -> None:
        print("\nВыберите уровень сложности:")
        print("1. Легкий")
        print("2. Средний")
        print("3. Сложный")
        
        while True:
            choice = input("Ваш выбор (1-3): ")
            if choice in ['1', '2', '3']:
                difficulty = ["easy", "medium", "hard"][int(choice)-1]
                break
            print("Неверный выбор. Попробуйте снова.")
        
        self.player1 = Player(input("Введите ваше имя: "))
        self.player2 = AIPlayer(difficulty)
        self.current_player = self.player1
        self.opponent = self.player2
    
    def setup_game_vs_player(self) -> None:
        self.player1 = Player(input("Введите имя первого игрока: "))
        self.player2 = Player(input("Введите имя второго игрока: "))
        self.current_player = self.player1
        self.opponent = self.player2
    
    def show_stats(self, filename: str = "battleship_stats.json") -> None:
        if not os.path.exists(filename):
            print("Статистика пока недоступна.")
            return
        
        try:
            with open(filename, "r") as f:
                stats = json.load(f)
            
            if not stats:
                print("Статистика пока недоступна.")
                return
            
            print("\nИстория игр:")
            print("="*80)
            print(f"{'Игрок':<15} {'Дата':<20} {'Выстрелы':<10} {'Попадания':<10} {'Точность':<10} {'Потоплено':<10} {'Очки':<10}")
            print("-"*80)
            
            for game in sorted(stats, key=lambda x: x['date'], reverse=True)[:10]:
                print(f"{game['player']:<15} {game['date']:<20} {game['shots']:<10} {game['hits']:<10} "
                      f"{game['accuracy']:.1f}%{'':<3} {game['ships_sunk']:<10} {game['score']:<10}")
            
            input("\nНажмите Enter чтобы вернуться в меню...")
        except json.JSONDecodeError:
            print("Ошибка чтения файла статистики.")
    
    def setup(self) -> None:
        print("\nЭтап размещения кораблей:")
        print("="*40)
        
        print("\nИгрок 1 размещает корабли:")
        self.player1.place_ships()
        
        if isinstance(self.player2, AIPlayer):
            print("\nКомпьютер размещает корабли...")
            self.player2.place_ships()
        else:
            print("\nИгрок 2 размещает корабли:")
            self.player2.place_ships()