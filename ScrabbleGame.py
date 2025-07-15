import csv
import copy
import json


class ScrabbleGame:
    """ 
    Base class for Scrabble game logic. Contains methods to read game data from files along with 
    scoring algorithms and helper functions for other capabilities.
    """
    
    def __init__(self):
        
        
        self.moveScores = None
        self.completedGame = None
        self.tileValues = None
        self.tileCounts = None
        self.tileBag = None
        self.emptyBoard = None
        
        self.FAILURE_MESSAGE = "No solution found. My bad"

        
        self.currentBoard = None
        
    def setScores(self, moveScoresFile: str = "scores1.txt") -> None:
        """Reads scores for each move from a file and stores them in a list.

        Args:
            moveScoresFile (str, optional): Path to scores file. Defaults to "scores1.txt".
        """
        with open(moveScoresFile, "r", encoding='utf-8') as file:
            self.moveScores = list(map(int, file.read().split()))
            
    def setEmptyBoard(self, boardFile: str = "board.csv") -> None:
        """Reads the empty board from a CSV file and stores the board layout as a 2D list.

        Args:
            boardFile (str, optional): CSV file containing empty board layout. Defaults to "board.csv".
        """
        with open(boardFile, newline="", encoding='utf-8-sig') as csvfile:
            reader = csv.reader(csvfile)
            self.emptyBoard = [row for row in reader]
            self.currentBoard = copy.deepcopy(self.emptyBoard)
            
    def setCompletedGame(self, gameFile: str = "Game1.csv") -> None:
        """Reads the completed game from a CSV file and stores it as a 2D list.

        Args:
            gameFile (str, optional): CSV file containing board of completed game. Defaults to "Game1.csv".
        """
        with open(gameFile, newline="", encoding='utf-8-sig') as csvfile:
            reader = csv.reader(csvfile)
            self.completedGame = [row for row in reader]
            
    def setTileInfo(self, tileFile: str = 'tileInfo.json') -> None:
        """Reads tile information from a JSON file and initializes tile values, counts, and the tile bag contents.

        Args:
            tileFile (str, optional): JSON file containing values and counts of each tile. Defaults to 'tileInfo.json'.
        """
        # tileInfo is a dict mapping each tile to another dict with "value" and "count" keys
        with open(tileFile, "r", encoding='utf-8') as file:
            tileInfo: dict[str, dict[str, int]] = json.load(file)   
        
        self.tileValues = {letter: data["value"] for letter, data in tileInfo.items()}
        self.tileCounts = {letter: data["count"] for letter, data in tileInfo.items()}

        self.tileBag = [letter for letter, value in self.tileCounts.items() for _ in range(value)]
      
    
    def setBoardAndScores(self, scoresFile: str, tileFile: str, boardFile: str, gameFile: str = None) -> None:
        """Creates list of scores, empty board, completed game, tile values, tile counts, and tile bag from files.

        Args:
            scoresFile (str): TXT file containing scores for each move.
            tileFile (str): JSON file containing tile values and counts.
            boardFile (str): CSV file containing the empty board layout.
            gameFile (str, optional): CSV file containing the completed board. Defaults to None.
        """
        self.setScores(scoresFile)
        self.setEmptyBoard(boardFile)
        
        if gameFile:
            self.setCompletedGame(gameFile)
            
        self.setTileInfo(tileFile)
        
    def getTileBag(self) -> list[str]:
        """Produces the tile bag based on the tiles placed on the board and the original tile counts.

        Returns:
            list[str]: List of tiles in the tile bag.
        """
        if not self.tileBag:
            return None
        
        # create a copy of the tile bag
        tileBag = copy.deepcopy(self.tileBag)
        
        # remove tiles that are already placed on the board
        for row in self.currentBoard:  
            for tile in row:
                if self.isTile(tile) and tile in tileBag:
                    tileBag.remove(tile)
                    
        return tileBag
        
    def countPlay(self, startPair: tuple, endPair: tuple, board: list[list[str]] = None, returnTilesPlayed: bool = False, returnBoard: bool = False):
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
        
        if board is None:
            board = self.currentBoard
        else:
            board = copy.deepcopy(board)
        
        # start scores at 0, tiles at 0, and multiplier at 1
        score = 0
        nonModifiedScore = 0
        multiplier = 1
        tilesUsed = 0
        tilesUsedList = []
        
        # converts coordinates with vertical boolean (true for vertical, false for horizontal)
        vert, basis, start, end = self.coordsToVertBoolAndCoords(startPair, endPair)
        
        # loop through each tile played
        for i in range(start, end+1):
            # temp multiplier resets for each tile, so is used for letter scores or intersecting words
            tempMultiplier = 1
            # sets current tile coordinates and gets tile from board
            coords = (i, basis) if vert else (basis, i)
            tile = board[coords[0]][coords[1]]
            
            # check if tile is already placed (adds tile to score without multipliers if so)
            if self.isTile(tile):
                score += self.tileValues[tile]
                continue
            
            # tile is placed, so one more tile used, and need to check for intersections
            tilesUsed += 1
            tilesUsedList.append(coords)
            adjacency1 = ((i, basis-1) if vert else (basis-1, i)) if basis > 0 else None
            adjacency2 = ((i, basis+1) if vert else (basis+1, i)) if basis < 14 else None
            
            # check for modifiers at placed tile (should be applied to current word and intersections)
            mod = board[coords[0]][coords[1]]
            newTile = self.completedGame[coords[0]][coords[1]]
            
            if not self.isTile(newTile):
                # if it is not a tile, it is an invalid move
                return (-1, []) if returnTilesPlayed else -1
            
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
            if (adjacency1 and self.isTile(board[adjacency1[0]][adjacency1[1]])) or \
                (adjacency2 and self.isTile(board[adjacency2[0]][adjacency2[1]])):
                nonModifiedScore += tempMultiplier*(value + self.countWord(coords, not vert, board))
            score += value

            board[coords[0]][coords[1]] = self.completedGame[coords[0]][coords[1]]
        bingo = 50 if tilesUsed > 6 else 0
        moveScore = score * multiplier + nonModifiedScore + bingo
        if returnTilesPlayed:
            return moveScore, tilesUsedList
        if returnBoard:
            return moveScore, board
        return moveScore
    
    def countWord(self, startCoords: tuple, vert: str, gameBoard: list[list[str]]) -> int:
        """Counts the score of a word placed on the board, starting from the given coordinates and without
        modifiers applied.

        Args:
            startCoords (tuple): Starting coordinates of word (x, y)
            vert (str): Orientation of word being counted
            gameBoard (list[list[str]]): Board state after move is played

        Returns:
            int: Unmodified score of word
        """
        
        score = 0
        if vert:
            # loop descending and ascending from start coordinates and add values until a non-tile is reached
            for i in range(startCoords[0]-1, -1, -1):
                # one coordinate is fixed, and the other is from the loop
                if not self.isTile(gameBoard[i][startCoords[1]]):
                    break
                score += self.tileValues[gameBoard[i][startCoords[1]]]
            for j in range(startCoords[0]+1, 15):
                if not self.isTile(gameBoard[j][startCoords[1]]):
                    break
                score += self.tileValues[gameBoard[j][startCoords[1]]]
        else:
            # for non-vertical, y coordinate is fixed, so loop through x coordinates
            for i in range(startCoords[1]-1, -1, -1):
                if not self.isTile(gameBoard[startCoords[0]][i]):
                    break
                score += self.tileValues[gameBoard[startCoords[0]][i]]
            for j in range(startCoords[1]+1, 15):
                if not self.isTile(gameBoard[startCoords[0]][j]):
                    break
                score += self.tileValues[gameBoard[startCoords[0]][j]]
        return score
    
    def tileBagScore(self) -> int:
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
        
        return sum(self.tileValues.get(tile, 0) for tile in self.tileBag)
    
    def makeAntiBoard(self, board: list[list[str]]) -> list[list[str]]:
        antiBoard = []
        for i in range(len(board)):
            antiBoard.append([tile if tile == "" else " " for tile in board[i]])
        for i in range(len(self.completedGame)):
            for j in range(len(self.completedGame[0])):
                if self.isTile(self.completedGame[i][j]) and not self.isTile(board[i][j]):
                    antiBoard[i][j] = self.completedGame[i][j]
                else:
                    antiBoard[i][j] = "x"
        return antiBoard
    
    def isTileToBePlaced(self, coords: tuple, board: list[list[str]]) -> bool:
        """
        Checks if a tile at the given coordinates is to be placed (i.e., it is not already placed on the board).
        
        Args:
            coords (tuple): coordinates of the tile (x, y)
            board (list[list[str]]): current state of the board
            
        Returns:
            bool: True if the square is a tile yet to be placed, False otherwise
        """
        return self.isTile(self.makeAntiBoard(board)[coords[0]][coords[1]])
    
    
    def getTileSet(self, board: list[list[str]]) -> set[tuple]:
        """
        Returns a set of coordinates of tiles that are currently placed on the board.
        
        Args:
            board (list[list[str]]): current state of the board
            
        Returns:
            set: set of coords of tiles that are currently placed on the board
        """
        tileSet = set()
        for i in range(len(board)):
            for j in range(len(board[0])):
                if self.isTile(board[i][j]):
                    tileSet.add((i, j))
        return tileSet
        

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
    def isTile(tile: str) -> bool:
        """Checks if a square on the Scrabble board is occupied by a tile.

        Args:
            tile (str): one-character string representing a tile ('_' is a blank tile)

        Returns:
            bool: true if it is a tile
        """
        return tile.isupper() or tile == '_'


if __name__ == "__main__":
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

    game = ScrabbleGame()
    game.setBoardAndScores("scores1.txt", "tileInfo.json", "board.csv", "Game1.csv")

    for row in game.makeAntiBoard(game.currentBoard):
        print(row)

    for move in moves[:2]:
        v1 = game.countPlay(*move)
        print(v1)
    # print(-game.tileBagScore())
    # print(game.tileBagScore())
    
    # print(game.completedGame)
    # print(game.currentBoard)
    for row in game.makeAntiBoard(game.currentBoard):
        print(row)

