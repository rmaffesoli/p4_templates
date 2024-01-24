import pytest

from p4_templates.kernel.create_user import create_user

class MockP4(object):
    def __init__(self, user_exists=0):
        self.user = {
            'User': None,
            'Type': 'standard',
            'Email': None,
            'FullName': None,
            'AuthMethod': None,
            'Reviews': None,
            'JobView': None,
        }

        if user_exists:
            self.user['Update'] = 1

        self.fetch_called = 0
        self.save_called = 0

    def fetch_user(self, name):
        self.user['User'] = name
        self.fetch_called = 1
        return self.user
    
    def save_user(self, user_dict, arg):
        self.user = user_dict
        self.save_called = 1
        return self.user
    

@pytest.mark.parametrize(
    'name,email,full_name,job_view,auth_method,reviews,dryrun,expected_user,save_called,user_exists',
    [
        ('test_dude', 'x@x.com', 'Test Dude', 'job_view', 'auth_method', 'reviews', False, {'User': 'test_dude', 'Type': 'standard', 'Email': 'x@x.com', 'FullName': 'Test Dude', 'AuthMethod': 'auth_method', 'Reviews': 'reviews', 'JobView': 'job_view'}, 1, False),
        ('test_dude', None, None, None, None, None, True, {'User': 'test_dude', 'Type': 'standard', 'Email': None, 'FullName': None, 'AuthMethod': None, 'Reviews': None, 'JobView': None}, 0, False),
        ('test_dude', None, None, None, None, None, True, {'User': 'test_dude', 'Update': 1, 'Type': 'standard', 'Email': None, 'FullName': None, 'AuthMethod': None, 'Reviews': None, 'JobView': None}, 0, True),
    ]
)
def test_create_user(name, email, full_name, job_view, auth_method, reviews, dryrun, expected_user, save_called, user_exists):
    m_server = MockP4(user_exists)

    create_user(m_server, name, email, full_name, job_view, auth_method, reviews, dryrun)
    
    assert m_server.user == expected_user
    assert m_server.fetch_called == 1
    assert m_server.save_called == save_called
