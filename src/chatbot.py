import os
from datetime import datetime
import msgParser as p
from flask import Flask, render_template, request, url_for, redirect, make_response
from werkzeug.utils import secure_filename
import json
import time

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

#--- App Pages ---#

@app.route('/')
def indexPage():
    f = open("test/logs.txt", "w")
    message = "Halo! Ketik nama kamu untuk memulai percakapan"
    now = datetime.now()
    log = "B"+now.strftime("%m/%d/%Y %H:%M:%S")+message+"\n"
    f.write(log)
    f.close()

    f = open("test/status.json", "w")
    status = {'nama': None, 'waktu': now.strftime("%m/%d/%Y %H:%M:%S"), 'bidang': None, 'lastProcess': 'login', 'masalah': None, 'isMasalahSelesai': False, 'assignedMentor': None}
    f.write(json.dumps(status))
    f.close()
    
    return render_template('index.html')

@app.route('/displayKontakMentor')
def displayKontakMentor():
    f = open("test/logs.txt", "a+")
    now = datetime.now()

    #--- Database Call ---#

    with open('test/status.json') as g:
        status = json.load(g)

    namaMentor = "Johann"
    bidangMentor = status['bidang'].title()
    linkMeeting = "https://meet.google.com/yyz-hraf-cdk"

    #--- End ---#

    response =  "Nama mentor  : "+namaMentor+"<br>"
    response += "Keahlian     : "+bidangMentor+"<br>"
    response += "Link meeting : <a href=\""+linkMeeting+"\" class=\"meeting-link\" target=\"_blank\">"+linkMeeting[8::]+"</a>"

    status['assignedMentor'] = "Johann"
    status['waktu'] = now.strftime("%m/%d/%Y %H:%M:%S")

    log = "B"+now.strftime("%m/%d/%Y %H:%M:%S")+response+"\n"
    f.write(log)
    f.close()

    f = open("test/status.json", "w")
    f.write(json.dumps(status))
    f.close()

    time.sleep(0.5)
    return redirect(url_for('chatPage'))

@app.route('/Chat', methods = ['GET', 'POST'])
def chatPage():
    if request.method == "POST":
        msg = request.form.get("messageInput").lstrip()
        if (msg.count(" ") < len(msg)):
            f = open("test/logs.txt", "a")
            now = datetime.now()
            log = "U"+now.strftime("%m/%d/%Y %H:%M:%S")+msg+"\n"
            f.write(log)
            f.close()

            html = generateChatContent()

            with open("src/templates/chat.html", "w", encoding="utf8") as file:
                file.write(html)
            
            processInput(msg)
            resp = make_response(render_template('chat.html'))
            resp.headers['Refresh'] = '0.8'
            return resp
    
    time.sleep(0.5)
    checkLog()

    html = generateChatContent()

    with open("src/templates/chat.html", "w", encoding="utf8") as file:
        file.write(html)
    
    resp = make_response(render_template('chat.html'))
    resp.headers['Refresh'] = '15'
    return resp

@app.route('/Rekap')
def rekapPage():
    html = generateRekapContent()

    with open("src/templates/chat.html", "w", encoding="utf8") as file:
        file.write(html)
    
    resp = make_response(render_template('chat.html'))
    return resp


#--- Text Processing ---#

def generateChatContent():
    f = open("test/logs.txt", "r")
    chatLogs = f.readlines()
    
    html = ''
    html += '<!DOCTYPE html>\n'
    html += '<html>\n'
    html += '    <head>\n'
    html += '        <title>Pilihmentor</title>\n'
    html += '        <link rel=\"stylesheet\" href=\"static/styles/chatbotstyles.css\">'
    html += '        <link rel=\"stylesheet\" href=\"static/styles/headerstyles.css\">'
    html += '    </head>\n'
    html += '    <body>\n'
    html += '    <div class=\"header\">'
    html += '        <div class=\"header-box\">'
    html += '            <table class=\"header-table\">'
    html += '                <tr>'
    html += '                    <td>'
    html += '                        <a class=\"header-text\" href=\"http://localhost:5000/\"><img class=\"header-logo\" src=\"https://pilihmentor.com/wp-content/uploads/2021/10/logo.png\" alt=\"Pilihmentor.com\"></a>'
    html += '                    </td>'
    html += '                    <td>'
    html += '                        <a class="register-button" href="#">Register</a>'
    html += '                    </td>'
    html += '                </tr>'
    html += '            </table>'
    html += '        </div>'
    html += '    </div>'
    html += '    <div class=\"chatarea\">\n'
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
    f.close()
    
    html += '        </table>\n'
    html += '    </div>\n'
    html += '    <form action=\"http://localhost:5000/Chat\" method=POST>\n'
    html += '        <div class=\"messageBox\">\n'
    html += '            <input type=\"text\" name=\"messageInput\" id=\"message\" placeholder=\"Tulis pesan kamu di sini...\" autocomplete="off">\n'
    html += '            <input type=\"submit\" id=\"send\" name=\"sendButton\" value=\"Kirim\">\n'
    html += '        </div>\n'
    html += '    </form>\n'
    html += '    </div>\n'
    html += '    </body>\n'
    html += '</html>'

    return html

def generateRekapContent():
    with open('test/rekap.json') as f:
        rekap = json.load(f)
    
    html = ''
    html += '<!DOCTYPE html>\n'
    html += '<html>\n'
    html += '    <head>\n'
    html += '        <title>Pilihmentor</title>\n'
    html += '        <link rel=\"stylesheet\" href=\"static/styles/rekapstyles.css\">'
    html += '        <link rel=\"stylesheet\" href=\"static/styles/headerstyles.css\">'
    html += '    </head>\n'
    html += '    <body>\n'
    html += '    <div class=\"header\">'
    html += '        <div class=\"header-box\">'
    html += '            <table class=\"header-table\">'
    html += '                <tr>'
    html += '                    <td>'
    html += '                        <a class=\"header-text\" href=\"http://localhost:5000/\"><img class=\"header-logo\" src=\"https://pilihmentor.com/wp-content/uploads/2021/10/logo.png\" alt=\"Pilihmentor.com\"></a>'
    html += '                    </td>'
    html += '                    <td>'
    html += '                        <a class="register-button" href="#">Register</a>'
    html += '                    </td>'
    html += '                </tr>'
    html += '            </table>'
    html += '        </div>'
    html += '    </div>'
    html += '    <div class=\"rekap-area\">'
    html += '        <div class=\"title-area\">'
    html += '            <p class=\"rekap-title\">Chat History Bot</p>'
    html += '        </div>'
    html += '        <div class=\"rekap-items\">'

    for i in range(len(rekap['logs'])):
        if (rekap['logs'][i]['status'] == "Solved"):
            html += '            <div class=\"solved-item\">'
        else:
            html += '            <div class=\"not-solved-item\">'
        html += '                <table class=\"rekap-item\">'
        html += '                    <tr>'
        html += '                        <td class=\"nomer-rekap\">'
        html += '                            <b>'+str(i+1)+'.</b>'
        html += '                        </td>'
        html += '                        <td class=\"info-rekap\">'
        assignedMentorMessage = ""
        if (rekap['logs'][i]['assignedMentor'] != None):
            assignedMentorMessage = "<br>Assigned Mentor: "+rekap['logs'][i]['assignedMentor']
        html += '                            <b><i>'+rekap['logs'][i]['waktu']+"</b><br>User: "+rekap['logs'][i]['user']+"<br>Masalah: "+rekap['logs'][i]['masalah']+assignedMentorMessage+"<br>Status: "+rekap['logs'][i]['status']+"</i>"
        html += '                        </td>'
        html += '                    </tr>'
        html += '                </table>'
        html += '            </div>'
    
    html += '        </div>'
    html += '    </div>'
    html += '    </body>\n'
    html += '</html>'

    return html

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
    
    with open('test/status.json') as f:
        status = json.load(f)

    if (status['lastProcess'] == 'login' and status['nama'] == None):
        status['nama'] = text

        f = open("test/logs.txt", "a+")
        response = "Halo, "+text+"! Bisa ceritakan masalahmu?"
        log = "B"+now.strftime("%m/%d/%Y %H:%M:%S")+response+"\n"
        f.write(log)
        f.close()

        f = open("test/status.json", "w")
        f.write(json.dumps(status))
        f.close()

        return None
    
    if (status['lastProcess'] == "request-elaborasi-masalah" and status['masalah'] == "ads"):
        return handleAdsMasalah(now, textl, status, exitFlag)
    
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
            status['bidang'] = bidang

            #--- INI NANTI AMBIL DARI DATABASE ---#

            keywords_list = ["instagram", " ig", "facebook", " fb", "google", "adsense", " ads", "iklan", "advertisement", " ad", "hire", "programmer", "ari orang", "stakeholder", "modal", "capital", "invest"]
            keywords_ads = ["instagram", " ig", "facebook", " fb", "google", "adsense", " ads", "iklan", "advertisement", " ad"]
            keywords_hire = ["hire", "ari orang"]
            keywords_modal = ["modal", "capital", "stakeholder", "invest"]

            #--- END ---#
            
            keywords = p.findKeywords(textl, status['bidang'], keywords_list)
            if (p.keywordsIntersect(keywords, keywords_ads)):
                handleAdsMasalah(now, textl, status, exitFlag)
            elif (p.keywordsIntersect(keywords, keywords_hire)):
                handleHireMasalah(now, textl, status, exitFlag)
            elif (p.keywordsIntersect(keywords, keywords_modal)):
                handleModalMasalah(now, textl, status, exitFlag)
            else:
                handleUnknownMasalah(textl, status)

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


def handleAdsMasalah(now, textl, status, exitFlag):
    #--- INI NANTI AMBIL DARI DATABASE ---#

    keywords_level2_list = ["instagram", "ig", "facebook", "fb", "google", "adsense"]

    #--- END ---#

    keywords = p.findKeywords(textl, status['bidang'], keywords_level2_list)
    if (p.keywordsIntersect(keywords, ["instagram", " ig"])):
        status['lastProcess'] = "jawab-masalah"
        status['masalah'] = "instagram ads"
        status['isMasalahSelesai'] = True
        
        f = open("test/status.json", "w")
        f.write(json.dumps(status))
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
        status['lastProcess'] = "jawab-masalah"
        status['masalah'] = "facebook ads"
        status['isMasalahSelesai'] = True

        f = open("test/status.json", "w")
        f.write(json.dumps(status))
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
        status['lastProcess'] = "jawab-masalah"
        status['masalah'] = "google ads"
        status['isMasalahSelesai'] = True

        f = open("test/status.json", "w")
        f.write(json.dumps(status))
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
            status['lastProcess'] = "jawab-masalah"

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

        status['lastProcess'] = "request-elaborasi-masalah"
        status['masalah'] = "ads"
        status['isMasalahSelesai'] = False
        
        f = open("test/status.json", "w")
        f.write(json.dumps(status))
        f.close()

def handleHireMasalah(now, textl, status, exitFlag):
    #--- INI NANTI AMBIL DARI DATABASE ---#

    keywords_level2_list = ["programmer"]

    #--- END ---#

    keywords = p.findKeywords(textl, status['bidang'], keywords_level2_list)
    if (p.keywordsIntersect(keywords, ["programmer"])):
        status['lastProcess'] = "jawab-masalah"
        status['masalah'] = "hire programmer"
        status['isMasalahSelesai'] = True

        f = open("test/status.json", "w")
        f.write(json.dumps(status))
        f.close()

        #--- DATABASE CALL ---#
        response = "<b>STEPS FOR HIRE PROGRAMMER<b>"
        #--- END ---#

        f = open("test/logs.txt", "a+")
        log = "B"+now.strftime("%m/%d/%Y %H:%M:%S")+response+"\n"
        f.write(log)
        f.close()

        responFollowUpMentor()
    else:
        status['masalah'] = "sumber daya manusia"

        handleUnknownMasalah(textl, status)
    
def handleModalMasalah(now, textl, status, exitFlag):
    #--- INI NANTI AMBIL DARI DATABASE ---#

    keywords_level2_list = ["invest"]

    #--- END ---#

    keywords = p.findKeywords(textl, status['bidang'], keywords_level2_list)
    if (p.keywordsIntersect(keywords, ["invest"])):
        status['lastProcess'] = "jawab-masalah"
        status['masalah'] = "cari investor"
        status['isMasalahSelesai'] = True

        f = open("test/status.json", "w")
        f.write(json.dumps(status))
        f.close()

        #--- DATABASE CALL ---#
        response = "<b>STEPS FOR CARI INVESTOR<b>"
        #--- END ---#

        f = open("test/logs.txt", "a+")
        log = "B"+now.strftime("%m/%d/%Y %H:%M:%S")+response+"\n"
        f.write(log)
        f.close()

        responFollowUpMentor()
    else:
        status['masalah'] = "modal"
        handleUnknownMasalah(textl, status)

def handleUnknownMasalah(textl, status):
    now = datetime.now()

    f = open("test/logs.txt", "a+")
    response = "Bot belum bisa membantu masalahmu saat ini, silahkan hubungi mentor dengan menekan tombol di bawah ini"
    log = "B"+now.strftime("%m/%d/%Y %H:%M:%S")+response+"\n"
    f.write(log)
    f.close()
    
    status['lastProcess'] = "solusi-tidak-ditemukan"
    f = open("test/status.json", "w")
    f.write(json.dumps(status))
    f.close()

    responFollowUpMentor()

def responFollowUpMentor():
    now = datetime.now()

    f = open("test/logs.txt", "a+")
    response = "Bila ada kendala, kamu bisa langsung menghubungi salah satu mentor kami dengan menekan tombol di bawah ini"
    log = "B"+now.strftime("%m/%d/%Y %H:%M:%S")+response+"\n"
    f.write(log)
    f.close()

    with open('test/status.json') as f:
        status = json.load(f)
    
    status['lastProcess'] = "tawar-bantuan-mentor"
    f = open("test/status.json", "w")
    f.write(json.dumps(status))
    f.close()

def displayHubungiMentorButton():
    button = '<a href=\"http://localhost:5000/displayKontakMentor\" id=hubmentorbutton class=\"hubungi-mentor-button\"><b><i>Hubungi Mentor</i></b></a>'
    html = '            <tr><td><form>'+button+'</form></td></tr>\n'
    return html

def badPesanBody():
    body = "Maaf, bot tidak mengenal pesan itu. Bisa ceritakan masalahmu?"

    return body

def checkLog():
    with open('test/status.json') as f:
        status = json.load(f)
    
    if (status['waktu'] != None):
        waktu = datetime.strptime(status['waktu'], "%m/%d/%Y %H:%M:%S")
        now = datetime.now()
        diff = now-waktu
        if (diff.total_seconds() > 14.5):
            writeLog()

def writeLog():
    with open('test/status.json') as f:
        status = json.load(f)

    with open('test/rekap.json') as f:
        rekap = json.load(f)

    if (status['masalah'] == None):
        return None
    
    statusSelesai = "Not Solved"
    if (status['isMasalahSelesai'] == True):
        statusSelesai = "Solved"

    for i in range(len(rekap['logs'])):
        log = rekap['logs'][i]
        if (log['user'] == status['nama'] and log['masalah'] == status['masalah']):
            if (log['waktu'] == status['waktu']):
                return None
            
            rekap['logs'][i]['status'] = statusSelesai
            rekap['logs'][i]['assignedMentor'] = status['assignedMentor']
    
            f = open("test/rekap.json", "w")
            f.write(json.dumps(rekap))
            f.close()

            return None

    new_log = {'waktu': status['waktu'], 'user': status['nama'], 'masalah': status['masalah'], 'status': statusSelesai, 'assignedMentor': status['assignedMentor']}
    rekap['logs'].append(new_log)
    
    f = open("test/rekap.json", "w")
    f.write(json.dumps(rekap))
    f.close()

#--- Main ---#

if __name__ == '__main__':
    app.run()