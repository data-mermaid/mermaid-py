import pytest
import requests
from mermaid_py.client import Client

# Valid data
# Run jupyter notebook sign-in widget to get token, if tests fail with unauthorized 401 error, attempt token refresh
valid_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL2RhdGFtZXJtYWlkLmF1dGgwLmNvbS8iLCJzdWIiOiJnb29nbGUtb2F1dGgyfDEwMzQxOTkwNDcwMDU3MjAyMzQxMiIsImF1ZCI6WyJodHRwczovL2Rldi1hcGkuZGF0YW1lcm1haWQub3JnIl0sImlhdCI6MTYyNjkwMjM3MCwiZXhwIjoxNjI2OTA5NTcwLCJhenAiOiI0QUhjVkZjd3hIYjdwMVZGQjlzRldHNTJXTDdwZE5tNSIsInNjb3BlIjoib3BlbmlkIHByb2ZpbGUgZW1haWwifQ.s7Aj1PcCH0Npd_FtHGqmMvfJVwpcuZEPF6n7GKS1HCk"
valid_name = "Bronx River"
valid_id = "2c56b92b-ba1c-491f-8b62-23b1dc728890"
valid_project_filter = "sites"
# Fail data
fail_name = "fail"
fail_id = "0"
fail_project = {}
# Client object for testing
client = Client(token=valid_token)


# Add tuples for more test cases
@pytest.mark.parametrize("fetch, response", [(fail_name, None), ("health", "ok")])
@pytest.mark.client_info
def test_fetch_response(fetch, response):
    assert client.fetch_resource(fetch) == response


# Non-project resources data fetch tests grouped by client_info marker
# get_info()
@pytest.mark.parametrize(
    "npr",
    [
        fail_name,
        "health",
        "managements",
        "profiles",
        "projecttags",
        "sites",
        "summarysites",
        "version",
    ],
)
@pytest.mark.client_info
def test_get_info(npr):
    if npr == fail_name:
        assert client.get_info(npr) is None
    # non-project resources endpoints
    resp = client.get_info(npr)
    api_resp = client.fetch_resource(npr)
    assert resp == api_resp


@pytest.mark.client_info
def test_get_info__me():
    # Unauthenticated client trying to access fetch_resource('me') returns None
    if not client.authenticated:
        assert client.get_info("me") is None

    user = client.get_info("me")
    if not isinstance(user, dict):
        print(f"Authenticated: {client.authenticated}")
        print(f"type is: {type(client.get_info('me'))}")
        print(f"Returned value:{client.get_info('me')} ")

    assert isinstance(user, dict)


@pytest.mark.client_info
def test_get_choices():
    assert client.get_choices()[0].get("name") == "belttransectwidths"


@pytest.mark.parametrize(
    "attrs",
    [
        "benthicattributes",
        "fishfamilies",
        "fishgenera",
        "fishgroupings",
        "fishsizes",
        "fishspecies",
    ],
)
@pytest.mark.client_info
def test_get_attrs(attrs):
    resp = client.get_attribute(attrs)
    api_resp = client.fetch_resource(attrs)
    assert resp == api_resp


# Project resources data fetch tests grouped by client_project marker
# get_projects()
@pytest.mark.client_project
def test_get_projects():
    resp = client.get_projects()
    api_resp = client.fetch_resource("projects")
    assert resp == api_resp


@pytest.mark.client_project
def test_get_projects__showall():
    resp = client.get_projects(showall=True)
    api_resp = client.fetch_resource("projects", parameters="showall")
    assert resp == api_resp


@pytest.mark.client_project
@pytest.mark.parametrize("param", [fail_name, fail_id, "valid_name", "valid_id"])
def test_get_my_project(param):
    if param == fail_name:
        assert client.get_my_project(name=param) is None
    elif param == fail_id:
        assert client.get_my_project(id=param) is None
    elif param == valid_name:
        path = f"projects/{valid_id}/"
        api_resp = client.fetch_resource(path)
        assert client.get_my_project(name=param) == api_resp
    elif param == valid_id:
        path = f"projects/{valid_id}/"
        api_resp = client.fetch_resource(path)
        assert client.get_my_project(id=param) == api_resp


@pytest.mark.parametrize("param", [fail_name, fail_project, "valid_name"])
@pytest.mark.client_project
def test_get_project_id(param):
    if param == fail_name:
        assert client.get_project_id(name=param) is None
    elif param == fail_id:
        assert client.get_project_id(project=param) is None
    elif param == valid_name:
        path = f"projects/{valid_id}/"
        assert client.get_project_id(name=param) == client.fetch_resource(path).get(
            "id"
        )


@pytest.mark.client_project
def test_get_project_id__project():
    p = client.get_my_project(name=valid_name)
    assert client.get_project_id(project=p) == valid_id


@pytest.mark.parametrize(
    "project_res",
    [
        fail_name,
        fail_id,
        "fail_filter",
        "sites",
        "managements",
        "project_profiles",
        "observers",
        "collectrecords",
        "obstransectbeltfishs",
        "obsbenthiclits",
        "obsbenthicpits",
        "obshabitatcomplexities",
        "obscoloniesbleached",
        "obsquadratbenthicpercent",
        "sampleevents",
        "fishbelttransects",
        "benthictransects",
        "quadratcollections",
        "beltfishtransectmethods",
        "benthiclittransectmethods",
        "benthicpittransectmethods",
        "habitatcomplexitytransectmethods",
        "bleachingquadratcollectionmethods",
        "sampleunitmethods",
    ],
)
@pytest.mark.client_project
def test_get_project_data(project_res):
    # Fail test cases
    if project_res == fail_name:
        assert client.get_project_data(valid_project_filter, name=project_res) is None
    elif project_res == fail_id:
        assert client.get_project_data(valid_project_filter, id=project_res) is None
    elif project_res == "fail_filter":
        assert client.get_project_data(data=project_res) is None

    # API path
    path = f"projects/{valid_id}/{project_res}/"
    assert client.get_project_data(
        project_res, name=valid_name
    ) == client.fetch_resource(path)


@pytest.mark.parametrize(
    "obsv",
    [
        fail_name,
        fail_id,
        "fail_obs",
        "fail_filter",
        "fail_fval",
        "obstransectbeltfishs",
        "obsbenthiclits",
        "obsbenthicpits",
        "obshabitatcomplexities",
    ],
)
@pytest.mark.client_project
def test_get_obs_data(obsv):
    obs_filters = {
        "obstransectbeltfishs": [
            "beltfish",
            "beltfish__transect",
            "beltfish__transect__sample_event",
            "fish_attribute",
            "size_min",
            "size_max",
            "count_min",
            "count_max",
        ],
        "obsbenthiclits": [
            "benthiclit",
            "benthicpit__transect",
            "benthiclit__transect__sample_event",
            "attribute",
            "growth_form",
            "length_min",
            "length_max",
        ],
        "obsbenthicpits": [
            "benthicpit",
            "benthicpit__transect",
            "benthicpit__transect__sample_event",
            "attribute",
            "growth_form",
        ],
        "obshabitatcomplexities": [
            "habitatcomplexity",
            "habitatcomplexity__transect",
            "habitatcomplexity__transect__sample_event",
            "score",
        ],
    }
    f_vals = [
        "size_min",
        "size_max",
        "count_min",
        "count_max",
        "length_min",
        "length_max",
    ]

    # Fail test cases
    if obsv == fail_name:
        assert (
            client.get_obs_data(
                obs="obstransectbeltfishs", filter="beltfish", name=obsv
            )
            is None
        )
    elif obsv == fail_id:
        assert (
            client.get_obs_data(obs="obstransectbeltfishs", filter="beltfish", id=obsv)
            is None
        )
    elif obsv == "fail_filter":
        assert (
            client.get_obs_data(obs="obstransectbeltfishs", filter=obsv, id=valid_id)
            is None
        )
    elif obsv == "fail_fval":
        assert (
            client.get_obs_data(
                obs="obstransectbeltfishs",
                filter="size_min",
                filter_val=obsv,
                id=valid_id,
            )
            is None
        )
    elif obsv == "fail_obs":
        assert client.get_obs_data(obs=obsv, filter="beltfish", id=valid_id) is None

    # API observations path
    path = f"projects/{valid_id}/{obsv}/"

    # Test each observation filter
    # Added if conditional due to issue with pytest still running obs_filters[obsv] after above assert fail cases
    # producing KeyError
    if (
        obsv != fail_name
        and obsv != fail_id
        and obsv != "fail_obs"
        and obsv != "fail_filter"
        and obsv != "fail_fval"
    ):
        for fil in obs_filters[obsv]:

            # API call compare
            if fil in f_vals:
                # filter requires parameter value
                resp = client.get_obs_data(
                    obs=obsv, filter=fil, filter_val=10, id=valid_id
                )
                payload = {fil: 10}
                api_resp = client.fetch_resource(path, parameters=payload)
                assert resp == api_resp
            else:
                resp = client.get_obs_data(obs=obsv, filter=fil, id=valid_id)
                api_resp = client.fetch_resource(path, parameters=fil)
                assert resp == api_resp


@pytest.mark.parametrize(
    "unit",
    [
        fail_name,
        fail_id,
        "fail_unit",
        "fail_filter",
        "fail_fil_val",
        "fishbelttransects",
        "benthictransects",
        "quadratcollections",
    ],
)
@pytest.mark.client_project
def test_get_sample_unit(unit):
    # Fail test cases
    if unit == fail_name:
        assert client.get_sample_unit(unit="fishbelttransects", name=unit) is None
    elif unit == fail_id:
        assert client.get_sample_unit(unit="fishbelttransects", id=unit) is None
    elif unit == "fail_unit":
        assert client.get_sample_unit(unit=unit, filter="beltfish", id=valid_id) is None
    elif unit == "fail_filter":
        assert (
            client.get_sample_unit(unit="fishbelttransects", filter=unit, id=valid_id)
            is None
        )
    elif unit == "fail_fval":
        resp = client.get_sample_unit(
            unit="fishbelttransects",
            filter="len_surveyed_min",
            filter_val=unit,
            id=valid_id,
        )
        assert resp is None

    # API sample units path
    path = f"projects/{valid_id}/{unit}/"

    # API call compare
    if unit == "fishbelttransects" or unit == "benthictransects":
        # filter requires parameter value
        sample_filters = ["len_surveyed_min", "len_surveyed_max"]
        for fil in sample_filters:
            resp = client.get_sample_unit(
                unit=unit, filter=fil, filter_val=20, id=valid_id
            )
            payload = {fil: 20}
            api_resp = client.fetch_resource(path, parameters=payload)
            assert resp == api_resp
        else:
            resp = client.get_sample_unit(unit=unit, id=valid_id)
            api_resp = client.fetch_resource(path)
            assert resp == api_resp


@pytest.mark.parametrize(
    "method",
    [
        fail_name,
        fail_id,
        "fail_method",
        "beltfishtransectmethods",
        "benthiclittransectmethods",
        "benthicpittransectmethods",
        "habitatcomplexitytransectmethods",
        "bleachingquadratcollectionmethods",
        "sampleunitmethods",
    ],
)
@pytest.mark.client_project
def test_get_sample_method(method):
    # Fail test cases
    if method == fail_name:
        assert (
            client.get_sample_method(method="beltfishtransectmethods", name=method)
            is None
        )
    elif method == fail_id:
        assert (
            client.get_sample_method(method="beltfishtransectmethods", id=method)
            is None
        )
    elif method == "fail_method":
        assert client.get_sample_method(method=method, id=valid_id) is None

    # API comparison sample units path
    path = f"projects/{valid_id}/{method}/"
    assert client.get_sample_method(method, id=valid_id) == client.fetch_resource(path)


@pytest.mark.parametrize(
    "event", [fail_name, fail_id, "fail_filter", "fail_fval", "sampleevents"]
)
@pytest.mark.client_project
def test_get_sample_events(event):
    # Fail test cases
    if event == fail_name:
        assert client.get_sample_events(name=event) is None
    elif event == fail_id:
        assert client.get_sample_events(id=event) is None
    elif event == "fail_filter":
        assert client.get_sample_events(filter=event, id=valid_id) is None
    elif event == "fail_fval":
        assert (
            client.get_sample_events(
                filter="sample_date_after", filter_val=event, id=valid_id
            )
            is None
        )

    filters = ["sample_date_before", "sample_date_after"]

    # API observations path
    path = f"projects/{valid_id}/sampleevents/"

    # Test each filter
    for fil in filters:
        resp = client.get_sample_events(
            filter=fil, filter_val="2018-11-16", id=valid_id
        )
        payload = {fil: "2018-11-16"}
        api_resp = client.fetch_resource(path, parameters=payload)
        assert resp == api_resp
