import Pyro4
import random
import threading

@Pyro4.expose
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
        return True

# Función para ejecutar el servidor de InsultService
def run_insult_server():
    daemon = Pyro4.Daemon()  # Crea un daemon para el servidor
    ns = Pyro4.locateNS()  # Localiza el nombre del servidor Pyro
    uri = daemon.register(InsultService)  # Registra el servicio
    ns.register("example.insultservice", uri)  # Registra el servicio en el servidor de nombres

    print("InsultService está funcionando...")
    daemon.requestLoop()  # Mantiene el servidor en ejecución

if __name__ == "__main__":
    run_insult_server()
