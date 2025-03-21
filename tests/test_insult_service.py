import xmlrpc.client
import unittest

class TestInsultService(unittest.TestCase):
    def setUp(self):
        self.client = xmlrpc.client.ServerProxy("http://localhost:8000/")

    def test_add_insult(self):
        result = self.client.add_insult("You are a fool!")
        self.assertTrue(result)

    def test_get_insults(self):
        self.client.add_insult("You are a fool!")
        insults = self.client.get_insults()
        self.assertIn("You are a fool!", insults)

if __name__ == "__main__":
    unittest.main()
