import unittest
import xmlrpc.client
import random
import time

class TestXMLRPC(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # Conectar a los servidores de InsultService e InsultFilter
        cls.insult_service = xmlrpc.client.ServerProxy("http://localhost:8000/")
        cls.insult_filter = xmlrpc.client.ServerProxy("http://localhost:8001/")
        
        # Registrar InsultFilter como suscriptor en InsultService
        cls.insult_service.add_subscriber("http://localhost:8001/")

    def test_add_insult(self):
        # Probar si un insulto se agrega correctamente
        result = self.insult_service.add_insult("patán")
        self.assertTrue(result, "El insulto no se agregó correctamente.")
        
        # Intentar agregar el mismo insulto de nuevo
        result = self.insult_service.add_insult("patán")
        self.assertFalse(result, "El insulto ya debería estar en la lista.")
        
    def test_get_insults(self):
        # Obtener la lista de insultos
        insults = self.insult_service.get_insults()
        self.assertIn("patán", insults, "El insulto 'patán' no está en la lista.")
    
    def test_filter_insults(self):
        # Filtrar un texto usando el servidor InsultFilter
        text = "Eres un patán y un imbécil"
        filtered_text = self.insult_filter.filter_insults(text, ["patán", "imbécil"])
        self.assertEqual(filtered_text, "Eres un CENSURADO y un CENSURADO", "El texto no fue filtrado correctamente.")
    
    def test_notify(self):
        # Verificar si el notify funciona en InsultFilter
        self.insult_filter.notify("tonto")
        filtered_texts = self.insult_filter.get_filtered_texts()
        self.assertIn("Eres un CENSURADO", filtered_texts, "El insulto no fue filtrado correctamente.")

if __name__ == "__main__":
    unittest.main()
