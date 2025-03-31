import unittest

from spyllm.core import Singleton
from spyllm.event_processor import EventProcessor


class TestHybridSingleton(unittest.TestCase):

    def setUp(self):
        self.singleton = Singleton[EventProcessor]()

    def test_initialize(self):
        service = self.singleton.initialize(EventProcessor)
        self.assertIsInstance(service, EventProcessor)

    def test_get_instance(self):
        service1 = self.singleton.initialize(EventProcessor)
        service2 = self.singleton.get_instance()
        self.assertIs(service1, service2)

    def test_reset(self):
        self.singleton.initialize(EventProcessor)
        self.singleton.reset()
        with self.assertRaises(RuntimeError):
            self.singleton.get_instance()

if __name__ == '__main__':
    unittest.main()