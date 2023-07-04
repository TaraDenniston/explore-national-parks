import urllib.request, json
from flask import Flask, jsonify, redirect, render_template, request, url_for
from flask_debugtoolbar import DebugToolbarExtension
from forms import SearchByStateForm
from keys import SECRET_KEY, NPS_API_KEY
from models import BASE_URL, connect_db, User, Activity, Topic
from park import Park

app = Flask(__name__)
app.app_context().push()

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///explore_national_parks'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = SECRET_KEY
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)

connect_db(app)

@app.route('/', methods=["GET", "POST"])
def display_homepage():
    """Display home page and make general requests to API to populate database"""
    
    ### Search form for States ###
    statesForm = SearchByStateForm()
    
    # When states form is submitted
    if statesForm.validate_on_submit():
        # Get state from form data and redirect to search results
        state = (statesForm.state.data)
        return redirect(f'/search/states/{state}')

    return render_template('index.html', statesForm=statesForm)

@app.route('/search/states/<state>')
def display_results_states(state):
    """Display search results by state"""

    # Make request to API
    url = f'{BASE_URL}/parks?stateCode={state}&api_key={NPS_API_KEY}'
    response = urllib.request.urlopen(url)

    res_body = response.read()
    data = json.loads(res_body.decode("utf-8"))

    parks = []
    for obj in data['data']:
        parks.append(Park(obj))
    
    return render_template('results.html', parks=parks)

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