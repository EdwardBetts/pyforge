from types import *

def renumerate(collection):
    for index in xrange(len(collection) - 1, -1, -1):
        yield (index, collection[index])

### object predicates
def is_bound_method(obj):
    return isinstance(obj, MethodType) and obj.im_self is not None
def is_function(obj):
    return isinstance(obj, FunctionType) or isinstance(obj, BuiltinFunctionType)
def is_class(obj):
    return isinstance(obj, type) or isinstance(obj, ClassType)
def is_class_method(obj):
    if not is_bound_method(obj):
        return False
    return is_class(obj.im_self)

### some useful shortcuts
class EXPECTING(object):

    def __init__(self, mock):
        self.mock = mock
    def __setattr__(self, attr, value):
        if attr == 'mock':
            super(EXPECTING, self).__setattr__(attr, value)
        else:
            self.mock.__forge__.expect_setattr(attr, value)
