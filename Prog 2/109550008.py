import STcpClient_1 as STcpClient
import numpy as np
import random
import time


'''
    input position (x,y) and direction
    output next node position on this direction
'''
def Next_Node(pos_x,pos_y,direction):
    if pos_y%2==1:
        if direction==1:
            return pos_x,pos_y-1
        elif direction==2:
            return pos_x+1,pos_y-1
        elif direction==3:
            return pos_x-1,pos_y
        elif direction==4:
            return pos_x+1,pos_y
        elif direction==5:
            return pos_x,pos_y+1
        elif direction==6:
            return pos_x+1,pos_y+1
    else:
        if direction==1:
            return pos_x-1,pos_y-1
        elif direction==2:
            return pos_x,pos_y-1
        elif direction==3:
            return pos_x-1,pos_y
        elif direction==4:
            return pos_x+1,pos_y
        elif direction==5:
            return pos_x-1,pos_y+1
        elif direction==6:
            return pos_x,pos_y+1


def checkRemainMove(mapStat):
    free_region = (mapStat == 0)
    temp = []
    for i in range(len(free_region)):
        for j in range(len(free_region[0])):
            if(free_region[i][j] == True):
                temp.append([i,j])
    return temp


'''
    輪到此程式移動棋子
    mapStat : 棋盤狀態(list of list), 為 12*12矩陣, 0=可移動區域, -1=障礙, 1~2為玩家1~2佔領區域
    gameStat : 棋盤歷史順序
    return Step
    Step : 3 elements, [(x,y), l, dir]
            x, y 表示要畫線起始座標
            l = 線條長度(1~3)
            dir = 方向(1~6),對應方向如下圖所示
              1  2
            3  x  4
              5  6
'''
def Getstep(mapStat, gameStat):
    #Please write your code here
    #TODO
    step = GetBestStep(mapStat)
    return step
    
def GetLegalMovements(mapStat):
    legal_points = checkRemainMove(mapStat)
    legal_movements = []
    for point in legal_points:
        legal_movements.append([point,1,1])
    for point in legal_points:
        for i in range(1,4):
            x, y = point[0], point[1]
            for l in range(2,4):
                x,y = Next_Node(x,y,i)
                if(x>=0 and x<12 and y>=0 and y<12 and mapStat[x][y]==0):
                    legal_movements.append([point,l,i])
                else:
                    break
    return legal_movements

def GetBestStep(mapStat):
    DEPTH = 4
    def MaxAgent(mapStat, depth, alpha=float('-inf'), beta=float('inf')):
        if isEnd(mapStat):
            return GetScore(mapStat) * 10, [0]
        moves = GetLegalMovements(mapStat)
        bestScore = float('-inf')
        score = float('-inf')
        bestMove = moves[0]
        for move in moves:
            score = MinAgent(UpdateMapStat(mapStat, move), depth, alpha, beta)
            if score > bestScore:
                bestScore = score
                bestMove = move
            alpha = max(alpha, bestScore)
            if alpha >= beta:
                return bestScore, bestMove
            
        return bestScore, bestMove
        
    def MinAgent(mapStat, depth, alpha=float('-inf'), beta=float('inf')):
        if isEnd(mapStat):
            return -10 * GetScore(mapStat)
        moves = GetLegalMovements(mapStat)
        bestScore = float('inf')
        score = float('inf')
        for move in moves:
            if depth == DEPTH - 1:
                score = -1 * GetScore(UpdateMapStat(mapStat, move))
            else:
                score, _ = MaxAgent(UpdateMapStat(mapStat, move), depth + 1, alpha, beta)
                if score < bestScore:
                    bestScore = score
            beta = min(beta, bestScore)
            if beta <= alpha:
                return bestScore
        return bestScore
    
    BestMove = []
    moves = GetLegalMovements(mapStat)
    if len(moves) == 1:
        return moves[0]  
    elif len(moves) > 19:
        print('random')
        return random.choice(moves)
    BestScore, BestMove = MaxAgent(mapStat, 0)
    
    if BestMove == 0 or BestScore == float('inf'):
        print('random')
        return random.choice(GetLegalMovements(mapStat))
    return BestMove
                   

def UpdateMapStat(mapStat, step):
    tmp = mapStat.copy()
    x = step[0][0]
    y = step[0][1]
    l = step[1]
    dir = step[2]
    for i in range(l):
        tmp[x][y] = 1
        x,y = Next_Node(x,y,dir)
    return tmp

def GetScore(mapStat):
    legal_points = checkRemainMove(mapStat)
    if(len(legal_points)==0):
        return 100
    elif (len(legal_points) == 1):
        return -100
    else:
        return -1 * legal_points
    
def isEnd(mapStat):
    legal_points = checkRemainMove(mapStat)
    return len(legal_points)==0
    
# start game
print('start game')
while (True):

    (end_program, id_package, mapStat, gameStat) = STcpClient.GetBoard()
    if end_program:
        STcpClient._StopConnect()
        break
    
    decision_step = Getstep(mapStat, gameStat)
    
    STcpClient.SendStep(id_package, decision_step)
