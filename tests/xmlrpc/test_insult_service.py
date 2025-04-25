import xmlrpc.client
import unittest
import time

class TestInsultService(unittest.TestCase):
    def setUp(self):
        # Nos conectamos al servidor XMLRPC de InsultService
        self.client = xmlrpc.client.ServerProxy("http://localhost:8000/")

    def test_add_insult(self):
        # Añadir un insulto y comprobar si se ha añadido correctamente
        result = self.client.add_insult("Eres un tonto")
        self.assertTrue(result)  # Debería ser True si se añadió correctamente

    def test_get_insults(self):
        # Añadir un insulto y comprobar si se devuelve en la lista
        self.client.add_insult("Eres un idiota")
        insults = self.client.get_insults()
        self.assertIn("Eres un idiota", insults)

    def test_subscribe_and_broadcast(self):
        # Creamos un suscriptor que pueda recibir insultos
        class Subscriber:
            def __init__(self):
                self.received = None

            def notify(self, insult):
                self.received = insult

        # Crear un suscriptor y suscribirlo al servidor de insultos
        subscriber = Subscriber()
        self.client.add_subscriber(subscriber)

        # Añadir un insulto para que el suscriptor lo reciba
        self.client.add_insult("Eres un morón")

        # Esperamos un poco para que el insulto sea transmitido
        time.sleep(6)

        # Comprobamos que el suscriptor ha recibido el insulto
        self.assertEqual(subscriber.received, "Eres un morón")

    def tearDown(self):
        # Limpiamos los insultos y suscriptores después de cada prueba
        self.client.insults = []
        self.client.subscribers = []

if __name__ == "__main__":
    unittest.main()
