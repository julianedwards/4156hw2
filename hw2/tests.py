# !/usr/bin/env python
import os
import hw2
import unittest
import tempfile


class hw2UnitTests(unittest.TestCase):

    def setUp(self):
        self.db_fd, hw2.app.config['DATABASE'] = tempfile.mkstemp()
        hw2.app.config['TESTING'] = True
        self.app = hw2.app.test_client()
        with hw2.app.app_context():
            hw2.initDB()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(hw2.app.config['DATABASE'])

    def testEmptyDb(self):
        rv = self.app.get('/')
        assert 'Enter your name to add it to the list!' in rv.data

    def login(self, username, password):
        return self.app.post('/login', data=dict(
            username=username,
            password=password
            ), follow_redirects=True)

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)

    def testLogin(self):
        rv = self.login('hw2', 'password')
        assert 'Successfully logged in' in rv.data
        rv = self.logout()
        assert 'Successfully logged out' in rv.data
        rv = self.login('hw', 'password')
        assert 'Invalid username' in rv.data
        rv = self.login('hw2', 'passwor')
        assert 'Invalid password' in rv.data

    def testList(self):
        self.login('hw2', 'password')

        # testing adding to list
        rv = self.app.post('/add', data=dict(
            name='testing'
        ), follow_redirects=True)
        assert 'Enter your name to add it to the list!' not in rv.data
        assert 'testing' in rv.data
        # add to list again
        rv = self.app.post('/add', data=dict(
            name='testing2'
        ), follow_redirects=True)
        assert 'Enter your name to add it to the list!' not in rv.data
        assert 'testing' in rv.data
        assert 'testing2' in rv.data

        # testing clear list
        rv = self.app.post('/clear', follow_redirects=True)
        assert 'Enter your name to add it to the list!' in rv.data

if __name__ == '__main__':
    unittest.main()
