class ForgeException(Exception):
    pass

class SignatureException(ForgeException):
    pass

class UnauthorizedMemberAccess(ForgeException):
    def __init__(self, object, attribute):
        super(UnauthorizedMemberAccess, self).__init__()
        self.object = object
        self.attribute = attribute
    def __str__(self):
        return "%s.%s was unexpectedly accessed!" % (self.object, self.attribute)

class UnexpectedCall(ForgeException):
    def __init__(self, expected, got, is_method):
        super(UnexpectedCall, self).__init__()
        self.expected = expected
        self.got = got
        self.is_method = is_method
    def __str__(self):
        returned = "Unexpected %s called!" % ("method" if self.is_method else "function")
        returned += "\n Expected: %s" % (self.expected,)
        returned += "\n Got: %s" % (self.got,)
        return returned

class ExpectedCallsNotFound(ForgeException):
    def __init__(self, calls):
        super(ExpectedCallsNotFound, self).__init__()
        self.calls = calls
    def __str__(self):
        return "Expected calls not found:\n%s" % "\n".join(map(str, self.calls))

