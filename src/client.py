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
    # Project resources
    proj_resources = ['sites', 'managements', 'project_profiles', 'observers', 'collectrecords']
    # Project observations
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
        :return: JSON object containing MERMAID api data.
        :rtype: None, dict
        """
        # Creates full URL path.
        prep_url = self.url + subdirectory
        # Prepares Request and send from Client class Session.
        req = requests.Request(method, url=prep_url, params=parameters, data=data)
        prepped = self.session.prepare_request(req)
        resp = self.session.send(prepped)

        # Checks response status code and returns JSON if OK.
        if resp.status_code == requests.codes.ok:
            return resp.json()
        else:
            if resp.status_code == 401:
                print('api_root response code: ' + str(resp.status_code) + ' -- Attempt token refresh')
            else:
                print('api_root response code: ' + str(resp.status_code))
            return None

    def valid_project(self, name=None, id=None):
        """
        Check for valid name or ID resource.
        :param name: Name for validation check.
        :param id: project ID for validation check.
        :return: bool
        """
        if name and self.get_my_project(name=name):
            return True
        if id and self.get_my_project(id=id):
            return True
        return False

    def get_info(self, info):
        """
        Access non-project resource information. Authentication not required for health, version, profiles,
        projecttags, sites, managements. Authentication required for me.
        :param info: health, version, profiles, projecttags, sites, managements, me.
        :type info: str
        :return: non-project resource data.
        :rtype: None, dict, str
        """
        # TODO: Handle pagination, filters, PUT, HEAD OPTIONS requests
        # Check if client is authenticated for access 'me' endpoint.
        if info == 'me' and not self.authenticated:
            return None

        # Check if info in non-project resources endpoints list
        if info in self.npr_endpoints:
            return self.api_root(info)

        return None

    def get_choices(self):
        """
        Convenience resource that returns a list of objects, each one of which has a name item (e.g., countries)
        and a data item that is a list of available choice objects.
        :return: list of choice objects.
        :rtype: list
        """
        # TODO: Filter: /updates/?timestamp="DATE"
        return self.api_root('choices')

    def get_attribute(self, attr):
        """
        Attributes are “things that can be observed” – coral and other taxa as well as non-organic benthic substrates
        for benthic transects and bleaching surveys, fish species/genera/families as well as arbitrary fish groupings
        for fish belt transects, and so on.
        :param attr: fishsizes, benthicattributes, fishfamilies, fishgenera, fishspecies, fishgroupings.
        :type attr: str
        :return: attribute data.
        :rtype: None, dict
        """
        if attr not in self.attrs_endpoints:
            return None
        return self.api_root(attr)

    def get_projects(self,  showall=False):
        """
        Gets the projects subdirectory. Without query parameters, returns a list of projects of which
        the user is a member. The showall query parameter may be used to return projects unfiltered by the user’s
        membership. showall is important when the user is unauthenticated.
        :param showall: (optional) Returns all projects unfiltered by the user’s membership.
        :return: projects.
        :rtype: None, dict
        """
        if not showall:
            return self.api_root('projects')
        else:
            payload = 'showall'
            return self.api_root('projects', parameters=payload)

    def get_my_project(self, name=None, id=None):
        """
        Gets a specific project. Either name or id required.
        :param name: (optional if 'id' provided) project name.
        :type name: str
        :param id: (optional if 'name' provided) project ID.
        :type id: str
        :return: project with associated data.
        :rtype: None, dict
        """
        if id:
            return self.api_root(subdirectory=projects_path(id))

        elif name:
            projects = self.get_projects(showall=True)
            # Projects not None type
            if projects:
                return lookup('name', name, projects['results'])
        return None

    def get_project_id(self, name=None, project=None):
        """
        Gets an ID for given project.
        :param name: (optional if 'project' dict provided) Name of project.
        :type: str
        :param project: (optional if 'name' provided) project dict containing project data.
                         eg. project dict returned from get_my_project().
        :type: dict
        :return: project ID.
        :rtype: None, str
        """
        if project and isinstance(project, dict):
            return project.get('id')
        else:
            proj = self.get_my_project(name)
            if self.valid_project(name=name):
                return proj.get('id')
        return None

    def get_project_data(self, data, name=None, id=None,):
        """
        Gets project resource data including resources and observations. Authenticated access to project data
        depends on the association of a user profile with a project. Unauthenticated access to project data
        depends on the data sharing policies chosen per survey method for a project.
        Project resources include; sites, managements, project_profiles, observers, collectrecords.
        Project observations include; obstransectbeltfishs, obsbenthiclits, obsbenthicpits, obshabitatcomplexities,
        obscoloniesbleached, obsquadratbenthicpercent.
        :param id: (optional if 'name' provided) project ID.
        :type id: str
        :param name: (optional if 'id' provided) project name.
        :type name: str
        :param data: project resource or observation data.
        :return: project data.

        """
        # Valid data filter
        if data not in self.proj_resources and data not in self.proj_obs:
            return None

        if id:
            if self.valid_project(id=id):
                path = projects_path(id, data)
                return self.api_root(subdirectory=path)
        else:
            pr_id = self.get_project_id(name=name)
            if self.valid_project(id=pr_id):
                path = projects_path(pr_id, data)
                return self.api_root(subdirectory=path)
        return None

