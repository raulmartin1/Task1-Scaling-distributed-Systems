import xmlrpc.client
import unittest

class TestInsultFilter(unittest.TestCase):
    def setUp(self):
        # Nos conectamos al servidor XMLRPC de InsultFilter
        self.client = xmlrpc.client.ServerProxy("http://localhost:8001/")

    def test_filter_insults(self):
        # Definimos los insultos a filtrar
        insults = ["tonto", "idiota"]
        text = "Eres un tonto y un idiota"
        # Filtrar el texto usando el servicio
        filtered_text = self.client.filter_insults(text, insults)
        # Comprobamos que el texto filtrado es correcto
        self.assertEqual(filtered_text, "Eres un CENSURADO y un CENSURADO")

    def test_get_filtered_texts(self):
        # Añadimos un texto con insultos
        insults = ["tonto", "idiota"]
        text = "Eres un tonto y un idiota"
        self.client.filter_insults(text, insults)
        # Obtenemos los textos filtrados
        filtered_texts = self.client.get_filtered_texts()
        # Verificamos que el texto filtrado se encuentra en la lista
        self.assertIn("Eres un CENSURADO y un CENSURADO", filtered_texts)

    def tearDown(self):
        # Limpiamos los textos filtrados después de cada prueba
        self.client.filtered_texts = []

if __name__ == "__main__":
    unittest.main()
