"""
Coding concepts.
"""


# pylint: disable=R0903
class Curry(object):
    """ Supports curry algorithm.
    defer calling a function with a specific set of parameters.
    """

    def __init__(self, func, *args, **kwargs):
        """ Store arguments and function for later. """
        self.func = func
        self.pending = args[:]
        self.kwargs = kwargs.copy()

    def __call__(self, *args, **kwargs):
        """ Call's the self.func with arguments now. """

        if kwargs and self.kwargs:
            kwarg = self.kwargs.copy()
            kwarg.update(kwargs)
        else:
            kwarg = kwargs or self.kwargs

        return self.func(*(self.pending + args), **kwarg)
