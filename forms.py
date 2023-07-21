import json
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, SelectField, TextAreaField
from wtforms.validators import InputRequired, Length

# Parse JSON files into Python dictionaries
with open('static/states.json') as file:
    states = json.load(file)
# statesList = [(item['value'], item['text']) for item in states]

with open('static/activities.json') as file:
    activities = json.load(file)


class RegisterForm(FlaskForm):
    """Form for registering a new user"""
    email = EmailField('Email', validators=[InputRequired(), Length(max=50)])
    password = PasswordField('Password', validators=[InputRequired()])
    first_name = StringField('First Name', validators=[InputRequired(), Length(max=30)])
    last_name = StringField('First Name', validators=[InputRequired(), Length(max=30)])

class LoginForm(FlaskForm):
    """Form for logging a user in"""
    email = EmailField('Email', validators=[InputRequired(), Length(max=50)])
    password = PasswordField('Password', validators=[InputRequired()])

class SearchByStateForm(FlaskForm):
    """Form for searching parks by state."""
    state = SelectField('', 
                        choices = [('', '')] + [(item['value'], item['text']) for item in states],
                        validators=[InputRequired()])
    
class SearchByActivityForm(FlaskForm):
    """Form for searching parks by activity."""
    activity = SelectField('', 
                           choices = [('', '')] + [(item['value'], item['text']) for item in activities],
                           validators=[InputRequired()])