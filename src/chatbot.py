import os
from datetime import datetime, timedelta
import msgParser as p
from flask import Flask, render_template, flash, request, url_for, redirect
from werkzeug.utils import secure_filename
import levenshtein as l
import json

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

#--- App Pages ---#

@app.route('/')
def mainPage():
    f = open("test/logs.txt", "w")
    message = "Halo! Bisa ceritakan masalahmu?"
    now = datetime.now()
    log = "B"+now.strftime("%m/%d/%Y %H:%M:%S")+message+"\n"
    f.write(log)
    f.close()

    f = open("test/config.json", "w")
    config = {'bidang': None, 'lastProcess': None, 'masalah': None, 'isMasalahSelesai': False}
    f.write(json.dumps(config))
    f.close()
    
    return render_template('mainpage.html')

@app.route('/displayKontakMentor')
def displayKontakMentor():
    f = open("test/logs.txt", "a+")
    now = datetime.now()

    #--- Database Call ---#

    with open('test/config.json') as g:
        config = json.load(g)

    response =  "Nama mentor  : Johann<br>"
    response += "Keahlian     : "+config['bidang'].title()+"<br>"
    response += "Link meeting : <a href=\"https://meet.google.com/yyz-hraf-cdk\">meet.google.com/yyz-hraf-cdk</a>"

    #--- End ---#

    log = "B"+now.strftime("%m/%d/%Y %H:%M:%S")+response+"\n"
    f.write(log)
    f.close()

    return redirect(url_for('chatPage'))

@app.route('/Chat', methods = ['GET', 'POST'])
def chatPage():
    f = open("test/logs.txt", "a")
    
    if request.method == "POST":
        msg = request.form.get("messageInput").lstrip()
        if (msg.count(" ") < len(msg)):
            now = datetime.now()
            log = "U"+now.strftime("%m/%d/%Y %H:%M:%S")+msg+"\n"
            f.write(log)
            f.close()
            processInput(msg)
    
    f = open("test/logs.txt", "r")
    chatLogs = f.readlines()
    
    html = ''
    html += '<!DOCTYPE html>\n'
    html += '<html>\n'
    html += '    <head>\n'
    html += '        <title>Pilihmentor</title>\n'
    html += '        <link rel=\"stylesheet\" href=\"static/styles/chatbotstyles.css\">'
    html += '    </head>\n'
    html += '    <body>\n'
    html += '    <div class=\"header\">\n'
    html += '        <table class=\"headergrid\" cellspacing=0 cellpadding=0>\n'
    html += '            <tr><td class=\"avatarimg\"><img class=\"avatar\" src=\"static/avatar.png\"></td>\n'
    html += '            <td><p class=\"botname\"><a class=\"botlink\" href=\"http://127.0.0.1:5000/Chat\"><b>Pilihmentor Bot</b></a></p></td></tr>\n'    
    html += '        </table>\n'
    html += '    </div>\n'
    html += '    <div class=\"chatscroll\">\n'
    html += '        <table class=\"chat\">\n'
    
    bar = None
    
    for line in chatLogs:
        type = line[0]
        date_time_obj = datetime.strptime(line[1:20], "%m/%d/%Y %H:%M:%S")
        if ((bar == None) or (date_time_obj.date() > bar.date())):
            bar = date_time_obj
            datestr = date_time_obj.strftime("%m/%d/%Y")
            now = datetime.now()
            sDiff = (now-bar).total_seconds()
            if sDiff < 60*60*24:
                if bar.day == now.day:
                    datestr = "Today"
                else:
                    datestr = "Yesterday"
            html += '            <tr><td><p class=\"datebubble\">'+datestr+'</p></td></tr>\n'
        message = line[20:-1]
        if type == "U":
            html += '            <tr><td><p class=\"userbubble\">'+message+'</p>'
            html += '<p class=\"usertime\">'+date_time_obj.time().isoformat(timespec='minutes')+'</p></td></tr>\n'
        elif type == "B":
            html += '            <tr><td><p class=\"botbubble\">'+message+'</p>'
            html += '<p class=\"bottime\">'+date_time_obj.time().isoformat(timespec='minutes')+'</p></td></tr>\n'

            if (message == "Bila ada kendala, kamu bisa langsung menghubungi salah satu mentor kami dengan menekan tombol di bawah ini"):
                html += displayHubungiMentorButton()
    
    html += '        </table>\n'
    html += '    </div>\n'
    html += '    <form action=\"http://127.0.0.1:5000/Chat\" method=POST>\n'
    html += '        <div class=\"messageBox\">\n'
    html += '            <input type=\"text\" name=\"messageInput\" id=\"message\" placeholder=\"Type your message...\" autocomplete="off">\n'
    html += '            <input type=\"submit\" id=\"send\" name=\"sendButton\" value=\"send\">\n'
    html += '        </div>\n'
    html += '    </form>\n'
    html += '    </body>\n'
    html += '</html>'
    with open("src/templates/chat.html", "w", encoding="utf8") as file:
        file.write(html)
    
    return html #render_template('chat.html')

#--- Text Processing ---#

def processInput(text):
    #ignore trailing/leading whitespace
    text = text.strip()
    #check kata-kata kunci setiap command menggunakan algoritma boyer-moore untuk exact string matching
    #algoritma mengembalikan -1 jika tidak ditemukan, jika ditemukan mengembalikan indeks mulai substring
    textl = text.lower()
    bidangFlag = p.bm(textl, "bidang")
    sapaFlag = max(p.bm(textl, "halo"), p.bm(textl, "hai"), p.exactmatch(textl, "hi"), p.bm(textl, "hei"), p.bm(textl, "hey"), p.bm(textl, "hello"), p.bm(textl, "hallo"))
    terimakasihFlag = max(p.bm(textl, "terima kasih"), p.bm(textl, "terimakasih"), p.bm(textl, "thanks"), p.bm(textl, "tks"), p.bm(textl, "makasih"), p.bm(textl, "tq"), p.bm(textl, "thank you"))
    exitFlag = max(p.bm(textl, "exit"), p.bm(textl, "keluar"), p.bm(textl, "cancel"))

    now = datetime.now()

    f = open("test/logs.txt", "r")
    chatLogs = f.readlines()
    for line in chatLogs:
        type = line[0]
        if type == "U":
            lastBotMessage = line[20:-1]
    
    with open('test/config.json') as f:
        config = json.load(f)
    
    if (config['lastProcess'] == "request-elaborasi-masalah" and config['masalah'] == "ads"):
        return handleAdsMasalah(now, textl, config, exitFlag)
    
    #jika bukan sambungan dari previous process
    if (bidangFlag) != -1:
        bidang = p.extractBidang(textl, bidangFlag)
        if (bidang == None):
            f = open("test/logs.txt", "a+")
            response = "Maaf, kami tidak bisa mendeteksi bidang perusahaan kamu. Silahkan jelaskan kembali masalah kamu dengan penjabaran \"perusahaan saya di bidang X\"."
            log = "B"+now.strftime("%m/%d/%Y %H:%M:%S")+response+"\n"
            f.write(log)
            f.close()
        else:
            config['bidang'] = bidang
            
            handleAdsMasalah(now, textl, config, exitFlag)
    elif(sapaFlag != -1):
        f = open("test/logs.txt", "a+")
        response = "Halo! Bisa ceritakan masalahmu?"
        log = "B"+now.strftime("%m/%d/%Y %H:%M:%S")+response+"\n"
        f.write(log)
        f.close()
    elif(terimakasihFlag != -1):
        f = open("test/logs.txt", "a+")
        response = "Sama-sama! Apakah ada hal lain yang bisa bot bantu?"
        log = "B"+now.strftime("%m/%d/%Y %H:%M:%S")+response+"\n"
        f.write(log)
        f.close()
    else:
        f = open("test/logs.txt", "a+")
        response = badPesanBody()
        log = "B"+now.strftime("%m/%d/%Y %H:%M:%S")+response+"\n"
        f.write(log)
        f.close()
        
def loadTasks():
    #read data
    f = open("test/tasks.txt", "r")
    lines = f.readlines()
    f.close()
    
    #gunakan dictionary, {<date1>: [<task1>, <task2>, ...], <date2>: [<task3>, <task4>, ...], ...}
    tasks = {}
    
    for line in lines:
        #abaikan newline
        line = line.replace("\n", "")
        #separator "---"
        info = line.split("---")
        if (info[1] in tasks.keys()):
            #jika tanggal sudah di dictionary, tambahkan task ke values
            tasks[info[1]].append([info[0], info[2], info[3]])
        else:
            #jika tidak, inisialisasi entri tanggal di dictionary dengan value = task kini
            tasks[info[1]] = [[info[0], info[2], info[3]]]
    
    return tasks


def handleAdsMasalah(now, textl, config, exitFlag):
    #--- INI NANTI AMBIL DARI DATABASE ---#

    keywords_level2_list = ["instagram", "ig", "facebook", "fb", "google", "adsense"]

    #--- END ---#

    keywords = p.findKeywords(textl, config['bidang'], keywords_level2_list)
    if (p.keywordsIntersect(keywords, ["instagram", " ig"])):
        config['lastProcess'] = "jawab-masalah"
        config['masalah'] = "instagram ads"
        config['isMasalahSelesai'] = True
        
        f = open("test/config.json", "w")
        f.write(json.dumps(config))
        f.close()

        #--- DATABASE CALL ---#
        response = "<b>Cara memasang ads di Instagram:</b><br>"
        response += "1. Buat Fanpage di Facebook<br>"
        response += "2. Pilih Create Ads<br>"
        response += "3. Pilih tujuan beriklan<br>"
        response += "4. Tentukan target audiens dan anggaran<br>"
        response += "5. Format iklan"
        #--- END ---#

        f = open("test/logs.txt", "a+")
        log = "B"+now.strftime("%m/%d/%Y %H:%M:%S")+response+"\n"
        f.write(log)
        f.close()

        responFollowUpMentor()
    elif (p.keywordsIntersect(keywords, ["facebook", "fb"])):
        config['lastProcess'] = "jawab-masalah"
        config['masalah'] = "facebook ads"
        config['isMasalahSelesai'] = True

        f = open("test/config.json", "w")
        f.write(json.dumps(config))
        f.close()
        
        #--- DATABASE CALL ---#
        response = "STEPS FOR FB ADS"
        #--- END ---#

        f = open("test/logs.txt", "a+")
        log = "B"+now.strftime("%m/%d/%Y %H:%M:%S")+response+"\n"
        f.write(log)
        f.close()

        responFollowUpMentor()
    elif (p.keywordsIntersect(keywords, ["google", "adsense"])):
        config['lastProcess'] = "jawab-masalah"
        config['masalah'] = "google ads"
        config['isMasalahSelesai'] = True

        f = open("test/config.json", "w")
        f.write(json.dumps(config))
        f.close()

        #--- DATABASE CALL ---#
        response = "STEPS FOR GOOGLE ADS"
        #--- END ---#
        
        f = open("test/logs.txt", "a+")
        log = "B"+now.strftime("%m/%d/%Y %H:%M:%S")+response+"\n"
        f.write(log)
        f.close()

        responFollowUpMentor()
    else:
        if (exitFlag != -1):
            config['lastProcess'] = "jawab-masalah"

            f = open("test/logs.txt", "a+")
            response = "Halo! Bisa ceritakan masalahmu?"
            log = "B"+now.strftime("%m/%d/%Y %H:%M:%S")+response+"\n"
            f.write(log)
            f.close()
        
        f = open("test/logs.txt", "a+")
        response = "Kamu ingin memasang advertisement dari penyedia iklan apa? (Instagram/Facebook/Google)"
        log = "B"+now.strftime("%m/%d/%Y %H:%M:%S")+response+"\n"
        f.write(log)
        f.close()

        config['lastProcess'] = "request-elaborasi-masalah"
        config['masalah'] = "ads"
        config['isMasalahSelesai'] = False
        
        f = open("test/config.json", "w")
        f.write(json.dumps(config))
        f.close()

def responFollowUpMentor():
    now = datetime.now()

    f = open("test/logs.txt", "a+")
    response = "Bila ada kendala, kamu bisa langsung menghubungi salah satu mentor kami dengan menekan tombol di bawah ini"
    log = "B"+now.strftime("%m/%d/%Y %H:%M:%S")+response+"\n"
    f.write(log)
    f.close()

    with open('test/config.json') as f:
        config = json.load(f)
    
    config['lastProcess'] = "tawar-bantuan-mentor"
    f = open("test/config.json", "w")
    f.write(json.dumps(config))
    f.close()

def displayHubungiMentorButton():
    button = '<a href=\"http://localhost:5000/displayKontakMentor\" id=hubmentorbutton class=\"hubungi-mentor-button\"><b><i>Hubungi Mentor</i></b></a>'
    html = '            <tr><td><form>'+button+'</form></td></tr>\n'
    return html

def responseBody(mindate=None, maxdate=None, matkul=None, jenis=None):
    body = ""
    tasks = loadTasks()
    
    times = sorted(list(tasks.keys()))
    i = 1
    j = 1
    for time in times:
        date = datetime.strptime(time, "%m/%d/%Y").date()
        validDate = True
        if (mindate != None):
            validDate = validDate and (date >= mindate)
        if (maxdate != None):
            validDate = validDate and (date <= maxdate)
        
        for task in tasks[time]:
            validObj = True
            if (matkul != None):
                validObj = validObj and (matkul == task[1])
            if (jenis != None):
                if (jenis != "Tugas"):
                    validObj = validObj and (jenis == task[0])
                else:
                    validObj = validObj and ((task[0] == "Tubes") or (task[0] == "Tucil"))
            
            if (validDate and validObj):
                body += str(j)+". (ID: "+str(i)+") "+date.strftime("%d/%m/%Y")+" - "+task[1]+" - "+task[0]+" - "+task[2]+"<br>"
                j += 1
            i += 1
            
    return body

def helpBody():
    body = ""
    body += "<b>[FITUR]</b><br>"
    body += "1. Mencatat task<br>"
    body += "2. Melihat daftar task<br>"
    body += "3. Menampilkan tanggal task dan deadline tugas<br>"
    body += "4. Mengubah tanggal task<br>"
    body += "5. Menghapus task dari daftar<br>"
    body += "<br>"
    body += "<b>[DAFTAR KATA PENTING]</b><br>"
    body += "1. Kuis<br>"
    body += "2. Ujian<br>"
    body += "3. Tubes<br>"
    body += "4. Tucil<br>"
    body += "5. Praktikum<br>"
    
    return body

def badPesanBody():
    body = "Maaf, bot tidak mengenal pesan itu. Bisa ceritakan masalahmu?"

    return body


#--- Main ---#

if __name__ == '__main__':
    app.run()