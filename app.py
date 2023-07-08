import os
import urllib.request, json
from flask import Flask, flash, jsonify, redirect, render_template, session, g, request, url_for
from flask_debugtoolbar import DebugToolbarExtension
from forms import RegisterForm, SearchByStateForm
from keys import SECRET_KEY, NPS_API_KEY
from models import BASE_URL, connect_db, User, Activity, Topic, Park
from sqlalchemy.exc import IntegrityError

CURR_USER_KEY = "curr_user"

app = Flask(__name__)
app.app_context().push()

app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///explore_national_parks'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = SECRET_KEY
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)

connect_db(app)

#################################################################################
# User methods & routes
#################################################################################

@app.before_request
def add_user_to_g():
    """If user is logged in, add user to Flask global."""
    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])
    else:
        g.user = None

def login_user(user):
    """Log in user."""
    session[CURR_USER_KEY] = user.id

def logout_user():
    """Log out user."""
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

@app.route('/register', methods=['GET', 'POST'])
def register_user():
    form = RegisterForm()

    if form.validate_on_submit():
        # Use form data to register user
        email = form.email.data
        password = form.password.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        try:
            new_user = User.register(email, password, first_name, last_name)            
        except IntegrityError:
            flash("Email already exists in database", 'danger')
            return render_template('register.html', form=form)

        login_user(new_user)
        return redirect(f'/users/{new_user.id}')

    return render_template('register.html', form=form)


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
        # Grab the park_code from the park data
        park_code = obj['parkCode']

        # Find the Park object with the code
        park = Park.query.get(park_code)

        # Add the Park object to the list
        parks.append(park)
    
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