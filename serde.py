from typing import T
from dataclasses import fields, is_dataclass
import json


class CustomJSONEncoder(json.JSONEncoder):
	"""
	Custom JSON encoder that converts objects to dicts
	"""
	def default(self, o):
			if hasattr(o, 'to_dict'): # Usually most of the objects will have a to_dict method but we want to be sure
					return o.to_dict()
			return super().default(o)


class CustomJSONDecoder(json.JSONDecoder):
	"""
	Custom JSON decoder that converts dicts to objects.
	"""
	def __init__(self, *args, **kwargs):
			super().__init__(object_hook=self.from_dict, *args, **kwargs)

	def from_dict(self, d: dict):
			for k, v in d.items():
					if isinstance(v, dict):
							d[k] = self.from_dict(v)
					elif isinstance(v, list):
							for i, e in enumerate(v):
									if isinstance(e, dict):
											v[i] = self.from_dict(e)
			return d


def serde(cls: T) -> T:
	"""
	Decorator to add serialization methods to a dataclass.
	"""
	setattr(cls, 'to_dict', to_dict)
	setattr(cls, 'from_dict', classmethod(from_dict))
	setattr(cls, 'serialize', serialize)
	setattr(cls, 'deserialize', classmethod(deserialize))
	return cls


def to_dict(self) -> dict:
	"""
	Return a dict representation of the object. 
	"""
	return {f.name: getattr(self, f.name) for f in fields(self)}


def from_dict(cls, dictionary: dict) -> object:
    """
    Return an instance of the class from a dict while checking types to ensure data validation.
    """
    obj = cls.__new__(cls)

    for field in fields(cls):
        field_name = field.name
        field_type = field.type

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
                raise TypeError(f"Incorrect type for {field_name}: {str(type(value).__name__)}, expected {str(field_type.__name__)}")
            
            setattr(obj, field_name, value)

    return obj


def serialize(self, indent: int = 2) -> str:
	"""
	Return a JSON representation of the object.
	"""
	return json.dumps(self.to_dict(), cls=CustomJSONEncoder, indent=indent)


def deserialize(cls, json_str: str) -> object:
	"""
	Return an instance of the class from a JSON string.
	"""
	dictionary = json.loads(json_str)

	if not isinstance(dictionary, dict): # We want to ensure that the JSON string is a JSON object and not just a dict
			raise TypeError(f"{cls.__name__}.deserialize(): expected a JSON object, but got {type(dictionary).__name__}")
	return cls.from_dict(dictionary)
