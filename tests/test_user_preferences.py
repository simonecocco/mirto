import json
from unittest.mock import mock_open, patch
from mirto.user.user_preferences import UserPreferences
from mirto.utils.const import get_preferences_json_path


@patch('mirto.user.user_preferences.exists')
def test_user_preferences_init_no_file(mock_exists):
    mock_exists.return_value = False
    prefs = UserPreferences()
    assert prefs.preferences['mirto']['host'] == '127.0.0.1'


@patch('mirto.user.user_preferences.exists')
@patch('builtins.open', new_callable=mock_open, read_data=json.dumps({'mirto': {'host': 'test_host'}}))
def test_user_preferences_init_with_file(mock_file, mock_exists):
    mock_exists.return_value = True
    prefs = UserPreferences()
    assert prefs.preferences['mirto']['host'] == 'test_host'


@patch('mirto.user.user_preferences.exists')
def test_create_default(mock_exists):
    prefs = UserPreferences()
    default_prefs = prefs.create_default()
    assert 'mirto' in default_prefs
    assert 'services' in default_prefs
    assert default_prefs['mirto']['port'] == 6969


@patch('mirto.user.user_preferences.exists')
def test_update_preferences(mock_exists):
    prefs = UserPreferences()
    prefs.preferences['mirto']['port'] = 9999
    prefs.update_preferences()

    prefs2 = UserPreferences()
    assert prefs2.preferences['mirto']['port'] == 9999
