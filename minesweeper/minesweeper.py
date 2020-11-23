import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        mines = set()
        if len( self.cells ) == self.count:
            mines = self.cells
            
        return(mines)
        
        
    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        safes = set()
        if self.count == 0:
            safes = self.cells
            
        return(safes)        
        
        
    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        #If the cell to mark is in the sentence, remove it. And since it's a mine, the count goes down by one
        if cell in self.cells:
            new_cells = set()
            for x in self.cells:
                 if x == cell:
                     continue
                 new_cells.add(x)
    
            self.cells = new_cells
            self.count = self.count - 1
    
    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        #If the cell to mark is in the sentence, remove it. And since it's a safe, the count stays the same.
        if cell in self.cells:
            new_cells = set()
            for x in self.cells:
                  if x == cell:
                      continue
                  new_cells.add(x)
            
            self.cells = new_cells


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        self.moves_made.add(cell) #Number 1
        self.mark_safe(cell)      #Number 2
        
        #In order to update knowledge, we need the surrounding cells. Let's
        #check if our selected cell is a border or a corner.
        ci = cell[0]
        cf = cell[1]
        adyacent = set()
        
        #Corner check
        if   ci == 0 and cf == 0:                           #Top-left corner
            adyacent = {(0,1), (1,0), (1,1)}
        elif ci == 0 and cf == (self.width - 1):            #Top-right corner
            adyacent = {(0,self.width - 2), (1,self.width - 2), (1,self.width - 1)}       
        elif ci == (self.height - 1) and cf == 0:           #Bottom-left corner
            adyacent = {(self.height-2,0), (self.height-2,1), (self.height-1,1)}
        elif ci == (self.height-1) and cf == (self.width-1): #Bottom-right corner
            adyacent = {(self.height-1,self.width-2), (self.height-2,self.width-2), (self.height-2,self.width-1)}
        
        #Border but not corner check (If its a corner, these statements are not evaluated)
        elif ci == 0:                                       #Top border
            for i in range(2):
                for j in range(cf-1, cf+2):
                    if (i,j) == cell:                      
                        continue
                    adyacent.add((i,j))
        elif ci == (self.height-1):                         #Bottom border
            for i in range(self.height-2, self.height):
                for j in range(cf-1,cf+2):
                    if (i,j) == cell:                       
                        continue
                    adyacent.add((i,j))
        elif cf == 0:                                       #Left border
            for i in range(ci-1, ci+2):
                for j in range(2):
                    if (i,j) == cell:                       
                        continue
                    adyacent.add((i,j))
        elif cf == (self.width-1):                         #Right border
            for i in range(ci-1, ci+2):
                for j in range(self.width-2,self.width):
                    if (i,j) == cell:                       
                        continue
                    adyacent.add((i,j))
        else:    #In any other case, the cell is not in a border or a corner,thus we have no restriction for adyacent cells.
            for i in range(ci-1,ci+2):
                for j in range(cf-1,cf+2):
                    if (i,j) == cell:
                        continue
                    adyacent.add((i,j))
        
       # After getting the adyacent tiles, we just add them to the knowledge base as a Sentence     
        self.knowledge.append( Sentence(adyacent, count) ) #Number 3
       # In order to update the new sentences with the known safes and mines, we mark them again
        for safe in self.safes:
            self.mark_safe(safe)
        for mine in self.mines:
            self.mark_mine(mine)
        
        
        #Number 4 and 5 - the while loop is to make sure all possible inferences are made
        # To avoid missing information that could be vital. The inference and marking process
        # must be done until no more info can be gathered
        while True:
            added_sentences = 0
            safes_marked = 0
            mines_marked = 0
            
            #Inferring new sentences using the existing ones. If they're the same sentence, it's skipped, otherwise we check if one
            #is subset of the other one, if it is, we inferre, otherwise, we do nothing.
            for sentence1 in self.knowledge:
                for sentence2 in self.knowledge:
                    if sentence1 == sentence2:
                        continue
                    elif sentence1.cells.issubset(sentence2.cells):
                        new_cells = sentence2.cells - sentence1.cells
                        new_count = sentence2.count - sentence1.count
                        new_sentence = Sentence( new_cells, new_count )
                        if new_sentence not in self.knowledge and new_cells != set():   
                            self.knowledge.append( new_sentence )
                            added_sentences += 1     
            
            #We check if our new sentences can help us find new safes. If we find any, we mark them.
            for sentence in self.knowledge:        
                if sentence.count == 0 and sentence.cells != set():
                    for x in sentence.cells:
                       if x not in self.safes:
                            self.mark_safe(x)  
                            safes_marked += 1

            #We check if our new sentences can help us find new mines. If we find any, we mark them.                
            for sentence in self.knowledge:                 
                if len(sentence.cells) == sentence.count and sentence.cells != set():
                    #for i in self.knowledge:
                    #    print(i)
                    for x in sentence.cells:
                        if x not in self.mines:
                            self.mark_mine(x)      
                            mines_marked += 1
            
            #Clean empty sets if there's any, so the knowledge base doesn't grow too much, since it would make the algorithm slow.
            for sentence in self.knowledge:
                if sentence == Sentence(set(),0):
                    self.knowledge.remove(sentence)

            #If no more inferences are made, as well as no new safe/mine markings, we have gathered all the information we could, so
            #we break the cicle. It can't iterate indefinitely, since the information we can gather is finite.    
            if added_sentences + safes_marked + mines_marked == 0:
                break
        

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.
        
        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        #Possible moves are all safe moves that haven't been made. Taking out self.mines is just a precaution. It shouldn't happen since
        #a cell can't be a mine and a safe at the same time. 
        possible = self.safes - self.moves_made - self.mines
        
        #If no safe move can be made, return None so runner.py calls for a random move.
        if possible == set():
            return(None)
        
        #Since sets have no order, calling the .pop() method will take a random move from the possible set.
        move = possible.pop()
        
        return(move)
    
    
    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        #We fill a set with all cells that are known NOT to be mines AND all the cells that haven't been clicked.
        possible_moves = set()
        for i in range(self.height):
            for j in range(self.width):
                if (i,j) not in self.moves_made and (i,j) not in self.mines:
                    possible_moves.add((i,j))
        
        #If all possible cells are either mines or have been clicked, we have reached our goal, thus we return None and let runner.py
        #handle the rest.
        if possible_moves == set():
            return(None)
        
        #Otherwise, we take a random cell of the possible set.
        move = possible_moves.pop()
        return(move)
