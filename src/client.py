import requests
from src.utilities import *


# Production MERMAID API root URL.
api_root = 'https://api.datamermaid.org/v1/'
# Development MERMAID API root URL.
api_root_dev = 'https://dev-api.datamermaid.org/v1/'


class Client:
    """
    Client base class used for accessing MERMAID API.
    """
    # Class variables.
    # Non-project resource endpoints.
    npr_endpoints = ['health', 'managements', 'me', 'profiles', 'projecttags', 'sites', 'summarysites', 'version']
    # Attributes.
    attrs_endpoints = ['benthicattributes', 'fishfamilies', 'fishgenera', 'fishgroupings', 'fishsizes', 'fishspecies']
    # Project resources.
    proj_resources = ['sites', 'managements', 'project_profiles', 'observers', 'collectrecords']
    # Project observations.
    proj_obs = ['obstransectbeltfishs', 'obsbenthiclits', 'obsbenthicpits', 'obshabitatcomplexities',
                'obscoloniesbleached', 'obsquadratbenthicpercent']

    def __init__(self, token=None, url=api_root_dev):
        """
        Constructor for Client base class used for accessing MERMAID API data.
        :param token: (optional) Authenticated JWT token. Defaults to (token=None).
        :type token: str
        :param url: (optional) API URL. Defaults to (url='https://api.datamermaid.org/v1/').
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
        self.session.headers.update({
            'content-type': "application/json",
            'authorization': "Bearer %s" % self.token

        })

    # API paths
    def api_root(self, subdirectory='', method='GET', parameters=None, data=None):
        """
        Prepares API call and utilizes Client Session to make MERMAID API calls.
        :param subdirectory: (optional) subdirectory path. Defaults to (subdirectory='').
        :type subdirectory: str
        :param method: HTTP request method. Defaults to (method='GET').
        :type method: str
        :param parameters: (optional) parameters for request.
        :type parameters: dict: (../?key=val), str: (../?str).
        :param data: (optional) data. Defaults to (data=None).
        :return: JSON object containing MERMAID API data.
        :rtype: dict, None
        """
        # Creates full URL path.
        prep_url = self.url + subdirectory
        # Prepares Request and send from Client class Session.
        req = requests.Request(method, url=prep_url, params=parameters, data=data)
        prepped = self.session.prepare_request(req)
        resp = self.session.send(prepped)

        # Returns JSON if response code OK.
        if resp.status_code == requests.codes.ok:
            return resp.json()
        else:
            if resp.status_code == 401:
                print('api_root response code: ' + str(resp.status_code) + ' -- Attempt token refresh')
            else:
                print('api_root response code: ' + str(resp.status_code))
            return None

    def projects_path(self, name=None, id=None, resource=None):
        """
        Helper class function used to return projects path '/projects/<project_id>/' based on name or id of project.
        :param name: (optional if 'id' provided) MERMAID project name.
        :type name: str
        :param id: (optional if 'name' provided) MERMAID project ID.
        :type: id: str
        :param resource:
        :return: projects path, returns None if invalid project name or id.
        :rtype: str, None
        """
        if resource:
            if id:
                return 'projects/' + id + '/' + resource + '/'
            elif name:
                p_id = self.get_project_id(name=name)
                # Nested if instead of elif name and self.get_project_id(name=name) to improve performance by reducing
                # the number of API calls for name or id NoneType check.
                if p_id:
                    return 'projects/' + p_id + '/' + resource + '/'
        else:
            if id:
                return 'projects/' + id + '/'
            elif name:
                p_id = self.get_project_id(name=name)
                if p_id:
                    return 'projects/' + p_id + '/'
        return None

    # Get functions
    def get_info(self, info):
        """
        Gets non-project resource information. Authentication not required for health, version, profiles, projecttags,
        sites, managements. Authentication required for me.
        :param info: health, version, profiles, projecttags, sites, managements, me.
        :type info: str
        :return: non-project resource data.
        :rtype: dict, str, None
        """
        # TODO: Handle pagination, filters, PUT, HEAD OPTIONS requests
        # Authentication required for access to 'me' API endpoint.
        if info == 'me' and not self.authenticated:
            return None

        if info in self.npr_endpoints:
            return self.api_root(info)
        return None

    def get_choices(self):
        """
        Gets a list of objects, each one of which has a name item (e.g., countries) and a data item that is a list
        of available choice objects.
        :return: list of choice objects.
        :rtype: list
        """
        # TODO: Filter: /updates/?timestamp="DATE"
        return self.api_root('choices')

    def get_attribute(self, attr):
        """
        Gets attributes which are “things that can be observed” – coral and other taxa as well as non-organic
        benthic substrates for benthic transects and bleaching surveys, fish species/genera/families as well
        as arbitrary fish groupings for fish belt transects, and so on.
        :param attr: fishsizes, benthicattributes, fishfamilies, fishgenera, fishspecies, fishgroupings.
        :type attr: str
        :return: attribute data.
        :rtype: dict, None
        """
        if attr not in self.attrs_endpoints:
            return None
        return self.api_root(attr)

    def get_projects(self, showall=False):
        """
        Gets the projects subdirectory. Without query parameters, returns a list of projects of which
        the user is a member. The showall query parameter may be used to return projects unfiltered by the user’s
        membership. showall is important when the user is unauthenticated.
        :param showall: (optional) Returns all projects unfiltered by the user’s membership.
        :type showall: bool
        :return: projects.
        :rtype: dict, None
        """
        if not showall:
            return self.api_root('projects')
        else:
            payload = 'showall'
            return self.api_root('projects', parameters=payload)

    def get_my_project(self, name=None, id=None):
        """
        Gets a specific MERMAID project. Either name or id required.
        :param name: (optional if 'id' provided) MERMAID project name.
        :type name: str
        :param id: (optional if 'name' provided) MERMAID project ID.
        :type id: str
        :return: project with associated data.
        :rtype: dict, None
        """
        if id:
            path = self.projects_path(id=id)
            return self.api_root(path)
        elif name:
            projects = self.get_projects(showall=True)
            # Projects not None type
            if projects:
                return lookup('name', name, projects['results'])
        return None

    def get_project_id(self, name=None, project=None):
        """
        Gets an ID for given MERMAID project.
        :param name: (optional if 'id' provided) MERMAID project name.
        :type: str
        :param project: (optional if 'name' provided) project dict containing project data.
        eg. project dict returned from get_my_project().
        :type: dict
        :return: project ID.
        :rtype: str, None
        """
        if project and isinstance(project, dict):
            return project.get('id')
        elif name:
            project = self.get_my_project(name)
            # Nested if instead of elif name and self.get_my_project(name=name) to improve performance by reducing
            # the number of API calls for name or id NoneType check.
            if project:
                return project.get('id')
        return None

    def get_project_data(self, data, name=None, id=None):
        """
        Gets project resource data including resources and observations. Authenticated access to project data
        depends on the association of a user profile with a project. Unauthenticated access to project data
        depends on the data sharing policies chosen per survey method for a project.
        :param name: (optional if 'id' provided) MERMAID project name.
        :type name: str
        :param id: (optional if 'name' provided) MERMAID project ID.
        :type id: str
        :param data: project resource or observation data. Project resources include; sites, managements,
         project_profiles, observers, collectrecords. Project observations include; obstransectbeltfishs,
         obsbenthiclits, obsbenthicpits, obshabitatcomplexities, obscoloniesbleached, obsquadratbenthicpercent.
        :return: project data.
        :rtype: dict, None
        """
        # Valid data check
        if data not in self.proj_resources and data not in self.proj_obs:
            return None
        # Create path from either name or id parameter
        path = self.projects_path(name=name, id=id, resource=data)
        if path:
            return self.api_root(path)
        return None

    def get_obs_data(self, obs, filter, filter_val=None, name=None, id=None):
        """
        Gets observation resources which are the lowest level of MERMAID data, representing individual observations
        in sample unit methods, belonging to sample events (a set of sample unit methods at a site on a specific date).
        :param obs: Project observations include; obstransectbeltfishs, obsbenthiclits, obsbenthicpits,
         obshabitatcomplexities, obscoloniesbleached, obsquadratbenthicpercent.
        :type obs: str
        :param filter:see https://mermaid-api.readthedocs.io/en/latest/projects.html#observations for list of
         observation and filter options
        :type filter: str
        :param filter_val: (optional) Required for filters requiring values eg. size_min, size_max, count_min,
         count_max, length_min, length_max filters
        :param name: (optional if 'id' provided) MERMAID project name.
        :type name: str
        :param id: (optional if 'name' provided) MERMAID project ID.
        :type id: str
        :return:
        """
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
        # Valid observation and filter for observation.
        if obs not in obs_filters or filter not in obs_filters[obs]:
            return None
        # API observations path
        path = self.projects_path(name=name, id=id, resource=obs)

        # Filters
        if path:
            if filter_val:
                payload = {filter: filter_val}
                return self.api_root(path, parameters=payload)
            else:
                return self.api_root(path, parameters=filter)
        return None





