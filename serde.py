from typing import T
from dataclasses import fields, is_dataclass

import json


class Serializer(json.JSONEncoder):
    """
    Serialize data class objects into a dictionary.
    """
    def default(self, obj: object):
        if hasattr(obj, 'to_dict'):
            return obj.to_dict()
        return super().default(obj)


class Deserializer(json.JSONDecoder):
    """
    Deserialize dictionary objects back to a data class instance.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(object_hook=self.from_dict, *args, **kwargs)

    def from_dict(self, dictionary: dict) -> T:
        for key, value in dictionary.items():
            if isinstance(value, dict):
                dictionary[key] = self.from_dict(value)
            elif isinstance(value, list):
                for i, e in enumerate(value):
                    if isinstance(e, dict):
                        value[i] = self.from_dict(e)
        return dictionary

def serde(cls: T) -> T:
    """
    Decorator to add serialization/deserialization methods to a dataclass.
    """
    setattr(cls, 'to_dict', to_dict)
    setattr(cls, 'from_dict', classmethod(from_dict))
    setattr(cls, 'serialize', serialize)
    setattr(cls, 'deserialize', classmethod(deserialize))

    return cls


def to_dict(self) -> dict:
    """
    Return a dictionary representation of the data class object.
    """
    return {f.name: getattr(self, f.name) for f in fields(self)}


def from_dict(cls, dictionary: dict) -> T:
    """
    Return an instance of the data class from a dictionary while also performing type validation.
    """
    obj: T = cls.__new__(cls)

    for field in fields(cls):
        field_name: str = field.name
        field_type: T = field.type

        if field_name in dictionary:
            value = dictionary[field_name]

            if getattr(field_type, '__origin__', None) is list:
                inner_type = field_type.__args__[0]
                value = [inner_type.from_dict(x) if isinstance(x, dict) else x for x in value]

                if not all(isinstance(v, inner_type) for v in value):
                    raise TypeError(f"Invalid type for {field_name}: {type(value)}")

            elif is_dataclass(field_type):
                value = field_type.from_dict(value)

            elif not isinstance(value, field_type):
                raise TypeError(f"Incorrect type for {field_name}: {str(type(value).__name__)}, expected {str(field_type.__name__)} instead")

            setattr(obj, field_name, value)

    return obj


def serialize(self, indent: int = 2) -> str:
    """
    Return a JSON representation of the data class object using the Serializer.
    """
    return json.dumps(self.to_dict(), cls=Serializer, indent=indent)


def deserialize(cls, json_str: str) -> object:
    """
    Return an instance of the data class from a JSON string, ensuring it represents a JSON object.
    """
    dictionary: dict = json.loads(json_str)

    if not isinstance(dictionary, dict):
        raise TypeError(f"{cls.__name__}.deserialize(): expected a JSON object, but got {type(dictionary).__name__}")
    return cls.from_dict(dictionary)
