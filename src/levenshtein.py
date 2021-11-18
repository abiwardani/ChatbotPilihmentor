import numpy

def levenshteinDistanceDP(A, B):
    distances = numpy.zeros((len(A) + 1, len(B) + 1))

    for i in range(len(A) + 1):
        distances[i][0] = i

    for j in range(len(B) + 1):
        distances[0][j] = j
        
    a = 0
    b = 0
    c = 0
    
    for i in range(1, len(A) + 1):
        for j in range(1, len(B) + 1):
            if (A[i-1] == B[j-1]):
                distances[i][j] = distances[i - 1][j - 1]
            else:
                a = distances[i][j - 1]
                b = distances[i - 1][j]
                c = distances[i - 1][j - 1]
                
                if (a <= b and a <= c):
                    distances[i][j] = a + 1
                elif (b <= a and b <= c):
                    distances[i][j] = b + 1
                else:
                    distances[i][j] = c + 1

    return distances[len(A)][len(B)]

def calcDictDistance(word, numWords):
    file = open('kamus.txt', 'r') 
    lines = file.readlines() 
    file.close()
    dictWordDist = []
    wordIdx = 0
    
    for line in lines: 
        wordDistance = levenshteinDistanceDP(word, line.strip())
        if wordDistance >= 10:
            wordDistance = 9
        dictWordDist.append(str(int(wordDistance)) + "-" + line.strip())
        wordIdx = wordIdx + 1

    closestWords = []
    wordDetails = []
    currWordDist = 0
    dictWordDist.sort()
    for i in range(numWords):
        currWordDist = dictWordDist[i]
        wordDetails = currWordDist.split("-")
        closestWords.append(wordDetails[1])
    return closestWords