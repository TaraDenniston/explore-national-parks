import os
import urllib.request, urllib.parse, json
from flask import Flask, flash, redirect, render_template, \
    session, g, request, url_for
from forms import RegisterForm, LoginForm, SearchByStateForm, SearchByActivityForm, \
    SearchByTopicForm, EditUserForm, EditPasswordForm, EditNotesForm
from models import BASE_URL, NPS_API_KEY, db, connect_db, User, Park, Note
from sqlalchemy.exc import IntegrityError

# Uncomment/comment for development only
# from keys import SECRET_KEY, NPS_API_KEY
SECRET_KEY = '0f,%|6MAf8|@:Tq'

CURR_USER_KEY = "none"

app = Flask(__name__)
app.app_context().push()

app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///explore_national_parks'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', SECRET_KEY)

connect_db(app)

#################################################################################
# Helper functions
#################################################################################

def update_favorite():
    """Receive data from ajax request and use it to update user's list of favorites"""
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

def create_favorites_list(user_id):
    """Create a list of just the park codes of favorited parks for a user"""
    list = []

    # Make user object
    user = User.query.get(user_id)

    # Pull list of favorite parks from user object
    favorite_parks = user.favorites

    # Add park code to favorites list
    for park in favorite_parks:
        list.append(park.park_code)

    return list

def create_notes_list(user_id):
    """Create a list of just the park codes of notes for a user"""
    list = []

    # Make user object
    user = User.query.get(user_id)

    # Pull list of notes from user object
    notes = user.notes

    # Add park code to favorites list
    for note in notes:
        list.append(note.park_id)

    return list

def get_note_text(park_code):
    """Return text of note for a park"""
    if g.user:
        # Get list of user's notes
        notes = create_notes_list(g.user.id)

        # If the user has a note for the park, return the text
        if park_code in notes:
            note = Note.query.filter_by(park_id=park_code).first()
            return note.text
        # Otherwise return an empty string
        else:
            return ''
    else:
        return ''

def create_parks_list(data):
    """Create a list of park objects from data returned from the API"""
    list = []

    for obj in data:
        # Grab the park_code from the park data
        park_code = obj['parkCode']

        # Find the Park object with the code
        park = Park.query.get(park_code)

        # Add the Park object to the list
        list.append(park)
    
    return list

def lookup_state(state_code):
    """Use 2-digit state code to get full state name"""

    # Turn JSON file into list of Python dictionaries
    with open('static/json/states.json') as file:
        states_data = json.load(file)
    
    # Find dictionary containing our state code
    state_dict = next(item for item in states_data if item['value'] == state_code)

    # Return name of state
    return state_dict['text']


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
        
        flash('The credentials you entered are invalid', 'danger')
    
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

    favorite_codes = create_favorites_list(g.user.id)

    if request.method == "POST":
        update_favorite()
        # We don't want the page to refresh when the POST request is made,
        # so we send a status of 204 No Content back to the request
        return ('', 204)
    
    return render_template('profile.html', user=user, url=url, favorites=favorites, \
                           favorite_codes=favorite_codes)

@app.route('/edit-user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    # Redirect if there is no current user
    if not g.user:
        flash('Please log in', 'danger')
        return redirect('/login')
    
    user = User.query.get_or_404(user_id)
    form = EditUserForm()

    if request.method == "POST":
        if form.validate_on_submit():
            # Use form data to update user
            email = form.email.data
            first_name = form.first_name.data
            last_name = form.last_name.data

            user.email = email
            user.first_name = first_name
            user.last_name = last_name

            db.session.commit()

            flash('User details updated successfully', 'success')
            return redirect(f'/profile/{user_id}')
    
    form.email.data = user.email
    form.first_name.data = user.first_name
    form.last_name.data = user.last_name

    return render_template('edit-user.html', form=form)

@app.route('/edit-password/<int:user_id>', methods=['GET', 'POST'])
def edit_password(user_id):
    # Redirect if there is no current user
    if not g.user:
        flash('Please log in', 'danger')
        return redirect('/login')
    
    user = User.query.get_or_404(user_id)
    form = EditPasswordForm()

    if form.validate_on_submit():
        # Get data from form        
        curr_pw = form.curr_pw.data
        new_pw_1 = form.new_pw_1.data
        new_pw_2 = form.new_pw_2.data

        # Make sure current password matches data submitted
        if user.authenticate(user.email, curr_pw):
            # Make sure new passwords are identical
            if new_pw_1 == new_pw_2:
                # change stored password and display success message
                user.update_pw(new_pw_1)
                flash('Password updated successfully', 'success')
                return redirect(f'/profile/{user_id}')
            else:
                # If new passwords don't match, show error message
                flash("New passwords don't match", 'danger')
                return redirect(f'/edit-password/{user_id}')
        else:
            # If data for current password is incorrect, show message
            flash('Password is incorrect', 'danger')
            return redirect(f'/edit-password/{user_id}')

    return render_template('edit-password.html', form=form)


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

    return render_template('index.html', states_form=states_form, topics_form=topics_form, \
                           activities_form=activities_form)

@app.route('/search/states/<state>', methods=["GET", "POST"])
def display_results_states(state):
    """Display search results by state"""

    # Make request to API
    api_url = f'{BASE_URL}/parks?stateCode={state}&api_key={NPS_API_KEY}'
    response = urllib.request.urlopen(api_url)

    res_body = response.read()
    data = json.loads(res_body.decode("utf-8"))

    parks =  create_parks_list(data['data'])
    name = lookup_state(state)
   
    favorite_codes = []
    if g.user:
        favorite_codes = create_favorites_list(g.user.id)

    url = url_for('display_results_states', state=state)

    # If the page sends a POST request regarding favorite status for a park
    if request.method == "POST":
        update_favorite()
        return ('', 204)

    return render_template('results.html', parks=parks, name=name, url=url, \
                           favorite_codes=favorite_codes)

@app.route('/search/activities/<activity_id>', methods=["GET", "POST"])
def display_results_activities(activity_id):
    """Display search results by activity"""

    # Make request to API
    api_url = f'{BASE_URL}/activities/parks?id={activity_id}&api_key={NPS_API_KEY}'
    response = urllib.request.urlopen(api_url)

    res_body = response.read()
    data = json.loads(res_body.decode("utf-8"))

    parks =  create_parks_list(data['data'][0]['parks'])
    name = data['data'][0]['name']
   
    favorite_codes = []
    if g.user:
        favorite_codes = create_favorites_list(g.user.id)
    
    url = url_for('display_results_activities', activity_id=activity_id)

    # If the page sends a POST request regarding favorite status for a park
    if request.method == "POST":
        update_favorite()
        return ('', 204)

    return render_template('results.html', parks=parks, name=name, url=url, \
                           favorite_codes=favorite_codes)

@app.route('/search/topics/<topic_id>', methods=["GET", "POST"])
def display_results_topics(topic_id):
    """Display search results by topic"""

    # Make request to API
    api_url = f'{BASE_URL}/topics/parks?id={topic_id}&api_key={NPS_API_KEY}'
    response = urllib.request.urlopen(api_url)

    res_body = response.read()
    data = json.loads(res_body.decode("utf-8"))

    parks =  create_parks_list(data['data'][0]['parks'])
    name = data['data'][0]['name']
   
    favorite_codes = []
    if g.user:
        favorite_codes = create_favorites_list(g.user.id)
    
    url = url_for('display_results_topics', topic_id=topic_id)

    # If the page sends a POST request regarding favorite status for a park
    if request.method == "POST":
        update_favorite()
        return ('', 204)

    return render_template('results.html', parks=parks, name=name, url=url, \
                           favorite_codes=favorite_codes)


#################################################################################
# Park routes
#################################################################################

@app.route('/parks/<park_code>', methods=["GET", "POST"])
def display_park_details(park_code):
    """Display all the details of one park, including notes and favorite status
    if the user is logged in"""

    park = Park.query.get_or_404(park_code)
    park_data = park.get_park_details()

    # Get list of states related to the park
    states_list = park_data['states']
    state_codes = states_list.split(',')
    states = []
    for code in state_codes:
        states.append(lookup_state(code))
    states_str = states[0]
    if len(states) > 1:
        for item in states[1:]:
            states_str += ', ' + item

    # Get list of activities related to the park
    activities_list = park_data['activities']
    activities = []
    for item in activities_list:
        activities.append(item['name'])
    activities_str = activities[0]
    if len(activities) > 1:
        for item in activities[1:]:
            activities_str += ', ' + item

    # Get list of topics related to the park
    topics_list = park_data['topics']
    topics = []
    for item in topics_list:
        topics.append(item['name'])
    topics_str = topics[0]
    if len(topics) > 1:
        for item in topics[1:]:
            topics_str += ', ' + item

    # Get url of official park website
    park_url = park_data['url']

    # Get the note text (empty string if it doesn't exist)
    note = get_note_text(park_code)

    # Get data for images
    images = park_data['images']

    # Get list of park_codes from favorite parks
    favorite_codes = []
    if g.user:
        favorite_codes = create_favorites_list(g.user.id)
    
    url = url_for('display_park_details', park_code=park_code)

    # If the page sends a POST request regarding favorite status for a park
    if request.method == "POST":
        update_favorite()
        return ('', 204)    

    return render_template('parks.html', park=park, park_url=park_url, states=states_str, \
                           activities=activities_str, topics=topics_str, note=note, \
                           images=images, favorite_codes=favorite_codes, url=url)

@app.route('/parks/<park_code>/edit-notes', methods=['GET', 'POST'])
def edit_notes(park_code):
    # Redirect if there is no current user
    if not g.user:
        flash('Please log in to add or edit notes', 'danger')
        return redirect(f'/parks/{park_code}')
    
    user = User.query.get_or_404(g.user.id)
    form = EditNotesForm()

    if request.method == "POST":
        if form.validate_on_submit():
            # Use form data to update notes
            text = form.text.data

            existing_note = Note.query.filter(Note.park_id==park_code) \
                .filter(Note.user_id==user.id).scalar()
            # If there is already a notes record for this park, update it
            if existing_note:
                existing_note.text = text

                db.session.commit()

                flash('Notes updated successfully', 'success')
                return redirect(f'/parks/{park_code}')

            # Otherwise, create a new record
            else:
                note = Note(park_id=park_code, user_id=user.id, text=text)

                db.session.add(note)
                db.session.commit()

                flash('Notes updated successfully', 'success')
                return redirect(f'/parks/{park_code}')
    
    form.text.data = get_note_text(park_code)
    park=Park.query.get_or_404(park_code)

    return render_template('edit-notes.html', form=form, park_name=park.full_name)