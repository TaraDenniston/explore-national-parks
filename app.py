import os
import urllib.request, urllib.parse, json
from flask import Flask, flash, jsonify, make_response, redirect, render_template, \
    session, g, request, url_for
from flask_debugtoolbar import DebugToolbarExtension
from forms import RegisterForm, LoginForm, SearchByStateForm, SearchByActivityForm, \
    SearchByTopicForm
from keys import SECRET_KEY, NPS_API_KEY
from models import BASE_URL, db, connect_db, User, Park, Favorite, Note
from sqlalchemy.exc import IntegrityError

CURR_USER_KEY = "none"

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
# Helper functions
#################################################################################

# Receive data from ajax request and use it to update user's list of favorites
def update_favorite():
    request_data = request.get_json()
    fav_data = json.loads(request_data)

    # Get the data from the request
    fav_park_id = fav_data['park']
    fav_user_id = fav_data['user']
    fav_value = fav_data['favValue']

    # Find the user
    fav_user = User.query.get(fav_user_id)

    # Add or remove the park to/from the user's favorites list
    fav_park = Park.query.get(fav_park_id)

    if fav_value == "true":
        fav_user.favorites.append(fav_park)
    elif fav_value == "false":
        fav_user.favorites.remove(fav_park)

    db.session.add(fav_user)
    db.session.commit()

    return

# Create a list of just the park codes of favorited parks for a user
def create_favorites_list(user_id):
    list = []

    # Make user object
    user = User.query.get(user_id)

    # Pull list of favorite parks from user object
    favorite_parks = user.favorites

    # Add park code to favorites list
    for park in favorite_parks:
        list.append(park.park_code)

    return list

# Create a list of park objects from data returned from the API
def create_parks_list(data):
    list = []

    for obj in data:
        # Grab the park_code from the park data
        park_code = obj['parkCode']

        # Find the Park object with the code
        park = Park.query.get(park_code)

        # Add the Park object to the list
        list.append(park)
    
    return list


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

def login(user):
    """Log in user."""
    session[CURR_USER_KEY] = user.id

def logout():
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

        login(new_user)
        return redirect(f'/profile/{new_user.id}')

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_user():
    form = LoginForm()

    # Redirect if current user is already logged in
    if g.user:
        flash('You are already logged in', 'danger')
        return redirect(f'/profile/{g.user.id}')
        
    # User form data to log user in
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.authenticate(email, password)

        if user:
            login(user)
            flash('You have successfully logged in', 'success')
            return redirect(f'/profile/{user.id}')
        
        flash('The credentials you entered are invalid')
    
    return render_template('login.html', form=form)

@app.route('/logout')
def logout_user():
    # Verify current user is logged in
    if g.user:
        logout()
        flash('You have successfully logged out', 'success')
        return redirect(f'/login')
    
    # If no current user
    flash('You are not logged in', 'danger')
    return redirect(f'/login')

@app.route('/profile/<int:user_id>', methods=["GET", "POST"])
def display_profile(user_id):
    # Redirect if there is no current user
    if not g.user:
        flash('Please log in', 'danger')
        return redirect('/login')
    
    user = User.query.get_or_404(user_id)
    url = url_for('display_profile', user_id=user_id)
    favorites = user.favorites

    if request.method == "POST":
        update_favorite()
        # We don't want the page to refresh when the POST request is made,
        # so we send a status of 204 No Content back to the request
        return ('', 204)
    
    return render_template('profile.html', user=user, url=url, favorites=favorites)


#################################################################################
# Home and search routes
#################################################################################

@app.route('/', methods=["GET", "POST"])
def display_homepage():
    """Display home page"""
    
    #####  Search form for States  #####
    states_form = SearchByStateForm()
    
    # When states form is submitted
    if states_form.validate_on_submit():
        # Get state from form data and redirect to search results
        state = (states_form.state.data)
        return redirect(f'/search/states/{state}')
    
    #####  Search form for Activities  #####
    activities_form = SearchByActivityForm()
    
    # When activities form is submitted
    if activities_form.validate_on_submit():
        # Get activity from form data and redirect to search results
        activity = (activities_form.activity.data)
        return redirect(f'/search/activities/{activity}')
    
    #####  Search form for Topics  #####
    topics_form = SearchByTopicForm()
    
    # When topics form is submitted
    if topics_form.validate_on_submit():
        # Get activity from form data and redirect to search results
        topic = (topics_form.topic.data)
        return redirect(f'/search/topics/{topic}')

    return render_template('index.html', states_form=states_form, activities_form=activities_form, \
                           topics_form=topics_form)

@app.route('/search/states/<state>', methods=["GET", "POST"])
def display_results_states(state):
    """Display search results by state"""

    # Make request to API
    api_url = f'{BASE_URL}/parks?stateCode={state}&api_key={NPS_API_KEY}'
    response = urllib.request.urlopen(api_url)

    res_body = response.read()
    data = json.loads(res_body.decode("utf-8"))

    parks =  create_parks_list(data['data'])
   
    favorites = []
    if g.user:
        favorites = create_favorites_list(g.user.id)

    url = url_for('display_results_states', state=state)

    # If the page sends a POST request regarding favorite status for a park
    if request.method == "POST":
        update_favorite()
        return ('', 204)

    return render_template('results.html', parks=parks, url=url, favorites=favorites)

@app.route('/search/activities/<activity>', methods=["GET", "POST"])
def display_results_activities(activity):
    """Display search results by activity"""
    encoded_activity = urllib.parse.quote(activity)

    # Make request to API
    api_url = f'{BASE_URL}/activities/parks?q={encoded_activity}&api_key={NPS_API_KEY}'
    response = urllib.request.urlopen(api_url)

    res_body = response.read()
    data = json.loads(res_body.decode("utf-8"))

    parks =  create_parks_list(data['data'][0]['parks'])
   
    favorites = []
    if g.user:
        favorites = create_favorites_list(g.user.id)
    
    url = url_for('display_results_activities', activity=activity)

    # If the page sends a POST request regarding favorite status for a park
    if request.method == "POST":
        update_favorite()
        return ('', 204)

    return render_template('results.html', parks=parks, url=url, favorites=favorites)

@app.route('/search/topics/<topic>', methods=["GET", "POST"])
def display_results_topics(topic):
    """Display search results by topic"""
    encoded_topic = urllib.parse.quote(topic)

    # Make request to API
    api_url = f'{BASE_URL}/topics/parks?q={encoded_topic}&api_key={NPS_API_KEY}'
    response = urllib.request.urlopen(api_url)

    res_body = response.read()
    data = json.loads(res_body.decode("utf-8"))

    parks =  create_parks_list(data['data'][0]['parks'])
   
    favorites = []
    if g.user:
        favorites = create_favorites_list(g.user.id)
    
    url = url_for('display_results_topics', topic=topic)

    # If the page sends a POST request regarding favorite status for a park
    if request.method == "POST":
        update_favorite()
        return ('', 204)

    return render_template('results.html', parks=parks, url=url, favorites=favorites)


#################################################################################
# Park routes
#################################################################################

@app.route('/parks/<park_code>')
def display_park_details(park_code):
    """Display all the details of one park, including notes and favorite status
    if the user is logged in"""

    park = Park.query.get_or_404(park_code)

    return render_template('park.html', park=park)
