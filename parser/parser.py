import nltk
import sys

TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and" | "until"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""

NONTERMINALS = """
S -> NP VP
S -> NP VP Pred

NP -> N | Det N | Det AdjP NP | NP P NP

VP -> V | V NP
VP -> V P NP 
VP -> Adv VP | VP Adv 

AdjP -> Adj | Adj AdjP
Pred -> Conj NP | Conj VP | Conj S | P NP | Pred Pred
"""

grammar = nltk.CFG.fromstring(NONTERMINALS + TERMINALS)
parser = nltk.ChartParser(grammar)


def main():

    # If filename specified, read sentence from file
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            s = f.read()

    # Otherwise, get sentence as input
    else:
        s = input("Sentence: ")

    # Convert input into list of words
    s = preprocess(s)

    # Attempt to parse sentence
    try:
        trees = list(parser.parse(s))
    except ValueError as e:
        print(e)
        return
    if not trees:
        print("Could not parse sentence.")
        return

    # Print each tree with noun phrase chunks
    for tree in trees:
        tree.pretty_print()

        print("Noun Phrase Chunks")
        for np in np_chunk(tree):
            print(" ".join(np.flatten()))


def preprocess(sentence):
    """
    Convert `sentence` to a list of its words.
    Pre-process sentence by converting all characters to lowercase
    and removing any word that does not contain at least one alphabetic
    character.
    """
    #Declaring auxiliary variables and tokenizing the lowercased sentence
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    words = nltk.tokenize.word_tokenize(sentence.lower())
    aux = []
    
    #Now let's iterate over the words. If the word is valid, we append it to
    #a list that we'll return at the end. Since it iterates in order, we
    #won't have any problems with syntax.
    for word in words:
        for letter in word:
            if letter in alphabet:
                aux.append(word)
                break
    
    return(aux)
    

def np_chunk(tree):
    """
    Return a list of all noun phrase chunks in the sentence tree.
    A noun phrase chunk is defined as any subtree of the sentence
    whose label is "NP" that does not itself contain any other
    noun phrases as subtrees.
    """
    #This was a pain. I originally had Nouns and Noun Phrases as separate things
    #but after joining them to make the rules "simpler" getting the chunks became
    #a headache. I managed to do so correctly, even when it looks like a mess.
    
    
    
    #Declaring auxiliary variables
    np_chunks = []
    np_subtrees = list(tree.subtrees(filter=lambda t: t.label()=="NP"))

    #We check all subtrees with the NP label
    for subtree in np_subtrees:
        #We make a list of all of the subtrees of the one that has an NP label.
        #Trivially, it is a subtree of itself and maybe the subtree Tree(N,[word])
        #so a list of a correct Noun Phrase will have at least 3 subtrees.
        subtree_subtrees = list(subtree.subtrees())
        if len(subtree_subtrees) > 2:
            
            #If it has more than 2 subtrees it's a candidate for a Noun Phrase Chunk
            #Now let's see if there's any subtree which is also a Noun Phrase AND
            #that hasn't been coupled with a Determinant or anything else.
            #(Thus not making it really a Noun Phrase)
            subtree_np_subtrees = list(subtree.subtrees(filter=lambda t: t.label()=="NP"))
            n = len(list(subtree_np_subtrees))
            subtree_np_subtrees = subtree_np_subtrees[1:n] #Renivubg the trivial one
            add_subtree = True
            for sub_subtree in subtree_np_subtrees: #Checking all NP subtrees
                m = len(list(sub_subtree.subtrees()))
                if m > 2:
                    #If it has more than two subtrees, there's a smaller Noun Phrase
                    add_subtree = False
                    break
            
            #If there's a smaller Noun Phrase, we don't add it. If there isn't we do
            if add_subtree is True:
                np_chunks.append(subtree)    
    
    #After all subtrees with the NP label have been checked, and added if it's
    #neccesary, then we are done, so we just return the tree list.
    return np_chunks






if __name__ == "__main__":
    main()
