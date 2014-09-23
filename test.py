import unittest
import ogeapi
# import tempfile
# import urllib2
# import os


class TestProgrammaticAccess(unittest.TestCase):

    def setUp(self):
        ogeapi.app.config['TESTING'] = True
        self.app = ogeapi.app.test_client()

    def tearDown(self):
        pass

    def test_login_page(self):
        response = self.app.get('/login')
        self.assertTrue(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
