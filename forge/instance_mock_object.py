from instance_mock_handle import InstanceMockHandle
from mock_object import MockObject

class InstanceMockObject(MockObject):
    def __init__(self, forge, mocked_class):
        super(InstanceMockObject, self).__init__()
        self.__forge__ = InstanceMockHandle(forge, self, mocked_class)
    @property
    def __class__(self):
        return self.__forge__.mocked_class
