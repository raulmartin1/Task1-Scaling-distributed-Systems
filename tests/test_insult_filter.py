import xmlrpc.client
import unittest

class TestInsultFilter(unittest.TestCase):
    def setUp(self):
        self.client = xmlrpc.client.ServerProxy("http://localhost:8001/")

    def test_filter_insults(self):
        insults = ["fool", "idiot"]
        text = "You are a fool and an idiot!"
        filtered_text = self.client.filter_insults(text, insults)
        self.assertEqual(filtered_text, "You are a CENSORED and an CENSORED!")

    def test_get_filtered_texts(self):
        insults = ["fool", "idiot"]
        text = "You are a fool and an idiot!"
        self.client.filter_insults(text, insults)
        filtered_texts = self.client.get_filtered_texts()
        self.assertIn("You are a CENSORED and an CENSORED!", filtered_texts)

if __name__ == "__main__":
    unittest.main()

