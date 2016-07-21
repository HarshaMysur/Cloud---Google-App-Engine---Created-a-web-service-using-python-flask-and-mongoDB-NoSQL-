from flask import Flask,request,render_template,session
from pymongo import MongoClient
from bson import ObjectId
import base64
import os
app = Flask(__name__)
app.secret_key = 'Your Secret key'


def checkcredentials(uname,encrpted):
    client = MongoClient('mongodb://ipaddress:portnumber')
    db = client.chklogin
    id = db.chklogin.find_one({'username': uname, 'password': encrpted})
    return id

def checkusercredentials(uname):
    client = MongoClient('mongodb://ipaddress:portnumber')
    db = client.chklogin
    id = db.chklogin.find_one({'username': uname})
    return id

def insertnewuser(uname,encrpted):
    client = MongoClient('mongodb://ipaddress:portnumber')
    db = client.chklogin
    db.chklogin.insert({'username': uname, 'password': encrpted})
    return

@app.route('/showimages',methods=['POST', 'GET'])
def showimages():
    client = MongoClient('mongodb://ipaddress:portnumber')
    if request.method == 'POST':
        if request.form['submit'] == 'Show':
            uname = request.form['uname']
            if(session['username'] == uname):

                db = client.posts
                rec = db.posts.find({'username':uname})
                return render_template('showimages.html',datas=rec,username=session['username'])
            else:
                db = client.posts
                rec = db.posts.find({'username': uname})
                return render_template('showothersimages.html', datas=rec,username=session['username'])

@app.route('/takeuserinput',methods=['POST', 'GET'])
def takeuserinput():
    client = MongoClient('mongodb://ipaddress:portnumber')
    if request.method == 'POST':
        if request.form['submit'] == 'User Input':
            uname = request.form['uname']
            input1 = request.form['input1']
            input2 = request.form['input2']
            if(session['username'] == uname):

                db = client.posts
                rec = db.posts.find({'username':uname})
                return render_template('showimages.html',datas=rec,username=session['username'])
            else:
                db = client.posts
                rec = db.posts.find({'username': uname})
                return render_template('showothersimages.html', datas=rec,username=session['username'])

@app.route('/upload',methods=['POST', 'GET'])
def upload():
    client = MongoClient('mongodb://ipaddress:portnumber')
    if request.method == 'POST':
        if request.form['submit'] == 'Upload':
            db = client.posts
            count = db.posts.find({'username':session['username']}).count()
            print count
            if (count > 5):
                message = 'No of files Limit exceeded'
                return render_template('login.html', username=session['username'], message=message)
            ufile = request.files['fileToUpload']
            filesize = os.stat(ufile.filename).st_size
            if (filesize > 1000000):
                message = 'File too large to upload'
                return render_template('login.html', username=session['username'],message=message)
            encoded_string = base64.b64encode(ufile.read())
            post = {"image": encoded_string,"username": session['username']}
            post_id = db.posts.insert_one(post).inserted_id
    return render_template('login.html',username=session['username'])

@app.route('/delete/<id>')
def delete(id):
    client = MongoClient('mongodb://ipaddress:portnumber')
    db = client.posts
    db.posts.delete_one({'_id':ObjectId(id)})
    rec = db.posts.find({'username': session['username']})

    return render_template('showimages.html', datas=rec,username=session['username'])

@app.route('/deletecomment/<id>/<username>/<comment>')
def deletecomment(id,username,comment):
    client = MongoClient('mongodb://ipaddress:portnumber')
    db = client.posts
    db.posts.update({'_id':ObjectId(id)},{"$pull":{"commentlist":{"username":username,"comment":comment}}})
    rec = db.posts.find({'username': session['username']})

    return render_template('showimages.html', datas=rec,username=session['username'])

@app.route('/postcomment',methods=['POST', 'GET'])
def postcomment():
    client = MongoClient('mongodb://ipaddress:portnumber')
    imageid = request.form['imageid']
    comment = request.form['mycomment']
    username = session['username']
    db = client.posts
    db.posts.update({"_id":ObjectId(imageid)},{"$push":{"commentlist":{"username":username,"comment":comment}}})

    return render_template('login.html', username=session['username'])

@app.route('/logout',methods=['POST', 'GET'])
def logout():
    return render_template('index.html')


@app.route('/', methods=['POST', 'GET'])
def hello_world():
    if request.method == 'POST':
        if request.form['submit'] == 'Login':

            session['username'] = request.form['username']
            pwd = request.form['password']
            MongoClient('mongodb://ipaddress:portnumber').close()
            #dbconnect()
            #db = client.chklogin
            encrped = base64.b64encode(pwd)
            id = checkcredentials(session['username'],encrped)
            #print id
            if (id == None):
                result = 'Invalid username and password. Please try again.'
                return render_template('index.html', result=result)

            return render_template('login.html', username=session['username'])

    return render_template('index.html')

@app.route('/newuser', methods=['POST', 'GET'])
def newuser():
    if request.method == 'POST':
        if request.form['submit'] == 'Sign up':

            newusername = request.form['username']
            pwd = request.form['password']

            #dbconnect()
            encrped = base64.b64encode(pwd)
            id = checkusercredentials(newusername)
            #print id
            if (id != None):
                result = 'User Name already exists. Please try again.'
                return render_template('index.html', result=result)
            session['username'] = newusername
            insertnewuser(newusername,encrped)
            return render_template('login.html', username=session['username'])

    return render_template('index.html')

if __name__ == '__main__':
    app.run()
