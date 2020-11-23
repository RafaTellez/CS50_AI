import os
import random
import re
import sys
import math
from numpy import cumsum

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    #Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    #Let's get the links on said page and initialize the dictionary to return
    values   = corpus.get(page)
    dist     = dict()
    n_pages  = len(corpus)
    
    #If the page has no links, return a discrete uniform distribution.
    if values == set():
        for key in list(corpus.keys()):
            dist[key] = 1/n_pages
        return(dist)
    
    #We assign the prob of each key (link) to be jumped to at random. Then, if
    #said link is in the actual page, we add the probability of it being jumped
    #to from the list itself. Since they're all unconditional, the probs will
    #sum up to 1.
    for key in corpus:
        dist[key] = (1-damping_factor)/len(corpus)
        if key in values:
            dist[key] = dist.get(key) + damping_factor/len(values) 
    
    #Return the loot
    return(dist)


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    #Declaring variables
    keys = list(corpus.keys())
    n_pages = len(corpus)
    actual_page = keys[ math.floor( random.uniform(0,n_pages) ) ]
    jumps_made = [0]*n_pages
    
    """If a representation or sum error happens, and the random number lands
    on a place where it wont satisfy any condition on line 110, it won't jump
    and won't count any jump, so that iteration is lost but nothing else happens"""
    for k in range(n):
        dist = transition_model(corpus, actual_page, damping_factor)
        aux  = [0] + list(cumsum(list(dist.values())))
        rand = random.uniform(0,1)
    
        for i in range(n_pages):
            if aux[i] < rand < aux[i+1]:
                actual_page    = keys[i]
                jumps_made[i] += 1
                break
    #Calculating probs based on the jumps made
    ranking = corpus.copy()
    for j in range(n_pages):
        ranking[keys[j]] = jumps_made[j]/n
    #Output of the function
    return(ranking)


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    #Declaring variables, initializing and filling
    tol      = 0.001
    keys     = list(corpus.keys())
    n_pages  = len(corpus)
    ranking  = dict()
    NumLinks = dict()
    for key in keys:
        if  corpus[key] == set():
            corpus[key] =  set(keys)
        ranking[key]  = 1/n_pages
        NumLinks[key] = len( corpus.get(key) )
    
    #Iterating until all rankings are "static"
    Done = False
    while not Done:
        #We save the rankings before modifying to measure how much they change
        old = list(ranking.values())
        for p in keys:
            S = 0
            for i in keys:
                if p in corpus[i]:
                    S += (ranking[i] / NumLinks[i])
            ranking[p] = ((1-damping_factor)/n_pages) + (damping_factor * S)
        #We save the rankings after modifying to measure how much they change
        new = list(ranking.values())
        #We check if the variation is lower than our tolerance for each page
        bool_vec = [False]*n_pages
        for k in range(n_pages):
            bool_vec[k] = abs(old[k] - new[k]) < tol
        #Finally, if ALL elements inside bool_vec are true, we are done:
        Done = all(bool_vec)
    
    #After we are done with the process, we can return the ranking
    return(ranking)        


if __name__ == "__main__":
    main()
