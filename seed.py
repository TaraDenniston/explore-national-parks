from models import db, User, Park, Favorite
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
    email='testuser@email.com',
    password='$2b$12$DJJLHT5BPWf5eIh4ryHIcOhOeb5.HZxGIJDI7wQsNrGPU6EVapD6u',   
    first_name='Test',
    last_name='User'
)

db.session.add_all([u1])
db.session.commit()


# Create data for favorites table
u1f1 = Favorite(
    park_id = 'arch',
    user_id = 1
)

db.session.add_all([u1f1])
db.session.commit()