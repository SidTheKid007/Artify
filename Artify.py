from flask import Flask, render_template, request, session
from flask_session import Session
from PIL import Image, ImageFilter
from werkzeug.utils import secure_filename
from flask_socketio import SocketIO
import os
import shutil
import uuid
import cloudinary as Cloud


app = Flask(__name__)
SESSION_TYPE = 'filesystem'
app.config.from_object(__name__)
Session(app)
socketio = SocketIO(app)

images_directory = 'static/images'

#Cloud.config.update = ({
#    'cloud_name':os.environ.get('CLOUDINARY_CLOUD_NAME'),
#    'api_key': os.environ.get('CLOUDINARY_API_KEY'),
#    'api_secret': os.environ.get('CLOUDINARY_API_SECRET')
#})

@app.route('/')
def loadHome():
    deleteImages()
    return render_template('home-form.html')


@app.route('/example')
def loadExample():
    deleteImages()
    session['example'] = True
    session['ext'] = 'JPG'
    mainPic = '/static/images/example/default.JPG'
    return render_template('index.html', mainPic=mainPic)


@app.route('/', methods=['POST'])
def loadIndex():
    session['example'] = False
    upload = request.files['mainpic']
    filename = upload.filename
    filename = secure_filename(filename)
    ext = os.path.splitext(filename)[1][1:].strip().lower()
    session['ext'] = ext
    if ext in set(['jpg', 'jpeg', 'png']):
        saveImage(upload, ext)
    else:
        return render_template('error-page.html')
    preloadImages()
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
            shutil.rmtree(oldFolder)
    return 'success'


def preloadImages():
    imageFolder = 'static/images/' + session['imgPath']
    defaultFile = imageFolder + '/default.' + session['ext']
    default = Image.open(defaultFile)
    loadSid(default, imageFolder)
    loadShark(default, imageFolder)
    loadShawn(default, imageFolder)
    loadSram(default, imageFolder)
    # refactor later with name as an argument?
    return 'success'


def loadSid(default, imageFolder):
    sidPic = default.filter(ImageFilter.MaxFilter(size=5))
    sidPic.save(imageFolder + '/Sid.' + session['ext'])
    return 'success'


def loadShark(default, imageFolder):
    sharkPic = default.filter(ImageFilter.EDGE_ENHANCE_MORE)
    sharkPic.save(imageFolder + '/Shark.' + session['ext'])
    return 'success'


def loadShawn(default, imageFolder):
    shawnPic = default.filter(ImageFilter.ModeFilter(size=15))
    shawnPic.save(imageFolder + '/Shawn.' + session['ext'])
    return 'success'


def loadSram(default, imageFolder):
    sramPic = default.filter(ImageFilter.MinFilter(size=5))
    sramPic.save(imageFolder + '/Sram.' + session['ext'])
    return 'success'


def loadImage(filter):
    if session['example']:
        imageFolder = '/static/images/example'
    else:
        imageFolder = '/static/images/' + session['imgPath']
    img = imageFolder + '/' + filter + '.' + session['ext']
    return img


@app.route('/changeImage', methods=['GET', 'POST'])
def changeImg():
    filter = request.args['filter']
    img = loadImage(filter)
    return img

# wrap everything in try catches later

@socketio.on('disconnect')
def disconnect_user():
    flask.ext.login.logout_user()
    deleteImages()
    session.clear()



