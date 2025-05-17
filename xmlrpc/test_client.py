from xmlrpc.client import ServerProxy
import xmlrpc.server
import threading
import time
import socket

class TestClient:
    def __init__(self):
        self.service = ServerProxy('http://localhost:8000')
        self.filter = ServerProxy('http://localhost:8001')
        # Servidor para recibir notificaciones
        self.client_server = xmlrpc.server.SimpleXMLRPCServer(("localhost", 9000), allow_none=True)
        self.client_server.register_function(self.notify, 'notify')
        self.client_thread = threading.Thread(target=self.client_server.serve_forever)
        self.client_thread.daemon = True
        self.client_thread.start()

    def notify(self, insult):
        print(f"Cliente recibió insulto: {insult}")
        return True

    def test_insult_service(self):
        print("Probando InsultService...")
        print("Limpiando insultos:", self.service.clear_insults())
        print("Añadiendo 'tonto':", self.service.add_insult("tonto"))
        print("Añadiendo 'tonto' otra vez:", self.service.add_insult("tonto"))
        print("Añadiendo 'idiota':", self.service.add_insult("idiota"))
        print("Lista de insultos:", self.service.get_insults())
        print("Suscribiendo cliente:", self.service.add_subscriber('http://localhost:9000'))
        print("Esperando broadcasts (10 segundos)...")
        time.sleep(10)
        print("Desuscribiendo cliente:", self.service.remove_subscriber('http://localhost:9000'))

    def test_insult_filter(self):
        print("\nProbando InsultFilter...")
        print("Limpiando textos filtrados:", self.filter.clear_filtered_texts())
        print("Enviando texto 'Eres tonto':", self.filter.filter_insults("Eres tonto"))
        time.sleep(1)
        print("Textos filtrados:", self.filter.get_filtered_texts())

if __name__ == "__main__":
    try:
        # Verificar que el puerto 9000 está libre
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 9000))
        sock.close()
        if result == 0:
            print("Error: El puerto 9000 está ocupado. Libéralo antes de continuar.")
            exit(1)
        client = TestClient()
        client.test_insult_service()
        client.test_insult_filter()
    except ConnectionError as e:
        print(f"Error de conexión: {e}. Asegúrate de que los servidores están corriendo en los puertos 8000 y 8001.")
    except xmlrpc.client.Fault as e:
        print(f"Error en el servidor: {e}")