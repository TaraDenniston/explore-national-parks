import os
import urllib.request, json
from flask import Flask, flash, jsonify, make_response, redirect, render_template, \
    session, g, request, url_for
from flask_debugtoolbar import DebugToolbarExtension
from forms import RegisterForm, LoginForm, SearchByStateForm
from keys import SECRET_KEY, NPS_API_KEY
from models import BASE_URL, db, connect_db, User, Activity, Topic, Park, Favorite, Note
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

@app.route('/profile/<int:user_id>')
def display_profile(user_id):
    # Redirect if there is no current user
    if not g.user:
        flash('Please log in', 'danger')
        return redirect('/login')
    
    user = User.query.get_or_404(user_id)

    # # Get list of user's favorite parks
    # favorites = (UserPark
    #             .query
    #             .filter(UserPark.user_id == user_id, UserPark.is_favorite == True)
    #             .all())
    
    # favorite_parks = []
    # for item in favorites:
    #     favorite_parks.append(Park.query.get(item.park_id))

    return render_template('profile.html', user=user)


#################################################################################
# Home and search routes
#################################################################################

def jsonify_no_content():
    response = make_response('', 204)
    response.mimetype = app.config['JSONIFY_MIMETYPE']
 
    return response

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

@app.route('/search/states/<state>', methods=["GET", "POST"])
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

    favorites = []
    if g.user:
        # Make user object
        user = User.query.get(g.user.id)

        # Pull list of favorite parks from user object
        favorite_parks = user.favorites

        # Add park code to favorites list
        for park in favorite_parks:
            favorites.append(park.park_code)

    url = url_for('display_results_states', state=state)


    # If the page sends a POST request regarding favorite status for a park
    if request.method == "POST":
        # request_data = request.form
        # print(request_data)

        # # Get the data from the request
        # fav_park_id = request.form.get('park')
        # print(fav_park_id)
        # fav_user_id = request.form.get('user')
        # print(fav_user_id)
        # fav_value = request.form.get('favValue')
        # print(fav_value)

        request_data = request.get_json()
        print(request_data)
        new_data = json.loads(request_data)
        print(new_data)

        # Get the data from the request
        fav_park_id = new_data['park']
        print(fav_park_id)
        fav_user_id = new_data['user']
        print(fav_user_id)
        fav_value = new_data['favValue']
        print(fav_value)

        # Find the user
        fav_user = User.query.get(fav_user_id)

        # Add or remove the park to/from the user's favorites list
        fav_park = Park.query.get(fav_park_id)

        if fav_value:
            fav_user.favorites.append(fav_park)
        else:
            fav_user.favorites.remove(fav_park)

        db.session.add(fav_user)
        db.session.commit()

        # We don't want the page to refresh when the POST request is made,
        # so we send a status of 204 No Content back to the request
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