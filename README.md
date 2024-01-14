# serdepy
Serialization and deserialization framework for Python data classes.


# Usage
```py
from serdepy import serde
```

Here's an example of how you serialize a Python data structure that has a nested field:
```py
@serde
@dataclass
class Car:
    name: str
    year: int

@serde
@dataclass
class Person:
    name: str
    age: int
    cars: List[Car]

# We start by creating an instance of our Person data class
p = Person("Tom", 30, [Car("Porshe", 2019), Car("BMW", 2020)])

print(p.serialize()) # This would yield {"name": "Tom", "age": 30, "cars": [{"name": "Porshe", "year": 2019}, {"name": "BMW", "year": 2020}]}
```

We can also convert a JSON input (a Python dictionary is also valid) to an instance of our Person data class:
```py
# Some JSON input as a str, could be from a file or a network request
data = """{
    "name": "Tom",
    "age": 30,
    "cars": [
        {"name": "Porshe", "year": 2019},
        {"name": "BMW", "year": 2020}
    ]
}"""


# We create a Person instance from the JSON data using the deserialize method
p = Person.deserialize(data) 

# Then we can access the dataclass fields as usual
print(p.name) # Tom
```

Validation is done automatically to ensure that mismatched field types are handled during compile time:
```py
# This would throw TypeError: Incorrect type for age: str, expected int instead
data = """{
    "name": "Tom",
    "age": "30",
    ...
}"""
```



# License
This project is licensed under the MIT License - see the LICENSE file for details.
