from models import db, User, Activity, Topic
from app import app

# Create (or recreate) tables
db.drop_all()
db.create_all()

# Populate activities table
Activity.populate_table()

# Populate topics table
Topic.populate_table()

# Populate states table

# Create data for users table