import urllib.request, json
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from keys import NPS_API_KEY

db = SQLAlchemy()
bcrypt = Bcrypt()

def connect_db(app):
    db.app = app
    db.init_app(app)

BASE_URL = 'https://developer.nps.gov/api/v1'


class User(db.Model):
    """Model for a user"""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)

    favorites = db.relationship('Park', secondary='favorites')

    def __repr__(self):
        return f'< User {self.id}: {self.email}, {self.first_name}, {self.last_name} >'

    @classmethod
    def register(cls, email, pwd, first_name, last_name):
        """Register user with hashed password and return user instance"""

        # Create hashed version of password to store
        pw_hash = bcrypt.generate_password_hash(pwd).decode('utf8')

        # Create user instance
        user = cls(email=email, password=pw_hash, first_name=first_name, last_name=last_name)
        
        # Add user to database
        db.session.add(user)
        db.session.commit()
        
        return user
    
    @classmethod
    def authenticate(cls, email, pwd):
        """Validate that user exists & password is correct
		   Return user if valid; else return False"""

        # Find user
        u = User.query.filter_by(email=email).first()

        # If user exists and pw matches, return user; otherwise return False
        if u and bcrypt.check_password_hash(u.password, pwd):
            return u
        else:
            return False


class Park(db.Model):
    """Model for a park"""

    __tablename__ = 'parks'

    park_code = db.Column(db.String(10), primary_key=True, unique=True)
    full_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.Text, nullable=False)
    image_alt = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'< Park {self.park_code}: {self.full_name} >'
    
    @classmethod
    def populate_table(cls):
        """Request parks data from the NPS API and use it to populate
           the parks table in the database"""
        
        # Delete any records currently in the table
        cls.query.delete()
        
        parks = []

        # Make request to API
        url = f'{BASE_URL}/parks?limit=500&api_key={NPS_API_KEY}'
        response = urllib.request.urlopen(url)

        res_body = response.read()
        data = json.loads(res_body.decode("utf-8"))

        parks_list = data['data']

        # From the data, create new Park objects and append to list
        for item in parks_list:
            if item['images']:
                img_url=item['images'][0]['url']
                img_alt=item['images'][0]['altText']
            else:
                img_url='https://placehold.co/400x300?text=No+Image'
                img_alt='no default image'

            park = Park(park_code=item['parkCode'], full_name=item['fullName'], \
                        description=item['description'], image_url=img_url, image_alt=img_alt)
            parks.append(park)

        # Add list of parks to the db
        db.session.add_all(parks)
        db.session.commit()


class Favorite(db.Model):
    """Mapping a user to a favorited park"""

    __tablename__ = 'favorites'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    park_id = db.Column(db.String(10), db.ForeignKey('parks.park_code', ondelete='cascade'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'))

    def __repr__(self):
        return f'< Favorite {self.id}: park {self.park_id} for user {self.user_id} >'

class Note(db.Model):
    """Mapping a user to a park with a note"""

    __tablename__ = 'notes'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    park_id = db.Column(db.String(10), db.ForeignKey('parks.park_code', ondelete='cascade'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'))
    text = db.Column(db.Text)

    def __repr__(self):
        return f'< Note {self.id}: park {self.park_id} for user {self.user_id} >'


class Activity(db.Model):
    """Model for an activity"""

    __tablename__ = 'activities'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'< Activity {self.id}: {self.name} >'
    
    @classmethod
    def populate_table(cls):
        """Request activities data from the NPS API and use it to populate
           the activities table in the database"""
        
        # Delete any records currently in the table
        cls.query.delete()
        
        activities = []

        # Make request to API
        url = f'{BASE_URL}/activities?api_key={NPS_API_KEY}'
        response = urllib.request.urlopen(url)

        res_body = response.read()
        data = json.loads(res_body.decode("utf-8"))

        activities_list = data['data']

        # From the data, create new activity objects and append to list
        for item in activities_list:
            activity = Activity(name=item['name'])
            activities.append(activity)

        # Add list of activities to the db
        db.session.add_all(activities)
        db.session.commit()

    @classmethod
    def create_json_file(cls):
        """Create JSON file from populated table"""
        activities = Activity.query.all()
        activities_dict = []

        # Create dictionary containing all activity ids and names
        for a in activities:
            activities_dict.append({'text': a.name, 'value': a.id})

        # Write dictionary data to a file in JSON format
        with open('static/activities.json', 'w') as outfile:
            json.dump(activities_dict, outfile)


class Topic(db.Model):
    """Model for a topic"""

    __tablename__ = 'topics'

    id = db.Column(db.String(40), primary_key=True, unique=True)
    name = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'< Topic {self.id}: {self.name} >'
    
    @classmethod
    def populate_table(cls):
        """Request topics data from the NPS API and use it to populate
           the topics table in the database"""
        
        # Delete any records currently in the table
        cls.query.delete()
        
        topics = []

        # Make request to API
        url = f'{BASE_URL}/topics?limit=100&api_key={NPS_API_KEY}'
        response = urllib.request.urlopen(url)

        res_body = response.read()
        data = json.loads(res_body.decode("utf-8"))

        topics_list = data['data']

        # From the data, create new topic objects and append to list
        for item in topics_list:
            topic = Topic(id=item['id'], name=item['name'])
            topics.append(topic)

        # Add list of topics to the db
        db.session.add_all(topics)
        db.session.commit()    
