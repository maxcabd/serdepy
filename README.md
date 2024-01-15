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
# Some JSON input as a str, could be from a file or a network request.
data = """{
    "name": "Tom",
    "age": 30,
    "cars": [
        {"name": "Porshe", "year": 2019},
        {"name": "BMW", "year": 2020}
    ]
}"""


# We create a Person instance from the JSON data using the deserialize method.
p = Person.deserialize(data) 

# Then we can access the dataclass fields as usual.
print(p.name) # Tom
```


Validation is done automatically to ensure that mismatched field types are handled during compile time:
```py
# This would throw TypeError: Incorrect type for age: str, expected int instead.
data = """{
    "name": "Tom",
    "age": "30",
    ...
}"""
```


In cases where a custom `__init__` method conflicts with the automatically generated `__init__` method, the `dataclass` decorator can be ommitted:
```py
# Using a declarative approach to reading binary data from the PyBinaryReader module which uses a custom __init__ method.
@serde
class Person(BrStruct):
    name: str
    age: int
    cars: List[Car]

    def __br_read__(self, br: BinaryReader) -> None:
        br.set_endian(Endian.LITTLE)

        self.name = br.read_str()
        self.age = br.read_int32()

        self.cars = br.read_struct(Car, 2)

file = open("example.bin", "rb")

with BinaryReader(file.read()) as br:
    p: Person = br.read_struct(Person)
```


The binary data can then be serialized:
```
4A 6F 68 6E 00 1E 00 00 00 4D 
63 43 6C 61 72 65 6E 00 E4 07 
00 00 4D 65 72 63 65 64 65 73 
00 DF 07 00 00
```

```py
print(p.serialize()) # output: {"name": "John", "age": 30, "cars": ["name": "McClaren", "year": 2020}, {"name": "Mercedes", "year": 2015}]}
```


# License
This project is licensed under the MIT License - see the LICENSE file for details.
