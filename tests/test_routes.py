import unittest
from flask_login import login_user
from app import create_app, db
from app.models import User

class TestRoutes(unittest.TestCase):
    def setUp(self):
        # Create a test configuration
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Create a test user
        self.test_user = User(
            email='test@example.com',
            address='Test Address',
            company='Test Company',
            interested_companies=['Company1', 'Company2']
        )
        db.session.add(self.test_user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_index_route(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_profile_get_unauthorized(self):
        response = self.client.get('/profile')
        self.assertEqual(response.status_code, 401)  # or 302 if redirecting to login

    def test_profile_post(self):
        with self.client:
            # Login the test user
            login_user(self.test_user)
            
            # Test updating profile
            data = {
                'address': 'New Address',
                'company': 'New Company',
                'interested_companies': ['Company3', 'Company4']
            }
            response = self.client.post('/profile', 
                                      json=data,
                                      content_type='application/json')
            
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json['status'], 'success')
            
            # Verify database updates
            updated_user = User.query.filter_by(email='test@example.com').first()
            self.assertEqual(updated_user.address, 'New Address')
            self.assertEqual(updated_user.company, 'New Company')
            self.assertEqual(updated_user.interested_companies, ['Company3', 'Company4'])

    def test_user_preferences_get(self):
        with self.client:
            login_user(self.test_user)
            response = self.client.get('/user/preferences')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json['interested_companies'], 
                           self.test_user.interested_companies)

    def test_user_preferences_put(self):
        with self.client:
            login_user(self.test_user)
            
            data = {
                'interested_companies': ['NewCompany1', 'NewCompany2']
            }
            response = self.client.put('/user/preferences',
                                     json=data,
                                     content_type='application/json')
            
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json['status'], 'success')
            
            # Verify database updates
            updated_user = User.query.filter_by(email='test@example.com').first()
            self.assertEqual(updated_user.interested_companies, 
                           ['NewCompany1', 'NewCompany2'])

    def test_error_handling(self):
        with self.client:
            login_user(self.test_user)
            
            # Test with invalid data
            response = self.client.post('/profile',
                                      json={},
                                      content_type='application/json')
            
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json['status'], 'error')

if __name__ == '__main__':
    unittest.main() 