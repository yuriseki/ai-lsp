class test:
    print "Hello, it is a test"

if __name__ == "__main__":
  test()

class Hello(object):
    def __init__(self, name):
        self.name = name

    def greet(self):
        print("Hello, " + self.name)

class Calculator:
    def sum(a, b):
        return a + b

    def subtraction(self, a, b):
        return a - b

    def multiply(self, s):
    return self.sum(s, s)



