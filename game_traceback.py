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


class ScrabbleTraceback(ScrabbleGame):
    def __init__(self, scoresFile: str = "scores1.txt", tileFile: str = "tileInfo.json", boardFile: str = "board.csv", gameFile: str = "Game1.csv"):
        super().__init__()
        self.setBoardAndScores(scoresFile, tileFile, boardFile, gameFile)
        self.START_COORDS = (7, 7) # Assuming the center of the board is (7, 7)
        

    def traceback(self):
        # self.tracebackRecursive(self.board, self.completedGame, 0)
        pass

    
    def tracebackRecursive(self, board: list[list[str]], antiBoard: list[list[str]], moveIndex: int):
        score = self.moveScores[moveIndex]
        
        if moveIndex == 0:
            pass # do something else here
        
        
        for i in range(len(board)):
            for j in range(len(board[0])):
                if self.isTile(board[i][j]):
                    moves = self.searchMoves((i, j), board, antiBoard, score)
            
    def searchMoves(self, startingCoords: tuple[int, int], board: list[list[str]], targetScore: int, isAdjacent: bool = False, firstMove: bool = False) -> set[tuple[tuple[int, int], tuple[int, int]]]:
        xBase, yBase = startingCoords
        
        leftBound = xBase
        rightBound = xBase
        
        upperBound = yBase
        lowerBound = yBase
        
        antiBoardSet = self.getTileSet(self.makeAntiBoard(board))
        completedGameSet = self.getTileSet(self.completedGame)
        movesPlayedSet = set()
        
        # # different logic for first move
        # if firstMove:
            
        #     if (xBase, yBase) != self.START_COORDS:
        #         return set()
            
        #     for i in range(xBase - 1, -1, -1):
        #         if (i, yBase) in antiBoardSet:
        #             leftBound = i
        #         if not (i, yBase) in completedGameSet:
        #             break
            
        
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
                if (i, yBase) not in antiBoardSet or (j, yBase) not in antiBoardSet:
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
            upperBound = board[0] + 1    
        for i in range(yBase + 1, len(board[0])):
            if (xBase, i) in antiBoardSet:
                lowerBound = i
            if not (xBase, i) in completedGameSet:
                break
            
        for i in range(upperBound, lowerBound):
            for j in range(i + 1, lowerBound + 1):
                if (xBase, i) not in antiBoardSet or (xBase, j) not in antiBoardSet:
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
                downMoveSet = self.searchMoves((xBase, yBase + 1), board, targetScore, False)
                movesPlayedSet.update(downMoveSet)
        
        return movesPlayedSet
        
        
        # TODO: handle cases where tiles only placed in one direction
        # (This means that one of the x1s or x2s will be None)
        
        # bidirectional case:
        # if innerx1 is None:
        #     for i in range(innerx2, outerx2 + 1):
        #         if (i, startingCoords[1]) not in antiBoardSet:
        #             continue
        #         resultingScore, tilesUsed = self.countPlay((i, startingCoords[1]), (i, startingCoords[1]), board, True)
        #         if resultingScore == targetScore:
        #             movesPlayedSet.add(((innerx2, startingCoords[1]), (i, startingCoords[1])))
        # for i in range(outerx1, outerx2):
        #     for j in range(i + 1, outerx2 + 1):
        #         if i > innerx1 or j < innerx2:
        #             continue
        #         if (i, startingCoords[1]) not in antiBoardSet or (j, startingCoords[1]) not in antiBoardSet:
        #             continue
        #         resultingScore, tilesUsed = self.countPlay((i, startingCoords[1]), (j, startingCoords[1]), board, True)
        #         if resultingScore == targetScore:
        #             movesPlayedSet.add(((i, startingCoords[1]), (j, startingCoords[1])))
        
        # unidirectional case:
        
        
        
        # for i in range(outerx1, outerx2 + 1):
        #     for j in range(i, outerx2 + 1):
        #         if not i in antiBoardSet or not j in antiBoardSet:
        #             continue
        #         if i > innerx2 or j < innerx1:
        #             continue
        #         resultingScore, tilesUsed = self.countPlay((i, startingCoords[1]), (j, startingCoords[1]), board, True)
        #         if resultingScore == targetScore and ((i, startingCoords[1]), (j, startingCoords[1])) not in movePlayedDict:
        #             movePlayedDict[((i, startingCoords[1]), (j, startingCoords[1]))] = tilesUsed
            
        
        # antiBoardSet.clear()  
            
        # for i in range(startingCoords[1] - 1, -1, -1):
        #     if self.isTile(antiBoard[startingCoords[0]][i]):
        #         if innery1 is None:
        #             innery1 = i
        #         antiBoardSet.add(i)
        #     if not self.isTile(self.completedGame[startingCoords[0]][i]):
        #         break
            
        # outery1 = min(antiBoardSet) if antiBoardSet else None # TODO: handle case where tiles only placed in one direction
        
        # for i in range(startingCoords[1] + 1, len(board[0])):
        #     if self.isTile(antiBoard[startingCoords[0]][i]):
        #         if innery2 is None:
        #             innery2 = i
        #         antiBoardSet.add(i)
        #     if not self.isTile(self.completedGame[startingCoords[0]][i]):
        #         break
            
        # outery2 = max(antiBoardSet) if antiBoardSet else None # TODO: handle case where tiles only placed in one direction
        
        # for i in range(outery1, outery2 + 1):
        #     for j in range(i, outery2 + 1):
        #         if not i in antiBoardSet or not j in antiBoardSet:
        #             continue
        #         if i > innery2 or j < innery1:
        #             continue
        #         resultingScore, tilesUsed = self.countPlay((startingCoords[0], i), (startingCoords[0], j), board, False)
        #         if resultingScore == score and ((startingCoords[0], i), (startingCoords[0], j)) not in movePlayedDict:
        #             movePlayedDict[((startingCoords[0], i), (startingCoords[0], j))] = tilesUsed
            
        # return movePlayedDict
                    
        # Figure out how far placeable tiles extend in each direction
        # x1 = startingCoords[0]
        # for i in range(startingCoords[0] - 1, -1, -1):
        #     if self.isTile(antiBoard[i][startingCoords[1]]):
        #         x1 = i
        #     else:
        #         break
        # x2 = startingCoords[0]
        # for i in range(startingCoords[0] + 1, len(board)):
        #     if self.isTile(antiBoard[i][startingCoords[1]]):
        #         x2 = i
        #     else:
        #         break
        # y1 = startingCoords[1]
        # for i in range(startingCoords[1] - 1, -1, -1):
        #     if self.isTile(antiBoard[startingCoords[0]][i]):
        #         y1 = i
        #     else:
        #         break
        # y2 = startingCoords[1]
        # for i in range(startingCoords[1] + 1, len(board[0])):
        #     if self.isTile(antiBoard[startingCoords[0]][i]):
        #         y2 = i
        #     else:
        #         break
            
        # Now we have the bounds of the placeable tiles
        
    
            
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


print(traceback.searchMoves((7,7), traceback.currentBoard, 70))