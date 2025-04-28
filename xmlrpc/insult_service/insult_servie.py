import xmlrpc.server
import random
import threading

class InsultService:
    def __init__(self):
        self.insults = [
            "tonto", "idiota", "estúpido", "imbécil", "bobo", 
            "cabeza de chorlito", "morón", "burro", "papanatas", 
            "pelmazo", "torpe", "bestia", "bruto", "tonto el culo"
        ]
        self.subscribers = []

    # Método para añadir un insulto
    def add_insult(self, insult):
        if insult not in self.insults:
            self.insults.append(insult)
            # Notificar a los suscriptores cuando se agrega un nuevo insulto
            for subscriber in self.subscribers:
                subscriber.notify(insult)
            print(f"InsultService: Insulto '{insult}' agregado.")
            return True
        return False

    # Método para obtener la lista de insultos
    def get_insults(self):
        return self.insults

    # Método para obtener un insulto aleatorio
    def insult_me(self):
        if self.insults:
            return random.choice(self.insults)
        return "No hay insultos disponibles."

    # Método para registrar nuevos suscriptores
    def add_subscriber(self, subscriber):
        self.subscribers.append(subscriber)
        print(f"InsultService: Nuevo suscriptor agregado.")
        return True

# Función para ejecutar el servidor de InsultService
def run_insult_server():
    server = xmlrpc.server.SimpleXMLRPCServer(("localhost", 8000))
    insult_service = InsultService()
    server.register_instance(insult_service)
    print("InsultService está funcionando en el puerto 8000...")
    server.serve_forever()

if __name__ == "__main__":
    # Ejecutar el servidor de InsultService
    run_insult_server()
