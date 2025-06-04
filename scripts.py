import csv
import copy
import json

FAILURE_MESSAGE = "No solution found. My bad"

class ScrabbleGame:
    
    def __init__(self):
        self.moveScores = None
        self.game = None
        self.tileValues = None
        self.tileCounts = None
        self.tileBag = None
        self.board = None
        
        self.currentBoard = None
        
    def getScores(self, moveScoresFile: str = "scores.txt"):
        with open(moveScoresFile, "r", encoding='utf-8') as file:
            self.moveScores = list(map(int, file.read().split()))
            
    def getEmptyBoard(self, boardFile: str = "board.csv"):
        with open(boardFile, newline="", encoding='utf-8-sig') as csvfile:
            reader = csv.reader(csvfile)
            self.board = [row for row in reader]
            self.currentBoard = copy.deepcopy(self.board)
            
    def getCompletedGame(self, gameFile: str = "Game1.csv"):
        with open(gameFile, newline="", encoding='utf-8-sig') as csvfile:
            reader = csv.reader(csvfile)
            self.game = [row for row in reader]
            
    def getTileInfo(self, tileFile: str = 'tileInfo.json'):
        with open(tileFile, "r", encoding='utf-8') as file:
            tileInfo = json.load(file)   
        
        self.tileValues = {letter: data["value"] for letter, data in tileInfo.items()}
        self.tileCounts = {letter: data["count"] for letter, data in tileInfo.items()}

        self.tileBag = [letter for letter, value in self.tileCounts.items() for _ in range(value)]
      
    
    def setBoardAndScores(self, scoresFile: str, tileFile: str, boardFile: str, gameFile: str = None):
        self.getScores(scoresFile)
        self.getEmptyBoard(boardFile)
        
        if gameFile:
            self.getCompletedGame(gameFile)
            
        self.getTileInfo(tileFile)
        
    def countPlay(self, startPair: tuple, endPair: tuple) -> int:
        """
        Counts the score of a play given the start and end coordinates of the move,
        the current board state, and the tile values.
        
        Args:
            startPair (tuple): starting coordinates (x, y)
            endPair (tuple): ending coordinates (x, y)
            currentBoard (list): current state of the board
            tileValues (dict): dictionary mapping tile characters to their values
            
        Returns:
            tuple: total score for the play and the updated board state TODO fix
        """
        
        # start scores at 0, tiles at 0, and multiplier at 1
        score = 0
        nonModifiedScore = 0
        multiplier = 1
        tilesUsed = 0
        
        # converts coordinates with vertical boolean (true for vertical, false for horizontal)
        vert, basis, start, end = self.coordsToVertBoolAndCoords(startPair, endPair)
        
        # loop through each tile played
        for i in range(start, end+1):
            # temp multiplier resets for each tile, so is used for letter scores or intersecting words
            tempMultiplier = 1
            # sets current tile coordinates and gets tile from board
            coords = (i, basis) if vert else (basis, i)
            tile = self.currentBoard[coords[0]][coords[1]]
            
            # check if tile is already placed (adds tile to score without multipliers if so)
            if isTile(tile):
                score += self.tileValues[tile]
                continue
            
            # tile is placed, so one more tile used, and need to check for intersections
            tilesUsed += 1
            adjacency1 = ((i, basis-1) if vert else (basis-1, i)) if basis > 0 else None
            adjacency2 = ((i, basis+1) if vert else (basis+1, i)) if basis < 14 else None
            
            # check for modifiers at placed tile (should be applied to current word and intersections)
            mod = self.currentBoard[coords[0]][coords[1]]
            newTile = self.game[coords[0]][coords[1]]
            self.tileBag.remove(newTile)
            value = self.tileValues[newTile]
            if 'd' in mod:
                value *= 2
            elif 't' in mod:
                value *= 3
            elif 's' in mod or '2' in mod:
                tempMultiplier = 2
            elif '3' in mod:
                tempMultiplier = 3
            multiplier *= tempMultiplier
            if (adjacency1 and isTile(self.currentBoard[adjacency1[0]][adjacency1[1]])) or \
                (adjacency2 and isTile(self.currentBoard[adjacency2[0]][adjacency2[1]])):
                nonModifiedScore += tempMultiplier*(value + self.countWord(coords, not vert, self.currentBoard))
                # print("intersection", tempMultiplier*(value + countWord(coords, not vert, currentBoard)))
            score += value
            # print("placed tile", value)
            self.currentBoard[coords[0]][coords[1]] = self.game[coords[0]][coords[1]]
        bingo = 50 if tilesUsed > 6 else 0
        return score * multiplier + nonModifiedScore + bingo
    
    def countWord(self, startCoords: tuple, vert: str, gameBoard: list[list[str]]) -> int:
        score = 0
        if vert:
            for i in range(startCoords[0]-1, -1, -1):
                if not isTile(gameBoard[i][startCoords[1]]):
                    break
                score += self.tileValues[gameBoard[i][startCoords[1]]]
            for j in range(startCoords[0]+1, 15):
                if not isTile(gameBoard[j][startCoords[1]]):
                    break
                score += self.tileValues[gameBoard[j][startCoords[1]]]
        else:
            for i in range(startCoords[1]-1, -1, -1):
                if not isTile(gameBoard[startCoords[0]][i]):
                    break
                score += self.tileValues[gameBoard[startCoords[0]][i]]
            for j in range(startCoords[1]+1, 15):
                if not isTile(gameBoard[startCoords[0]][j]):
                    break
                score += self.tileValues[gameBoard[startCoords[0]][j]]
        return score
    

    # emptyBoard = copy.deepcopy(board)    

    # for i, score in enumerate(moveScores):
    #     moveNum = i + 1
        
    #     if board == emptyBoard:
    #         mountTiles = [(7, 7)]
        
    #     for y, x in mountTiles:
    #         # try vert
    #         for i in range(y-1, -1, -1):
    #             if not isTile(game[i][y]):
    #                 break
            
    #         y1 = i + 1
    #         for j in range(y+1, 15):
    #             if not isTile(game[j][y]):
    #                 break
    #         y2 = j - 1
            
    #     break          
    

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

    # HELPER FUNCTIONS
    @staticmethod
    def coordsToVertBoolAndCoords(start: tuple, end: tuple) -> tuple:
        """
        Determines whether the move is vertical or horizontal and returns a boolean
        with that info, along with a basis coordinate, and the start and end coordinates
        respective to the dimension that the move is in (i.e. the dimension that differs between
        the start and end coordinates).
        
        Args:
            start (tuple(int, int)): start coordinates (x, y)
            end (tuple(int, int)): end coordinates (x, y)

        Returns:
            tuple(bool, int, int, int): 
            - first value is True if the move is placed vertically,
            - second value is the basis coordinate (y if vertical, x if horizontal),
            - third value is the start coordinate (x if vertical, y if horizontal),
            - fourth value is the end coordinate (x if vertical, y if horizontal).
        """
        if start[0] == end[0]:
            return False, start[0], start[1], end[1]
        return True, start[1], start[0], end[0]

    @staticmethod
    def tileBagScore(tileValues: dict[str, int], tileBag: list[str]) -> int:
        """
        Calculates the total score of tiles that haven't been played yet. 
        Assuming a two-player game, this value times two is added to the difference between scores
        upon a player using all their tiles, thus ending the game.
        
        Args:
            tileValues (dict[str, int]): dictionary mapping tile characters to their values
            tileBag (list[str]): list of tiles in the bag (with duplicates to represent quantities)
            
        Returns:
            int: total score of the tiles in the bag based on their values
        """
        
        return sum(tileValues.get(tile, 0) for tile in tileBag)
    
    @staticmethod
    def isTile(tile: str) -> bool:
        return tile.isupper() or tile == '_'


def countPlay(startPair: tuple, endPair: tuple, currentBoard: list[list[str]], tileValues: dict[str, int]):
    
    # start scores at 0, tiles at 0, and multiplier at 1
    score = 0
    nonModifiedScore = 0
    multiplier = 1
    tilesUsed = 0
    
    # converts coordinates with vertical boolean (true for vertical, false for horizontal)
    vert, basis, start, end = coordsToVertBoolAndCoords(startPair, endPair)
    
    # loop through each tile played
    for i in range(start, end+1):
        # temp multiplier resets for each tile, so is used for letter scores or intersecting words
        tempMultiplier = 1
        # sets current tile coordinates and gets tile from board
        coords = (i, basis) if vert else (basis, i)
        tile = currentBoard[coords[0]][coords[1]]
        
        # check if tile is already placed (adds tile to score without multipliers if so)
        if isTile(tile):
            score += tileValues[tile]
            # print("already placed tile", tileValues[currentBoard[coords[0]][coords[1]]])
            continue
        
        # tile is placed, so one more tile used, and need to check for intersections
        tilesUsed += 1
        adjacency1 = ((i, basis-1) if vert else (basis-1, i)) if basis > 0 else None
        adjacency2 = ((i, basis+1) if vert else (basis+1, i)) if basis < 14 else None
        
        # check for modifiers at placed tile (should be applied to current word and intersections)
        mod = currentBoard[coords[0]][coords[1]]
        newTile = game[coords[0]][coords[1]]
        tileBag.remove(newTile)
        value = tileValues[newTile]
        if 'd' in mod:
            value *= 2
        elif 't' in mod:
            value *= 3
        elif 's' in mod or '2' in mod:
            tempMultiplier = 2
        elif '3' in mod:
            tempMultiplier = 3
        multiplier *= tempMultiplier
        if (adjacency1 and isTile(currentBoard[adjacency1[0]][adjacency1[1]])) or \
            (adjacency2 and isTile(currentBoard[adjacency2[0]][adjacency2[1]])):
            nonModifiedScore += tempMultiplier*(value + countWord(coords, not vert, currentBoard))
            # print("intersection", tempMultiplier*(value + countWord(coords, not vert, currentBoard)))
        score += value
        # print("placed tile", value)
        currentBoard[coords[0]][coords[1]] = game[coords[0]][coords[1]]
    bingo = 50 if tilesUsed > 6 else 0
    return score * multiplier + nonModifiedScore + bingo, currentBoard
        
        
            
"""
startCoords: 5, 10

"""
    
    
    
def countWord(startCoords, vert, gameBoard):
    score = 0
    if vert:
        for i in range(startCoords[0]-1, -1, -1):
            if not isTile(gameBoard[i][startCoords[1]]):
                break
            score += tileValues[gameBoard[i][startCoords[1]]]
        for j in range(startCoords[0]+1, 15):
            if not isTile(gameBoard[j][startCoords[1]]):
                break
            score += tileValues[gameBoard[j][startCoords[1]]]
    else:
        for i in range(startCoords[1]-1, -1, -1):
            if not isTile(gameBoard[startCoords[0]][i]):
                break
            score += tileValues[gameBoard[startCoords[0]][i]]
        for j in range(startCoords[1]+1, 15):
            if not isTile(gameBoard[startCoords[0]][j]):
                break
            score += tileValues[gameBoard[startCoords[0]][j]]
    # print(startCoords, vert, score)
    return score

def isTile(tile: str) -> bool:
    return tile.isupper() or tile == '_'

def getBoardAndScores(moveScoresFile: str = "scores.txt", tileFile: str = 'tileInfo.json', boardFile: str = "board.csv", gameFile: str = None):
    
    with open(moveScoresFile, "r", encoding='utf-8') as file:
        moveScores = list(map(int, file.read().split()))

    with open(boardFile, newline="", encoding='utf-8-sig') as csvfile:
        reader = csv.reader(csvfile)
        board = [row for row in reader]
    
    if gameFile:
        with open("Game1.csv", newline="", encoding='utf-8-sig') as csvfile:
            reader = csv.reader(csvfile)
            game = [row for row in reader]
    else:
        game = None
    
    with open("tileInfo.json", "r", encoding='utf-8') as file:
        tileInfo = json.load(file)   
    
    tileValues = {letter: data["value"] for letter, data in tileInfo.items()}
    tileCounts = {letter: data["count"] for letter, data in tileInfo.items()}

    tileBag = [letter for letter, value in tileCounts.items() for _ in range(value)]

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
            y2 = j - 1
             
        break

moves = [
    ((7,2),(7,8)),
    ((5,9),(8,9)),
    ((4,10),(6,10)),
    ((8,6),(8,7)),
    ((2,11),(5,11)),
    ((9,4),(9,7)),
    ((6,2),(8,2)),
    ((6,2),(6,4)),
    ((5,3),(5,5)),
    ((4,4),(4,7)),
    ((2,8),(4,8)),
    ((3,6),(3,9)),
    ((0,9),(3,9)),
    ((10,0),(10,4)),
    ((7,0),(14,0)),
    ((12,1),(13,1)),
    ((8,10),(11,10)),
    ((12,8),(12,11)),
    ((10,12),(13,12)),
    ((9,13),(10,13)),   
    ((10,14),(14,14)),
    ((13,3),(13,9)),
    ((14,6),(14,8)),
    ((2,11),(2,13)),
    ((9,9),(9,11)),
    ((11,3),(11,5)),
    ((0,9),(0,11)),    
]

for move in moves:
    v1, board = countPlay(*move, board)
    print(v1)
print(-tileBagScore())
print(tileBagScore())
# for row in board:
#     print(*row)

