from contextlib import contextmanager
from ut_utils import ForgeTestCase
from forge.stub import FunctionStub
from forge import UnexpectedCall
from forge import ExpectedCallsNotFound
from forge import SignatureException
from forge import ConflictingActions
from forge.dtypes import NOTHING
from forge.stub_handle import StubHandle

def _func1(a, b, c=2):
    raise NotImplementedError()

def _func2(a, b, c=2, *args, **kwargs):
    raise NotImplementedError()




class FunctionStubInitializationTest(ForgeTestCase):

    def test__bind(self):
        def func_with_self(self):
            raise NotImplementedError()
        def func_no_args():
            raise NotImplementedError()
        class Blap(object):
            def already_bound(self):
                raise NotImplementedError()
            def boundable(self):
                raise NotImplementedError()

        some_obj = object()
        with self.assertRaises(SignatureException):
            FunctionStub(self.forge, func_with_self).__forge__.bind(some_obj)
        stub = FunctionStub(self.forge, func_no_args)
        with self.assertRaises(SignatureException):
            stub.__forge__.bind(some_obj)
        stub = FunctionStub(self.forge, Blap().already_bound)
        with self.assertRaises(SignatureException):
            stub.__forge__.bind(some_obj)
        stub = FunctionStub(self.forge, Blap.boundable)
        self.assertFalse(stub.__forge__.signature.is_bound())
        with self.assertRaises(SignatureException):
            stub()
        stub.__forge__.bind(some_obj)
        stub()
        self.forge.replay()
        stub()
        self.forge.verify()
        self.forge.reset()

class FunctionStubRecordTest(ForgeTestCase):
    def setUp(self):
        super(FunctionStubRecordTest, self).setUp()
        def _f():
            raise NotImplementedError()
        self.stub = FunctionStub(self.forge, _f)
    def test__record_invalid_arguments(self):
        args = (1, 2, 3)
        kwargs = dict(a=2, b=3, c=4)
        expected_failure = SignatureException()
        def _fake_get_normalized_args(given_args, given_kwargs):
            self.assertEquals(given_args, args)
            self.assertEquals(given_kwargs, kwargs)
            raise expected_failure
        self.stub.__forge__.signature.get_normalized_args = _fake_get_normalized_args
        with self.assertRaises(SignatureException) as caught:
            self.stub(*args, **kwargs)
        self.assertIs(caught.exception, expected_failure)
        self.assertEquals(len(self.forge.queue), 0)
    def test__record_valid_arguments(self):
        args = (1, 2, 3)
        kwargs = dict(a=2)
        normalized_args = dict(some_key=1, some_other_key=2)
        def _fake_get_normalized_args(given_args, given_kwargs):
            self.assertEquals(given_args, args)
            self.assertEquals(given_kwargs, kwargs)
            return normalized_args
        self.stub.__forge__.signature.get_normalized_args = _fake_get_normalized_args
        self.stub(*args, **kwargs)
        self.assertEquals(len(self.forge.queue), 1)
        expected_call = self.forge.pop_expected_call()
        self.assertIs(expected_call.target, self.stub)
        self.assertIs(expected_call.args, normalized_args)

class FunctionStubReplayTest(ForgeTestCase):
    def setUp(self):
        super(FunctionStubReplayTest, self).setUp()
        self.stub = FunctionStub(self.forge, lambda *args, **kwargs: None)
    def test__record_replay_valid(self):
        self.stub(1, 2, 3)
        self.forge.replay()
        self.stub(1, 2, 3)
        self.forge.verify()
    def test__record_replay_different(self):
        self.stub(1, 2, 3)
        self.forge.replay()
        with self.assertRaises(UnexpectedCall) as caught:
            self.stub(1, 2, 6)
        exc = caught.exception
        self.assertEquals(exc.expected.args, {0:1, 1:2, 2:3})
        self.assertEquals(exc.got.args, {0:1, 1:2, 2:6})
        self.assertExpectedNotMet([self.stub])
    def test__replay_queue_empty(self):
        self.stub(1, 2, 3)
        self.forge.replay()
        self.stub(1, 2, 3)
        with self.assertUnexpectedCall(self.stub, None):
            self.stub(1, 2, 3)
        self.assertNoMoreCalls()
        self.forge.verify()
    def test__record_replay_different_more_args(self):
        self.stub(1, 2, 3)
        self.forge.replay()
        with self.assertRaises(UnexpectedCall) as caught:
            self.stub(1, 2, 3, 4, 5)
        exc = caught.exception
        self.assertEquals(exc.expected.args, {0:1, 1:2, 2:3})
        self.assertEquals(exc.got.args, {0:1, 1:2, 2:3, 3:4, 4:5})
        self.assertExpectedNotMet([self.stub])
    def test__record_replay_different_less_args(self):
        self.stub(1, 2, 3)
        self.forge.replay()
        with self.assertRaises(UnexpectedCall) as caught:
            self.stub()
        exc = caught.exception
        self.assertEquals(exc.expected.args, {0:1, 1:2, 2:3})
        self.assertEquals(exc.got.args, {})
        self.assertExpectedNotMet([self.stub])
    def test__record_replay_no_actual_call(self):
        self.stub(1, 2, 3)
        self.forge.replay()
        self.assertExpectedNotMet([self.stub])
    def assertExpectedNotMet(self, stubs):
        self.assertGreater(len(stubs), 0)
        with self.assertRaises(ExpectedCallsNotFound) as caught:
            self.forge.verify()
        self.assertEquals(len(caught.exception.calls), len(stubs))
        for stub, exception_call in zip(stubs, caught.exception.calls):
            expected_call = self.forge.pop_expected_call()
            self.assertIs(expected_call, exception_call)
            self.assertIs(expected_call.target, stub)
        self.assertNoMoreCalls()
    def assertNoMoreCalls(self):
        self.assertEquals(len(self.forge.queue), 0)
    @contextmanager
    def assertUnexpectedCall(self, got, expected):
        with self.assertRaises(UnexpectedCall) as caught:
            yield caught
        self.assertIs(caught.exception.got.target, got)
        if expected is not None:
            self.assertIs(caught.exception.expected.target, expected)
        else:
            self.assertIsNone(caught.exception.expected)



