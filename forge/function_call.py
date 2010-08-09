class FunctionCall(object):
    def __init__(self, target, args, kwargs):
        super(FunctionCall, self).__init__()
        self.target = target
        self.args = self.get_signature().get_normalized_args(args, kwargs)
        self._return_value = None    
    def get_signature(self):
        return self.target._signature
    def matches_call(self, target, args, kwargs):
        return self.target is target and self.get_signature().get_normalized_args(args, kwargs) == self.args
    def __str__(self):
        return "<Function call: %s(%s)" % (self.target, self._get_argument_string())
    def _get_argument_string(self):
        args = ["%s=%s" % (arg_name, value) for arg_name, value in sorted(self.args.iteritems())
                if isinstance(arg_name, basestring)]
        args.extend(str(value) for arg_name, value in sorted((k, v) for k, v in self.args.iteritems()
                                                        if not isinstance(k, basestring)))
        return ", ".join(args)
    def and_return(self, rv):
        self._return_value = rv
        return rv
    def get_return_value(self):
        return self._return_value
        
