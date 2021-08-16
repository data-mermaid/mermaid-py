import pytest
from mermaid_py.client import Client

# Valid data
# Run jupyter notebook sign-in widget to get token, if tests fail with unauthorized 401 Exception, attempt token refresh
valid_token = "JWT Token"
valid_name = "MERMAID Project Name"
valid_id = "MERMAID Project ID"
valid_project_filter = "sites"
# Fail data
fail_name = "fail"
fail_id = "0"
# Client object for testing
client = Client(token=valid_token)


@pytest.mark.parametrize("resource", (fail_name, "health"))
@pytest.mark.client_info
def test_fetch_resource(resource):
    # Fail test case with invalid resource name raises exception
    if resource == fail_name:
        with pytest.raises(Exception):
            client._fetch_resource(resource)
    else:
        api_resp = client._fetch_resource(resource)
        client_call = client._fetch_resource(resource)
        assert client_call == api_resp


@pytest.mark.parametrize(
    "resource", (fail_name, fail_id, "fail_resource", valid_name, valid_id)
)
@pytest.mark.client_info
def test_api_projects_path(resource):
    # Fail test case with invalid resource name raises exception
    if resource == fail_name:
        with pytest.raises(Exception):
            client._api_projects_path(name=resource)
    elif resource == fail_id:
        with pytest.raises(Exception):
            client._api_projects_path(id=resource)
    elif resource == "fail_resource":
        with pytest.raises(Exception):
            client._api_projects_path(resource=resource)
    else:
        # API call with associated valid project name and id
        path = f"projects/{valid_id}/"
        api_resp = client._fetch_resource(resource=path)

        if resource == valid_name:
            client_call = client._api_projects_path(name=resource)
            assert client_call == api_resp
        elif resource == valid_id:
            client_call = client._api_projects_path(id=resource)
            assert client_call == api_resp


# Non-project resources data fetch tests grouped by client_info marker
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
    # non-project resources endpoints
    if npr == fail_name:
        with pytest.raises(Exception):
            client.get_info(npr)
    elif npr == "me":
        if not client.authenticated:
            with pytest.raises(Exception):
                client.get_info("me")
        else:
            user = client.get_info("me")
            assert isinstance(user, dict)
    else:
        api_resp = client._fetch_resource(npr)
        client_call = client.get_info(npr)
        assert client_call == api_resp


@pytest.mark.parametrize(
    "attrs",
    [
        fail_name,
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
    if attrs == fail_name:
        with pytest.raises(Exception):
            client.get_attribute(attrs)

    else:
        api_resp = client._fetch_resource(attrs)
        client_call = client.get_attribute(attrs)
        assert client_call == api_resp


# Project resources data fetching tests are grouped by client_project marker
@pytest.mark.client_project
def test_get_projects():
    api_resp = client._fetch_resource("projects")
    client_call = client.get_projects()
    assert client_call == api_resp


@pytest.mark.client_project
def test_get_projects__showall():
    api_resp = client._fetch_resource("projects", parameters="showall")
    client_call = client.get_projects(showall=True)
    assert client_call == api_resp


@pytest.mark.client_project
@pytest.mark.parametrize("param", [fail_name, fail_id, "valid_name", "valid_id"])
def test_get_my_project(param):
    if param == fail_name:
        with pytest.raises(Exception):
            client.get_my_project(name=param)
    elif param == fail_id:
        with pytest.raises(Exception):
            client.get_my_project(id=param)
    elif param == valid_name:
        api_resp = client._api_projects_path(id=valid_id)
        assert client.get_my_project(name=param) == api_resp
    elif param == valid_id:
        api_resp = client._api_projects_path(id=valid_id)
        client_call = client.get_my_project(id=param)
        assert client_call == api_resp


@pytest.mark.parametrize("param", [fail_name, valid_name,])
@pytest.mark.client_project
def test_get_project_id(param):
    if param == fail_name:
        with pytest.raises(Exception):
            client.get_project_id(name=param)
    elif param == valid_name:
        api_resp = client._api_projects_path(id=valid_id).get("id")
        client_call = client.get_project_id(name=param)
        assert client_call == api_resp


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
    if project_res == fail_name:
        with pytest.raises(Exception):
            client.get_project_data(valid_project_filter, name=project_res)
    elif project_res == fail_id:
        with pytest.raises(Exception):
            client.get_project_data(valid_project_filter, id=project_res)
    elif project_res == "fail_filter":
        with pytest.raises(Exception):
            client.get_project_data(data=project_res)
    else:
        api_resp = client._api_projects_path(name=valid_name, resource=project_res)
        client_call = client.get_project_data(project_res, name=valid_name)
        assert client_call == api_resp


@pytest.mark.parametrize(
    "obsv",
    [
        fail_name,
        fail_id,
        "fail_obs",
        "fail_filter",
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
    if obsv == fail_name:
        with pytest.raises(Exception):
            client.get_obs_data(
                obs="obstransectbeltfishs", filter="beltfish", name=obsv
            )
    elif obsv == fail_id:
        with pytest.raises(Exception):
            client.get_obs_data(obs="obstransectbeltfishs", filter="beltfish", id=obsv)
    elif obsv == "fail_filter":
        with pytest.raises(Exception):
            client.get_obs_data(obs="obstransectbeltfishs", filter=obsv, id=valid_id)
    elif obsv == "fail_obs":
        with pytest.raises(Exception):
            client.get_obs_data(obs=obsv, filter="beltfish", id=valid_id)

    # Test each observation with available filter options
    else:
        path = f"projects/{valid_id}/{obsv}/"
        for fil in obs_filters[obsv]:
            # API call for filters requiring values, value input = 10
            if fil in f_vals:
                payload = {fil: 10}
                api_resp = client._fetch_resource(path, parameters=payload)
                client_call = client.get_obs_data(
                    obs=obsv, filter=fil, filter_val=10, id=valid_id
                )
                assert client_call == api_resp
            # Test filters without required value
            else:
                api_resp = client._fetch_resource(path, parameters=fil)
                client_call = client.get_obs_data(obs=obsv, filter=fil, id=valid_id)
                assert client_call == api_resp


@pytest.mark.parametrize(
    "unit",
    [
        fail_name,
        fail_id,
        "fail_unit",
        "fail_filter",
        "fishbelttransects",
        "benthictransects",
        "quadratcollections",
    ],
)
@pytest.mark.client_project
def test_get_sample_unit(unit):
    # Fail test cases
    if unit == fail_name:
        with pytest.raises(Exception):
            client.get_sample_unit(unit="fishbelttransects", name=unit)
    elif unit == fail_id:
        with pytest.raises(Exception):
            client.get_sample_unit(unit="fishbelttransects", id=unit)
    elif unit == "fail_unit":
        with pytest.raises(Exception):
            client.get_sample_unit(unit=unit, filter="beltfish", id=valid_id)
    elif unit == "fail_filter":
        with pytest.raises(Exception):
            client.get_sample_unit(unit="fishbelttransects", filter=unit, id=valid_id)

    else:
        # API sample units path
        path = f"projects/{valid_id}/{unit}/"
        # API call compare
        # filter requires parameter value
        sample_filters = ["len_surveyed_min", "len_surveyed_max"]
        for fil in sample_filters:
            payload = {fil: 20}
            api_resp = client._fetch_resource(path, parameters=payload)
            client_call = client.get_sample_unit(
                unit=unit, filter=fil, filter_val=20, id=valid_id
            )
            assert client_call == api_resp
        else:
            client_call = client.get_sample_unit(unit=unit, id=valid_id)
            api_resp = client._fetch_resource(path)
            assert client_call == api_resp


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
        with pytest.raises(Exception):
            client.get_sample_method(method="beltfishtransectmethods", name=method)
    elif method == fail_id:
        with pytest.raises(Exception):
            client.get_sample_method(method="beltfishtransectmethods", id=method)
    elif method == "fail_method":
        with pytest.raises(Exception):
            client.get_sample_method(method=method, id=valid_id)
    # Pass test cases
    else:
        api_resp = client._api_projects_path(name=valid_name, resource=method)
        client_call = client.get_sample_method(method, id=valid_id)
        assert client_call == api_resp


@pytest.mark.parametrize(
    "event", [fail_name, fail_id, "fail_filter", "fail_fval", "sampleevents"]
)
@pytest.mark.client_project
def test_get_sample_events(event):
    # Fail test cases
    if event == fail_name:
        with pytest.raises(Exception):
            client.get_sample_events(name=event)
    elif event == fail_id:
        with pytest.raises(Exception):
            client.get_sample_events(id=event)
    elif event == "fail_filter":
        with pytest.raises(Exception):
            client.get_sample_events(filter=event, id=valid_id)
    elif event == "fail_fval":
        with pytest.raises(Exception):
            client.get_sample_events(
                filter="sample_date_after", filter_val=event, id=valid_id
            )
    # Pass test cases
    else:
        filters = ["sample_date_before", "sample_date_after"]

        # API observations path
        path = f"projects/{valid_id}/sampleevents/"

        # Test each filter
        for fil in filters:
            payload = {fil: "2018-11-16"}
            api_resp = client._fetch_resource(path, parameters=payload)
            client_call = client.get_sample_events(
                filter=fil, filter_val="2018-11-16", id=valid_id
            )
            assert client_call == api_resp
