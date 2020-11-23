import nltk
import sys
import os
import string
import math

FILE_MATCHES = 1
SENTENCE_MATCHES = 1


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """
    #Declaring auxiliary variables
    texts = dict()
    
    #Let's read one file at a time for every file at the dir
    for file in os.listdir(directory):
        f_loc = os.path.join(directory,file)
        with open(f_loc,"r", encoding="utf8") as f:
            doc = f.read()
        texts[file] = doc
        
    return texts

def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """
    
    #First we lowercase the doc and declare some aux variables
    document = document.lower()
    stopwords = nltk.corpus.stopwords.words("english")
    #I'll update punctuation to add smileys that may linger from using TwitterTokenizer
    punctuation = string.punctuation + ":(:):[:]:o;(;);[;];o:._.-.,_,-,:/:\:;/;\;"
    
    #Next, tokenization. I used TeetTokenizer because it doesn't separate 
    #words by apostrophes which would have ruined the removal of several
    #stopwords. (Also, we make a copy of document so the size doesn't change
    #during iterations)
    tokenizer = nltk.TweetTokenizer()
    document = tokenizer.tokenize(document)
    output = list(document)

    #We check every token. If it's a punctuation or a stopword, we remove it.
    for word in document:
        if (word in stopwords) or (word in punctuation):
            output.remove(word)

    #Here we take the commas out of any word. Mainly to remove thousands
    #separators from numbers, so they can be read in a regular python format.
    for word in output:
        if "," in word:
            output[output.index(word)] = word.replace(",","")
         
    #To make sure that the removal of commas didn't turn a word to a punctuation
    #or smiley, we'll run a final cleaning only for punctuation.
    document = list(output)
    for word in document:
        if word in punctuation:
            output.remove(word)
    
    #We return our output
    return output

def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """
    #Declaring auxiliary variables. #Specifically, unique will hold all the
    #unique words among all texts so we can assign the idf to each unique word.
    words_idf = dict()
    unique = set()
    N = len(documents)
    
    #Making a list of unique words of all the documents.
    for key in documents:
        unique = unique.union(set(documents[key]))
    
    #Computing and assigning the idf to each unique word in the corpus.
    for word in unique:
        #Calculating df (Number of documents that contain the word)
        k = 0
        for document in documents:
            if word in documents[document]:
                k+=1
        #Computing idf and assigning it to the word
        words_idf[word] = math.log(N/k)
    
    return words_idf
    
def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """
    #Declaring auxiliary variables.
    tf_idfs = dict() #Dictionary mapping names to their tf-idfs
    
    #Counting ngram frecuency and assigning the tf_idf 
    for file in files:
        tf_idfs[file] = 0
        #Computing the tf-idf score for the query. If a word is not in the
        #file text, it's tf will be 0, thus it won't add to de tf-idf score.
        #Also, if the word isn't in any text, the default will give off 0 aswell.
        for word in query:
            #aux is just so that my count_ngrams function works well
            aux = []
            aux.append(word)
            tf_idfs[file] += count_ngrams(aux, files[file]) * idfs.setdefault(aux[0],0)
            aux.clear()
    
    #Now we just need to sort the filenames by their tfidf score
    keys = tf_idfs.keys()
    values = tf_idfs.values()
    sorted_zipped = sorted(zip(values,keys), reverse=True)
    sorted_keys = [element for _, element in sorted_zipped]
    
    #We take a list with the n top filenames by tf-idf score and return said list
    output = sorted_keys[:n]
    return output
    
    
def count_ngrams(query, text):
    """
    Function made by miself to count how many matching ngrams there are in
    a given text. Query is a tokenized query and text is a tokenized document
    text. It returns how many matching ngrams were found in the text (integer)
    
    This is a function I'll keep, this is why it's so general for this application
    """
    #Declaring auxiliary variables
    lq = len(query)
    lt = len(text)
    N = 0

    #For every index that marks the beggining of all possible ngrams in the text
    for i in range(lt-lq+1):
        #Declaring aux variable. The corresponding text ngram to check.
        text_ngram = text[i:i+lq]
        #For every index of the query word and the text ngram to check for equality
        for j in range(lq):
            #Check if word j in query matches word j in the text ngram.
            match = (query[j]==text_ngram[j])
            if not match: #If a word doesn't match in a position, it isn't a match
                break
        
        #Update the number of matches if a match is found
        if match:
            N+=1
    
    return N            

def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """
    #Declaring auxiliary variables
    mwm = dict() #Dictionary mapping sentences to their matching word measure
    output = [] #The list of sentences that will be returned.
    
    for sentence in sentences:
        mwm[sentence] = 0
        #Computing the mwm score for the query. If a word is not in the
        #sentence, it won't sum anything. If the word doesn't exist in any text
        #the default method will give off 0, adding 0 to de score.
        for word in query:
            if word in sentences[sentence]:
                mwm[sentence] += idfs.setdefault(word,0)
    
    #Now we sort the filenames by their mwm score
    keys = list(mwm.keys())
    values = list(mwm.values())
    sorted_zipped = sorted(zip(values,keys), reverse=True)
    sorted_keys = [element for _, element in sorted_zipped]
    sorted_values = [element for element, _ in sorted_zipped]
    
    #Now let's sort each group of keys that share the same mwm score by their
    #query term density (qtm) score
    unique = sorted(list(set(values)), reverse=True)
    for value in unique:
        #Declaring aux variables
        qtm = []
        l = values.count(value)
        #Compute qtm for each sentence
        for i in range(l):
            qtm.append( compute_qtm(query, sentences[sorted_keys[i]]) )
        
        #We sort the sentences by the qtm
        sorted_zipped = sorted(zip(qtm,sorted_keys[:l]), reverse=True)
        sorted_output_chunk = [element for _, element in sorted_zipped]
        
        #We append every sentence obtained to our output. This will leave the
        #terms sorted by descending tdf but now they will be sorted with qtm
        #as an untie measure.
        for sentence in sorted_output_chunk:
            output.append(sentence)
        
        #We remove the used keys from sorted_keys so the next iterations run properly.
        sorted_keys = sorted_keys[l:]
        
    #Now, we take the first n sentences, taking to our advantage that they're
    #in descending tdf score order and untie by descending qtm score.
    output = output[:n]
    
    #Finally we return the output
    return output


def compute_qtm(query, sentence):
    """
     Computes the qtm for a sentence given a query. It does so by summing up
     the qtm's for each word of the query.
    """
    #Checking for a list and not a string
    if str(type(sentence)) != "<class 'list'>":
        print("ERROR in compute_qtm. sentence input must be a list. Exiting program")
        sys.exit(1)

    #Declaring aux variables
    qtm = 0

    #Getting the qtm for every word of the query. The aux is to make the 
    #count_ngrams function work right, passing a list instead of a string.
    for word in query:
        aux = []
        aux.append(word)
        qtm += count_ngrams(aux, sentence)
        aux.clear()

    #Scaling the qtm using the ammount of tokens in sentence
    qtm /= len(sentence)
    
    #Finally, return qtm.
    return qtm
    



if __name__ == "__main__":
    main()




























