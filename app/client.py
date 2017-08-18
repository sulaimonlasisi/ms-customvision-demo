from custom_vision_client import TrainingClient, TrainingConfig
from custom_vision_client import PredictionClient, PredictionConfig
from app import app
import json
import os
from werkzeug.utils import secure_filename
import pdb
from datetime import datetime

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


with open('./custom_vision_client/cv_secrets.json') as data_file:    
    data = json.load(data_file)


def predict_file(filename, project_name):
	training_client = TrainingClient(TrainingConfig(data["region"], project_name, data["training_key"]))
	project_id = training_client._fetch_project_id()
	prediction_client = PredictionClient(PredictionConfig(data["region"], project_id, data["prediction_key"]))
	predictions = prediction_client.classify_image(filename, training_client._fetch_iteration_id())
	os.remove(filename)
	best_prediction = max(predictions, key=lambda _: _.Probability)
	return best_prediction

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_file(file):
	name = secure_filename(file.filename)
	filename = os.path.join(app.config['UPLOAD_FOLDER'], name)
	file.save(filename)
	return name

def add_and_tag_file(filename, project_name, input_tag_list):
	training_client = TrainingClient(TrainingConfig(data["region"], project_name, data["training_key"]))
	if training_client._fetch_project_id() == '':
		training_client._create_project(project_name)
		proj_tags_list = training_client._check_then_create_tags(input_tag_list)
	return training_client._add_training_image(filename, input_tag_list)

def train_project(project_name):
	training_client = TrainingClient(TrainingConfig(data["region"], project_name, data["training_key"]))
	return training_client.trigger_training()
	

def format_new_iteration(training_response):
	iteration_info = {"Id": training_response.Id, "Name": training_response.Name, "Status": 'Completed', "Created": training_response.Created,
	                   "LastModified": training_response.LastModified, "TrainedAt": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"), "IsDefault": True, 
	                   "ProjectId": training_response.ProjectId }
	return iteration_info;


