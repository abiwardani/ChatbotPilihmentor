import re
import datetime

formatTanggal1 = '([0-3]?[0-9]) ([a-zA-Z]+) ([0-9]{2,4})' #tanggal bulan tahun
formatTanggal2 = '([a-zA-Z]+) ([0-3]?[0-9]) ([0-9]{2,4})' #bulan tanggal tahun
formatTanggal3 = '([0-3][0-9])/([0-1][0-9])/([0-9]{2,4})' #DD/MM/YYYY
formatTanggal4 = '([0-1][0-9])/([0-3][0-9])/([0-9]{2,4})' #MM/DD/YYYY, bukan untuk user input
formatJenis = '([Tt]ubes|[Tt]ucil|[Kk]uis|[Uu]jian|[Pp]raktikum)'

def bm(text, pattern):
    lastx = {}
    lenP = len(pattern)
    lenT = len(text)
    i = lenP-1
    j = lenP-1
    found = False

    if (lenT < lenP):
        return -1
    
    while (i < lenT and not found):
        j = lenP-1
        found = True
        #print(text)
        #print(" "*(i-(lenP-1))+pattern)
        #print(i)
        while (found and j >= 0):
            if (pattern[j] != text[i]):
                found = False
            else:
                i -= 1
                j -= 1
        
        if (not found):
            if (text[i] not in lastx.keys()):
                k = lenP-1
                while (k >= 0 and pattern[k] != text[i]):
                    k -= 1
                lastx[text[i]] = k
                    
            if (lastx[text[i]] >= 0):
                if (lastx[text[i]] < j):
                    i += lenP-lastx[text[i]]-1
                    #print("case 1")
                else:
                    i += lenP-j
                    #print("case 2")
            else:
                i += lenP
                #print("case 3") 
        #print()
        
        if (i >= lenT):
            return -1
    
    i += 1
    
    #print("Loc:", i)
    
    return i

def exactmatch(text, pattern):
    if (text == pattern):
        return 0
    else:
        return -1

def extractBidang(text, start):
    if (start != -1):
        lenT = len(text)
        if (lenT-start < 8): #pengguna tidak mengelaborasi bidang bisnisnya
            return None
        
        candidates = [bm(text[start+7::], ","), bm(text[start+7::], " dan"), bm(text[start+7::]," terus"), bm(text[start+7::], ".")]
        eligible = [e for e in candidates if e >= 0]
        if (len(eligible) == 0):
            return None
        
        end = min(eligible)

        return (text[start+7::])[0:end]

def findKeywords(text, bidang, keyword_list):
    result = []
    for pattern in keyword_list:
        if (bm(text, pattern) != -1):
            result.append(pattern)
    
    return result

def keywordsIntersect(list1, list2):
    for word in list1:
        if (word in list2):
            return True
    
    return False
