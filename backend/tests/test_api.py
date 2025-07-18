import unittest
import json
from app import app, db, User, Product

class ApiTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        with app.app_context():
            db.create_all()
            admin_user = User(username='admin', password='admin', role='admin')
            db.session.add(admin_user)
            db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_login(self):
        response = self.app.post('/login',
                                 data=json.dumps(dict(username='admin', password='admin')),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('access_token', response.get_json())

    def test_get_products(self):
        response = self.app.get('/products')
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
