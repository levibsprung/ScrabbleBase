from ScrabbleGame import ScrabbleGame
from collections import deque


class ScrabbleTraceback(ScrabbleGame):
    """
    Class to handle move traceback for Scrabble games based on completed board and move scores. Extends
    ScrabbleGame to utilize its methods for reading game data and scoring.
    """
    
    def __init__(self, scoresFile: str = "scores1.txt", tileFile: str = "tileInfo.json", boardFile: str = "board.csv", gameFile: str = "Game1.csv"):
        super().__init__()
        self.setBoardAndScores(scoresFile, tileFile, boardFile, gameFile)
        self.numMoves = len(self.moveScores)
        self.START_COORDS = (7, 7) # Assuming the center of the board is (7, 7)
        

    def traceback(self) -> list[deque[tuple[tuple[int, int], tuple[int, int]]]] | None:
        """
        Main function to start the traceback process.
        Finds all possible combinations of moves that lead to the completed game state as specified
        in the board csv and scores txt files. 

        Returns:
            list[deque[tuple[tuple[int, int], tuple[int, int]]]] | None: List of deques, each containing a sequence of tuples representing
            moves made in the game using two pairs of ints to represent the start and end coordinates of each move. Returns None
            if no valid sequence of moves is found.
        """
        moveList = self.tracebackRecursive(self.currentBoard, 0)
        if not moveList:
            print(self.FAILURE_MESSAGE)
            return
        
        for moveDeque in moveList:
            print("Moves:", list(moveDeque))
        
        return moveList

    
    def tracebackRecursive(self, board: list[list[str]], moveIndex: int) -> list[deque[tuple[tuple[int, int], tuple[int, int]]]] | None:
        """
        Given the game board and an index (move number), attempts to find all possible sequences of moves recursively that match the target scores
        from the moveScores attribute, with the move number used to get the target score. 

        Args:
            board (list[list[str]]): 2d list representing the current state of the board.
            moveIndex (int): Index of the moveScores attribute list to get the target score for the current move.

        Returns:
            list[deque[tuple[tuple[int, int], tuple[int, int]]]] | None: List of deques, each containing a sequence of tuples representing
            moves made in the game using two pairs of ints to represent the start and end coordinates of each move. Returns None
            if no move is found that matches the target score.
        """
        # Get the target score
        score: int = self.moveScores[moveIndex]
        
        # Base case:
        # Penultimate move entry should be negative, and should be right after the last move 
        # (this is the deduction for having tiles remaining after the game ends)
        if score < 0:
            # TODO: check tile bag to see if deduction matches remaining tiles
            return [deque()]
        
        # Set used to hold all possible moves for the current board and index
        moveSet: set[tuple[tuple[int, int], tuple[int, int]]] = set()
        
        # List is used for all sequences of moves from the next recursive call
        moveSeqList: list[deque[tuple[tuple[int, int], tuple[int, int]]]] = []
        
        # Check for all squares that are either the starting coordinates or tiles on the board
        # (this is where moves can be build from)
        for i in range(len(board)):
            for j in range(len(board[0])):
                if (i, j) == self.START_COORDS or self.isTile(board[i][j]):
                    # search for all valid moves and add them to the moveSet
                    moveSet.update(self.searchMoves((i, j), board, score))
        
        # Return None if no moves are found (end of recursive branch)
        if not moveSet:
            return
        
        for move in moveSet:
            # Recursive call:
            # Get the next board by using countPlay and call the function for the next move index
            nextMoveList: list[deque[tuple[tuple[int, int], tuple[int, int]]]] = self.tracebackRecursive(self.countPlay(move[0], move[1], board, False, True)[1], moveIndex + 1)
            # No possible moves found after the current move
            # (end of recursive branch)
            if not nextMoveList: 
                continue
            # Prepend the current move to each deque in nextMoveList and add the deque to the moveSeqList
            for moveDeque in nextMoveList:
                moveDeque.appendleft(move)
                moveSeqList.append(moveDeque)
            
        return moveSeqList
        
        
        
            
                    
            
    def searchMoves(self, startingCoords: tuple[int, int], board: list[list[str]], targetScore: int, isAdjacent: bool = False) -> set[tuple[tuple[int, int], tuple[int, int]]]:
        """
        Searches for all possible moves that can be made from the given starting coordinates on the current board
        that result in the target score. Also searches for parallel plays if isAdjacent is False.

        Args:
            startingCoords (tuple[int, int]): Coordinates to start searching for moves from (any move found will use this tile).
            board (list[list[str]]): 2d list representing current board state.
            targetScore (int): Score to match for moves found.
            isAdjacent (bool, optional): Whether the current call is adjacent to the original starting coords. Defaults to False.

        Returns:
            set[tuple[tuple[int, int], tuple[int, int]]]: Set of moves, each represented as a tuple of two pairs of ints, 
            where each pair represents the start and end coordinates of the move.
        """
        # individual vars for starting coords for convenience and readability
        xBase, yBase = startingCoords
        
        # bounds default to starting coords
        leftBound = xBase
        rightBound = xBase
        
        upperBound = yBase
        lowerBound = yBase
        
        # Get the location set of tiles yet to be played and the location set of tiles played in completed game
        antiBoardSet = self.getTileSet(self.makeAntiBoard(board))
        completedGameSet = self.getTileSet(self.completedGame)
        
        # Set to hold moves found
        movesPlayedSet = set()            
        
        # Check for left edge of board
        if xBase == 0:
            leftBound = 0
        else:
            # Loop to the left to find the left bound for the move
            for i in range(xBase - 1, -1, -1):
                if (i, yBase) in antiBoardSet:
                    leftBound = i
                if not (i, yBase) in completedGameSet:
                    break
        
        # Check for right edge of board
        if xBase == len(board) - 1:
            rightBound = len(board) - 1
        else:
            # Loop to the right to find the right bound for the move
            for i in range(xBase + 1, len(board)):
                if (i, yBase) in antiBoardSet:
                    rightBound = i
                if not (i, yBase) in completedGameSet:
                    break
        
        # Use bounds to find all horizontal moves
        for i in range(leftBound, rightBound):
            for j in range(i + 1, rightBound + 1):
                # Both tiles must either be in antiBoardSet or be already on the board
                if (i, yBase) not in antiBoardSet or (j, yBase) not in antiBoardSet and i != xBase and j != xBase:
                    continue
                # Base must be within the start and end of the move
                if not (i <= xBase <= j):
                    continue
                # Calculate score and compare to target score
                # If the score matches, add the move to the set of moves played
                resultingScore = self.countPlay((i, yBase), (j, yBase), board)
                if resultingScore == targetScore and ((i, yBase), (j, yBase)) not in movesPlayedSet:
                    movesPlayedSet.add(((i, yBase), (j, yBase)))
        
        # vertical moves
        
        # Check for upper edge of board
        if yBase == 0:
            upperBound = 0
        else:
            # Loop to the top to find the upper bound for the move
            for i in range(yBase - 1, -1, -1):
                if (xBase, i) in antiBoardSet:
                    upperBound = i
                if not (xBase, i) in completedGameSet:
                    break
        
        # Check for lower edge of board
        if yBase == len(board[0]) + 1:
            upperBound = len(board[0]) + 1    
        else:
            # Loop to the bottom to find the lower bound for the move
            for i in range(yBase + 1, len(board[0])):
                if (xBase, i) in antiBoardSet:
                    lowerBound = i
                if not (xBase, i) in completedGameSet:
                    break
            
        for i in range(upperBound, lowerBound):
            for j in range(i + 1, lowerBound + 1):
                # Same logic as horizontal moves
                if ((xBase, i) not in antiBoardSet or (xBase, j) not in antiBoardSet) and i != yBase and j != yBase:
                    continue
                if not (i <= yBase <= j):
                    continue
                resultingScore = self.countPlay((xBase, i), (xBase, j), board)
                if resultingScore == targetScore and ((xBase, i), (xBase, j)) not in movesPlayedSet:
                    movesPlayedSet.add(((xBase, i), (xBase, j)))
        
        # check for parallel plays for one square adjacent to the original starting coords
        if not isAdjacent:
            # Check for adjacent squares in every direction
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