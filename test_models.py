import os
from unittest import TestCase
from models import db, User, Favorite, Note, Park

os.environ['DATABASE_URL'] = "postgresql:///explore-np-test"

from app import app

db.create_all()


class ModelTestCase(TestCase):
    def setUp(self):
        """Create test client, clean up tables."""

        # Delete any existing data in tables
        User.query.delete()
        Favorite.query.delete()
        Note.query.delete()
        Park.query.delete()

        self.client=app.test_client()

        # Create sample data
        p = Park(
            park_code='smpl',
            full_name='Sample Park',
            description='Sample description of a park.',
            image_url='https://placehold.co/400x300?text=No+Image',
            image_alt='sample image'
        )
        u = User(
            email='testuser1@email.com',
            password='$2b$12$iFRR4FQYqSrCOiJ0ZDhoyOcOL4aPWYCktYRY2KKO6iKK5TFZ4tpPm',   
            first_name='Test1',
            last_name='User1'
        )

        db.session.add_all([p, u])
        db.session.commit()
    
    def test_user_model(self):
        """Test creating user"""

        u2 = User(
            email='testuser2@email.com',
            password='$2b$12$KgdKBO/UDaPaXM9b23ri9.FiwqY2rOZA6HKEg2NbnLAd6Zl4E68pq',   
            first_name='Test2',
            last_name='User2'
        )

        db.session.add(u2)
        db.session.commit()

        # Assert that there are now 2 records in the database
        self.assertEqual(User.query.count(), 2)

    def test_add_favorite(self):
        """Test adding a favorite park for a user"""

        # Get database objects
        u = User.query.filter_by(email='testuser1@email.com').first()
        p = Park.query.get('smpl')

        # First check to make sure user doesn't currently have any favorites
        self.assertEqual(len(u.favorites), 0)

        # Add favorite
        u.favorites.append(p)

        # Now user should have 1 favorite
        self.assertEqual(len(u.favorites), 1)

    def test_add_note(self):
        """Test adding a note to a park"""

        # Get user
        u = User.query.filter_by(email='testuser1@email.com').first()

        # Add note
        n = Note(park_id='smpl', user_id=u.id, text='Sample note')
        db.session.add(n)
        db.session.commit()

        # Now database should have 1 record for notes table
        self.assertEqual(Note.query.count(), 1)
        



