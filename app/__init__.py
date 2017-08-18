from flask_wtf.csrf import CSRFProtect
from flask import Flask
UPLOAD_FOLDER = './custom_vision_client'

app = Flask(__name__)
csrf = CSRFProtect(app)
app.config.from_object('config')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
from app import views