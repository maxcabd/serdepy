from typing import T
from dataclasses import fields, is_dataclass
import json


class CustomJSONEncoder(json.JSONEncoder):
	"""
	Custom JSON encoder that converts objects to dicts
	"""
	def default(self, obj: object):
		if hasattr(obj, 'to_dict'): # Usually most of the objects will have a to_dict method but we want to be sure
				return obj.to_dict()
		return super().default(obj)


class CustomJSONDecoder(json.JSONDecoder):
	"""
	Custom JSON decoder that converts dicts to objects.
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(object_hook=self.from_dict, *args, **kwargs)

	def from_dict(self, dictionary: dict) -> dict:
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
    obj: object = cls.__new__(cls)

    for field in fields(cls):
        field_name: str = field.name
        field_type: str = field.type

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
	Return a JSON representation of the object.
	"""
	return json.dumps(self.to_dict(), cls=CustomJSONEncoder, indent=indent)


def deserialize(cls, json_str: str) -> object:
	"""
	Return an instance of the class from a JSON string.
	"""
	dictionary: dict = json.loads(json_str)

	if not isinstance(dictionary, dict): # We want to ensure that the JSON string is a JSON object and not just a dict
			raise TypeError(f"{cls.__name__}.deserialize(): expected a JSON object, but got {type(dictionary).__name__}")
	return cls.from_dict(dictionary)
