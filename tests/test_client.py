import pytest
from src.client import Client

#
# Valid data
# Run jupyter notebook sign-in widget to get token, if tests fail with unauthorized 401 error, attempt token refresh
valid_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL2RhdGFtZXJtYWlkLmF1dGgwLmNvbS8iLCJzdWIiOiJnb29nbGUtb2F1dGgyfDEwMzQxOTkwNDcwMDU3MjAyMzQxMiIsImF1ZCI6WyJodHRwczovL2Rldi1hcGkuZGF0YW1lcm1haWQub3JnIl0sImlhdCI6MTYyNDMzMDgxNCwiZXhwIjoxNjI0MzM4MDE0LCJhenAiOiI0QUhjVkZjd3hIYjdwMVZGQjlzRldHNTJXTDdwZE5tNSIsInNjb3BlIjoib3BlbmlkIHByb2ZpbGUgZW1haWwifQ.0fUtx7rb2QDCQXmzfyIVzEWoAympOsXrCVFORIamUqQ'
valid_name = 'Bronx River'
valid_id = '2c56b92b-ba1c-491f-8b62-23b1dc728890'
# Fail data
fail_name = 'fail'
fail_id = '0'
fail_filter = 'fail'
fail_project = {}

# client object for testing
client = Client(token=valid_token)


# Initialization and api root access tests grouped by client_init marker
@pytest.mark.client_init
def test_authenticated__fail():
    # Check authenticated flag
    not_auth = Client()
    assert not not_auth.authenticated


@pytest.mark.client_init
def test_authenticated():
    # Authorized JWT Token will be authenticated and provided from jupyter notebook before initializing Client
    assert client.authenticated


# Add tuples for more test cases
@pytest.mark.parametrize("fetch, response", [
    ('fail', None),
    ('health', 'ok')
])
@pytest.mark.client_info
def test_api_root(fetch, response):
    assert client.api_root(fetch) == response


# Non-project resources data fetch tests grouped by client_info marker
# get_info()
@pytest.mark.parametrize("npr", ['health', 'managements', 'me', 'profiles', 'projecttags', 'sites', 'summarysites',
                                 'version'])
@pytest.mark.client_info
def test_get_info__type(npr):
    # non-project resources endpoints type check
    assert type(client.get_info(npr)) == dict or str


@pytest.mark.client_info
def test_get_info__me():
    # Unauthenticated client trying to access api_root('me') returns None
    if not client.authenticated:
        assert client.get_info('me') is None

    user = client.get_info('me')
    if not isinstance(user, dict):
        print('Authenticated: ' + str(client.authenticated))
        print(type(client.get_info('me')))
        print(client.get_info('me'))

    assert isinstance(user, dict)


# get_choices()
@pytest.mark.client_info
def test_get_choices():
    assert isinstance(client.get_choices(), list)


# get_attrs()
@pytest.mark.parametrize("attrs", ['benthicattributes', 'fishfamilies', 'fishgenera', 'fishgroupings', 'fishsizes',
                                   'fishspecies'])
@pytest.mark.client_info
def test_get_attrs__type(attrs):
    # attribute endpoints type check
    assert isinstance(client.get_attribute(attrs), dict)


# Project resources data fetch tests grouped by client_project marker
# get_projects()
# Check against current user token project count
@pytest.mark.client_project
def test_get_projects():
    assert client.get_projects().get('count') == 3


@pytest.mark.client_project
def test_get_projects__showall():
    # current number of projects are 316
    assert client.get_projects(showall=True).get('count') > 100


# get_my_project()
@pytest.mark.client_project
@pytest.mark.parametrize('param', ['fail_name', 'fail_id', 'valid_name', 'valid_id'])
def test_get_my_project(param):
    if param == fail_name:
        assert client.get_my_project(name=param) is None
    elif param == fail_id:
        assert client.get_my_project(id=param) is None
    elif param == valid_name:
        assert client.get_my_project(name=param).get('name') == valid_name
    elif param == valid_id:
        assert client.get_my_project(id=param).get('id') == valid_id


# valid_project()
@pytest.mark.client_project
@pytest.mark.parametrize("param", ['fail_name', 'fail_id', 'valid_name', 'valid_id'])
def test_valid_project(param):
    if param == fail_name:
        assert client.valid_project(name=param) is False
    elif param == fail_id:
        assert client.valid_project(id=param) is False
    elif param == valid_name:
        assert client.valid_project(name=valid_name) is True
    elif param == valid_id:
        assert client.get_my_project(id=valid_id) is True


# get_project_id()
@pytest.mark.parametrize("param", ['fail_name', 'fail_project', 'valid_name'])
@pytest.mark.client_project
def test_get_project_id(param):
    if param == fail_name:
        assert client.get_project_id(name=param) is None
    elif param == fail_id:
        assert client.get_project_id(project=param) is None
    elif param == valid_name:
        assert client.get_project_id(name=param) == valid_id


@pytest.mark.client_project
def test_get_project_id__project():
    assert client.get_project_id(name=valid_name) == valid_id
