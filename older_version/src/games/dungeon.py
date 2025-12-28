import random

class DungeonGame:
    def __init__(self, size=6):
        self.size = size
        self.player_pos = [0, 0]
        self.exit_pos = [size-1, size-1]
        self.hp = 100
        self.gold = 0
        self.log = ["Welcome to the Dungeon of Bugs! Find the exit (🏁)."]
        self.game_over = False
        self.won = False
        
        # 初始化地圖
        # 0: Empty, 1: Bug (Enemy), 2: Coffee (Heal), 3: Feature (Gold)
        self.board = [[0 for _ in range(size)] for _ in range(size)]
        self._generate_map()

    def _generate_map(self):
        # 隨機放置陷阱 (Bugs) 和 寶物 (Features)
        for r in range(self.size):
            for c in range(self.size):
                if (r, c) == (0, 0) or (r, c) == (self.size-1, self.size-1):
                    continue
                
                rand = random.random()
                if rand < 0.2:
                    self.board[r][c] = 1 # Bug (Damage)
                elif rand < 0.3:
                    self.board[r][c] = 2 # Coffee (Heal)
                elif rand < 0.4:
                    self.board[r][c] = 3 # Feature (Gold)

    def move(self, direction):
        if self.game_over: return

        r, c = self.player_pos
        new_r, new_c = r, c

        if direction == "UP" and r > 0: new_r -= 1
        elif direction == "DOWN" and r < self.size - 1: new_r += 1
        elif direction == "LEFT" and c > 0: new_c -= 1
        elif direction == "RIGHT" and c < self.size - 1: new_c += 1
        else:
            self.log.append("🚫 Can't move that way!")
            return

        self.player_pos = [new_r, new_c]
        self._encounter_event(new_r, new_c)

    def _encounter_event(self, r, c):
        cell = self.board[r][c]
        
        if [r, c] == self.exit_pos:
            self.won = True
            self.game_over = True
            self.log.append("🏆 You deployed to Production successfully!")
            return

        if cell == 1: # Bug
            dmg = random.randint(10, 25)
            self.hp -= dmg
            self.log.append(f"👾 You encountered a Critical Bug! -{dmg} HP")
            self.board[r][c] = 0 # Clear event
        elif cell == 2: # Coffee
            heal = random.randint(10, 20)
            self.hp += heal
            if self.hp > 100: self.hp = 100
            self.log.append(f"☕ You drank some coffee. +{heal} HP")
            self.board[r][c] = 0
        elif cell == 3: # Feature
            gain = random.randint(100, 500)
            self.gold += gain
            self.log.append(f"💎 You shipped a new feature! +${gain}")
            self.board[r][c] = 0
        
        if self.hp <= 0:
            self.game_over = True
            self.log.append("💀 Project Failed. The bugs won.")