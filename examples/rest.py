import json
import requests
import unittest
import testpool.core.commands

TEST_URL = "http://127.0.0.1:8000/testpool/api/"
class Testsuite(unittest.TestCase):
    def test_profile_list(self):
        """ test_profile_list. """
        arg_parser = testpool.core.commands.main()

        cmd = "profile add localhost fake fake.profile fake.template 10"
        args = arg_parser.parse_args(cmd.split())
        self.assertEqual(testpool.core.commands.args_process(args), 0)

        url = TEST_URL + "profiles"
        resp = requests.get(url)
        resp.raise_for_status()
        profiles = json.loads(resp.text)
        self.assertEqual(len(profiles), 1)
        self.assertEqual(profiles[0]["name"], "fake.profile")
