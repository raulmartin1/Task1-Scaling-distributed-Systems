import Pyro4

@Pyro4.expose
class InsultService:
    def __init__(self):
        self.insults = [
            "tonto", "idiota", "estúpido", "imbécil", "bobo", 
            "burro", "papanatas", "pelmazo", "torpe", 
            "bestia", "bruto"
        ]
        self.subscribers = []  # Lista de suscriptores (servidores que se suscriben)

    # Método para añadir un insulto
    def add_insult(self, insult):
        if insult not in self.insults:
            self.insults.append(insult)
            # Notificar a todos los suscriptores cuando se agrega un nuevo insulto
            for subscriber_uri in self.subscribers:
                subscriber = Pyro4.Proxy(subscriber_uri)  # Proxy al suscriptor
                subscriber.notify(insult)  # Notificar al suscriptor
            print(f"InsultService: Insulto '{insult}' agregado y notificado a suscriptores.")
            return True
        print(f"InsultService: El insulto '{insult}' ya está en la lista.")
        return False  # El insulto ya estaba en la lista

    # Método para obtener la lista de insultos
    def get_insults(self):
        return self.insults

    # Método para registrar nuevos suscriptores
    def add_subscriber(self, subscriber_uri):
        if subscriber_uri not in self.subscribers:
            self.subscribers.append(subscriber_uri)
            print(f"InsultService: Nuevo suscriptor registrado.")
            return True
        print(f"InsultService: El suscriptor ya está registrado.")
        return False

# Función para ejecutar el servidor de InsultService
def run_insult_server():
    daemon = Pyro4.Daemon()  # Crear el Daemon de Pyro
    ns = Pyro4.locateNS()  # Localizar el Name Server de Pyro
    insult_service = InsultService()
    uri = daemon.register(insult_service)  # Registrar InsultService
    ns.register("example.insultservice", uri)  # Registrar en el Name Server con un nombre único

    print("InsultService está funcionando...")
    daemon.requestLoop()  # Mantener el servidor funcionando y esperando solicitudes

if __name__ == "__main__":
    run_insult_server()
