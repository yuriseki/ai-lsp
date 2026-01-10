class Hello(object):
    def __init__(self, name):
        self.name = name

    def greet(self):
        print("Hello, " + self.name)


class Calculator:
    def sum(self, a, b):
        return a + b

    def multiply(self, a, b):
        return a * b

class Polygon:
    def __init__(self, sides=0):
        self.sides = sides

    def perimeter(self):
        return sum([self.sides[i] for i in range(len(self.sides))])

    def area(self):
        return multiply(self.sides)

class Dog:
    def  __init__(self, name: str, race: str, age: int):
        STRICT

