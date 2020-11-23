"""
Tic Tac Toe Player
"""
import copy
import math

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """

    #Number of moves each player has made    
    nX=nO=0

    for i in range(3):
        for j in range(3):
            if board[i][j] =="X":
                nX += 1
            elif board[i][j] =="O":
                nO += 1
    
    #X always plays first, so X is either 1 move ahead of O, or 0 moves ahead. Thus, if X is a move ahead, it's O's turn, otherwise
    #it's X's turn
    if nX==nO: 
        return("X")
    elif nX==(nO+1):
        return("O")
    else:
        raise Exception("Not a valid board")
    

def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    actions = set()
    #We start with an empty action set. We check each cell, and if it's empty, we add it to the possible actions set.
    for i in range(3):
        for j in range (3):
            if board[i][j]==None: 
                actions.add((i,j))
    
    return(actions)


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    #Checking if the action is valid
    if action not in actions(board):
        raise Exception("Invalid move...")
    #We make a copy of the board before the move and change the corresponding cell's value to the corresponding player's value
    new_board = copy.deepcopy(board)
    new_board[action[0]][action[1]] = player(board)
    return(new_board)


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    #Vertical checking
    for k in [0,1,2]:
        if board[0][k]==board[1][k]==board[2][k] and board[0][k] is not None:
            return(board[0][k])
    
    #Horizontal Checking
    for k in [0,1,2]:
        if board[k][0]==board[k][1]==board[k][2] and board[k][0] is not None:
            return(board[k][0])
   
    #Diagonal Checking
    if board[0][0]==board[1][1]==board[2][2] and board[0][0] is not None:
        return(board[0][0])
    if board[0][2]==board[1][1]==board[2][0] and board[0][2] is not None:
        return(board[0][2])
    
    return(None)


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    #If there's a winner, or there are no possible moves to take, the game is over.
    if winner(board) is not None or len(actions(board)) == 0:
        return(True)
    else:
        return(False)


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    #Pretty self-explainatory, does as indicated above
    if winner(board)=="X":
        return(1)
    elif winner(board)=="O":
        return(-1)
    else:
        return(0)

#From this point, we implement the minmax algorithm and it's two auxiliar functions
def max_value(board):
    if terminal(board):
        return(utility(board))
    v=-float("inf")
    for action in actions(board):
        v = max( v, min_value( result(board,action) ) )
    return v


def min_value(board):
    if terminal(board):
        return(utility(board))
    v=float("inf")
    for action in actions(board):
        v = min( v, max_value( result(board,action) ) )
    return v


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    #If the game is over, return None
    if terminal(board):
        return None
    #Variable declaration
    act = actions(board)
    values = []
    moves = []
    i = -1
    #If it's x's turn, try to maximize, if it's o's turn, try to minimize.
    if player(board)=="X":    
        for action in act:
            i+=1
            values.append( min_value(result(board,action)) )
            moves.append( action )
        m = max(values)
    elif player(board)=="O":
        for action in act:
            i+=1
            values.append( max_value(result(board,action)) )
            moves.append( action )
        m = min(values)      
    else:
        raise Exception("Fatal error. Self-destruction in 10 seconds...")
     
    #Check and return the optimal move for the AI
    for i in range(i+1):
        if values[i]==m:
            return moves[i]
        
    raise Exception("Unexpected end of code. Minimax")
    
    


    