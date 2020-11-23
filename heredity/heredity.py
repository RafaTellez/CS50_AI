import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])
    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    names = set(people)
    joint = 1 #Identity of multiplication, since we'll be multiplying, not adding
    
    for name in names:
        # If the person has no parents, we use the probs in PROBS for the gene
        if (people[name]["mother"] == None) and (people[name]["father"] == None):
            # Considering the gene and trait factors
            if name in two_genes:
                joint *= PROBS["gene"][2]
                if name in have_trait:
                    joint *= PROBS["trait"][2][True]
                else:
                    joint *= PROBS["trait"][2][False]
            elif name in one_gene:
                joint *= PROBS["gene"][1]
                if name in have_trait:
                    joint *= PROBS["trait"][1][True]
                else:
                    joint *= PROBS["trait"][1][False]
            else:
                joint *= PROBS["gene"][0]
                if name in have_trait:
                    joint *= PROBS["trait"][0][True]
                else:
                    joint *= PROBS["trait"][0][False]
        # If the person has parents, we calculate for each possible case
        elif (people[name]["mother"] != None) and (people[name]["father"] != None):
            # Declaring auxiliary variables
            mother = people[name]["mother"]
            father = people[name]["father"]
            p_parents = dict()
            p_parents[mother] = None
            p_parents[father] = None
            # Now let's calculate the prob of inheriting genes
            if name in two_genes: # It needs to inherit one from each parent
                # First, let's account for the trait factor
                joint *= PROBS["trait"][2][name in have_trait]
                # Now let's account for the probs of the child's genes
                for parent in p_parents.keys():    
                    # Let's check the chances of inheriting one from the father
                    if parent in two_genes: 
                        # Passing a bad copy that doesn't mutate
                        p_parents[parent] = 1-PROBS["mutation"]
                    elif parent in one_gene: 
                        # Passing a bad copy that doesn't mutate
                        # OR passing a good copy that mutates
                        p_parents[parent] = (0.5*(1-PROBS["mutation"]) + 0.5*PROBS["mutation"])
                    else: # Father has no bad copies of the gene
                        # Passing a good copy that mutates
                        p_parents[parent] = PROBS["mutation"]
                    # This prob is equal to the product of probs for each parent
                    joint *= p_parents[parent]               
            
            elif name in one_gene: #Gene must come from one parent
                #First, let's account for the trait factor
                joint *= PROBS["trait"][1][name in have_trait]
                # Now let's account for the probs of the child's genes
                if father in two_genes:
                    if mother in two_genes:
                        #Inheriting a bad copy that mutates and one that doesn't (This can be done from two different ways, from father and from mother)
                        joint *= (1-PROBS["mutation"])*PROBS["mutation"]*2
                    elif mother in one_gene: 
                        joint *= ((1-PROBS["mutation"])*(0.5*(1-PROBS["mutation"]))) + ((1-PROBS["mutation"])*(0.5*PROBS["mutation"])) + ((PROBS["mutation"])*(0.5*(1-PROBS["mutation"]))) + ((PROBS["mutation"])*(0.5*PROBS["mutation"]))
                        # THE ABOVE PROBS REPRESENT THE FOLLOWING CASES RESPECTIVELY
                        # Bad copy from father that mutates and good copy from mother that mutates
                        # Bad copy from father that doesn't mutate and good copy of mother that doesn't mutate
                        # Bad copy from father that doesn't mutate and bad copy from mother that mutates
                        # Bad copy from father that mutates and bad copy from mother that doesn't                                 
                    else:
                        joint *= ((1-PROBS["mutation"])*(1-PROBS["mutation"])) + ((PROBS["mutation"])*(PROBS["mutation"]))
                        # THE ABOVE PROBS REPRESENT THE FOLLOWING CASES RESPECTIVELY
                        # Bad copy from the father that doesn't mutate and the mother's copy doesn't mutate
                        # Bad copy from father that mutates and good copy from mother that mutates
                
                elif father in one_gene:
                    if mother in two_genes:
                        joint *= ((1-PROBS["mutation"])*(0.5*(1-PROBS["mutation"]))) + ((1-PROBS["mutation"])*(0.5*PROBS["mutation"])) + ((PROBS["mutation"])*(0.5*(1-PROBS["mutation"]))) + ((PROBS["mutation"])*(0.5*PROBS["mutation"]))
                        # Same as the case in lines 194-200
                    elif mother in one_gene:
                        joint *= ((0.5*(1-PROBS["mutation"]))*(0.5*(1-PROBS["mutation"]))*2) + ((0.5*(1-PROBS["mutation"]))*(0.5*PROBS["mutation"])*2) + ((0.5*(1-PROBS["mutation"]))*(0.5*PROBS["mutation"]*2)) + ((0.5*PROBS["mutation"])*(0.5*PROBS["mutation"])*2)
                        # THE ABOVE PROBS REPRESENT THE FOLLOWING CASES RESPECTIVELY
                        # Bad copy from one, good copy from another, none mutate. (Can be done from two different ways)
                        # Bad copy from one that doesn't mutate, bad copy from one that mutates. (Can be done from two different ways)
                        # Good copy from both, but only one mutates (Two ways to do this)
                        # One good copy and one bad copy, but both mutate. (Two ways to do this)
                        
                    else:
                        joint *= ((0.5*(1-PROBS["mutation"]))*(1-PROBS["mutation"])) + ((0.5*PROBS["mutation"])*(1-PROBS["mutation"])) + ((0.5*(1-PROBS["mutation"]))*PROBS["mutation"]) + ((0.5*PROBS["mutation"])*PROBS["mutation"])
                        # THE ABOVE PROBS REPRESENT THE FOLLOWING CASES RESPECTIVELY
                        # Bad copy from father that doesn't mutate and copy from mother that doesn't mutate
                        # Good copy from father that mutates and good copy from mother that doesn't
                        # Good copy from father that doesn't mutate and good copy from mother that mutates
                        # Bad copy from father that mutates and good copy from mother that mutates
                
                else:
                    if mother in two_genes:
                        joint *= ((1-PROBS["mutation"])*(1-PROBS["mutation"])) + ((PROBS["mutation"])*(PROBS["mutation"]))
                        # Same as the case in lines 201-205
                    elif mother in one_gene:
                        joint *= ((0.5*(1-PROBS["mutation"]))*(1-PROBS["mutation"])) + ((0.5*PROBS["mutation"])*(1-PROBS["mutation"])) + ((0.5*(1-PROBS["mutation"]))*PROBS["mutation"]) + ((0.5*PROBS["mutation"])*PROBS["mutation"])
                        # Same as the case in lines 219-225
                    else:
                        #One mutates and the other doesn't (This can be done from two different ways, from father and mother)
                        joint *= (1-PROBS["mutation"])*PROBS["mutation"]*2
            
            else: # None of the parents must pass a bad copy of the gene
                # First, let's account for the trait factor
                joint *= PROBS["trait"][0][name in have_trait]
                # Now let's account for the probs of the child's genes
                for parent in p_parents.keys():    
                    # Let's check the chances of inheriting one from the father
                    if parent in two_genes: 
                        # Passing a bad copy that doesn't mutate
                        p_parents[parent] = PROBS["mutation"]
                    elif parent in one_gene: 
                        # Passing a bad copy that doesn't mutate
                        # OR passing a good copy that mutates
                        p_parents[parent] = (0.5*(1-PROBS["mutation"]) + 0.5*PROBS["mutation"])
                    else: # Father has no bad copies of the gene
                        # Passing a good copy that mutates
                        p_parents[parent] = 1-PROBS["mutation"]
                    # This prob is equal to the product of probs for each parent
                    joint *= p_parents[parent]      
                
        else:
            print("Person has only one parent, critical error. Self destruction inminent.")
            raise NotImplementedError
        
    return(joint)

def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for person in probabilities.keys():
        if person in two_genes:
            probabilities[person]["gene"][2] += p
        elif person in one_gene:
            probabilities[person]["gene"][1] += p
        else:
            probabilities[person]["gene"][0] += p

        if person in have_trait:
            probabilities[person]["trait"][True] += p
        else:
            probabilities[person]["trait"][False] += p
        

def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for name in probabilities.keys():
        s_genes = sum(probabilities[name]["gene"].values())
        s_trait = sum(probabilities[name]["trait"].values())
    
        for key in probabilities[name]["gene"].keys():
            probabilities[name]["gene"][key] /= s_genes
        for key in probabilities[name]["trait"].keys():
            probabilities[name]["trait"][key] /= s_trait


if __name__ == "__main__":
    main()
