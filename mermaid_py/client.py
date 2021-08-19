import requests
from .utilities import *
from .exceptions import *


class Client:
    """
    Client base class used for accessing MERMAID API.
    """

    # Class variables.
    # Production MERMAID API root URL.
    API_URL = "https://api.datamermaid.org/v1"
    # Development MERMAID API root URL.
    API_DEV_URL = "https://dev-api.datamermaid.org/v1"
    # Non-project resource endpoints.
    non_project_resources = [
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
    project_attributes = [
        "benthicattributes",
        "fishfamilies",
        "fishgenera",
        "fishgroupings",
        "fishsizes",
        "fishspecies",
    ]
    # Project resources.
    project_resources = [
        "collectrecords",
        "managements",
        "observers",
        "project_profiles",
        "sites",
    ]
    # Project observations.
    project_observations = [
        "obsbenthiclits",
        "obsbenthicpits",
        "obscoloniesbleached",
        "obshabitatcomplexities",
        "obstransectbeltfishs",
        "obsquadratbenthicpercent",
    ]
    # Project sample units, methods.
    project_sample_units_methods = [
        "benthiclittransectmethods",
        "benthicpittransectmethods",
        "benthictransects",
        "beltfishtransectmethods",
        "bleachingquadratcollectionmethods",
        "fishbelttransects",
        "habitatcomplexitytransectmethods",
        "quadratcollections",
        "sampleunitmethods",
    ]

    def __init__(self, token: str = None, url: str = API_DEV_URL, *args, **kwargs):
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
    def _fetch_resource(self, resource: str, parameters=None):
        """
        Prepares API call and utilizes Client Session to make MERMAID API calls.
        :param resource: (optional) resource path. Defaults to (resource=None).
        :type resource: str
        :param parameters: (optional) parameters for request.
        :type parameters: dict:(../?key=val), str:(../?str).
        :return: JSON object containing MERMAID API data.
        :rtype: dict
        """
        # Creates full URL path.
        resource = resource.strip("/ ")
        prep_url = "/".join([self.url, resource])

        # Prepares Request and send from Client class Session.
        req = requests.Request("GET", url=prep_url, params=parameters)
        prepped = self.session.prepare_request(req)
        resp = self.session.send(prepped, timeout=10)

        # Returns JSON if response code OK.
        if resp.status_code == requests.codes.ok:
            return resp.json()
        elif resp.status_code == 401:
            raise UnauthorizedClientException()
        elif resp.status_code == 404:
            raise InvalidResourceException(resource)
        else:
            raise Exception(f"_fetch_resource Exception status code:{resp.status_code}")

    def _fetch_project_resource(
        self,
        id: str = None,
        name: str = None,
        resource: str = None,
        filter: str = None,
        filter_val=None,
    ):
        """
        Helper class function used to create and call projects path '/projects/<project_id>/' based on name or id
        of project.
        See https://mermaid-api.readthedocs.io/en/latest/projects.html#project-resources for more information.
        :param id: (optional if 'name' provided) MERMAID project ID. If both id and name are provided, then id is used.
        :type: id: str
        :param name: (optional if 'id' provided) MERMAID project name.
        :type name: str
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
        # Generate path favoring id for path creation over name parameter.
        path = ""
        if id or name:
            path = "projects/"
        p_id = id
        # If id not given then get the id from project name
        if name and p_id is None:
            p_id = self.get_project_id(name=name)
        if p_id:
            path += f"{p_id}/"
        if resource:
            path += f"{resource}/"

        payload = None
        if filter:
            payload = filter
        if filter and filter_val:
            payload = {filter: filter_val}
        return self._fetch_resource(path, parameters=payload)

    # Get functions.
    def get_info(self, info: str):
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
            raise UnauthorizedClientException(
                'Authentication required for access to "me" endpoint'
            )

        if info in self.non_project_resources:
            return self._fetch_resource(info)
        else:
            raise InvalidResourceException(info)

    def get_choices(self):
        """
        Gets a list of objects, each one of which has a name item (e.g., countries) and a data item that is a list
        of available choice objects.
        :return: list of choice objects.
        :rtype: list
        """
        # TODO: Filter: /updates/?timestamp="DATE"
        return self._fetch_resource("choices")

    def get_benthic_attributes(self):
        """
        Gets list of MERMAID benthic attributes. Includes inorganic substrates like “rubble” as well as coral and other
        taxa.
        :return: benthic attribute data.
        :rtype: dict
        """
        return self._fetch_resource("benthicattributes")

    def get_fish_families(self):
        """
        Gets list of MERMAID fish families. Biomass constants are the calculated means of all species belonging to each
        family.
        :return: fish families data.
        :rtype: dict
        """
        return self._fetch_resource("fishfamilies")

    def get_fish_genera(self):
        """
        Gets list of MERMAID fish genera. Biomass constants are the calculated means of all species belonging to each
        genus.
        :return: fish genera data.
        :rtype: dict
        """
        return self._fetch_resource("fishgenera")

    def get_fish_groupings(self):
        """
        Gets fish groupings are arbitrary (but useful) groupings of fish species, genera, and families that are treated
        as a single taxon for purposes of observation and analysis (typically some form of “other”). As with fish genera
        and families, biomass constants and regions are calculated from member taxa; additionally, a fish_attributes
        property is returned listing each member species, genus, and family.
        :return: fish groupings data.
        :rtype: dict
        """
        return self._fetch_resource("fishgroupings")

    def get_fish_species(self):
        """
        Gets list of MERMAID fish species. Includes biomass constants and maximum observed length as well as useful
        analytical properties such as vulnerability score, trophic level, trophic group, and functional group.
        :return: fish groupings data.
        :rtype: dict
        """
        return self._fetch_resource("fishspecies")

    def get_fish_sizes(self):
        """
        Gets Separate choice resource used only for looking up the actual size to record for a fish, given a particular
        fish size bin used for the survey.
        :return: fish sizes data.
        :rtype: dict
        """
        return self._fetch_resource("fishsizes")

    def get_projects(self, showall: bool = False):
        """
        Gets the projects resource. Without query parameters, returns a list of projects of which
        the user is a member. The showall query parameter may be used to return projects unfiltered by the user’s
        membership. showall is important when the user is unauthenticated.
        :param showall: (optional) Returns all projects unfiltered by the user’s membership.
        :type showall: bool
        :return: projects.
        :rtype: dict
        """
        if showall:
            payload = "showall"
            return self._fetch_resource("projects", parameters=payload)
        else:
            return self._fetch_resource("projects")

    def get_project(self, id: str = None, name: str = None):
        """
        Gets a specific MERMAID project. Either name or id required.
        See https://mermaid-api.readthedocs.io/en/latest/projects.html for more information on project resources.
        :param id: (optional if 'name' provided) MERMAID project ID. If both id and name are provided, then id is used.
        :type id: str
        :param name: (optional if 'id' provided) MERMAID project name.
        :type name: str
        :return: project with associated data.
        :rtype: dict
        """
        if id:
            self._fetch_project_resource(id=id)
        elif name:
            projects = self.get_projects(showall=True)
            project = get_dict_by_keyval("name", name, projects["results"])
            if project:
                return project
            else:
                raise InvalidProjectException(name=name)

    def get_project_id(self, name: str):
        """
        Gets an ID for given MERMAID project.
        :param name: (optional if 'id' provided) MERMAID project name.
        :type: str
        :return: project ID.
        :rtype: str
        """
        project = self.get_project(name=name)

        if project:
            return project.get("id")
        else:
            raise InvalidProjectException(name=name)

    def get_project_resource(self, resource: str, id: str = None, name: str = None):
        """
        Gets project resource data including resources and observations. Authenticated access to project data
        depends on the association of a user profile with a project. Unauthenticated access to project data
        depends on the data sharing policies chosen per survey method for a project.
        :param id: (optional if 'name' provided) MERMAID project ID. If both id and name are provided, then id is used.
        :type id: str
        :param name: (optional if 'id' provided) MERMAID project name.
        :type name: str
        :param resource: project resource, observation or sample units data.
        For more info visit https://mermaid-api.readthedocs.io/en/latest/projects.html#project-entity-resources
        :return: project data.
        :rtype: dict
        """
        # Valid data check.
        if resource not in self.project_resources:
            raise InvalidResourceException(resource=resource)
        # Create path from either name or id parameter.
        return self._fetch_project_resource(id=id, name=name, resource=resource)

    def get_observations(
        self,
        observation: str,
        id: str = None,
        name: str = None,
        filter: str = None,
        filter_val: int = None,
    ):
        """
        Gets observation resources which are the lowest level of MERMAID data, representing individual observations
        in sample units methods, belonging to sample events (set of sample units methods at a site on a specific date).
        See https://mermaid-api.readthedocs.io/en/latest/projects.html#observations for more information on
        observations.
        :param observation: Project observations include; obstransectbeltfishs, obsbenthiclits, obsbenthicpits,
        obshabitatcomplexities, obscoloniesbleached, obsquadratbenthicpercent.
        :type observation: str
        :param id: (optional if 'name' provided) MERMAID project ID. If both id and name are provided, then id is used.
        :type id: str
        :param name: (optional if 'id' provided) MERMAID project name.
        :type name: str
        :param filter: Visit https://mermaid-api.readthedocs.io/en/latest/projects.html#observations for list of
        observations filter options.
        :type filter: str
        :param filter_val: (optional) Required for filters requiring values eg. size_min, size_max, count_min,
        count_max, length_min, length_max filters.
        :type filter_val: int
        :return: observation data.
        :rtype: dict
        """
        observations_filters = {
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
        if observation not in observations_filters:
            raise InvalidResourceException(f"Invalid observation:{observation}")
        if filter not in observations_filters[observation]:
            raise InvalidResourceException(f"Invalid observation filter:{filter}")

        # API observations path.
        return self._fetch_project_resource(
            id=id, name=name, resource=observation, filter=filter, filter_val=filter_val
        )

    def get_sample_units(
        self,
        unit: str,
        id: str = None,
        name: str = None,
        filter: str = None,
        filter_val: int = None,
    ):
        """
        Gets sample units.
        :param unit: Sample units name. Sample units: fishbelttransects, benthictransects, quadratcollections. Visit
        https://mermaid-api.readthedocs.io/en/latest/projects.html#sample-units for more information on sample units.
        :type unit: str
        :param id: (optional if 'name' provided) MERMAID project ID. If both id and name are provided, then id is used.
        :type id: str
        :param name: (optional if 'id' provided) MERMAID project name.
        :type name: str
        :param filter: The only useful filters are likely to be len_surveyed_min/len_surveyed_max for fishbelttransects
         and benthictransects.
        :type filter: str
        :param filter_val: (optional) Required for filters requiring values, eg.(len_surveyed_min/len_surveyed_max).
        :type filter_val: int
        :return: Sample units data.
        :rtype: dict
        """
        unit_filters = ["len_surveyed_min", "len_surveyed_max"]
        # Valid unit and filter exits and in valid unit filters.
        if unit not in self.project_sample_units_methods:
            raise InvalidResourceException(f"Invalid unit:{unit}")
        if filter and filter not in unit_filters:
            raise InvalidResourceException(f"Invalid unit filter:{filter}")

        # API sample units path.
        return self._fetch_project_resource(
            id=id, name=name, resource=unit, filter=filter, filter_val=filter_val
        )

    def get_sample_methods(self, method: str, id: str = None, name: str = None):
        """
        Gets sample units methods.
        :param method: Sample units methods: beltfishtransectmethods, benthiclittransectmethods,
        benthicpittransectmethods, habitatcomplexitytransectmethods, bleachingquadratcollectionmethods,
        sampleunitmethods.
        See https://mermaid-api.readthedocs.io/en/latest/projects.html#sample-unit-methods for more information.
        :type method: str
        :param id: (optional if 'name' provided) MERMAID project ID. If both id and name are provided, then id is used.
        :type id: str
        :param name: (optional if 'id' provided) MERMAID project name.
        :type name: str
        :return: Sample units methods data.
        :rtype: dict
        """
        if method not in self.project_sample_units_methods:
            raise InvalidResourceException(f"Invalid sample methods:{method}")
        # API call sample units methods path.
        return self._fetch_project_resource(id=id, name=name, resource=method)

    def get_sample_events(
        self,
        id: str = None,
        name: str = None,
        filter: str = None,
        filter_val: str = None,
    ):
        """
        Gets sample events. A sample event in MERMAID is a unique combination of site, management regime (both of which
        are specific to a project), and sample date. It represents all observations from all sample units
        (of whatever type) collected at a place on a date.
        :param id: (optional if 'name' provided) MERMAID project ID. If both id and name are provided, then id is used.
        :type id: str
        :param name: (optional if 'id' provided) MERMAID project name.
        :type name: str
        :param filter: sample_date_before, sample_date_after
        :type filter: str
        :param filter_val: (optional) Required for filters requiring values, eg.(len_surveyed_min/len_surveyed_max).
        :type filter_val: str in format (YYYY-MM-DD)
        :return: sample events data.
        """
        event_filters = ["sample_date_before", "sample_date_after"]
        if filter and filter not in event_filters:
            raise InvalidResourceException(f"Invalid event filter:{filter}")
        # API call sample events path.
        return self._fetch_project_resource(
            name=name,
            id=id,
            resource="sampleevents",
            filter=filter,
            filter_val=filter_val,
        )
