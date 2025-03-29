import csv
import copy
import json

FAILURE_MESSAGE = "No solution found. My bad"

"""
tilesPlayed: 11,5 11,6 11,7; start:11,5; end:11,7"

grab modifiers and values:
- 11,5: 3, 2
- 11,6: 1, x
- 11,7: 4, x

mult = 1

go through each tile.
if tile multiplier, just multiply the tiles value and
- add the multiplied value to adjacent tiles
if total multiplier, multiply multiplier and:
- add tile value to adjacent tile values and multiply by the multiplier
if neither, add to total and:
- add tile value to adjacent tiles

"""
def coordsToVertBoolAndCoords(start, end):
    if start[0] == end[0]:
        return False, start[0], start[1], end[1]
    return True, start[1], end[0], end[1]

"""
4,10 - 6,10

True, 10, 4, 6

"""


def countPlay(startPair, endPair):
    score = 0
    multiplier = 1
    tempBoard = copy.deepcopy(board)
    vert, basis, start, end = coordsToVertBoolAndCoords(startPair, endPair)
    for i in range(start, end+1):
        tempMultiplier = 1
        coords = (i, basis) if vert else (basis, i)
        if isTile(tempBoard[coords[0]][coords[1]]):
            score += tileValues[tempBoard[coords[0]][coords[1]]]
            continue
        adjacency1 = ((i-1, basis) if vert else (basis, i-1)) if i > 0 else None
        adjacency2 = ((i+1, basis) if vert else (basis, i+1)) if i < 14 else None
        mod = tempBoard[coords[0]][coords[1]]
        value = tileValues[game[coords[0]][coords[1]]]
        if mod == 'd':
            value *= 2
        elif mod == 't':
            value *= 3
        elif mod == '2':
            tempMultiplier = 2
        elif mod == '3':
            tempMultiplier = 3
        multiplier *= tempMultiplier
        if (adjacency1 and isTile(tempBoard[adjacency1[0]][adjacency1[1]])) or \
            (adjacency2 and isTile(tempBoard[adjacency2[0]][adjacency2[1]])):
            score += tempMultiplier*(value + countWord(coords, vert))
        score += value
        tempBoard[coords[0]][coords[1]] = game[coords[0]][coords[1]]
    return score * multiplier, tempBoard
        
        
            

    
    
    
def countWord():
    score = 0
    

def isTile(tile: str) -> bool:
    return tile.isupper() or tile == '_'

with open("scores1.txt", "r", encoding='utf-8') as file:
    moveScores = list(map(int, file.read().split()))

with open("board.csv", newline="", encoding='utf-8-sig') as csvfile:
    reader = csv.reader(csvfile)
    board = [row for row in reader]
    
with open("Game1.csv", newline="", encoding='utf-8-sig') as csvfile:
    reader = csv.reader(csvfile)
    game = [row for row in reader]
    
with open("tileInfo.json", "r", encoding='utf-8') as file:
    tileInfo = json.load(file)   
    
tileValues = {letter: data["value"] for letter, data in tileInfo.items()}
tileCounts = {letter: data["count"] for letter, data in tileInfo.items()}


emptyBoard = copy.deepcopy(board)

for i, score in enumerate(moveScores):
    moveNum = i + 1
    
    if board == emptyBoard:
        mountTiles = [(7, 7)]
    
    for y, x in mountTiles:
        # try vert
        for i in range(y-1, -1, -1):
            if not isTile(game[i][y]):
                break
        
        y1 = i + 1
        for j in range(y+1, 15):
            if not isTile(game[j][y]):
                break
        y2 = j + 1
        
        

    break
           