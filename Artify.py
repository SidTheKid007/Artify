from flask import Flask, render_template, request, session
from flask_session import Session
from PIL import Image
from werkzeug.utils import secure_filename
from flask_socketio import SocketIO
import os
import shutil
import uuid
from glob import glob
import cloudinary as Cloud
import random


app = Flask(__name__)
SESSION_TYPE = 'filesystem'
app.config.from_object(__name__)
Session(app)
socketio = SocketIO(app)

images_directory = 'static/images'

Cloud.config.update = ({
    'cloud_name':os.environ.get('CLOUDINARY_CLOUD_NAME'),
    'api_key': os.environ.get('CLOUDINARY_API_KEY'),
    'api_secret': os.environ.get('CLOUDINARY_API_SECRET')
})

@app.route('/')
def loadHome():
    deleteImages()
    # check session and delete if something there
    return render_template('home-form.html')


@app.route('/example')
def loadExample():
    deleteImages()
    # check session and delete if something there
    mainPic = '/static/images/example/bear.JPG'
    return render_template('index.html', mainPic=mainPic)


@app.route('/', methods=['POST'])
def loadIndex():
    upload = request.files['mainpic']
    filename = upload.filename
    filename = secure_filename(filename)
    ext = os.path.splitext(filename)[1][1:].strip().lower()
    session['ext'] = ext
    if ext in set(['jpg', 'jpeg', 'png']):
        saveImage(upload, ext)
    else:
        return render_template('error-page.html')
    mainPic = loadImage('default')
    return render_template('index.html', mainPic=mainPic)


def saveImage(upload, ext):
    # change this to use the cloudiary api to be async and not cluttered
    deleteImages()
    session['imgPath'] = str(uuid.uuid1())
    newFolder = images_directory + '/' + session['imgPath']
    if not os.path.isdir(newFolder):
        os.mkdir(newFolder)
    destination = newFolder + '/default.' + ext
    upload.save(destination)
    return 'success'


def deleteImages():
    if session.get('imgPath'):
        oldFolder = 'static/images/' + session['imgPath']
        if os.path.isdir(oldFolder):
            print(oldFolder)
            shutil.rmtree(oldFolder)
    return 'success'


def loadImage(type):
    imageFolder = '/static/images/' + session['imgPath']
    img = ''
    if (type == 'default'):
        img = imageFolder + '/default.' + session['ext']
    return img


@socketio.on('disconnect')
def disconnect_user():
    flask.ext.login.logout_user()
    deleteImages()
    session.clear()



