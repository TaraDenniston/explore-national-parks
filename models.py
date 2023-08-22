from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

def connect_db(app):
    db.app = app
    db.init_app(app)


class User(db.Model):
    """Model for a user"""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)

    favorites = db.relationship('Park', secondary='favorites')
    notes = db.relationship('Note')

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
        
    def update_pw(self, new_pw):
        """Update hashed password and return user instance"""

        # Create hashed version of password to store
        pw_hash = bcrypt.generate_password_hash(new_pw).decode('utf8')

        # Update user's password
        user = User.query.get_or_404(self.id)
        user.password = pw_hash
        
        # Commit update to database
        db.session.commit()
        
        return


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


class Favorite(db.Model):
    """Mapping a user to a favorited park"""

    __tablename__ = 'favorites'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    park_id = db.Column(db.String(10), db.ForeignKey('parks.park_code', ondelete='cascade'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'))

    def __repr__(self):
        return f'< Favorite {self.id}: park {self.park_id} for user {self.user_id} >'


class Note(db.Model):
    """Mapping a user to a note for a park"""

    __tablename__ = 'notes'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    park_id = db.Column(db.String(10), db.ForeignKey('parks.park_code', ondelete='cascade'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'))
    text = db.Column(db.Text)

    def __repr__(self):
        return f'< Note {self.id}: park {self.park_id} for user {self.user_id} >'
