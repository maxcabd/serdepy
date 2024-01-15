from typing import T, Type
from dataclasses import fields, is_dataclass

import json


class Serializer(json.JSONEncoder):
    """
    Serialize objects into a dictionary.
    """
    def default(self, obj: object):
        if hasattr(obj, 'to_dict'):
            return obj.to_dict()
        return super().default(obj)


class Deserializer(json.JSONDecoder):
    """
    Deserialize dictionary objects back to an object.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(object_hook=self.from_dict, *args, **kwargs)

    def from_dict(self, dictionary: dict) -> object:
        for key, value in dictionary.items():
            if isinstance(value, dict):
                dictionary[key] = self.from_dict(value)
            elif isinstance(value, list):
                for i, e in enumerate(value):
                    if isinstance(e, dict):
                        value[i] = self.from_dict(e)
        return dictionary


def serde(cls: Type[T]) -> Type[T]:
    """
    Decorator to add serialization/deserialization methods to a class.
    """
    setattr(cls, 'to_dict', to_dict)
    setattr(cls, 'from_dict', classmethod(from_dict))
    setattr(cls, 'serialize', serialize)
    setattr(cls, 'deserialize', classmethod(deserialize))

    return cls


def to_dict(obj: object) -> dict:
    """
    Return a dictionary representation of the object.
    """
    if hasattr(obj, '__annotations__'):
        return {f: getattr(obj, f) for f in obj.__annotations__}
    return {}

def from_dict(cls: Type[T], dictionary: dict) -> T:
    """
    Return an instance of the class from a dictionary while also performing type validation.
    """
    obj: T = cls.__new__(cls)

    for field_name, field_type in obj.__annotations__.items():
        if field_name in dictionary:
            value = dictionary[field_name]  # The actual value from the dictionary

            if isinstance(value, list) or isinstance(field_type, _GenericAlias):
                inner_type = field_type.__args__[0]
                # Recursively call from_dict for each element in the list
                value = [inner_type.from_dict(v) if isinstance(v, dict) else v for v in value]
            elif isinstance(value, dict):
                # Recursively call from_dict for nested structures
                value = field_type.from_dict(value)

            # Set the value for each of the fields from the dictionary
            setattr(obj, field_name, value)

    return obj


def serialize(obj: object, indent: int = 2) -> str:
    """
    Return a JSON representation of the object using the Serializer.
    """
    return json.dumps(obj.to_dict(), cls=Serializer, indent=indent)


def deserialize(cls: Type[T], data: str) -> T:
    """
    Return an instance of the class from a JSON string, ensuring it represents a JSON object.
    """
    dictionary: dict = json.loads(data)

    if not isinstance(dictionary, dict):
        raise TypeError(f"{cls.__name__}.deserialize(): expected a JSON object, but got {type(dictionary).__name__}")

    return from_dict(cls, dictionary)
