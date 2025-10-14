import json
from utils.const import get_preferences_json_path
from os.path import exists

DEFAULT_MIRTO_CATEGORY_KEY = 'mirto'
DEFAULT_MIRTO_HOST_KEY = 'host'
DEFAULT_MIRTO_HOST_VALUE = '127.0.0.1'
DEFAULT_MIRTO_PORT_KEY = 'port'
DEFAULT_MIRTO_PORT_VALUE = 6969
DEFAULT_MIRTO_USERNAME_KEY = 'username'
DEFAULT_MIRTO_USERNAME_VALUE = None
DEFAULT_MIRTO_PASSWORD_KEY = 'password'
DEFAULT_MIRTO_PASSWORD_VALUE = None
DEFAULT_SERVICES_CATEGORY_KEY = 'services'


class UserPreferences:
    def __init__(self):
        if exists(get_preferences_json_path()):
            self._preferences_dict = self.read_from_json()
        else:
            self._preferences_dict = self.create_default()

    def create_default(self):
        return {
            DEFAULT_MIRTO_CATEGORY_KEY: {
                DEFAULT_MIRTO_HOST_KEY: DEFAULT_MIRTO_HOST_VALUE,
                DEFAULT_MIRTO_PORT_KEY: DEFAULT_MIRTO_PORT_VALUE,
                DEFAULT_MIRTO_USERNAME_KEY: DEFAULT_MIRTO_USERNAME_VALUE,
                DEFAULT_MIRTO_PASSWORD_KEY: DEFAULT_MIRTO_PASSWORD_VALUE,
            },
            DEFAULT_SERVICES_CATEGORY_KEY: [],
        }

    def read_from_json(self):
        with open(get_preferences_json_path()) as file_instance:
            json_content = file_instance.read()
            return json.loads(json_content)

    def update_preferences(self):
        with open(get_preferences_json_path(), 'w') as file_instance:
            file_instance.write(json.dumps(self._preferences_dict))

    def __len__(self):
        return len(self._preferences_dict)

    def __setitem__(self, key, value):
        self._preferences_dict[DEFAULT_MIRTO_CATEGORY_KEY][key] = value

    def __getitem__(self, key):
        if key not in self._preferences_dict:
            raise ValueError(f'No {key} in preferences')
        return self._preferences_dict[DEFAULT_MIRTO_CATEGORY_KEY][key]

    @property
    def preferences(self) -> dict:
        return self._preferences_dict

    @property
    def mirto_config(self) -> dict:
        return self.preferences()[DEFAULT_MIRTO_CATEGORY_KEY]

    @property
    def services_config(self) -> dict:
        return self.preferences()[DEFAULT_SERVICES_CATEGORY_KEY]
