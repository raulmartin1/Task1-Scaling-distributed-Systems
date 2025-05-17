import Pyro4
import random
import threading
import time
from multiprocessing import Process

@Pyro4.expose
class InsultService:
    def __init__(self):
        self.insults = []
        self.subscribers = []
        self.lock = threading.Lock()
        threading.Thread(target=self.broadcast_insults, daemon=True).start()

    def add_insult(self, insult):
        with self.lock:
            if insult not in self.insults:
                self.insults.append(insult)
                print(f"InsultService: Insulto '{insult}' agregado.")
                return True
            print(f"InsultService: El insulto '{insult}' ya está en la lista.")
            return False

    def get_insults(self):
        with self.lock:
            return self.insults.copy()

    def clear_insults(self):
        with self.lock:
            self.insults.clear()
            print("InsultService: Lista de insultos limpia.")
            return True

    def add_subscriber(self, subscriber_uri):
        with self.lock:
            try:
                subscriber_proxy = Pyro4.Proxy(subscriber_uri)  # Convertir URI a proxy
                if subscriber_proxy not in self.subscribers:
                    self.subscribers.append(subscriber_proxy)
                    print(f"InsultService: Nuevo suscriptor registrado.")
                    return True
                print(f"InsultService: El suscriptor ya está registrado.")
                return False
            except Exception as e:
                print(f"InsultService: Error al añadir suscriptor: {e}")
                return False

    def remove_subscriber(self, subscriber_uri):
        with self.lock:
            try:
                subscriber_proxy = Pyro4.Proxy(subscriber_uri)
                if subscriber_proxy in self.subscribers:
                    self.subscribers.remove(subscriber_proxy)
                    print(f"InsultService: Suscriptor eliminado.")
                    return True
                print(f"InsultService: El suscriptor no está registrado.")
                return False
            except Exception as e:
                print(f"InsultService: Error al eliminar suscriptor: {e}")
                return False

    def broadcast_insults(self):
        while True:
            with self.lock:
                if self.insults and self.subscribers:
                    insult = random.choice(self.insults)
                    for subscriber in self.subscribers[:]:
                        try:
                            subscriber.notify(insult)
                            print(f"InsultService: Insulto '{insult}' enviado a suscriptor.")
                        except Exception as e:
                            print(f"InsultService: Error notificando a suscriptor: {e}")
                            self.subscribers.remove(subscriber)
            time.sleep(5)

def run_insult_server():
    daemon = Pyro4.Daemon(host="localhost", port=9093)
    ns = Pyro4.locateNS()
    insult_service = InsultService()
    uri = daemon.register(insult_service)
    ns.register("InsultService", uri)
    print("InsultService está funcionando en el puerto 9093...")
    daemon.requestLoop()

if __name__ == "__main__":
    Process(target=run_insult_server).start()
