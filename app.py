import urllib.request, json
from flask import Flask, jsonify, request, url_for, render_template
from flask_debugtoolbar import DebugToolbarExtension
from keys import SECRET_KEY, NPS_API_KEY
from models import db, connect_db, User, Activity, Topic

app = Flask(__name__)
app.app_context().push()

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///explore_national_parks'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = SECRET_KEY
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)

connect_db(app)

@app.route('/')
def display_homepage():
    """Display home page and make general requests to API to populate database"""

    return render_template('index.html')

@app.route('/activities')
def display_activities():
    """Display list of all activities"""

    # Pull list of activities from database
    activities = Activity.query.all()

    return render_template('activities.html', activities=activities)

@app.route('/topics')
def display_topics():
    """Display list of all topics"""

    # Pull list of topics from database
    topics = Topic.query.all()

    return render_template('topics.html', topics=topics)