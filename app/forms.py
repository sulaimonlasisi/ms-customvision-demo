from wtforms.fields import FieldList
from wtforms import StringField, validators, ValidationError, SubmitField, FormField
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

class ImgTagForm(FlaskForm):
	tag = StringField('Tag', [validators.DataRequired(), validators.Length(max=25)])
	img = FileField('Image(s)', validators=[FileRequired(), FileAllowed(ALLOWED_EXTENSIONS, 'Images only!')])

class TagForm(FlaskForm):    
    img_tag = FieldList(FormField(ImgTagForm), min_entries=1)
    project = StringField('Project Name', [validators.DataRequired(), validators.Length(max=25)])
    new_row = SubmitField("More Images")
    submit = SubmitField("Send")


class ImgForm(FlaskForm):
	img = FileField('Image(s)', validators=[FileRequired(), FileAllowed(ALLOWED_EXTENSIONS, 'Images only!')])


class PredictForm(FlaskForm):
	img_field = FieldList(FormField(ImgForm), min_entries=1)
	project = StringField('Project Name', [validators.DataRequired(), validators.Length(max=25)])
	submit = SubmitField("Send")

