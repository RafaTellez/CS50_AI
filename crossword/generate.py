import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        # First we iterate over the dict keys (Variables). We save the required
        # length and we create an auxiliary set which will be our new domain.
        for var in self.domains.keys():
            #Declaring auxiliary variables
            n = var.length
            new_domain = set()
            for word in self.domains[var]:
                if len(word) == n:
                    new_domain.add(word)
            self.domains[var] = new_domain

        
    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        #Declaring auxiliary variables to keep the code as clean as possible
        aux_domain = set(self.domains[x])
        [c1,c2] = self.crossword.overlaps[x,y]
        
        revised = False
        for x_word in self.domains[x]:
            #The following chunk of code is the condition for the if.
            keep_x_word = False
            for y_word in self.domains[y]:
                if x_word[c1]==y_word[c2]:
                    keep_x_word = True
                    break
            
            #After the condition has been simplified, we continue with our code
            if not keep_x_word:
                aux_domain.remove(x_word)
                revised = True
        
        #Finally, we change the domain of X and return
        self.domains[x] = aux_domain
        return revised
            

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        #First, if arcs is none, let's make a list with all the arcs in the csp
        if arcs is None:
            arcs = []
            for v1,v2 in self.crossword.overlaps:
                if self.crossword.overlaps[v1,v2] is not None:
                    arcs.append((v1,v2))

        #Now we begin our code as the pseudocode we saw in the lesson
        queue = arcs
        while len(queue) != 0:
            (x,y) = queue.pop(0) #Dequeue(queue)
            if self.revise(x,y):
                if len(self.domains[x]) == 0:
                    return False
                for neighbor in (self.crossword.neighbors(x) - {y}):
                    queue.append((neighbor,x)) #Enqueue(Z,X)
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        #We check every variable in the crossword. If one is not in the assignment
        #it's incomplete. If all variables are in the assignment, it's complete.
        for variable in self.crossword.variables:
            if variable not in assignment:
                return False
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        #First, we check for duplicate values.
        if len(assignment.values()) != len(set(assignment.values())):
            return False
        
        #Second, we check for length consistency
        for x in assignment:
            if x.length != len(assignment[x]):
                return False
        
        #Last, we check for neighboring consistency
        for x in assignment:
            for y in self.crossword.neighbors(x):
                #If the neighbor is not in the assignment, it isn't inconsistent.
                if y not in assignment:
                    continue
                #If the neighbor is in the assignment, we check for consistency.
                [c1,c2] = self.crossword.overlaps[x,y]
                if assignment[x][c1] != assignment[y][c2]:
                    return False
        
        #If after all three checks the function has not ended returning false
        #then our assignment is consistent, thus we return True
        return True
            
                
    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        #First we declare our auxiliary variables
        words = list(self.domains[var])
        constrains = [None]*len(words)
        
        #Now we count up how many words each possible choice constrains and
        #save that count in the constrains list
        for i in range(len(words)):
            #Auxiliary variables
            x_word = words[i]
            count = 0
            #Counting up how many words we rule out for all neighbors.
            for neighbor in self.crossword.neighbors(var):
                #Check if neighbor is assigned. If it is, skip the iteration
                if neighbor in assignment:
                    continue
                #If neighbor is unassigned, count the constrained values.
                [c1,c2] = self.crossword.overlaps[var,neighbor]
                for y_word in self.domains[neighbor]:
                    if x_word[c1] != y_word[c2]:
                        count += 1
            #Assign the count to the corresponding place in the constrains list
            constrains[i] = count
        
        #All that reamains is to sort the constrains and sort the words list
        #according to the constrains sort, and return it
        sorted_zipped = sorted(zip(constrains, words))
        words = [element for _, element in sorted_zipped]
        return words

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        #Auxiliary variables
        unassigned = list(self.crossword.variables - set(assignment))
        index = list(range(len(unassigned)))
        domain_n_values = []
        node_degrees = []
        prospects = []
        
        #Filling the domain_values vector with the number of words in each domain
        for i in range(len(unassigned)):
            domain_n_values.append( len(self.domains[unassigned[i]]) )
            
        
        #If there's a single variable with minimal domain, return said variable
        m = min(domain_n_values)
        n_mins = domain_n_values.count(m)
        if  n_mins == 1:
            var = unassigned[domain_n_values.index(m)]
            return var
        
        #If there are several variables with minimal domain, we need to untie
        #with the grade of each of those nodes. let's calculate it.
        sorted_zipped = sorted(zip(domain_n_values, index))
        index = [element for _, element in sorted_zipped]
        for i in range(n_mins):
            prospects.append(unassigned[index[i]])
            node_degrees.append( len(self.crossword.neighbors(prospects[i])) )
        
        #Lastly, we calculate which is the highest degree, and return any
        #variable with said degree since they all are valid returns
        M = max(node_degrees)
        var = prospects[node_degrees.index(M)]
        return var
        
    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        #NOTE: DO NOT ADD OR INITIALIZE A DICT WITH VARIABLES UNLESS THEY HAVE A WORD
        if self.assignment_complete(assignment):
            return assignment
        var = self.select_unassigned_variable(assignment)
        for value in self.order_domain_values(var, assignment):
            #Here to check the conditional, we need a copy of assignment with 
            #the assigned value. Also, an empty inferences dict in case the
            #assignment isn't consistent so we don't reference inferences that
            #were never made.
            aux_assignment = assignment.copy()
            aux_assignment.update( {var:value} )
            inferences = dict()
            if self.consistent(aux_assignment):
                assignment.update( {var:value} )
                inferences = self.inference(assignment,var)
                #Here we must make another copy to check the inferences
                aux_assignment = assignment.copy()         #
                aux_assignment.update( inferences )        #
                if self.backtrack(assignment) is not None: #
                    assignment.update( inferences )        #
                result = self.backtrack(assignment)
                if result is not None:
                    return result
            aux_assignment = inferences
            aux_assignment.update( {var:value} )
            for item in aux_assignment:
                if item in assignment:
                    assignment.pop(item)
        return None
                    
                
    
    def inference(self, assignment, var):
        #Declaring auxiliary variables
        arcs = []
        inferences = dict()
        
        #First we make the list of all the arcs (Y,X) where Y is X's neighboor
        #and X is the var in our backtrack function.
        for neighbor in self.crossword.neighbors(var):
            arcs.append( (neighbor,var) )
        
        #Then we enforce arc-consistency with X.
        self.ac3(arcs)
        
        #Now we check every unassigned variable to see if we reduced the 
        #domain to only one word. If we did, we add it to our inferences.
        for Z in (self.crossword.variables - set(assignment)):
            if len(self.domains[Z]) == 1:
                word = list(self.domains[Z])[0]
                inferences.update( {Z:word} )
        
        #After we did all our inferences, we return them to the backtrack function
        return inferences




def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
