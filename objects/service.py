from exceptions.broken_serialized_object import BrokenSerializedObject
from objects.serializable import Serializable
from user.user_preferences import (
    DEFAULT_SERVICE_NAME_KEY,
    DEFAULT_SERVICE_PORT_KEY,
    DEFAULT_SERVICE_DESCRIPTION_KEY,
    DEFAULT_SERVICE_TAGS_KEY,
)


class Service(Serializable):
    def __init__(self, name, port, description, tags=[]):
        assert type(port) is int

        self._service_port = port
        self.name = name
        self.description = description
        self.tags = tags
    
    @property
    def port(self):
        return self._service_port

    def to_dict(self):
        return {
            DEFAULT_SERVICE_PORT_KEY: self._service_port,
            DEFAULT_SERVICE_NAME_KEY: self.name,
            DEFAULT_SERVICE_DESCRIPTION_KEY: self.description,
            DEFAULT_SERVICE_TAGS_KEY: self.tags,
        }

    @staticmethod
    def from_dict(serialized_service):
        try:
            return Service(
                serialized_service[DEFAULT_SERVICE_NAME_KEY],
                serialized_service[DEFAULT_SERVICE_PORT_KEY],
                serialized_service[DEFAULT_SERVICE_DESCRIPTION_KEY],
                tags=serialized_service.get(DEFAULT_SERVICE_TAGS_KEY, [])
            )
        except Exception as e:
            raise BrokenSerializedObject(e)
