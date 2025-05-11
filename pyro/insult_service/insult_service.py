import Pyro4
import random
import time

@Pyro4.expose
class InsultService:
    def __init__(self):
        self.insults = [
            "tonto", "idiota", "estúpido", "imbécil", "bobo", 
            "burro", "papanatas", "pelmazo", "torpe", 
            "bestia", "bruto"
        ]
        self.subscribers = []  # Lista de suscriptores (servidores que se suscriben)

    def add_insult(self, insult):
        if insult not in self.insults:
            self.insults.append(insult)
            # Notificar a todos los suscriptores cuando se agrega un nuevo insulto
            for subscriber_uri in self.subscribers:
                subscriber = Pyro4.Proxy(subscriber_uri)
                subscriber.notify(insult)  # Notificar al suscriptor
            print(f"InsultService: Insulto '{insult}' agregado y notificado a suscriptores.")
            return True
        print(f"InsultService: El insulto '{insult}' ya está en la lista.")
        return False

    def get_insults(self):
        return self.insults

    def add_subscriber(self, subscriber_uri):
        if subscriber_uri not in self.subscribers:
            self.subscribers.append(subscriber_uri)
            print(f"InsultService: Nuevo suscriptor registrado.")
            return True
        print(f"InsultService: El suscriptor ya está registrado.")
        return False

    def broadcast_insults(self):
        while True:
            if self.insults:
                insult = random.choice(self.insults)
                for subscriber_uri in self.subscribers:
                    subscriber = Pyro4.Proxy(subscriber_uri)
                    subscriber.notify(insult)  # Notificar al suscriptor
                print(f"InsultService: Insulto '{insult}' publicado a suscriptores.")
            time.sleep(5)  # Esperar 5 segundos para el siguiente broadcast

# Función para ejecutar el servidor de InsultService
def run_insult_server():
    daemon = Pyro4.Daemon(host="localhost", port=8000)  # Especifica el puerto 8000
    ns = Pyro4.locateNS()  # Localizar el Name Server
    insult_service = InsultService()
    uri = daemon.register(insult_service)  # Registrar InsultService
    ns.register("mi.insultservice", uri)  # Registrar en el Name Server con el nombre 'mi.insultservice'

    print("InsultService está funcionando...")
    daemon.requestLoop()  # Mantener el servidor funcionando

if __name__ == "__main__":
    run_insult_server()
