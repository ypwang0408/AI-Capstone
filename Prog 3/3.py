## Author: 109550008 Yu-Po Wang
import random
import numpy as np
import math
import itertools
    
class Board:
    def __init__(self, difficulty):
        self.difficulty = difficulty
        if self.difficulty == 'Easy':
            self.length = 9
            self.width = 9
            self.mines = 10
        elif self.difficulty == 'Medium':
            self.length = 16
            self.width = 16
            self.mines = 25
        elif self.difficulty == 'Hard':
            self.length = 30
            self.width = 16
            self.mines = 99
        elif self.difficulty == 'Custom':
            self.length = 5
            self.width = 5
            self.mines = 5
        else:
            print('Invalid difficulty')
            return
        
        self.mine_locations = self.generate_mines()
        self.ans_board = self.generate_board("Ans")
        self.player_board = self.generate_board("Player")
        self.assign_answer_board()
        self.KB = self.get_init_safe()
        self.KB0 = set()
        
    def game_start(self):
        for i in range(self.width * self.length + 100):
            #print("round:", i, "KB0:", len(self.KB0), "KB:", len(self.KB))
            if self.play() == -1:
                break
            #print("-" * self.length * 2)
            #self.print_board("Player")
            
        print("-" * self.length, "Final", "-" * self.length)
        self.print_board("Player")
        
        if self.check_win():
            print("You Win!")
        else:
            print("You Lose!")
              
    def generate_mines(self):
        mine_locations = []
        while len(mine_locations) < self.mines:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.length - 1)
            if (x, y) not in mine_locations:
                mine_locations.append((x, y))
        return mine_locations
    
    def generate_board(self, which_board):
        board = np.empty((self.width, self.length), dtype = str)
        for i in range(self.width):
            for j in range(self.length):
                if which_board == "Ans":
                    board[i][j] = '0'
                elif which_board == "Player":
                    board[i][j] = '.'
        return board
    
    def assign_answer_board(self):
        for mine in self.mine_locations:
            self.ans_board[mine[0]][mine[1]] = 'M'
        for i in range(self.width):
            for j in range(self.length):
                if self.ans_board[i][j] == 'M':
                    continue
                else:
                    count = 0
                    for x in range(i - 1, i + 2):
                        for y in range(j - 1, j + 2):
                            if (x, y) in self.mine_locations:
                                count += 1
                    self.ans_board[i][j] = str(count)
                    
    def get_init_safe(self):
        safe_locations = []
        self.init_safe = []
        for i in range(self.width):
            for j in range(self.length):
                if self.ans_board[i][j] != 'M':
                    tmp = set()
                    tmp.add((i * self.length + j + 1) * -1)
                    safe_locations.append(tmp)
        num_init = round(math.sqrt(self.width * self.length))
        tmp = random.sample(safe_locations, num_init)
        for i in tmp:
            self.init_safe.append(i)
        return self.init_safe
    
    def print_board(self, which_board):
        for i in range(self.width):
            for j in range(self.length):
                if which_board == "Ans":
                    print(self.ans_board[i][j], end = ' ')
                elif which_board == "Player":
                    print(self.player_board[i][j], end = ' ')
            print()
    
    def dig(self, x, y):
        if self.ans_board[x][y] == 'M':
            self.player_board[x][y] = 'M'
            return int(-1)
        elif int(self.ans_board[x][y]) > 0:
            self.player_board[x][y] = self.ans_board[x][y]
            return int(self.ans_board[x][y])
        else:             
            self.player_board[x][y] = self.ans_board[x][y]
            return int(0)
        
    def clean_KBs(self):
        change = True
        while change:
            change = False
            for c in self.KB:
                if c.copy().pop() in self.KB0:
                    self.KB.remove(c)
                    change = True
                    break
        self.KB = np.unique(self.KB)
        self.KB = sorted(self.KB, key = lambda x: len(x))
            
    def mark_mine(self, x, y):
        self.player_board[x][y] = 'T'
        
    def KB_to_KB0(self, target):
        tar = target.copy().pop()
        id = abs(tar)
        mine_or_safe = tar > 0
        self.KB.remove(target)
        self.KB0.add(tar)
        tmp_remove_KB = []
        for c in self.KB:
            tmp_remove_clause = []
            for l in c:
                if abs(l) == id:
                    if (l > 0) == mine_or_safe:
                        tmp_remove_KB.append(c)
                    else:
                        tmp_remove_clause.append(l)
            for l in tmp_remove_clause:
                c.remove(l)
            if len(c) == 0:
                tmp_remove_KB.append(c)
        for c in tmp_remove_KB:
            self.KB.remove(c)
        change = True
        while change:
            change = False
            for c in self.KB:
                for c1 in self.KB:
                    if c == c1:
                        continue
                    if c.issubset(c1):
                        self.KB.remove(c1)
                        change = True
                        break
    
    def add_to_KB(self, target):
        if target in self.KB:
            return
        if len(target) == 1:
            self.KB.append(target)
        # doing resolution
        tmp = []
        for t in target:
            if -t in self.KB0:
                tmp.append(t)
            elif t in self.KB0:
                return
        for t in tmp:
            target.remove(t)
        # need to check if target is a subset of any clause in KB
        cp = self.KB.copy()
        change = True
        while change:
            for c in self.KB:
                if c.issubset(target):
                    return
                elif target.issubset(c):
                    self.KB.remove(c)
                    self.KB.append(target)
                    break
            if cp == self.KB:
                change = False
            else:
                cp = self.KB.copy()
        self.KB.append(target)
        
    def play(self):
        self.clean_KBs()
        target = None
        for clause in self.KB:
            if len(clause) == 1:
                target = clause
                break
        if target == None:
            return -1
        self.KB_to_KB0(target)
        tar = target.copy().pop()
        id = abs(tar)
        x, y = (id - 1) // self.length, (id - 1) % self.length
        mine_or_safe = tar > 0
        if mine_or_safe:
            self.mark_mine(x, y)
            return 1
        else:
            num_mine = self.dig(x, y)
        if num_mine == -1:
            print("Game Over")
            return -2
        elif num_mine == 0:
            for i in range(x-1, x+2):
                for j in range(y-1, y+2):
                    if i < 0 or i >= self.width or j < 0 or j >= self.length or (i, j) == (x, y):
                        continue
                    else:
                        self.add_to_KB({(i * self.length + j + 1) * -1})
        else:
            around = []
            for i in range(x-1, x+2):
                for j in range(y-1, y+2):
                    if i < 0 or i >= self.width or j < 0 or j >= self.length or (i, j) == (x, y):
                        continue
                    else:
                        around.append((i * self.length + j + 1))
            if len(around) == num_mine:
                for i in around:
                    self.add_to_KB({i})
            else:
                comb = itertools.combinations(around, len(around) - num_mine + 1)
                for c in comb:
                    tmp = set()
                    for i in c:
                        tmp.add(i)
                    self.add_to_KB(tmp)
                
                comb = itertools.combinations(around, num_mine + 1)
                for c in comb:
                    tmp = set()
                    for i in c:
                        tmp.add(i * -1)
                    self.add_to_KB(tmp)
        self.clean_KBs()
    
    def check_win(self):
        cnt = 0
        for i in range(self.width):
            for j in range(self.length):
                if self.player_board[i][j] == self.ans_board[i][j] or self.player_board[i][j] == 'T' and self.ans_board[i][j] == 'M':
                    cnt += 1

        return cnt == self.width * self.length   
                    
if __name__ == '__main__':
    easy = Board('Easy')
    easy.game_start()
    medium = Board('Medium')
    medium.game_start()
    hard = Board('Hard')
    hard.game_start()
    
    