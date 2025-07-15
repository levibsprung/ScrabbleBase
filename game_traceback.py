""" 
Traceback:

Problem inputs:
* Empty board
* Moves that were played
* Scores for each move

Subproblem inputs:
* Board state
* Current move + score
* Board modifiers


Steps:
1. Have empty board and completed game (antiboard)



"""

from ScrabbleGame import ScrabbleGame
from collections import deque


class ScrabbleTraceback(ScrabbleGame):
    def __init__(self, scoresFile: str = "scores1.txt", tileFile: str = "tileInfo.json", boardFile: str = "board.csv", gameFile: str = "Game1.csv"):
        super().__init__()
        self.setBoardAndScores(scoresFile, tileFile, boardFile, gameFile)
        self.numMoves = len(self.moveScores)
        self.START_COORDS = (7, 7) # Assuming the center of the board is (7, 7)
        

    def traceback(self):
        """ 
        Main function to start the traceback process.
        """
        moveList = self.tracebackRecursive(self.currentBoard, 0)
        if not moveList:
            print("No valid moves found.")
            return
        
        for moveDeque in moveList:
            print("Moves:", list(moveDeque))

    
    def tracebackRecursive(self, board: list[list[str]], moveIndex: int) -> list[deque[tuple[tuple[int, int], tuple[int, int]]]]:
        score: int = self.moveScores[moveIndex]
        
        if score < 0:
            return [deque()]
        
        moveSet: set[tuple[tuple[int, int], tuple[int, int]]] = set()
        moveList: list[deque[tuple[tuple[int, int], tuple[int, int]]]] = []
        
        for i in range(len(board)):
            for j in range(len(board[0])):
                if (i, j) == self.START_COORDS or self.isTile(board[i][j]):
                    moveSet.update(self.searchMoves((i, j), board, score))
        
        if not moveSet:
            return
        
        for move in moveSet:
            nextMoveList: list[deque[tuple[tuple[int, int], tuple[int, int]]]] = self.tracebackRecursive(self.countPlay(move[0], move[1], board, False, True)[1], moveIndex + 1)
            if not nextMoveList: 
                continue
            for moveDeque in nextMoveList:
                moveDeque.appendleft(move)
                moveList.append(moveDeque)
            
        return moveList
        
        
        
            
                    
            
    def searchMoves(self, startingCoords: tuple[int, int], board: list[list[str]], targetScore: int, isAdjacent: bool = False) -> set[tuple[tuple[int, int], tuple[int, int]]]:
        xBase, yBase = startingCoords
        
        leftBound = xBase
        rightBound = xBase
        
        upperBound = yBase
        lowerBound = yBase
        
        antiBoardSet = self.getTileSet(self.makeAntiBoard(board))
        completedGameSet = self.getTileSet(self.completedGame)
        movesPlayedSet = set()            
        
        if xBase == 0:
            leftBound = 0
        else:
            for i in range(xBase - 1, -1, -1):
                if (i, yBase) in antiBoardSet:
                    leftBound = i
                if not (i, yBase) in completedGameSet:
                    break
        
        if xBase == len(board) - 1:
            rightBound = len(board) - 1
        else:
            for i in range(xBase + 1, len(board)):
                if (i, yBase) in antiBoardSet:
                    rightBound = i
                if not (i, yBase) in completedGameSet:
                    break
        
        for i in range(leftBound, rightBound):
            for j in range(i + 1, rightBound + 1):
                if (i, yBase) not in antiBoardSet or (j, yBase) not in antiBoardSet and i != xBase and j != xBase:
                    continue
                if not (i <= xBase <= j):
                    continue
                resultingScore, tilesUsed = self.countPlay((i, yBase), (j, yBase), board, True)
                if resultingScore == targetScore and ((i, yBase), (j, yBase)) not in movesPlayedSet:
                    movesPlayedSet.add(((i, yBase), (j, yBase)))
        
        # vertical moves
        
        if yBase == 0:
            upperBound = 0
        else:
            for i in range(yBase - 1, -1, -1):
                if (xBase, i) in antiBoardSet:
                    upperBound = i
                if not (xBase, i) in completedGameSet:
                    break
        
        if yBase == len(board[0]) + 1:
            upperBound = len(board[0]) + 1    
        for i in range(yBase + 1, len(board[0])):
            if (xBase, i) in antiBoardSet:
                lowerBound = i
            if not (xBase, i) in completedGameSet:
                break
            
        for i in range(upperBound, lowerBound):
            for j in range(i + 1, lowerBound + 1):
                if ((xBase, i) not in antiBoardSet or (xBase, j) not in antiBoardSet) and i != yBase and j != yBase:
                    continue
                if not (i <= yBase <= j):
                    continue
                resultingScore, tilesUsed = self.countPlay((xBase, i), (xBase, j), board, True)
                if resultingScore == targetScore and ((xBase, i), (xBase, j)) not in movesPlayedSet:
                    movesPlayedSet.add(((xBase, i), (xBase, j)))
        
        if not isAdjacent:
            # check for parallel plays
            if xBase > 0 and not self.isTile(board[xBase - 1][yBase]):
                leftMoveSet = self.searchMoves((xBase - 1, yBase), board, targetScore, True)
                movesPlayedSet.update(leftMoveSet)
            if xBase < len(board) - 1 and not self.isTile(board[xBase + 1][yBase]):
                rightMoveSet = self.searchMoves((xBase + 1, yBase), board, targetScore, True)
                movesPlayedSet.update(rightMoveSet)
            if yBase > 0 and not self.isTile(board[xBase][yBase - 1]):
                upMoveSet = self.searchMoves((xBase, yBase - 1), board, targetScore, True)
                movesPlayedSet.update(upMoveSet)
            if yBase < len(board[0]) - 1 and not self.isTile(board[xBase][yBase + 1]):
                downMoveSet = self.searchMoves((xBase, yBase + 1), board, targetScore, True)
                movesPlayedSet.update(downMoveSet)
        
        return movesPlayedSet
        
    
            
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

traceback = ScrabbleTraceback()

traceback.setBoardAndScores("scores1.txt", "tileInfo.json", "board.csv", "Game1.csv")

# for move in moves[:3]:
#     v1 = traceback.countPlay(*move)
#     print(v1)



# for row in traceback.currentBoard:
#     print(row)

traceback.traceback()

# print(traceback.moveScores)

# score, board = traceback.countPlay((7, 2), (7, 8), returnTilesPlayed=False, returnBoard=True)
# print(score)
# for row in board:
#     print(row)

# print(traceback.searchMoves((7,7), traceback.currentBoard, 70))