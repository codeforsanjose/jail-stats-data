#!/usr/bin/python3

class T1:
    def __init__(self, x="x", y="y"):
        self.x = x
        self.y = y
        var(self)

    def __call__(self):
        self.f1()

    def f1(self):
        print("x: {}  y: {}".format(self.x, self.y))

def main():
    d = dict()
    d["x"] = "this is x"
    d["y"] = "whyyyyy"
    d["z"] = "zzzebra"

    dt1 = T1(**d)
    var(dt1)

if __name__ == "__main__":
    main()    