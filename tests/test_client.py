from src.client import Client

# client object for testing
test_client = Client()


def test_authorization():
    # Check authenticated flag
    # Authorized JWT Token will be authenticated and provided from jupyter notebook before initializing Client
    tok = '12345'
    c = Client(token=tok)
    assert c.authenticated


def test_api_root_fail():
    assert test_client.api_root('fail') == 404


def test_api_root():
    assert type(test_client.api_root()) == dict


def test_get_info():
    assert test_client.get_info('health') == 'ok'


# Unauthenticated client trying to access api_root('me') returns None
def test_get_info_me():
    assert test_client.get_info('me') is None


def test_get_choices():
    assert type(test_client.get_choices()) == list


def test_get_attrs():
    for attr in test_client.attrs_endpoints:
        assert type(test_client.get_attribute(attr)) == dict


def test_get_my_project_name():
    project = test_client.get_my_project('Red Sea Monitoring')
    assert project.get('id') == '007e1fad-0967-4c7d-b3b6-7007b84a2ff4'


def test_get_my_project_id():
    project = test_client.get_my_project(id='007e1fad-0967-4c7d-b3b6-7007b84a2ff4')
    assert project.get('name') == 'Red Sea Monitoring'


def test_get_project_id():
    assert test_client.get_project_id(name='Red Sea Monitoring') == '007e1fad-0967-4c7d-b3b6-7007b84a2ff4'

