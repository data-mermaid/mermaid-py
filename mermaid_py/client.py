import requests
from mermaid_py.utilities import *


class Client:
    """
    Client base class used for accessing MERMAID API.
    """

    # Class variables.
    # Production MERMAID API root URL.
    api_url = "https://api.datamermaid.org/v1/"
    # Development MERMAID API root URL.
    api_dev_url = "https://dev-api.datamermaid.org/v1/"
    # Non-project resource endpoints.
    npr_endpoints = [
        "health",
        "managements",
        "me",
        "profiles",
        "projecttags",
        "sites",
        "summarysites",
        "version",
    ]
    # Attributes.
    attrs_endpoints = [
        "benthicattributes",
        "fishfamilies",
        "fishgenera",
        "fishgroupings",
        "fishsizes",
        "fishspecies",
    ]
    # Project resources.
    proj_resources = [
        "collectrecords",
        "managements",
        "observers",
        "project_profiles",
        "sites",
    ]
    # Project observations.
    proj_obs = [
        "obsbenthiclits",
        "obsbenthicpits",
        "obscoloniesbleached",
        "obshabitatcomplexities",
        "obstransectbeltfishs",
        "obsquadratbenthicpercent",
    ]
    # Project sample units, methods and events.
    samples = [
        "benthiclittransectmethods",
        "benthicpittransectmethods",
        "benthictransects",
        "beltfishtransectmethods",
        "bleachingquadratcollectionmethods",
        "fishbelttransects",
        "habitatcomplexitytransectmethods",
        "quadratcollections",
        "sampleevents",
        "sampleunitmethods",
    ]

    def __init__(self, token=None, url=api_dev_url):
        """
        Constructor for Client base class used for accessing MERMAID API data.
        :param token: (optional) Authenticated JWT token. Defaults to (token=None).
        :type token: str
        :param url: (optional) API URL. Defaults to (url='https://dev-api.datamermaid.org/v1/').
        :type url: str
        :return Client class object.
        """
        # Instance variables.
        # MERMAID API URL.
        self.url = url
        # JWT token.
        self.token = token
        # Authenticated Client instance variable.
        self.authenticated = False
        # Checks if a token is provided and assigns authenticated instance variable.
        if token:
            self.authenticated = True
        # Initializes requests Session and assigns headers for all Client MERMAID API calls.
        self.session = requests.Session()
        self.session.headers.update(
            {
                "content-type": "application/json",
                "authorization": "Bearer %s" % self.token,
            }
        )

    # API paths
    def _fetch_resource(self, resource=None, parameters=None, data=None):
        """
        Prepares API call and utilizes Client Session to make MERMAID API calls.
        :param resource: (optional) subdirectory path. Defaults to (subdirectory='').
        :type resource: str
        :param parameters: (optional) parameters for request.
        :type parameters: dict:(../?key=val), str:(../?str).
        :param data: (optional) data. Defaults to (data=None).
        :return: JSON object containing MERMAID API data.
        :rtype: dict
        """
        # Creates full URL path.
        if resource is None:
            raise Exception(f"_fetch_resource invalid resource:{resource}")

        prep_url = self.url + resource
        # Prepares Request and send from Client class Session.
        req = requests.Request("GET", url=prep_url, params=parameters, data=data)
        prepped = self.session.prepare_request(req)
        resp = self.session.send(prepped)

        # Returns JSON if response code OK.
        if resp.status_code == requests.codes.ok:
            return resp.json()
        else:
            if resp.status_code == 401:
                raise Exception(
                    f"_fetch_resource response code: {resp.status_code} -- Attempt token refresh"
                )

            else:
                raise Exception(f"_fetch_resource response code: {resp.status_code}")

    def _api_projects_path(
        self, name=None, id=None, resource=None, filter=None, filter_val=None
    ):
        """
        Helper class function used to create and call projects path '/projects/<project_id>/' based on name or id
        of project. See https://mermaid-api.readthedocs.io/en/latest/projects.html#project-resources for more
        information.
        :param name: (optional if 'id' provided) MERMAID project name.
        :type name: str
        :param id: (optional if 'name' provided) MERMAID project ID.
        :type: id: str
        :param resource: MERMAID project entity resources. /projects/<project_id>/<resource>
        :param filter: MERMAID project resource filters.
        :type filter: str
        :param filter_val: (optional) Required for resource filters requiring values. eg. (size_min/size_max,
        count_min/count_max, length_min/length_max, len_surveyed_min/len_surveyed_max,
        sample_date_before/sample_date_after).
        :type filter_val: str, int
        :return: project resource.
        :rtype: dict
        """
        # Generate path.
        path = None
        if resource:
            if id:
                path = f"projects/{id}/{resource}/"
            elif name:
                p_id = self.get_project_id(name=name)
                # Nested if instead of "elif name and self.get_project_id(name=name)"
                # to improve performance by reducing the number of API calls for only 'id' NoneType check.
                if p_id:
                    path = f"projects/{p_id}/{resource}/"

        # No resource given generate path
        else:
            if id:
                path = f"projects/{id}/"
            # Get id for name of project and create path
            elif name:
                p_id = self.get_project_id(name=name)
                if p_id:
                    path = f"projects/{p_id}/"

        # API call from generated path and valid filters check.
        if path:
            if filter and filter_val:
                payload = {filter: filter_val}
                return self._fetch_resource(path, parameters=payload)
            elif filter:
                return self._fetch_resource(path, parameters=filter)
            else:
                return self._fetch_resource(path)
        return self._fetch_resource(path)

    # Get functions.
    def get_info(self, info):
        """
        Gets non-project resource information. Authentication not required for health, version, profiles, projecttags,
        sites, managements. Authentication required for me.
        See https://mermaid-api.readthedocs.io/en/latest/nonproject.html for more information on non-project resources.
        :param info: health, version, profiles, projecttags, sites, managements, me.
        :type info: str
        :return: non-project resource data.
        :rtype: dict, str
        """
        # TODO: Handle pagination
        if info == "me" and not self.authenticated:
            raise Exception('Authentication Required for access to "me" endpoint')

        if info in self.npr_endpoints:
            return self._fetch_resource(info)
        else:
            raise Exception(f"get_info() invalid info parameter:{info}")

    def get_choices(self):
        """
        Gets a list of objects, each one of which has a name item (e.g., countries) and a data item that is a list
        of available choice objects.
        :return: list of choice objects.
        :rtype: list
        """
        # TODO: Filter: /updates/?timestamp="DATE"
        return self._fetch_resource("choices")

    def get_attribute(self, attr):
        """
        Gets attributes which are “things that can be observed” – coral and other taxa as well as non-organic
        benthic substrates for benthic transects and bleaching surveys, fish species/genera/families as well
        as arbitrary fish groupings for fish belt transects, and so on.
        :param attr: fishsizes, benthicattributes, fishfamilies, fishgenera, fishspecies, fishgroupings.
        :type attr: str
        :return: attribute data.
        :rtype: dict
        """
        if attr not in self.attrs_endpoints:
            raise Exception(f"Invalid attribute: {attr}")
        return self._fetch_resource(attr)

    def get_projects(self, showall=False):
        """
        Gets the projects subdirectory. Without query parameters, returns a list of projects of which
        the user is a member. The showall query parameter may be used to return projects unfiltered by the user’s
        membership. showall is important when the user is unauthenticated.
        :param showall: (optional) Returns all projects unfiltered by the user’s membership.
        :type showall: bool
        :return: projects.
        :rtype: dict
        """
        if not showall:
            return self._fetch_resource("projects")
        else:
            payload = "showall"
            return self._fetch_resource("projects", parameters=payload)

    def get_my_project(self, name=None, id=None):
        """
        Gets a specific MERMAID project. Either name or id required.
        See https://mermaid-api.readthedocs.io/en/latest/projects.html for more information on project resources.
        :param name: (optional if 'id' provided) MERMAID project name.
        :type name: str
        :param id: (optional if 'name' provided) MERMAID project ID.
        :type id: str
        :return: project with associated data.
        :rtype: dict
        """
        if id:
            return self._api_projects_path(id=id)
        elif name:
            projects = self.get_projects(showall=True)
            proj = lookup("name", name, projects["results"])
            if proj is None:
                raise Exception(f"No project with the name:{name}")
            else:
                return proj

    def get_project_id(self, name=None, project=None):
        """
        Gets an ID for given MERMAID project.
        :param name: (optional if 'id' provided) MERMAID project name.
        :type: str
        :param project: (optional if 'name' provided) project dict containing project data.
        eg. project dict returned from get_my_project().
        :type: dict
        :return: project ID.
        :rtype: str
        """

        if project and not isinstance(project, dict):
            raise Exception(f"Invalid project type")

        if project:
            id = project.get("id")
            if id:
                return id
            else:
                raise Exception(f"No id found")
        elif name:
            project = self.get_my_project(name)
            # Nested if instead of 'elif name and self.get_my_project(name=name)' to improve performance by reducing
            # the number of API calls for name or id NoneType check.
            if project:
                return project.get("id")

    def get_project_data(self, data, name=None, id=None):
        """
        Gets project resource data including resources and observations. Authenticated access to project data
        depends on the association of a user profile with a project. Unauthenticated access to project data
        depends on the data sharing policies chosen per survey method for a project.
        :param name: (optional if 'id' provided) MERMAID project name.
        :type name: str
        :param id: (optional if 'name' provided) MERMAID project ID.
        :type id: str
        :param data: project resource, observation or sample unit data.
        For more info visit https://mermaid-api.readthedocs.io/en/latest/projects.html#project-entity-resources
        :return: project data.
        :rtype: dict
        """
        # Valid data check.
        if (
            data not in self.proj_resources
            and data not in self.proj_obs
            and data not in self.samples
        ):
            raise Exception(f"Invalid project data:{data}")
        # Create path from either name or id parameter.
        return self._api_projects_path(name=name, id=id, resource=data)

    def get_obs_data(self, obs, filter, filter_val=None, name=None, id=None):
        """
        Gets observation resources which are the lowest level of MERMAID data, representing individual observations
        in sample unit methods, belonging to sample events (a set of sample unit methods at a site on a specific date).
        See https://mermaid-api.readthedocs.io/en/latest/projects.html#observations for more information on
        observations.
        :param obs: Project observations include; obstransectbeltfishs, obsbenthiclits, obsbenthicpits,
        obshabitatcomplexities, obscoloniesbleached, obsquadratbenthicpercent.
        :type obs: str
        :param filter: Visit https://mermaid-api.readthedocs.io/en/latest/projects.html#observations for list of
        observations filter options.
        :type filter: str
        :param filter_val: (optional) Required for filters requiring values eg. size_min, size_max, count_min,
        count_max, length_min, length_max filters.
        :type filter_val: int
        :param name: (optional if 'id' provided) MERMAID project name.
        :type name: str
        :param id: (optional if 'name' provided) MERMAID project ID.
        :type id: str
        :return: observation data.
        :rtype: dict
        """
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
        # Valid observation and filter for observation.
        if obs not in obs_filters:
            raise Exception(f"Invalid observation:{obs}")
        if filter not in obs_filters[obs]:
            raise Exception(f"Invalid observation filter:{filter}")

        # API observations path.
        return self._api_projects_path(
            name=name, id=id, resource=obs, filter=filter, filter_val=filter_val
        )

    def get_sample_unit(self, unit, filter=None, filter_val=None, name=None, id=None):
        """
        Gets sample unit.
        :param unit: Sample unit name. Same units: fishbelttransects, benthictransects, quadratcollections. Visit
        https://mermaid-api.readthedocs.io/en/latest/projects.html#sample-units for more information on sample units.
        :type unit: str
        :param filter: The only useful filters are likely to be len_surveyed_min/len_surveyed_max for
         fishbelttransects and benthictransects.
        :type filter: str
        :param filter_val: (optional) Required for filters requiring values, eg.(len_surveyed_min/len_surveyed_max).
        :type filter_val: int
        :param name: (optional if 'id' provided) MERMAID project name.
        :type name: str
        :param id: (optional if 'name' provided) MERMAID project ID.
        :type id: str
        :return: Sample unit data.
        :rtype: dict
        """
        unit_filters = ["len_surveyed_min", "len_surveyed_max"]
        # Valid unit and filter exits and in valid unit filters.
        if unit not in self.samples:
            raise Exception(f"Invalid unit:{unit}")
        if filter and filter not in unit_filters:
            raise Exception(f"Invalid unit filter:{filter}")

        # API sample unit path.
        return self._api_projects_path(
            name=name, id=id, resource=unit, filter=filter, filter_val=filter_val
        )

    def get_sample_method(self, method, name=None, id=None):
        """
        Gets sample unit method.
        :param method: Sample unit methods: beltfishtransectmethods, benthiclittransectmethods,
        benthicpittransectmethods, habitatcomplexitytransectmethods, bleachingquadratcollectionmethods,
        sampleunitmethods.
        See https://mermaid-api.readthedocs.io/en/latest/projects.html#sample-unit-methods for more information.
        :type method: str
        :param name: (optional if 'id' provided) MERMAID project name.
        :type name: str
        :param id: (optional if 'name' provided) MERMAID project ID.
        :type id: str
        :return: Sample unit methods data.
        :rtype: dict
        """
        if method not in self.samples:
            raise Exception(f"Invalid sample method:{method}")
        # API call sample unit methods path.
        return self._api_projects_path(name=name, id=id, resource=method)

    def get_sample_events(self, filter=None, filter_val=None, name=None, id=None):
        """
        Gets sample events. A sample event in MERMAID is a unique combination of site, management regime (both of which
        are specific to a project), and sample date. It represents all observations from all sample units
        (of whatever type) collected at a place on a date.
        :param filter: sample_date_before, sample_date_after
        :type filter: str
        :param filter_val: (optional) Required for filters requiring values, eg.(len_surveyed_min/len_surveyed_max).
        :type filter_val: str in format (YYYY-MM-DD)
        :param name: (optional if 'id' provided) MERMAID project name.
        :type name: str
        :param id: (optional if 'name' provided) MERMAID project ID.
        :type id: str
        :return: sample events data.
        """
        event_filters = ["sample_date_before", "sample_date_after"]
        if filter and filter not in event_filters:
            raise Exception(f"Invalid event filter:{filter}")
        # API call sample events path.
        return self._api_projects_path(
            name=name,
            id=id,
            resource="sampleevents",
            filter=filter,
            filter_val=filter_val,
        )
