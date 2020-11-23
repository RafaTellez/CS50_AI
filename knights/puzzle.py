from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

# Puzzle 0
# A says "I am both a knight and a knave."
knowledge0 = And(
    #Game Definitions
    Or(AKnight,AKnave),
    Not( And(AKnight, AKnave) ),
    #Either they're telling the truth, or they're a Knave
    Or( And(AKnight,AKnave), AKnave )
)

# Puzzle 1
# A says "We are both knaves."
# B says nothing.
knowledge1 = And(
    #Game Definitions
    Or(AKnight,AKnave),
    Not( And(AKnight, AKnave) ),
    Or(BKnight,BKnave),
    Not( And(BKnight, BKnave) ),
    #Either they're telling the truth, or they're a Knave
    Or( And(AKnave,BKnave), AKnave ),
    Not( And(And(AKnave,BKnave), AKnave) )
)

# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."
knowledge2 = And(
    #Game Definitions
    Or(AKnight,AKnave),
    Not( And(AKnight, AKnave) ),
    Or(BKnight,BKnave),
    Not( And(BKnight, BKnave) ),
    #Either they're telling the truth, or they're a Knave
    Or( Or( And(AKnight,BKnight) , And(AKnave,BKnave ) ) , AKnave ),    
    Or( Or( And(AKnight,BKnave ) , And(AKnave,BKnight) ) , BKnave ),
    #Either A is telling the truth, making them both Knights, or he's lying, which means theyre
    #NOT of the same kind
    Or( And(AKnight,BKnight), Not( Or(And(AKnight,BKnight) , And(AKnave,BKnave)) ) )
)

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
# B says "A said 'I am a knave'."
# B says "C is a knave."
# C says "A is a knight."
knowledge3 = And(
    #Game Definitions
    Or(AKnight,AKnave),
    Not( And(AKnight, AKnave) ),
    Or(BKnight,BKnave),
    Not( And(BKnight, BKnave) ),
    Or(CKnight,CKnave),
    Not( And(CKnight, CKnave) ),
    #Either they're telling the truth, or they're a Knave
    Or( Or(AKnight,AKnave) , AKnave ), #A's clause
    #Game definitions make it impossible for both to be true both at the same time.
    if Or(AKnight,AKnave) == AKnave:  #If A's clause is equivalent to what B states that A said, B is a knight, otherwise he isn't
        BKnight
    else:
        BKnave
    Or( CKnave, BKnave ), #B's second clause
    Not( And(CKnave, BKnave) ), #Can't happen both at once
    Or( AKnight , CKnave ), #C's clause
    Not( And(AKnight, CKnave) ) #Can't happen both at once
)


def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()
