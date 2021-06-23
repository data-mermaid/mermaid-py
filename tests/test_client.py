import pytest
import requests
from src.client import Client

# Valid data
# Run jupyter notebook sign-in widget to get token, if tests fail with unauthorized 401 error, attempt token refresh
valid_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL2RhdGFtZXJtYWlkLmF1dGgwLmNvbS8iLCJzdWIiOiJnb29nbGUtb2F1dGgyfDEwMzQxOTkwNDcwMDU3MjAyMzQxMiIsImF1ZCI6WyJodHRwczovL2Rldi1hcGkuZGF0YW1lcm1haWQub3JnIl0sImlhdCI6MTYyNDQ4NjEwOSwiZXhwIjoxNjI0NDkzMzA5LCJhenAiOiI0QUhjVkZjd3hIYjdwMVZGQjlzRldHNTJXTDdwZE5tNSIsInNjb3BlIjoib3BlbmlkIHByb2ZpbGUgZW1haWwifQ.FbOKWgqC-fwYAJy1xqLg4M3tp5eZBAdfdkbJVZFrtT0'
valid_name = 'Bronx River'
valid_id = '2c56b92b-ba1c-491f-8b62-23b1dc728890'
valid_project_filter = 'sites'
# Fail data
fail_name = 'fail'
fail_id = '0'
fail_project = {}
# Client object for testing
client = Client(token=valid_token)


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
@pytest.mark.parametrize("npr", ['health', 'managements', 'profiles', 'projecttags', 'sites', 'summarysites',
                                 'version'])
@pytest.mark.client_info
def test_get_info(npr):
    # non-project resources endpoints
    resp = client.get_info(npr)
    api_resp = client.api_root(npr)
    assert resp == api_resp


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
    assert client.get_choices()[0].get('name') == 'belttransectwidths'


# get_attrs()
@pytest.mark.parametrize("attrs", ['benthicattributes', 'fishfamilies', 'fishgenera', 'fishgroupings', 'fishsizes',
                                   'fishspecies'])
@pytest.mark.client_info
def test_get_attrs(attrs):
    resp = client.get_attribute(attrs)
    api_resp = client.api_root(attrs)
    assert resp == api_resp


# Project resources data fetch tests grouped by client_project marker
# get_projects()
@pytest.mark.client_project
def test_get_projects():
    resp = client.get_projects()
    api_resp = client.api_root('projects')
    assert resp == api_resp


@pytest.mark.client_project
def test_get_projects__showall():
    resp = client.get_projects(showall=True)
    api_resp = client.api_root('projects', parameters='showall')
    assert resp == api_resp


# get_my_project()
@pytest.mark.client_project
@pytest.mark.parametrize('param', ['fail_name', 'fail_id', 'valid_name', 'valid_id'])
def test_get_my_project(param):
    if param == fail_name:
        assert client.get_my_project(name=param) is None
    elif param == fail_id:
        assert client.get_my_project(id=param) is None
    elif param == valid_name:
        path = 'projects/' + valid_id + '/'
        api_resp = client.api_root(path)
        assert client.get_my_project(name=param) == api_resp
    elif param == valid_id:
        path = 'projects/' + valid_id + '/'
        api_resp = client.api_root(path)
        assert client.get_my_project(id=param) == api_resp


# get_project_id()
@pytest.mark.parametrize("param", ['fail_name', 'fail_project', 'valid_name'])
@pytest.mark.client_project
def test_get_project_id(param):
    if param == fail_name:
        assert client.get_project_id(name=param) is None
    elif param == fail_id:
        assert client.get_project_id(project=param) is None
    elif param == valid_name:
        path = 'projects/' + valid_id + '/'
        assert client.get_project_id(name=param) == client.api_root(path).get('id')


@pytest.mark.client_project
def test_get_project_id__project():
    p = client.get_my_project(name=valid_name)
    assert client.get_project_id(project=p) == valid_id


@pytest.mark.parametrize('project_res', [fail_name, fail_id, 'fail_filter', 'sites', 'managements', 'project_profiles',
                                         'observers', 'collectrecords', 'obstransectbeltfishs', 'obsbenthiclits',
                                         'obsbenthicpits', 'obshabitatcomplexities', 'obscoloniesbleached',
                                         'obsquadratbenthicpercent'])
@pytest.mark.client_project
def test_get_project_data(project_res):
    # Fail test cases
    if project_res == fail_name:
        assert client.get_project_data(valid_project_filter, name=project_res) is None
    elif project_res == fail_id:
        assert client.get_project_data(valid_project_filter, id=project_res) is None
    elif project_res == 'fail_filter':
        assert client.get_project_data(data=project_res) is None

    # API path
    path = 'projects/' + valid_id + '/' + project_res + '/'
    assert client.get_project_data(project_res, name=valid_name) == client.api_root(path)


@pytest.mark.parametrize('obs', [fail_name, fail_id, 'fail_obs', 'fail_filter', 'obstransectbeltfishs',
                                 'obsbenthiclits', 'obsbenthicpits', 'obshabitatcomplexities'])
@pytest.mark.client_project
def test_get_obs_data__fail(obs):
    # Fail test cases
    if obs == fail_name:
        print("ASSERT FAIL_NAME IS NONE REACHED")
        assert client.get_obs_data(obs='obstransectbeltfishs', filter='beltfish', name=obs) is None
    elif obs == fail_id:
        assert client.get_obs_data(obs='obstransectbeltfishs', filter='beltfish', id=obs) is None
    elif obs == 'fail_filter':
        assert client.get_obs_data(obs='obstransectbeltfishs', filter=obs, id=valid_id) is None
    elif obs == 'fail_obs':
        assert client.get_obs_data(obs=obs, filter='beltfish', id=valid_id) is None


@pytest.mark.parametrize('obs', ['obstransectbeltfishs',
                                 'obsbenthiclits', 'obsbenthicpits', 'obshabitatcomplexities'])
@pytest.mark.client_project
def test_get_obs_data__pass(obs):
    obs_filters = {
        'obstransectbeltfishs': ['beltfish', 'beltfish__transect', 'beltfish__transect__sample_event',
                                 'fish_attribute', 'size_min', 'size_max', 'count_min', 'count_max'],
        'obsbenthiclits': ['benthiclit', 'benthicpit__transect', 'benthiclit__transect__sample_event',
                           'attribute', 'growth_form', 'length_min', 'length_max'],
        'obsbenthicpits': ['benthicpit', 'benthicpit__transect', 'benthicpit__transect__sample_event',
                           'attribute', 'growth_form'],
        'obshabitatcomplexities': ['habitatcomplexity', 'habitatcomplexity__transect',
                                   'habitatcomplexity__transect__sample_event', 'score']
    }
    f_vals = ['size_min', 'size_max', 'count_min', 'count_max', 'length_min', 'length_max']

    # API observations path
    path = 'projects/' + valid_id + '/' + obs + '/'
    # Test each obsservation filter
    print('OBS:' + str(obs))
    for fil in obs_filters[obs]:

        # API path
        if fil in f_vals:
            print("fil in f_vals: " + str(fil))
            # filter requires parameter value
            payload = {fil: 1}
            resp = client.get_obs_data(obs=obs, filter=fil, filter_val=1, id=valid_id)
            api_resp = client.api_root(path, parameters=payload)
            assert resp == api_resp
        else:
            print("fil not in f_vals: " + str(fil))
            resp = client.get_obs_data(obs=obs, filter=fil, id=valid_id)
            api_resp = client.api_root(path, parameters=fil)
            assert resp == api_resp