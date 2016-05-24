#!/usr/bin/python3
# Eliminates usage of show.

from pprint import pprint, pformat

class show:
    def fset(where=False, fmtfunc=pformat, show=False):
        pass

    def fprettyprint():
        pass

    show = True
    where = True
    fmtfunc = pformat
    set = fset
    prettyprint = fprettyprint

    def __new__(self, *args, **kwargs):
        for arg in args:
            pprint(arg)

