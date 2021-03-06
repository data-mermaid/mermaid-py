import pytest
from ..client import Client
from ..exceptions import *

# Valid data
# Run jupyter notebook sign-in widget to get token, if tests fail with unauthorized 401 Exception, attempt token refresh
valid_token = "JWT Token"
valid_name = "MERMAID Project Name"
valid_id = "MERMAID Project ID"
valid_project_filter = "sites"
# Fail data
fail_name = "fail"
fail_resource = "fail"
fail_id = "0"
# Client object for testing
client = Client(token=valid_token)


@pytest.mark.parametrize("resource", (fail_resource, "failed_access", "health"))
@pytest.mark.client_info
def test_fetch_resource(resource):
    # Fail test case with invalid resource name raises exception
    if resource == fail_resource:
        with pytest.raises(InvalidResourceException):
            client._fetch_resource(resource=resource)
    elif resource == "failed_access":
        with pytest.raises(UnauthorizedClientException):
            unauthorized_client = Client()
            unauthorized_client._fetch_resource(resource="me")
    else:
        api_response = client._fetch_resource(resource=resource)
        client_call = client._fetch_resource(resource=resource)
        assert client_call == api_response


# Non-project resources data fetch tests grouped by client_info marker
@pytest.mark.parametrize(
    "npr",
    [
        fail_resource,
        "health",
        "managements",
        "profiles",
        "projecttags",
        "sites",
        "summarysites",
        "version",
        "me",
    ],
)
@pytest.mark.client_info
def test_get_info(npr):
    # non-project resources endpoints
    if npr == fail_resource:
        with pytest.raises(InvalidResourceException):
            client.get_info(npr)
    elif npr == "me" and not client.authenticated:
        with pytest.raises(UnauthorizedClientException):
            client.get_info(npr)
    else:
        api_response = client._fetch_resource(resource=npr)
        client_call = client.get_info(npr)
        assert client_call == api_response


# Project resources data fetching tests are grouped by client_project marker
@pytest.mark.client_project
@pytest.mark.parametrize("param", ["projects", "show all"])
@pytest.mark.client_project
def test_get_projects(param):
    if param == "projects":
        api_response = client._fetch_resource(resource="projects")
        client_call = client.get_projects()
        assert client_call == api_response
    if param == "show all":
        api_response = client._fetch_resource(resource="projects", parameters="showall")
        client_call = client.get_projects(showall=True)
        assert client_call == api_response


@pytest.mark.client_project
@pytest.mark.parametrize("param", [fail_name, fail_id, valid_name, valid_id])
def test_get_project(param):
    if param == fail_name:
        with pytest.raises(InvalidProjectException):
            client.get_project(name=param)
    elif param == fail_id:
        with pytest.raises(Exception):
            client.get_project(id=param)
    else:
        # API call with associated valid project name and id
        path = f"projects/{valid_id}/"
        api_response = client._fetch_resource(resource=path)

        if param == valid_name:
            client_call = client.get_project(name=param)
            assert client_call == api_response
        elif param == valid_id:
            client_call = client.get_project(id=param)
            assert client_call == api_response


@pytest.mark.parametrize("param", [fail_name, valid_name])
@pytest.mark.client_project
def test_get_project_id(param):
    if param == fail_name:
        with pytest.raises(InvalidProjectException):
            client.get_project_id(name=param)
    elif param == valid_name:
        api_response = client.get_project_resource(id=valid_id).get("id")
        client_call = client.get_project_id(name=param)
        assert client_call == api_response


@pytest.mark.parametrize(
    "resource",
    [
        fail_name,
        fail_id,
        fail_resource,
        "sites",
        "managements",
        "project_profiles",
        "observers",
        "collectrecords",
    ],
)
@pytest.mark.client_project
def test_get_project_resource(resource):
    if resource == fail_name:
        with pytest.raises(Exception):
            client.get_project_resource(valid_project_filter, name=resource)
    elif resource == fail_id:
        with pytest.raises(Exception):
            client.get_project_resource(valid_project_filter, id=resource)
    elif resource == fail_resource:
        with pytest.raises(InvalidResourceException):
            client.get_project_resource(resource=resource)
    else:
        # API call with associated valid project name and id
        path = f"projects/{valid_id}/"
        api_response = client._fetch_resource(resource=path)

        if resource == valid_name:
            client_call = client.get_project_resource(name=resource)
            assert client_call == api_response
        elif resource == valid_id:
            client_call = client.get_project_resource(id=resource)
            assert client_call == api_response


@pytest.mark.parametrize(
    "observation",
    [
        fail_name,
        fail_id,
        fail_resource,
        "fail_filter",
        "obstransectbeltfishs",
        "obsbenthiclits",
        "obsbenthicpits",
        "obshabitatcomplexities",
    ],
)
@pytest.mark.client_project
def test_get_observations(observation):
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
    if observation == fail_name:
        with pytest.raises(Exception):
            client.get_observations(
                observation="obstransectbeltfishs", filter="beltfish", name=observation
            )
    elif observation == fail_id:
        with pytest.raises(Exception):
            client.get_observations(
                observation="obstransectbeltfishs", filter="beltfish", id=observation
            )
    elif observation == fail_resource:
        with pytest.raises(InvalidResourceException):
            client.get_observations(
                observation=observation, filter=observation, id=valid_id
            )
    elif observation == "fail_filter":
        with pytest.raises(InvalidResourceException):
            client.get_observations(
                observation="obstransectbeltfishs", filter=observation, id=valid_id
            )

    # Test each observation with available filter options
    else:
        path = f"projects/{valid_id}/{observation}/"
        for fil in obs_filters[observation]:
            # API call for filters requiring values, value input = 10
            if fil in f_vals:
                payload = {fil: 10}
                api_response = client._fetch_resource(resource=path, parameters=payload)
                client_call = client.get_observations(
                    observation=observation, filter=fil, filter_val=10, id=valid_id
                )
                assert client_call == api_response
            # Test filters without required value
            else:
                api_response = client._fetch_resource(resource=path, parameters=fil)
                client_call = client.get_observations(
                    observation=observation, filter=fil, id=valid_id
                )
                assert client_call == api_response


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
def test_get_sample_units(unit):
    # Fail test cases
    if unit == fail_name:
        with pytest.raises(Exception):
            client.get_sample_units(unit="fishbelttransects", name=unit)
    elif unit == fail_id:
        with pytest.raises(Exception):
            client.get_sample_units(unit="fishbelttransects", id=unit)
    elif unit == "fail_unit":
        with pytest.raises(InvalidResourceException):
            client.get_sample_units(unit=unit, filter="beltfish", id=valid_id)
    elif unit == "fail_filter":
        with pytest.raises(InvalidResourceException):
            client.get_sample_units(unit="fishbelttransects", filter=unit, id=valid_id)

    else:
        # API sample units path
        path = f"projects/{valid_id}/{unit}/"
        # API call compare
        # filter requires parameter value
        sample_filters = ["len_surveyed_min", "len_surveyed_max"]
        for fil in sample_filters:
            payload = {fil: 20}
            api_response = client._fetch_resource(resource=path, parameters=payload)
            client_call = client.get_sample_units(
                unit=unit, filter=fil, filter_val=20, id=valid_id
            )
            assert client_call == api_response
        else:
            api_response = client._fetch_resource(resource=path)
            client_call = client.get_sample_units(unit=unit, id=valid_id)
            assert client_call == api_response


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
def test_get_sample_methods(method):
    # Fail test cases
    if method == fail_name:
        with pytest.raises(Exception):
            client.get_sample_methods(method="beltfishtransectmethods", name=method)
    elif method == fail_id:
        with pytest.raises(Exception):
            client.get_sample_methods(method="beltfishtransectmethods", id=method)
    elif method == "fail_method":
        with pytest.raises(InvalidResourceException):
            client.get_sample_methods(method=method, id=valid_id)
    # Pass test cases
    else:
        api_response = client.get_project_resource(id=valid_id, resource=method)
        client_call = client.get_sample_methods(method=method, id=valid_id)
        assert client_call == api_response


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
        with pytest.raises(InvalidResourceException):
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
            api_response = client._fetch_resource(resource=path, parameters=payload)
            client_call = client.get_sample_events(
                filter=fil, filter_val="2018-11-16", id=valid_id
            )
            assert client_call == api_response
