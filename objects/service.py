from exceptions.broken_serialized_object import BrokenSerializedObject
from objects.serializable import Serializable


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
            'port': self._service_port,
            'name': self.name,
            'description': self.description,
            'tags': self.tags,
        }

    @staticmethod
    def from_dict(serialized_service):
        try:
            return Service(
                serialized_service['name'],
                serialized_service['port'],
                serialized_service['description'],
                tags=serialized_service.get('tags', [])
            )
        except Exception as e:
            raise BrokenSerializedObject(e)
