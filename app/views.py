from flask import url_for, render_template, request, redirect, flash
from app import app
from app.forms import TagForm, PredictForm
from app.client import predict_file, allowed_file, save_file, add_and_tag_file, train_project
import os
import pdb




@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/predict', methods=['GET', 'POST'])
def predict():
    form = PredictForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            key_array = []
            prediction_array = []
            for key in request.files.keys():
                key_array.append(key)
            images = request.files.getlist(key_array[0])
            for img in images:
                filename = os.path.join(app.config['UPLOAD_FOLDER'], save_file(img))
                filename_array = filename.split('\\')
                name = filename_array[len(filename_array)-1].split('.')[0].split('_')[0]
                prediction_object = {'name': name, 'prediction': predict_file(filename, form.project.data)}
                prediction_array.append(prediction_object)
            return render_template('predictions.html', prediction = prediction_array)
    return render_template('predict.html', title = 'Predict', form = form)

@app.route('/tag', methods=['GET', 'POST'])
def tag():
    if request.method == 'POST':
        form = TagForm()
        if form.new_row.data:
            form.img_tag.append_entry()
        elif form.submit.data:
            if form.validate_on_submit():
                key_array = []
                for key in request.files.keys():
                    key_array.append(key)
                for idx in range(0,len(request.files)):
                    tags = form.img_tag.data[idx]['tag'].split(",")
                    images = request.files.getlist(key_array[idx])
                    for img in images:
                        filename = save_file(img)
                        add_and_tag_file(filename, form.project.data, tags)
                        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))                
                iteration_info = train_project(form.project.data)
                flash('Files uploaded')
                return render_template('train_result.html', info = iteration_info)
            flash('No files were uploaded')
        return render_template('tag.html', form=form)
    form = TagForm()
    return render_template('tag.html', form=form)