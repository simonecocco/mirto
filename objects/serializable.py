from abc import abstractmethod, ABC
from json import dumps, loads
from exceptions.broken_serialized_object import BrokenSerializedObject


class Serializable(ABC):
    @staticmethod
    @abstractmethod
    def from_dict(serialized_object):
        raise BrokenSerializedObject('dict not loadable!')

    @abstractmethod
    def to_dict(self):
        raise BrokenSerializedObject('dict not exportable!')

    def to_json_string(self):
        return dumps(self.to_dict())

    @staticmethod
    def from_json_string(serializable_object, json_string):
        assert isinstance(serializable_object, Serializable)

        return serializable_object.from_dict(loads(json_string))
