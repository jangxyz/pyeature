
class Calculator:
    def __init__(self):
        self.stack = []

    def append(self, n):
        self.stack.append(n)

    def add(self):
        sum = self.stack.pop() + self.stack.pop()
        return sum

