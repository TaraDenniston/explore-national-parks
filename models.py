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

    username = db.Column(db.String(20), primary_key=True, unique=True)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)

    def __repr__(self):
        return f'< User {self.username}: {self.first_name} {self.last_name}, {self.email} >'

    @classmethod
    def register(cls, username, pwd, email, first_name, last_name):
        """Register user with hashed password and return user instance"""

        # Create hashed version of password to store
        pw_hash = bcrypt.generate_password_hash(pwd).decode('utf8')

        # Create user instance
        user = cls(username=username, password=pw_hash, email=email, \
                   first_name=first_name, last_name=last_name)
        
        # Add user to database
        db.session.add(user)
        db.session.commit()
        
        return user
    
    @classmethod
    def authenticate(cls, username, pwd):
        """Validate that user exists & password is correct
		   Return user if valid; else return False"""

        # Find user
        u = User.query.filter_by(username=username).first()

        # If user exists and pw matches, return user; otherwise return False
        if u and bcrypt.check_password_hash(u.password, pwd):
            return u
        else:
            return False
        

class Activity(db.Model):
    """Model for an activity"""

    __tablename__ = 'activities'

    id = db.Column(db.String(40), primary_key=True, unique=True)
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
            activity = Activity(id=item['id'], name=item['name'])
            activities.append(activity)

        # Add list of activities to the db
        db.session.add_all(activities)
        db.session.commit()


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
    
