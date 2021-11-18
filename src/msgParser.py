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

def objek(text):
    try:
        o = re.search(formatJenis+' (.+?) pada', text).group(2)
    except:
        try:
            o = re.search(formatJenis+' (.+?)$', text).group(2)
        except:
            o = None
        
    return o

def matkul(text):
    try:
        s = re.search('([A-Z]{2}[0-9]{4}) ?(.*)$', text).group(1)
    except:
        s = None
        
    return s

def topik(text):
    try:
        t = re.search('([A-Z]{2}[0-9]{4}) ?(.+)$', text).group(2)
    except:
        t = None
        
    return t
    
def jenis(text):
    try:
        j = re.search(formatJenis, text).group(0)
    except:
        j = None
        
    return j

def tanggalPada(text):
    try:
        tp = re.search('pada ([a-zA-Z]+), (.+?)$', text).group(2)
    except:
        try:
            tp = re.search('pada (.+?),', text).group(1)
        except:
            try:
                tp = re.search('pada (.+?)$', text).group(1)
            except:
                tp = None
        
    return tp
    
def tanggalTipe(text):
    global formatTanggal1
    global formatTanggal2
    global formatTanggal3
    global formatTanggal4
    
    tipe = None
    
    try:
        tanggal = re.search(formatTanggal1, text).group(0)
        if (tanggal != None):
            tipe = 1
    except:
        try:
            tanggal = re.search(formatTanggal2, text).group(0)
            if (tanggal != None):
                tipe = 2
        except:
            try:
                tanggal = re.search(formatTanggal3, text).group(0)
                if (tanggal != None):
                    tipe = 3
            except:
                try:
                    tanggal = re.search(formatTanggal4, text).group(0)
                    if (tanggal != None):
                        tipe = 4
                except:
                    tipe = None
                
    return tipe

def duaTanggal(text):
    global formatTanggal1
    global formatTanggal2
    global formatTanggal3
    
    try:
        # /(<formatTanggal1>|<formatTanggal2>|<formatTanggal3>) .+ (<formatTanggal1>|<formatTanggal2>|<formatTanggal3>)/g
        dt = re.search('('+formatTanggal1+'|'+formatTanggal2+'|'+formatTanggal3+') .+ ('+formatTanggal1+'|'+formatTanggal2+'|'+formatTanggal3+')', text)
        t1 = dt.group(1)
        t2 = dt.group(11)
    except:
        t1 = None
        t2 = None
    
    return t1, t2
                
def translateTanggal(text):
    global formatTanggal1
    global formatTanggal2
    global formatTanggal3
    
    try:
        tanggal = re.search(formatTanggal1, text)
        d = tanggal.group(1)
        m = tanggal.group(2)
        y = tanggal.group(3)
        
        tanggalRes = d+" "+translateBulan(m)+" "+y
    except:
        try:
            tanggal = re.search(formatTanggal2, text)
            d = tanggal.group(2)
            m = tanggal.group(1)
            y = tanggal.group(3)
        
            tanggalRes = translateBulan(m)+" "+d+" "+y
        except:
            try:
                tanggal = re.search(formatTanggal3, text)
                d = tanggal.group(1)
                m = tanggal.group(2)
                y = tanggal.group(3)
            
                tanggalRes = d+" "+m+" "+y
            except:
                tanggalRes = text

    return tanggalRes

def toDateObj(tanggal, datetype=None):
        if (datetype == None):
            datetype = tanggalTipe(tanggal)
        tanggal = translateTanggal(tanggal)
        if (datetype == 1):
            try:
                date = datetime.datetime.strptime(tanggal, "%d %B %Y")
            except:
                try:
                    date = datetime.datetime.strptime(tanggal, "%d %B %y")
                except:
                    date = None
        elif (datetype == 2):
            try:
                date = datetime.datetime.strptime(tanggal, "%B %d %Y")
            except:
                try:
                    date = datetime.datetime.strptime(tanggal, "%B %d %y")
                except:
                    date = None
        elif (datetype == 3):
            try:
                date = datetime.datetime.strptime(tanggal, "%d %m %Y")
            except:
                try:
                    date = datetime.datetime.strptime(tanggal, "%d %m %y")
                except:
                    try:
                        date = datetime.datetime.strptime(tanggal, "%m %d %Y")
                    except:                        
                        try:
                            date = datetime.datetime.strptime(tanggal, "%m %d %y")
                        except:
                            date = None
        elif (datetype == 4):
            try:
                date = datetime.datetime.strptime(tanggal, "%m/%d/%Y")
            except:
                try:
                    date = datetime.datetime.strptime(tanggal, "%m/%d/%y")
                except:
                    try:
                        date = datetime.datetime.strptime(tanggal, "%d/%m/%Y")
                    except:
                        try:
                            date = datetime.datetime.strptime(tanggal, "%d/%m/%y")
                        except:
                            date = None
        else:
            date = None
            
        if (date != None):
            date = date.date()
            
        return date

def nWaktu(text):
    try:
        n = re.search('([0-9]+) (minggu|hari)', text).group(1)
        if (n != None):
            n = int(n)
    except:
        n = None
    
    return n

def pertanyaan(text):
    try:
        p = re.search('?$', text).group(0)
    except:
        p = None
    
    return (p != None)
    
def task(text):
    try:
        task = re.search('[Tt]ask ([0-9]+)', text).group(1)
        if (task != None):
            task = int(task)
    except:
        task = None
        
    return task
    
def translateBulan(bulan):
    bulan = bulan.capitalize()
    listbulan = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
    listmonth = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    
    try:
        id = listbulan.index(bulan)
        month = listmonth[id]
    except:
        month = None
    
    return month

def oneTaskOnly(text):
    try:
        oneTask = re.search('<br>(.*)', text).group(1)
    except:
        oneTask = None
    
    return oneTask

def bodyToTanggal(body):
    try:
        tanggal = re.search(formatTanggal4, body)
        d = tanggal.group(2)
        m = tanggal.group(1)
        y = tanggal.group(3)
        
        tanggalRes = d+" "+m+" "+y
    except:
        tanggalRes = body
    
    return tanggalRes
