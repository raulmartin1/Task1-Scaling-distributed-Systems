import xmlrpc.server
import random
import threading
import time

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
                try:
                    subscriber = xmlrpc.client.ServerProxy(subscriber_url)
                    subscriber.notify(insult)  # Llamar al método 'notify' del suscriptor
                    print(f"InsultService: Insulto '{insult}' agregado y notificado a suscriptores.")
                except Exception as e:
                    print(f"Error notificando al suscriptor {subscriber_url}: {e}")
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

    # Método para enviar insultos cada 5 segundos
    def broadcast_insults(self):
        while True:
            if self.insults:
                insult = random.choice(self.insults)
                for subscriber_url in self.subscribers:
                    try:
                        subscriber = xmlrpc.client.ServerProxy(subscriber_url)
                        subscriber.notify(insult)
                        print(f"InsultService: Insulto '{insult}' publicado a suscriptores.")
                    except Exception as e:
                        print(f"Error notificando al suscriptor {subscriber_url}: {e}")
            time.sleep(5)

# Función para ejecutar el servidor de InsultService
def run_insult_server():
    server = xmlrpc.server.SimpleXMLRPCServer(("localhost", 8000), allow_none=True)  # Habilitar None
    insult_service = InsultService()
    server.register_instance(insult_service)
    print("InsultService está funcionando en el puerto 8000...")

    # Iniciar el broadcast en un hilo
    threading.Thread(target=insult_service.broadcast_insults, daemon=True).start()

    server.serve_forever()

if __name__ == "__main__":
    run_insult_server()
