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
            list: Returns a list of dicts where each dict is a group records
        """
        return self._get_all_paginated_results(f"{self.url_api_3}/group/bulk")

    def get_all_groups_with_members(self):
        """This obtains all groups in the Jira instances and includes a new key in the group record
        `member` and adds all users records in the key that have membership in the group.

        Returns:
            list: Returns a list of dicts where each dict is a group records
        """
        groups = self.get_all_groups()
        for group in groups:
            group['members'] = self._get_all_paginated_results(
                f"{self.url_api_3}/group/member",
                params={'groupname': group['name']}
            )
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
