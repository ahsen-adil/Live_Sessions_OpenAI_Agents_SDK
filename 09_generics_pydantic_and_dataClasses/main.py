# simple class

# class Person:
#     def __init__(self, name , age):
#         self.name = name 
#         self.age = age

#     def welcome(self):
#         return f"Person(name={self.name}, age={self.age})"
    
# p1 = Person("Alice", 30)
# print(p1.welcome()) 

# use data classes

# from dataclasses import dataclass

# @dataclass
# class Person:
#     name : str
#     age : int

#     def welcome(self):
#        return f"Person(name={self.name}, age={self.age})"
    

# p1 = Person("ahsen",22)
# print(p1.welcome())

# # using pydantic
# from pydantic import BaseModel

# class PersonPydantic(BaseModel):
#     name: str
#     age: int

#     def welcome(self):
#         return f"PersonPydantic(name={self.name}, age={self.age})"
    
# p3 = PersonPydantic(name="Charlie", age=35)
# print(p3.welcome())

# generics  

# from typing import TypeVar, Generic
# from dataclasses import dataclass

# T = TypeVar('T')

# @dataclass
# class Person(Generic[T]):
#     name : T
#     age : T

#     def welcome(self) -> T :
#        return f"Person(name={self.name}, age={self.age})"
    

# p1 = Person("ahsen",22)
# print(p1.welcome())





































