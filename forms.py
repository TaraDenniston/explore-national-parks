import json
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, SelectField, TextAreaField
from wtforms.validators import InputRequired, Length


class RegisterForm(FlaskForm):
    email = EmailField('Email', validators=[InputRequired(), Length(max=50)])
    password = PasswordField('Password', validators=[InputRequired()])
    first_name = StringField('First Name', validators=[InputRequired(), Length(max=30)])
    last_name = StringField('First Name', validators=[InputRequired(), Length(max=30)])

# Parse states JSON file into Python dict
with open('static/states.json') as file:
    states = json.load(file)
statesList = [(item['value'], item['text']) for item in states]

class SearchByStateForm(FlaskForm):
    """Form for searching parks by state."""
    state = SelectField('', 
                        choices = [('', '')] + [(item['value'], item['text']) for item in states],
                        validators=[InputRequired()])