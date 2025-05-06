import xmlrpc.server
import random
import threading

class InsultService:
    def __init__(self):
        self.insults = [
            "tonto", "idiota", "estúpido", "imbécil", "bobo", 
            "burro", "papanatas", "pelmazo", "torpe", 
            "bestia", "bruto"
        ]
        self.subscribers = []  # Lista de suscriptores (URLs)

    # Método para añadir un insulto
    def add_insult(self, insult):
        if insult not in self.insults:
            self.insults.append(insult)
            # Notificar a todos los suscriptores cuando se agrega un nuevo insulto
            for subscriber_url in self.subscribers:
                subscriber = xmlrpc.client.ServerProxy(subscriber_url)
                subscriber.notify(insult)  # Llamar al método 'notify' del suscriptor
            print(f"InsultService: Insulto '{insult}' agregado y notificado a suscriptores.")
            return True
        print(f"InsultService: El insulto '{insult}' ya está en la lista.")
        return False  # El insulto ya estaba en la lista

    # Método para obtener la lista de insultos
    def get_insults(self):
        return self.insults

    # Método para registrar nuevos suscriptores
    def add_subscriber(self, subscriber_url):
        if subscriber_url not in self.subscribers:
            self.subscribers.append(subscriber_url)
            print(f"InsultService: Nuevo suscriptor registrado.")
            return True
        print(f"InsultService: El suscriptor ya está registrado.")
        return False

# Función para ejecutar el servidor de InsultService
def run_insult_server():
    server = xmlrpc.server.SimpleXMLRPCServer(("localhost", 8000))
    insult_service = InsultService()
    server.register_instance(insult_service)
    print("InsultService está funcionando en el puerto 8000...")
    server.serve_forever()

if __name__ == "__main__":
    run_insult_server()
