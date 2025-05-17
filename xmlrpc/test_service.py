import unittest
from xmlrpc.client import ServerProxy
import xmlrpc.server
import threading
import time
import xmlrpc.client

class TestXMLRPCServices(unittest.TestCase):
    def setUp(self):
        try:
            self.service = ServerProxy('http://localhost:8000')
            self.filter = ServerProxy('http://localhost:8001')
            self.client_server = xmlrpc.server.SimpleXMLRPCServer(("localhost", 9000), allow_none=True)
            self.received_insults = []
            self.client_server.register_function(self.notify, 'notify')
            self.client_thread = threading.Thread(target=self.client_server.serve_forever)
            self.client_thread.daemon = True
            self.client_thread.start()
        except xmlrpc.client.Fault as e:
            self.fail(f"Error conectando a los servidores: {e}")
        except ConnectionError as e:
            self.fail(f"Error de conexión: {e}")

    def notify(self, insult):
        self.received_insults.append(insult)
        return True

    def test_insult_service(self):
        try:
            self.service.clear_insults()
            self.assertTrue(self.service.add_insult("tonto"))
            self.assertFalse(self.service.add_insult("tonto"))
            self.assertEqual(self.service.get_insults(), ["tonto"])
            self.assertTrue(self.service.add_subscriber('http://localhost:9000'))
            time.sleep(10)
            self.assertTrue(len(self.received_insults) > 0, "No se recibieron notificaciones")
            self.assertIn("tonto", self.received_insults)
        except xmlrpc.client.Fault as e:
            self.fail(f"Error en InsultService: {e}")

    def test_filter_service(self):
        try:
            self.filter.clear_filtered_texts()
            self.filter.filter_insults("Eres tonto")
            time.sleep(1)
            filtered_texts = self.filter.get_filtered_texts()
            self.assertEqual(filtered_texts, ["Eres CENSORED"])
        except xmlrpc.client.Fault as e:
            self.fail(f"Error en InsultFilter: {e}")

    def tearDown(self):
        self.client_server.shutdown()

if __name__ == '__main__':
    unittest.main(verbosity=2)