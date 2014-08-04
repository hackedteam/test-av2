__author__ = 'zeno'


class Box:
    whatever = 123
    def __init__(self):
        self.whatever = 1


def test_class():

    assert Box.whatever == 123
    b = Box()
    assert b.whatever == 1
    assert Box.whatever == 123


if __name__ == "__main__":
    test_class()