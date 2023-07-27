import json
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, SelectField, TextAreaField
from wtforms.validators import InputRequired, Length

# Parse JSON files into Python dictionaries
with open('static/json/states.json') as file:
    states = json.load(file)
with open('static/json/activities.json') as file:
    activities_data = json.load(file)
activities = activities_data['data']
with open('static/json/topics.json') as file:
    topics_data = json.load(file)
topics = topics_data['data']


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
    """Form for searching parks by state"""
    state = SelectField('', 
                        choices = [('', '')] + [(item['value'], item['text']) for item in states],
                        validators=[InputRequired()])
    
class SearchByActivityForm(FlaskForm):
    """Form for searching parks by activity"""
    activity = SelectField('', 
                           choices = [('', '')] + [(item['id'], item['name']) for item in activities],
                           validators=[InputRequired()])
    
class SearchByTopicForm(FlaskForm):
    """Form for searching parks by topic"""
    topic = SelectField('', 
                           choices = [('', '')] + [(item['id'], item['name']) for item in topics],
                           validators=[InputRequired()])