import random
from typing import Any
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
        else:
            print('Invalid difficulty')
            return
        
        self.mine_locations = self.generate_mines()
        self.ans_board = self.generate_board("Ans")
        self.player_board = self.generate_board("Player")
        self.assign_answer_board()
        self.KB = self.get_init_save()
        self.KB0 = set()
        
        for i in range(1):
            self.play()
            
        print("KB0:", len(self.KB0), "KB:", len(self.KB))
        
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
                    safe_locations.add(Clause(Literal((i, j), False)))
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
            return "Over"
        elif int(self.ans_board[x][y]) > 0:
            self.player_board[x][y] = self.ans_board[x][y]
            return int(self.ans_board[x][y])
        else:             
            self.player_board[x][y] = self.ans_board[x][y]
            return int(0)

    
    def play(self):
        KB = self.KB.copy()
        for kb in KB:
            #print("len KB:", len(KB))
            if kb.check_single():
                #print("Digging", kb.literals[0].point[0], kb.literals[0].point[1])
                self.KB0.add(kb)
                self.KB.remove(kb)
                x, y = kb.literals[0].point[0], kb.literals[0].point[1]
                num_mine = self.dig(x, y)
                #print("num_mine:", num_mine)
                if num_mine == "Over":
                    print("Game over")
                    return False
                elif num_mine == 0:
                    #print("No mine in arrond")
                    for i in range(x-1, x+2):
                        for j in range(y-1, y+2):
                            if i < 0 or i >= self.width or j < 0 or j >= self.length:
                                continue
                            else:
                                #print("add KB", i, j)
                                self.KB.add(Clause(Literal((i, j), False)))
                else:
                    arrond = []
                    for i in range(x-1, x+2):
                        for j in range(y-1, y+2):
                            if i < 0 or i >= self.width or j < 0 or j >= self.length or (x, y) == (i, j):
                                continue
                            else:
                                arrond.append((i, j))
                    if len(arrond) == num_mine:
                        #print("len arrond == num_mine")
                        #print("All mines in arrond")
                        for i in arrond:
                            self.add_clause(Clause(Literal(i, True)))
                    else:
                        # positive
                        #print("arrond:", len(arrond), "num_mine:", num_mine)
                        c = itertools.combinations(arrond, len(arrond) - int(num_mine) + 1)
                        for i in c:
                            tmp = Clause()
                            for j in i:
                                tmp.add_literal(Literal(j, True))
                            #print("len tmp:", len(tmp.literals))
                            self.add_clause(tmp)
                        # negative
                        c = itertools.combinations(arrond, int(num_mine) + 1)
                        for i in c:
                            tmp = Clause()
                            for j in i:
                                    tmp.add_literal(Literal(j, False))
                            #print("len tmp:", len(tmp.literals))
                            self.add_clause(tmp)

        return True
    
    def add_clause(self, clause):
        # check kb0
        tmp = []

        for kb in self.KB0:
            for literal in clause.literals:
                if literal.point == kb.literals[0].point and literal.negative != kb.literals[0].negative:
                    #print("removing", literal.point, literal.negative, kb.literals[0].negative)
                    tmp.append(literal)
        for i in tmp:
            #print("removing", i.point)
            clause.literals.remove(i)
        if len(clause.literals) == 0:
            return
        # check kb
        KB_remove = []
        for kb in self.KB:
            # check if clause is subset of kb
            if len(clause.literals) <= len(kb.literals):
                flag = True
                for literal in kb.literals:
                    if literal not in clause.literals:
                        flag = False
                        break
                if flag: # kb is subset of clause
                    return
            else:
                flag = True
                for literal in clause.literals:
                    if literal not in kb.literals:
                        flag = False
                        break
                if flag: # clause is subset of kb
                    KB_remove.append(kb)
        for i in KB_remove:
            self.KB.remove(i)

        if len(clause.literals) == 1:
            print("len == 1")
            for kb in self.KB0:
                if clause.literals[0].point == kb.literals[0].point and clause.literals[0].negative == kb.literals[0].negative:
                    print("already in KB0")
                    return
        
        
        self.KB.add(clause)
                            
                        
class Literal:
    def __init__(self):
        self.point = None
        self.negative = False
        
    def __init__(self, point = None, negative = None):
        self.point = point
        self.negative = negative
        
        

class Clause:
    def __init__(self, literal = None):
        if literal is not None:
            self.literals = [literal]
        else:
            self.literals = []
        self.satisfied = False
        
    def add_literal(self, literal):
        self.literals.append(literal)
        
        
    def check_single(self):
        return len(self.literals) == 1 and self.literals[0].negative == False
    
    def print_clause(self):
        for literal in self.literals:
            print(literal.point, literal.negative, end = ' ')
        print()
    
    
def check_in_KB0(point, KB):
    for clause in KB:
        for literal in clause.literals:
            if literal.point == point:
                #print("Already in KB0")
                return True
    #print("Not in KB0")
    return False   

    
                    
if __name__ == '__main__':
    board = Board('Easy')
    board.print_board("Player")

    
    