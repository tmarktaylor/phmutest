class MyBumper:
    def __init__(self, value):
        self.value = value

    def bump(self):
        self.value += 1
        return self.value
