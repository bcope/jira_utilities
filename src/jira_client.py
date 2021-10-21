"""

Jira API Documentation: https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro/

"""

import os

import requests

from utils import get_logger


_JIRA_USER = os.environ.get('JIRA_USER')
_JIRA_API_TOKEN = os.environ.get('JIRA_API_TOKEN')
_JIRA_URL = os.environ.get('JIRA_URL')

_LOGGER = get_logger('jira_client')


class JiraClient:
    
    def __init__(self, user=_JIRA_USER, api_token=_JIRA_API_TOKEN, url=_JIRA_URL):
        self._headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        self._session = requests.Session()
        self._session.headers.update(self._headers)
        self._session.auth = (user, api_token)
        self.url = url
        self.url_api_3 = f"{self.url}/rest/api/3"
        self.url_agile_1 = f"{self.url}/rest/agile/1.0"

    def _get_paginated_results(self, url, results_key='values', parameters={}, use_post=False):
        """Get results of a paginated call that uses 'maxResults', 'startAt', and 'total' attributes.

        Args:
            url (str): The full url of the API endpoint.

        Kwargs:
            results_key (str): The name of the key in the results that contains the list of results.
                Defaults to 'values'.
            parameters (dict): If use_post is False, URL parameters. If use_post is True, json
                encoded body parameters.
            use_post (bool): Use POST instead of GET. Needed if parameters are too long to fit in an
                URL. If True then parameters are json encoded as body parameters.

        Yields:
            dict: Whatever single object is being retrieved by the paginated call.

        Returns:
            None

        Raises:
            HTTPError: calls raise_for_status which could raise this error. See more info in
                documentation here: https://docs.python-requests.org/en/latest/api/#requests.Response.raise_for_status
        """
        parameters = parameters or {}
        results_per_page = 1000
        parameters['maxResults'] = results_per_page
        next = 0
        while True:
            parameters['startAt'] = next
            if use_post:
                response = self._session.post(url, json=parameters)
            else:
                response = self._session.get(url, params=parameters)
            response.raise_for_status()
            response_json = response.json()
            results = response_json[results_key]

            # override results per page if call enforces limit
            if response_json['maxResults'] < results_per_page:
                results_per_page = response_json['maxResults']
                parameters['maxResults'] = results_per_page

            for result in results:
                yield result
            
            next += results_per_page
            if next >= response_json['total']:
                return

    def _get_all_paginated_results(self, url, results_key='values', parameters={}, use_post=False):
        """This is a handler function for accumulating all yielded results from _get_paginated_results.
        All parameters are passed into _get_paginated_results.

        Args:
            url (str): The full url of the API endpoint.

        Kwargs:
            results_key (str): The name of the key in the results that contains the list of results.
                Defaults to 'values'.
            parameters (dict): If use_post is False, URL parameters. If use_post is True, json
                encoded body parameters.
            use_post (bool): Use POST instead of GET. Needed if parameters are too long to fit in an
                URL. If True then parameters are json encoded as body parameters.

        Returns:
            list: Returns a list of dicts
        """
        results = []
        for result in self._get_paginated_results(url, results_key=results_key, parameters=parameters, use_post=use_post):
            results.append(result)
        return results
    
    ### GROUP METHODS ###
    def create_group(self, group):
        """API wrapper function to create a group
        https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-groups/#api-rest-api-3-group-post

        Args:
            group (dict): This should be a dict that represents a group and contain at least the
                `name` key.

        Returns:
            requests.Response: Returns the response from the API call
        """
        _LOGGER.debug(f"group: {group}")
        response = self._session.post(
            f"{self.url_api_3}/group",
            json={'name': group['name']}
        )
        return response

    def delete_group(self, group):
        """API wrapper function to delete a group
        https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-groups/#api-rest-api-3-group-delete

        Args:
            group (dict): This should be a dict that represents a group and contain at least the
                `name` key.

        Returns:
            requests.Response: Returns the response from the API call
        """
        response = self._session.delete(
            f"{self.url_api_3}/group",
            params={'groupname': group['name']}
        )
        return response
    
    def get_all_groups(self):
        """This obtains all groups in the Jira instances.
        https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-groups/#api-rest-api-3-group-bulk-get

        Returns:
            list: Returns a list of dicts where each dict is a group record
        """
        all_groups = self._get_all_paginated_results(f"{self.url_api_3}/group/bulk")
        valid_groups = [g for g in all_groups if not g['name'].startswith('atlassian-addons')]
        return valid_groups

    def get_group_members(self, group):
        """This obtains all users associated with a group.
        https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-groups/#api-rest-api-3-group-member-get
        
        Args:
            group (dict): This should be a dict that represents a group and contain at least the
                `name` key.
                
        Returns:
            list: Returns a list of dicts where each dict is a user record
        """
        return self._get_all_paginated_results(
            f"{self.url_api_3}/group/member",
            parameters={'groupname': group['name']}
        )
    
    def get_all_groups_with_members(self):
        """This obtains all groups in the Jira instances and includes a new key in the group record
        `member` and adds all users records in the key that have membership in the group.

        Returns:
            list: Returns a list of dicts where each dict is a group record
        """
        groups = self.get_all_groups()
        for group in groups:
            group['members'] = self.get_group_members(group)
        return groups

    def add_user_to_group(self, group, user):
        """API wrapper function to add a user to a group
        https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-groups/#api-rest-api-3-group-user-post

        Args:
            group (dict): This should be a dict that represents a group and contain at least the
                `name` key.
            user (dict): This should be a dict that represents a user and contain at least the
                `accountId` key.

        Returns:
            requests.Response: Returns the response from the API call
        """
        response = self._session.post(
            f"{self.url_api_3}/group/user",
            params={'groupname': group['name']},
            json={'accountId': user['accountId']}
        )
        return response

    def remove_user_from_group(self, group, user):
        """API wrapper function to remove a user from a group
        https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-groups/#api-rest-api-3-group-user-delete

        Args:
            group (dict): This should be a dict that represents a group and contain at least the
                `name` key.
            user (dict): This should be a dict that represents a user and contain at least the
                `accountId` key.

        Returns:
            requests.Response: Returns the response from the API call
        """
        response = self._session.delete(
            f"{self.url_api_3}/group/user",
            params={'groupname': group['name'], 'accountId': user['accountId']}
        )
        return response

    ### FIELD METHODS ###
    def get_all_fields(self):
        """Get all fields for Jira instance
        https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-fields/#api-rest-api-3-field-get
        
        Returns:
            list: list of dicts of all fields

        Raises:
            RuntimeError: raises this error if API call doesn't return a 200 status code
        """
        response = self._session.get(
            f"{self.url_api_3}/field"
        )
        if response.status != 200:
            raise RuntimeError(f"API called failed. Reason: {response.reason}. JSON: {response.json()}")
        return response.json()

    def get_field_by_name(self, name, exact_match=True):
        """Get one field that matches a passed string
        
        Args:
            name (str): the string to be used to identify a matching field.

        Kwargs:
            exact_match (bool): by default only a field with a name with an exact match will be 
                returned. User can set to False to find a field that contains the passed string.

        Returns:
            dict or None: will either return a single dict of the single matching field or None if 
                no matching fields
        
        Raises:
            RuntimeError: if more than one field matches raises an error
        """
        fields = self.get_all_fields()
        if exact_match:
            matching_fields = [f for f in fields if f['name'] == name]
        else:
            matching_fields = [f for f in fields if name in f['name']]
        
        if not matching_fields:
            return None
        elif len(matching_fields) == 1:
            return matching_fields[0]
        else:
            raise RuntimeError(f"More than one field matching '{name}': {matching_fields}")

    def get_all_custom_field_contexts(self, field_id, parameters={}):
        """Get contexts for a custom field
        https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-custom-field-contexts/#api-rest-api-3-field-fieldid-context-get

        Args:
            field_id (str): The ID of the custom field.

        Kwargs:
            parameters (dict): dict with any of the following keys: isAnyIssueType, isGlobalContext, 
                contextId, startAt, maxResults. See API documenation for more info

        Returns:
            list: list of dicts of contexts
        """
        results = self._get_all_paginated_results(
            f"{self.url_api_3}/field/{field_id}/context",
            parameters=parameters
        )
        return results
    
    def get_all_custom_field_options_by_context(self, field_id, context_id, parameters={}):
        """Get options from a fields
        https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-custom-field-options/#api-rest-api-3-field-fieldid-context-contextid-option-get
        
        Args:
            field_id (str): The ID of the custom field.
            context_id (str): The ID of the context.

        Kwargs:
            parameters (dict): dict with any of the following keys: optionId, onlyOptions, startAt, 
                maxResults. See API documentation for more info.

        Returns:
            list: list of dicts representing options
        """
        results = self._get_all_paginated_results(
            f"{self.url_api_3}/field/{field_id}/context/{context_id}/option",
            params=parameters
        )
        return results

    def update_custom_field_options_by_context(self, field_id, context_id, options):
        """Update one or more options for a custom field by context
        https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-custom-field-options/#api-rest-api-3-field-fieldid-context-contextid-option-put
        
        Args:
            field_id (str): The ID of the custom field.
            context_id (str): The ID of the context.
            options (list[dict]): A list of dicts of options with at leas the following keys: id, 
                value, disabled. See API documentation for more info.
        
        Returns:
            requests.Response: returns the response of the API call
        """
        response = self._session.put(
            f"{self.url_api_3}/field/{field_id}/context/{context_id}/option",
            json={'options': options}
        )
        return response

    def create_custom_field_options_by_context(self, field_id, context_id, options):
        """Update one or more options for a custom field by context
        https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-custom-field-options/#api-rest-api-3-field-fieldid-context-contextid-option-post
        
        Args:
            field_id (str): The ID of the custom field.
            context_id (str): The ID of the context.
            options (list[dict]): A list of dicts of options with at leas the following keys: value,
                disabled. See API documentation for more info.
        
        Returns:
            requests.Response: returns the response of the API call
        """
        response = self._session.post(
            f"{self.url_api_3}/field/{field_id}/context/{context_id}/option",
            json={'options': options}
        )
        return response

    ### COMPONENT RELATED ###
    def get_project_components(self, project_key):
        """Get all components for a project
        https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-project-components/#api-rest-api-3-project-projectidorkey-components-get
        
        Args:
            project_key (str): the key for the project in Jira
        
        Returns:
            list[dict]: returns a list of the project components

        Raises:
            RuntimeError: raises an error if the call fails
        """
        response = self._session.get(
            f"{self.url_api_3}/project/{project_key}/components"
        )
        if response.status_code != 200:
            raise RuntimeError(f"The call failed with a {response.status_code}: {response.reason}; JSON: {response.json()}")
        return response.json()

    def create_component(self, project_key, name, lead_account_id, description='', assignee_type='PROJECT_DEFAULT'):
        """Create a component in a project
        https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-project-components/#api-rest-api-3-component-post
        
        Args:
            project_key (str): The key of the project the component is assigned to. Required when 
                creating a component. Can't be updated.
            name (str): The unique name for the component in the project. Required when creating a 
                component. Optional when updating a component. The maximum length is 255 characters.
            lead_account_id (str): The accountId of the component's lead user. The accountId uniquely 
                identifies the user across all Atlassian products. For example, 
                5b10ac8d82e05b22cc7d4ef5. Max length: 128.
            
        Kwargs:
            description (str): The description for the component. Optional when creating or 
                updating a component.
            assignee_type (str): The nominal user type used to determine the assignee for issues 
                created with this component. See realAssigneeType for details on how the type of 
                the user, and hence the user, assigned to issues is determined. Can take the 
                following values:
                    PROJECT_LEAD the assignee to any issues created with this component is 
                        nominally the lead for the project the component is in.
                    COMPONENT_LEAD the assignee to any issues created with this component is 
                        nominally the lead for the component.
                    UNASSIGNED an assignee is not set for issues created with this component.
                    PROJECT_DEFAULT the assignee to any issues created with this component is 
                        nominally the default assignee for the project that the component is in.
                Default value: PROJECT_DEFAULT. Optional when creating or updating a component.
                Valid values: PROJECT_DEFAULT, COMPONENT_LEAD, PROJECT_LEAD, UNASSIGNED

        Returns:
            requests.Response: returns the response of the API call
        """
        response = self._session.post(
            f"{self.url_api_3}/component",
            json={
                'project': project_key,
                'name': name,
                'description': description,
                'leadAccountId': lead_account_id,
                'assigneeType': assignee_type,
            }
        )
        if response.status_code != 201:
            _LOGGER.warning(f"Call to create new component `{name}` in {project_key} failed with status code: {response.status_code}; Reason: {response.reason}; JSON: {response.json()}")
        return response

    def update_component(self, component_id, name=None, description=None, lead_account_id=None, assignee_type=None):
        """Update a component in a project
        https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-project-components/#api-rest-api-3-component-id-put

        Args:
            component_id (str): The ID of the component.
        
        Kwargs:
            name (str): The unique name for the component in the project. Optional when updating a 
                component. The maximum length is 255 characters.
            description (str): The description for the component. Optional when updating a 
                component.
            lead_account_id (str): The accountId of the component's lead user. The accountId 
                uniquely identifies the user across all Atlassian products. For example, 
                5b10ac8d82e05b22cc7d4ef5. Max length: 128
            assignee_type (str): The nominal user type used to determine the assignee for issues 
                created with this component. See realAssigneeType for details on how the type of 
                the user, and hence the user, assigned to issues is determined. Can take the 
                following values:
                    PROJECT_LEAD the assignee to any issues created with this component is 
                        nominally the lead for the project the component is in.
                    COMPONENT_LEAD the assignee to any issues created with this component is 
                        nominally the lead for the component.
                    UNASSIGNED an assignee is not set for issues created with this component.
                    PROJECT_DEFAULT the assignee to any issues created with this component is 
                        nominally the default assignee for the project that the component is in.
                Optional when updating a component.

        Returns:
            requests.Response: returns the response of the API call
        """
        update = {}
        if name is not None:
            update['name'] = name
        if description is not None:
            update['description'] = description
        if lead_account_id is not None:
            update['leadAccountId'] = lead_account_id
        if assignee_type is not None:
            update['assigneeType'] = assignee_type
        response = self._session.put(
            f"{self.url_api_3}/component/{component_id}",
            json=update
        )
        if response.status_code != 200:
            _LOGGER.warning(f"Call to update the component {component_id} {name} failed with status code: {response.status_code}; Reason: {response.reason}; JSON: {response.json()}")
        return response

    def create_or_update_components(self, project_key, components):
        """Create components in bulk. If component of the same name already exists, the existing
        component will be updated.

        Args:
            project_key (str):
            components (list[dict]): a list of components with the following keys:
                name (str): The unique name for the component in the project. The maximum length 
                    is 255 characters.
                description (str): The description for the component.
                lead_account_id (str): The accountId of the component's lead user. The accountId 
                    uniquely identifies the user across all Atlassian products. For example, 
                    5b10ac8d82e05b22cc7d4ef5. Max length: 128
                assignee_type (str): The nominal user type used to determine the assignee for 
                    issues created with this component. See realAssigneeType for details on how the 
                    type of the user, and hence the user, assigned to issues is determined. Can 
                    take the following values:
                        PROJECT_LEAD the assignee to any issues created with this component is 
                            nominally the lead for the project the component is in.
                        COMPONENT_LEAD the assignee to any issues created with this component is 
                            nominally the lead for the component.
                        UNASSIGNED an assignee is not set for issues created with this component.
                        PROJECT_DEFAULT the assignee to any issues created with this component is 
                            nominally the default assignee for the project that the component is in.
        
        Returns:
            list[dict]: a list of dicts of successfully updated components
        """
        existing_components = self.get_project_components(project_key)
        _LOGGER.debug(f"Components already existing in project {project_key}:")
        _LOGGER.debug([c.get('name') for c in existing_components])
        created_updated_components = []
        errors = []
        for c in components:
            exists = False
            for ec in existing_components:
                if c['name'] == ec['name']:
                    exists = ec
                    break
            if exists:
                response = self.update_component(
                    exists['id'],
                    name=c['name'],
                    description=c['description'],
                    lead_account_id=c['lead_account_id'],
                    assignee_type=c['assignee_type'],
                )
            else:
                response = self.create_component(
                    project_key,
                    c['name'],
                    c['lead_account_id'],
                    description=c['description'],
                    assignee_type=c['assignee_type'],
                )
            if response.status_code == 200:
                _LOGGER.debug(f"Component {c['name']} updated in {project_key}")
                created_updated_components.append(response.json())
            elif response.status_code == 201:
                _LOGGER.debug(f"Component {c['name']} created in {project_key}")
                created_updated_components.append(response.json())
            else:
                _LOGGER.error(f"""Call to create/update component "{c['name']}" failed with status code {response.status_code}""")
                _LOGGER.error(f"Reason: {response.reason}")
                _LOGGER.error(f"JSON: {response.json()}")
                errors.append(c)
        if errors:
            _LOGGER.error(f"There were {len(errors)}: {errors}")
        return created_updated_components
