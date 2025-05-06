import xmlrpc.server
import random
import threading

class InsultService:
    def __init__(self):
        # Lista de insultos con palabras sueltas
        self.insults = [
            "tonto", "idiota", "estúpido", "imbécil", "bobo", 
            "morón", "burro", "papanatas", "pelmazo", "torpe", 
            "bestia", "bruto"
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
        print(f"InsultService: El insulto '{insult}' ya está en la lista.")
        return False  # El insulto ya estaba en la lista

    # Método para obtener la lista de insultos
    def get_insults(self):
        return self.insults

    # Método para obtener un insulto aleatorio
    def insult_me(self):
        if self.insults:
            return random.choice(self.insults)
        return "No hay insultos disponibles."

    # Método para registrar nuevos suscriptores, sin duplicados
    def add_subscriber(self, subscriber):
        if subscriber not in self.subscribers:
            self.subscribers.append(subscriber)
            print(f"InsultService: Nuevo suscriptor agregado.")
            return True
        print(f"InsultService: El suscriptor ya está registrado.")
        return False

# Función para ejecutar el servidor de InsultService con hilos
def run_insult_server():
    server = xmlrpc.server.SimpleXMLRPCServer(("localhost", 8000))
    insult_service = InsultService()
    server.register_instance(insult_service)
    print("InsultService está funcionando en el puerto 8000...")
    
    # Ejecutar el servidor en un hilo
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.start()

if __name__ == "__main__":
    run_insult_server()
