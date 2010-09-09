from forge import UnexpectedCall, ExpectedCallsNotFound, SignatureException
from ut_utils import ForgeTestCase

class RecordReplayTest(ForgeTestCase):
    def setUp(self):
        super(RecordReplayTest, self).setUp()
        def some_function(a, b, c):
            raise NotImplementedError()
        self.stub = self.forge.create_function_stub(some_function)
    def tearDown(self):
        self.assertNoMoreCalls()
        super(RecordReplayTest, self).tearDown()
    def test__record_replay_valid(self):
        self.stub(1, 2, 3)
        self.forge.replay()
        self.stub(1, 2, 3)
        self.forge.verify()
    def test__record_replay_different_not_equal_value(self):
        self.stub(1, 2, 3)
        self.forge.replay()
        with self.assertRaises(UnexpectedCall) as caught:
            self.stub(1, 2, 6)
        exc = caught.exception
        self.assertEquals(exc.expected.args, dict(a=1, b=2, c=3))
        self.assertEquals(exc.got.args, dict(a=1, b=2, c=6))
        self.assertExpectedNotMet([self.stub])
    def test__record_replay_different_more_args(self):
        self.stub(1, 2, 3)
        self.forge.replay()
        with self.assertRaises(SignatureException):
            self.stub(1, 2, 3, 4, 5)
        self.assertExpectedNotMet([self.stub])
    def test__record_replay_different_less_args(self):
        self.stub(1, 2, 3)
        self.forge.replay()
        with self.assertRaises(SignatureException):
            self.stub()
        self.assertExpectedNotMet([self.stub])
    def test__record_replay_no_actual_call(self):
        self.stub(1, 2, 3)
        self.forge.replay()
        self.assertExpectedNotMet([self.stub])

    def test__replay_queue_empty_after_calls(self):
        self.stub(1, 2, 3)
        self.forge.replay()
        self.stub(1, 2, 3)
        with self.assertRaises(UnexpectedCall) as caught:
            self.stub(1, 2, 3)
        self.assertIs(caught.exception.expected, None)
        self.assertIs(caught.exception.got.target, self.stub)
        self.assertNoMoreCalls()
        self.forge.verify()
    def test__replay_queue_empty(self):
        self.forge.replay()
        with self.assertRaises(UnexpectedCall) as caught:
            self.stub(1, 2, 3)
        self.assertIs(caught.exception.expected, None)
        self.assertIs(caught.exception.got.target, self.stub)
        self.assertNoMoreCalls()
        self.forge.verify()
    def test__naming_stubs(self):
        def some_other_function():
            raise NotImplementedError()
        stub2 = self.forge.create_function_stub(some_other_function)
        self.stub(1, 2, 3)
        self.forge.replay()
        with self.assertRaises(UnexpectedCall) as caught:
            stub2()
        exc = caught.exception
        for r in (str, repr):
            self.assertIn('some_function', r(exc.expected))
            self.assertIn('some_other_function', r(exc.got))
        self.assertIn('some_function', str(exc))
        self.assertIn('some_other_function', str(exc))
        self.forge.reset()
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




