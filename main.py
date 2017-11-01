from flask import Flask, flash, redirect, render_template, request, session, current_app as app
import os
import time
from time import localtime
from twilio.rest import Client

app = Flask(__name__)
app.secret_key = os.urandom(12)

currentUser = ['']

#Virtual Line Lists
nameList = []
phoneList = []
ageList = []
abilityList = []
startTimeList = []
waitTimeList = []
hiddenList = []
lpList = []
expandBList = []
lastTextList = []
textSent = []
textColor = []
@app.route("/")
def virtualLine():
    if session.get('refresh') != 'refresh':
        session['refresh'] = 'refresh'
    else:
        session['refresh'] = ''
    i = len(expandBList) - 1
    while i < (len(nameList) - 1):
        i = i + 1
        expandBList.append('+')
        hiddenList.append('hidden')
        lpList.append(i)
    if len(lpList) > len(nameList):
        lpList.pop(len(lpList)-1)
    virtualLineUpdate()
    session['last_page'] = 'virtual-line.html'
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return(render_template('index.html',nameList=nameList,expandBList=expandBList,hiddenList=hiddenList,lpList=lpList,textColor=textColor,lastTextList=lastTextList,textSent=textSent,phoneList=phoneList,ageList=ageList,abilityList=abilityList,startTimeList=startTimeList,waitTimeList=waitTimeList,**locals()))

def virtualLineUpdate():
    item = len(nameList)
    while item > 0:
        item = item - 1
        if lastTextList[item] != 'No text sent.':
            if int((time.time() - textSent[item])/60) == 1:
                lastTextList[item] = 'Customer texted ' + str(int((time.time() - textSent[item])/60)) + ' minute ago.'
            else:
                lastTextList[item] = 'Customer texted ' + str(int((time.time() - textSent[item])/60)) + ' minutes ago.'
            if int((time.time() - textSent[item])/60) >= 10:
                textColor[item] = '#ff704d'
            else:
                textColor[item] = '#ffffb3'

        ogTime = startTimeList[item]
        currentTime = time.time()
        elapsed = str(int((currentTime - ogTime) / 60))
        if elapsed == '1':
            message = 'Waiting '+elapsed+' Minute'
        else:
            message = 'Waiting '+elapsed+' Minutes'
        waitTimeList[item] = message

@app.route("/virtual-line/add")
def virtualLineAdd():
    nameList.append(request.args.get('name'))
    phoneList.append(request.args.get('phone'))
    ageList.append(request.args.get('age'))
    abilityList.append(request.args.get('ability'))
    startTimeList.append(time.time())
    waitTimeList.append('0 minutes')
    lastTextList.append('No text sent.')
    textSent.append(-1)
    textColor.append('#ffffff')

    while True:
        #Change to your Twilio account sid
        account_sid = ""
        #Change to your Twilio auth token
        auth_token  = ""
        client = Client(account_sid, auth_token)

        number = request.args.get('phone')
        name = request.args.get('name')

        message = client.messages.create(
            to='+1'+number,
            #Change phone number to your Twilio phone number
            from_='+11111111111',
            #Message sent to client
            body='Hello ' + name + '! You have been added to the Virtual Line! We will text you when it is your turn!')
        number = 'reset'
        break

    virtualLineUpdate()
    session['last_page'] = 'virtual-line.html'
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return(virtualLine())

@app.route("/virtual-line/expand")
def virtualLineExpand():
    lp = int(request.args.get('lp'))
    if expandBList[lp] == '+':
        expandBList[lp] = '-'
        hiddenList[lp] = ''
    else:
        expandBList[lp] = '+'
        hiddenList[lp] = 'hidden'
    phone = phoneList[lp]
    age = ageList[lp]
    startTime = startTimeList[lp]
    waitTime = waitTimeList[lp]
    session['last_page'] = 'virtual-line.html'
    virtualLineUpdate()
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return(virtualLine())

@app.route("/virtual-line/delete")
def virtualLineDelete():
    lp = int(request.args.get('lp'))
    nameList.pop(lp)
    phoneList.pop(lp)
    ageList.pop(lp)
    startTimeList.pop(lp)
    waitTimeList.pop(lp)
    expandBList.pop(lp)
    hiddenList.pop(lp)
    lastTextList.pop(lp)
    textSent.pop(lp)
    textColor.pop(lp)
    virtualLineUpdate()
    session['last_page'] = 'virtual-line.html'
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return(virtualLine())

@app.route("/virtual-line/text")
def virtualLineText():
    while True:
        #Change to your Twilio account sid
        account_sid = ""
        #Change to your Twilio auth token
        auth_token  = ""
        client = Client(account_sid, auth_token)

        lp = int(request.args.get('lp'))

        number = phoneList[lp]
        name = nameList[lp]
        textSent[lp] = time.time()
        lastTextList[lp] = 'Text just sent.'

        message = client.messages.create(
            to='+1'+number,
            #Change to your Twilio phone number
            from_='+11111111111',
            ##Message sent to client
            body='Hello ' + name + '! This is your line alert! It is now your turn! You have 10 minutes to return before your place in line is surrendered.')
        number = 'reset'
        break
    virtualLineUpdate()
    session['last_page'] = 'virtual-line.html'
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return(virtualLine())

@app.route('/login', methods=['POST'])
def do_admin_login():
    session['refresh'] = 'refresh'
    userList = ['user']
    passList = ['111']
    while True:
        try:
            lIndex = userList.index(request.form['username'])
        except ValueError:
            flash('wrong password!')
            break
        if passList[lIndex] == request.form['password']:
            session['logged_in'] = True
            currentUser[0] = request.form['username'][0].upper() + request.form['username'][1:]
            break
        else:
            flash('wrong password!')
            break

    lastPageFunct = virtualLine()
    return(lastPageFunct)

@app.route("/logout")
def logout():
    currentUser[0] = ''
    session['logged_in'] = False
    return(render_template('login.html'))

if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run()
