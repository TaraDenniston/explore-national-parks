import json
from flask_wtf import FlaskForm
from wtforms import SelectField
from wtforms.validators import InputRequired






# Parse states JSON file into Python dict
with open('static/states.json') as file:
    states = json.load(file)
statesList = [(item['value'], item['text']) for item in states]

class SearchByStateForm(FlaskForm):
    """Form for searching parks by state."""
    state = SelectField('', 
                        choices = [('', '')] + [(item['value'], item['text']) for item in states],
                        validators=[InputRequired()])