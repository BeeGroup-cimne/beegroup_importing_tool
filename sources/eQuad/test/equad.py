import unittest

import utils.utils
from sources.eQuad.gather import get_projects, get_token


class SourceCase(unittest.TestCase):
    token = ''

    def setUp(self):
        self.config = utils.utils.read_config('../../../config.json')['eQuad']

    def test_1_get_token(self):
        response = get_token(**self.config)
        self.assertTrue(response.ok)
        self.__class__.token = response.json()['token']

    def test_2_get_project(self):
        response = get_projects(self.__class__.token)
        self.assertTrue(response.ok)
        self.assertTrue(isinstance(response.json(), list))
        self.assertTrue(len(response.json()) > 0)


if __name__ == '__main__':
    unittest.main()
