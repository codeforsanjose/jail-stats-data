#!/usr/bin/python3

from pprint import pprint

class T1(object):
    def __init__(self, x="x", y="y"):
        self.x = x
        self.y = y
        pprint(self.__dict__)

    def __call__(self):
        self.f1()

    def f1(self):
        print("x: {}  y: {}".format(self.x, self.y))

    def f2(self):
        for n in range(6):
            try:
                print("n: {}".format(n))
                x = 10/n
                if n == 2:
                    raise NameError("xyz")
            except ZeroDivisionError:
                print("zero div error")
                # continue
            except:
                print("some other exception...")

def main():
    d = dict()
    d["x"] = "this is x"
    d["y"] = "whyyyyy"

    dt1 = T1(**d)
    dt1.f1()
    dt1.f2()

if __name__ == "__main__":
    main()    