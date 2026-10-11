import unittest
from app import create_app, db
from app.models import Project

class TestRoutesAndSecurity(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.app.config["WTF_CSRF_ENABLED"] = False
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_dashboard_accessible(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Athar", response.data)

    def test_mock_auth_login(self):
        with self.client.session_transaction() as sess:
            sess["username"] = "TestVolunteer"
            sess["is_member"] = True

        response = self.client.get("/project/new")
        self.assertEqual(response.status_code, 200)

if __name__ == "__main__":
    unittest.main()
