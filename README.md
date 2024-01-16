# serdepy
Serialization and deserialization framework for Python data classes.


# Usage
```py
from typing import List
from serdepy import serde

@dataclass
@serde
class Car:
    name: str
    year: int

@dataclass
@serde
class Person:
    name: str
    age: int
    is_alive: bool
    cars: List[Car]

def main():
    # Create a Person instance with some data
    p = Person('John', 25, True, [Car('BMW', 2010), Car('Audi', 2015)])

    # Serialize the Person instance to a JSON string
    serialized = p.serialize()

    # Prints the serialized data: {"name": "John", "age": 25, "is_alive": true, "cars": [{"name": "BMW", "year": 2010}, {"name": "Audi", "year": 2015}]}
    print(serialized)

    # Deserialize the data string back to a Person instance
    deserialized: Person = Person.deserialize(serialized)

    # Prints the deserialized object: Person(name='John', age=25, is_alive=True, cars=[Car(name='BMW', year=2010), Car(name='Audi', year=2015)])
    print(deserialized) 
```


# License
This project is licensed under the MIT License - see the LICENSE file for details.
