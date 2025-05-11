import unittest
import Pyro4

class TestPyro4(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Verifica que los servicios están corriendo y que el servicio de filtro está registrado correctamente"""
        try:
            # Intentar conectar a InsultService
            cls.insult_service = Pyro4.Proxy("PYRONAME:mi.insultservice")  # Usamos Pyro4.Proxy para conectar con Pyro
            # Intentar conectar a InsultFilter
            cls.insult_filter = Pyro4.Proxy("PYRONAME:mi.insultfilter")  # Usamos Pyro4.Proxy para conectar con Pyro
            
            # Intentar agregar el filtro como suscriptor
            cls.insult_service.add_subscriber("PYRONAME:mi.insultfilter")
            print("Conexión con el servicio y suscripción exitosas.")
        except Exception as e:
            print("Error al conectar a los servicios:", e)
            raise

    def test_connection(self):
        """Prueba si los servicios están conectados y funcionando."""
        self.assertIsNotNone(self.insult_service)
        self.assertIsNotNone(self.insult_filter)

if __name__ == "__main__":
    unittest.main()
