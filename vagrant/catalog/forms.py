from flask_wtf import Form
from wtforms import StringField
from wtforms.validators import DataRequired
from wtforms.widgets import TextArea


class FormCategory(Form):
    name = StringField('name', validators=[DataRequired()])
    image_loc = StringField('image_loc', validators=[DataRequired()])


class FormItem(Form):
    name = StringField('name', validators=[DataRequired()])
    description = StringField('description', validators=[DataRequired()],
                              widget=TextArea())
    image_loc = StringField('image_loc', validators=[DataRequired()])
