# __init__ constructors

class Student:
    def __init__(self, name, age):
        self.name = name
        self.age = age

s1 = Student("Askar", 17)
print(s1.name, s1.age)