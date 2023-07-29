from models import db, User, Park, Note
from json_files import create_activities_json_file, create_topics_json_file
from app import app

# Create (or recreate) tables
db.drop_all()
db.create_all()

# Create JSON file for activities 
create_activities_json_file()

# Create JSON file for activities 
create_topics_json_file()

# Populate parks table
Park.populate_table()


# Create data for users table
u1 = User(
    email='testuser1@email.com',
    password='$2b$12$iFRR4FQYqSrCOiJ0ZDhoyOcOL4aPWYCktYRY2KKO6iKK5TFZ4tpPm',   
    first_name='Test1',
    last_name='User1'
)

u2 = User(
    email='testuser2@email.com',
    password='$2b$12$KgdKBO/UDaPaXM9b23ri9.FiwqY2rOZA6HKEg2NbnLAd6Zl4E68pq',   
    first_name='Test2',
    last_name='User2'
)

db.session.add_all([u1, u2])
db.session.commit()


# Create data for favorites table
u1 = User.query.filter_by(email='testuser1@email.com').first()

u1.favorites.append(Park.query.get('arch'))
u1.favorites.append(Park.query.get('yose'))
u1.favorites.append(Park.query.get('zion'))

u2 = User.query.filter_by(email='testuser2@email.com').first()

u2.favorites.append(Park.query.get('acad'))
u2.favorites.append(Park.query.get('blue'))
u2.favorites.append(Park.query.get('caco'))

db.session.commit()


# Create data for notes table
n1 = Note(
    park_id = 'arch',
    user_id = u1.id,
    text = 'Been there, done that.'
)

n2 = Note(
    park_id = 'blue',
    user_id = u2.id,
    text = 'I like to fish.'
)

db.session.add_all([n1, n2])
db.session.commit()