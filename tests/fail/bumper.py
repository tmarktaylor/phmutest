class MyBumper:
    def __init__(self, value):
        self.value = value

    def bump(self):
        self.value = helper(self.value)
        return self.value


def helper(value):
    return value + 1
