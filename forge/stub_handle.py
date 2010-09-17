from handle import ForgeHandle
from signature import FunctionSignature
from .dtypes import WILDCARD_FUNCTION
from .bound_signature_adapter import BoundSignatureAdapter

class StubHandle(ForgeHandle):
    def __init__(self, forge, stub, original, name=None, parent=None):
        super(StubHandle, self).__init__(forge)
        self.stub = stub
        self.original = original
        self.signature = FunctionSignature(self.original)
    def _describe(self):
        return self.original.__name__
    def bind(self, obj):
        self.signature = BoundSignatureAdapter(self.signature, obj)
    def is_bound(self):
        return self.signature.is_bound()
    def handle_call(self, args, kwargs):
        if self.forge.is_recording():
            returned = self._handle_recorded_call(args, kwargs)
            self.forge.stubs.mark_stub_recorded(self.stub)
            return returned
        else:
            return self._handle_replay_call(args, kwargs)
    def _handle_recorded_call(self, args, kwargs):
        return self.forge.queue.push_call(self.stub, args, kwargs)
    def _handle_replay_call(self, args, kwargs):
        expected_call = self.forge.queue.pop_matching_call(self.stub, args, kwargs)
        return_value = expected_call.get_return_value()
        #might raise...
        expected_call.do_side_effects(args, kwargs)
        return return_value
    def has_recorded_calls(self):
        return self.forge.stubs.was_stub_recorded(self.stub)

