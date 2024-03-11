import random
from typing import Any
import numpy as np
import math
import itertools
    
class Board:
    def __init__(self, difficulty):
        self.difficulty = difficulty
        if self.difficulty == 'Easy':
            self.length = 5
            self.width = 5
            self.mines = 9
        elif self.difficulty == 'Medium':
            self.length = 16
            self.width = 16
            self.mines = 25
        elif self.difficulty == 'Hard':
            self.length = 30
            self.width = 16
            self.mines = 99
        else:
            print('Invalid difficulty')
            return
        
        self.mine_locations = self.generate_mines()
        self.ans_board = self.generate_board("Ans")
        self.player_board = self.generate_board("Player")
        self.assign_answer_board()
        self.KB = self.get_init_save()
        self.KB0 = set()
        
        for i in range(10):
            print("-------- round", i, "--------")
            self.play()
            print("KB0:", len(self.KB0), "KB:", len(self.KB))
            print("-------- player board --------")
            self.print_board("Player")
            print("-------- KB0 --------")
            for clause in self.KB0:
                clause.print_clause()
            print("-------- KB --------")
            for clause in self.KB:
                clause.print_clause()
            

        
    def generate_mines(self):
        mine_locations = []
        while len(mine_locations) < self.mines:
            x, y = random.randint(0, self.width - 1), random.randint(0, self.length - 1)
            if (x, y) not in mine_locations:
                mine_locations.append((x, y))
        return mine_locations
    
    def get_init_save(self):
        safe_locations = set()
        self.init_save = set()
        for i in range(self.width):
            for j in range(self.length):
                if self.ans_board[i][j] != 'M':
                    safe_locations.add(Clause(Literal((i * self.length + j), False)))
        tmp = random.sample(safe_locations, round(math.sqrt(self.width * self.length)))
        for i in tmp:
            self.init_save.add(i)
        return self.init_save

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
    
    def KB_to_KB0(self, clause):
        id = clause.literals[0].point
        mine_or_not = clause.literals[0].negative
        self.KB.remove(clause)
        self.KB0.add(clause)
        tmp = []
        tmp_new = []
        for c in self.KB:
            tmp_l = []
            for l in c.literals:
                if l.point == id and l.negative == mine_or_not:         # 直接拿掉clause
                    tmp.append(c)
                elif l.point == id and l.negative != mine_or_not:       # 把那個literal拿掉
                    tmp_l.append(l)
            if len(tmp_l) > 0:
                copy = l
                for l in tmp_l:
                    copy.literals.remove(l)
                tmp_new.append(copy)
        
        for c in tmp:
            self.KB.remove(c)
            
        for c in tmp_new:
            self.KB.add(c)
        
    def check_same_clause(self, clause1, clause2):
        if len(clause1.literals) != len(clause2.literals):
            return False
        for l1 in clause1.literals:
            flag = False
            for l2 in clause2.literals:
                if l1.point == l2.point and l1.negative == l2.negative:
                    flag = True
                    break
            if flag == False:
                return False
        return True
    
    def check_subsumption(self, clause1, clause2):
        for l1 in clause1.literals:
            if l1 not in clause2.literals:
                return False
        print("Subsumption")
        return True
    
    def check_in_KB0(self, clause):
        for c in self.KB0:
            if c.literals[0].point == clause.point and c.literals[0].negative != clause.negative:
                return True
            
    def add_to_KB(self, clause):
        # doing resolution
        # print('Original clause:', end = ' ')
        # for c in clause:
        #     print(c.point, c.negative, end = ' ')
        # print()
        
        tmp = []
        for c in clause:
            if self.check_in_KB0(c):        # 如果KB0有相反的，把clause拿掉(return)
                return
        
        #print('After resolution:', end = ' ')
        #for c in clause:
        #    print(c.point, c.negative, end = ' ')
        #print()
        
        C = Clause()
        for c in clause:
            C.literals.append(c)
            
        # check subsumption
        tmp = []
        for c in self.KB:
            sub = self.check_subsumption(C, c)
            if sub == True:
                tmp.append(c)
            else:
                sub = self.check_subsumption(c, C)
                if sub == True:
                    return
                
        for c in tmp:
            print("Remove from KB:", end = ' ')
            c.print_clause()
            self.KB.remove(c)
            
        #print("Add to KB:", end = ' ')
        C.print_clause()
        self.KB.add(C)
    
    def mark(self, x, y):
        self.player_board[x][y] = 'T'
    
    def play(self):
        for kb in self.KB:
            if len(kb.literals) == 1:
                target = kb
                break
            
        self.KB_to_KB0(target)
        id = target.literals[0].point
        x, y = id // self.length, id % self.length
        if target.literals[0].negative == True:
            print("Marking:", x, y)
            self.mark(x, y)
            return True
        else:
            num_mine = self.dig(x, y)
        print("Dig:", x, y, num_mine)
        if num_mine == -1:
            print("You lose!")
            return False
        elif num_mine == 0:
            for i in range(x - 1, x + 2):
                for j in range(y - 1, y + 2):
                    if i < 0 or i >= self.width or j < 0 or j >= self.length:
                        continue
                    else:
                        tmp = []
                        tmp.append(Literal(i * self.length + j, False))
                        self.add_to_KB(tmp)
        else:
            around = []
            for i in range(x-1, x+2):
                for j in range(y-1, y+2):
                    if i < 0 or i >= self.width or j < 0 or j >= self.length or (x, y) == (i, j):
                        continue
                    else:
                        around.append(i * self.length + j)
            if len(around) == num_mine:
                print("All mines")
                for i in around:
                    self.add_to_KB([Literal(i, True)])
            else:
                # clause with mine
                comb = itertools.combinations(around, len(around) - num_mine + 1)
                for i in comb:
                    tmp = []
                    for j in i:
                        tmp.append(Literal(j, True))
                    self.add_to_KB(tmp)
                # clause with safe
                comb = itertools.combinations(around, num_mine + 1)
                for i in comb:
                    tmp = []
                    for j in i:
                        tmp.append(Literal(j, False))
                    self.add_to_KB(tmp)
                    
        
        
        
                            
                        
class Literal:
    def __init__(self, point = None, negative = None):
        self.point = point
        self.negative = negative
        
    def __hash__(self) -> int:
        return hash((self.point, self.negative))

class Clause:
    def __init__(self, literal = None):
        if literal is not None:
            self.literals = [literal]
        else:
            self.literals = []
        self.satisfied = False
    
        
    def print_clause(self):
        for literal in self.literals:
            if literal.negative:
                print(literal.point, "+", end = ' ')
            else:
                print(literal.point, "-", end = ' ')
        print()
        
    def __hash__(self) -> int:
        return hash(tuple(self.literals))
    
    def __eq__(self, o: object) -> bool:
        pass
    
        

    
                    
if __name__ == '__main__':
    board = Board('Easy')
    board.print_board("Player")
    
    