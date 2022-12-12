import unittest
import logging


# noinspection PyArgumentList
class TestRunner(unittest.TestCase):
    pass

    def __init__(self, *args, **kwargs):
        super(TestRunner, self).__init__(*args, **kwargs)
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s [%(levelname)s] %(message)s",
            datefmt='%Y-%m-%d %H:%M:%S',
            handlers=[
                logging.FileHandler("test_log.log"),
                logging.StreamHandler()
            ]
        )
