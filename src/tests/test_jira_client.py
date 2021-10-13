# TODO: figure out the right way to do this
import sys; sys.path.append('..')

from config import TEST_JIRA_USER
from config import TEST_JIRA_API_TOKEN
from config import TEST_JIRA_URL
from config import EXISTING_GROUP_NAMES
from config import TEST_GROUP
from config import TEST_USER
from jira_client import JiraClient
from utils import get_logger


_LOGGER = get_logger('test_jira_client', debug=True)
# TODO: refactor to use fixtures
JC = JiraClient(user=TEST_JIRA_USER, api_token=TEST_JIRA_API_TOKEN, url=TEST_JIRA_URL)


def test_config_import():

    assert TEST_JIRA_USER
    assert TEST_JIRA_API_TOKEN
    assert TEST_JIRA_URL
    assert EXISTING_GROUP_NAMES
    assert TEST_GROUP
    assert TEST_GROUP.get('name')
    assert TEST_GROUP.get('description')
    assert TEST_USER
    assert TEST_USER.get('accountId')


def test_get_all_groups():

    retrieved_groups = JC.get_all_groups()
    retrieved_groups_names = [g['name'] for g in retrieved_groups]
    groups_not_retrieved = [g for g in EXISTING_GROUP_NAMES if g not in retrieved_groups_names]
    groups_successfully_retrieved = [g for g in EXISTING_GROUP_NAMES if g in retrieved_groups_names]
    assert len(groups_not_retrieved) == 0
    assert EXISTING_GROUP_NAMES == groups_successfully_retrieved


def test_get_group_members():
    _LOGGER.warning('test_get_group_members not implemented')
    pass


def test_get_all_groups_with_members():
    """This is a lazy test that is dependent on get_all_groups working properly. Additionally, this
    test assumes that at least one group in your test server environment has at least one member.
    """

    get_all_groups_results = JC.get_all_groups()
    get_all_groups_with_members_results = JC.get_all_groups_with_members()

    # the names of the groups returned should be the same as get_all_groups
    get_all_groups_results_group_names = [g['name'] for g in get_all_groups_results]
    get_all_groups_with_members_results_group_names = [g['name'] for g in get_all_groups_with_members_results]
    assert get_all_groups_results_group_names == get_all_groups_with_members_results_group_names

    # all groups should have a key named 'members'
    groups_missing_members_key = [g for g in get_all_groups_with_members_results if 'members' not in g.keys()]
    assert len(groups_missing_members_key) == 0

    # at least one group should have a non-empty 'members' key
    groups_with_non_empty_members_key = [g for g in get_all_groups_with_members_results if g.get('members')]
    assert len(groups_with_non_empty_members_key) > 0


def test_create_group():

    # method should return a successfull status code
    response = JC.create_group(TEST_GROUP)
    assert response.status_code == 201

    get_all_groups_results = JC.get_all_groups()
    test_group_retrieved = False
    for g in get_all_groups_results:
        if g['name'] == TEST_GROUP['name']:
            test_group_retrieved = True
            break
    assert test_group_retrieved


def test_add_user_to_group():

    # method should return successful status code
    response = JC.add_user_to_group(TEST_GROUP, TEST_USER)
    assert response.status_code == 201

    get_group_members_results = JC.get_group_members(TEST_GROUP)
    test_user_in_test_group = False
    for m in get_group_members_results:
        if TEST_USER['accountId'] == m.get('accountId'):
            test_user_in_test_group = True
            break
    assert test_user_in_test_group


def test_remove_user_from_group():

    # method should return successful status code
    response = JC.remove_user_from_group(TEST_GROUP, TEST_USER)
    assert response.status_code == 200

    get_group_members_results = JC.get_group_members(TEST_GROUP)
    test_user_in_test_group = False
    for m in get_group_members_results:
        if TEST_USER['accountId'] == m.get('accountId'):
            test_user_in_test_group = True
            break
    assert test_user_in_test_group is False


def test_delete_group():

    # test group should already be present otherwise this test will fail
    # TODO: refactor how this works with a more mature pattern
    get_all_groups_results_before_delete = JC.get_all_groups()
    test_group_retrieved_before_delete = False
    for g in get_all_groups_results_before_delete:
        if g['name'] == TEST_GROUP['name']:
            test_group_retrieved_before_delete = True
            break
    assert test_group_retrieved_before_delete

    # method should return a successfull status code
    response = JC.delete_group(TEST_GROUP)
    assert response.status_code == 200

    # test group should be gone after successful deletion
    get_all_groups_results_after_delete = JC.get_all_groups()
    test_group_retrieved_after_delete = False
    for g in get_all_groups_results_after_delete:
        if g['name'] == TEST_GROUP['name']:
            test_group_retrieved_after_delete = True
            break
    assert test_group_retrieved_after_delete is False
