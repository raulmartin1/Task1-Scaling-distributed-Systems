import xmlrpc.server
import xmlrpc.client
import random
import threading
import time
from multiprocessing import Process

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
            return self.insults

    def clear_insults(self):
        with self.lock:
            self.insults.clear()
            print("InsultService: Lista de insultos limpia.")
            return True

    def add_subscriber(self, subscriber_url):
        with self.lock:
            if subscriber_url not in self.subscribers:
                self.subscribers.append(subscriber_url)
                print(f"InsultService: Nuevo suscriptor registrado: {subscriber_url}")
                return True
            print(f"InsultService: El suscriptor {subscriber_url} ya está registrado.")
            return False

    def remove_subscriber(self, subscriber_url):
        with self.lock:
            if subscriber_url in self.subscribers:
                self.subscribers.remove(subscriber_url)
                print(f"InsultService: Suscriptor {subscriber_url} eliminado.")
                return True
            print(f"InsultService: El suscriptor {subscriber_url} no está registrado.")
            return False

    def broadcast_insults(self):
        while True:
            with self.lock:
                if self.insults:
                    insult = random.choice(self.insults)
                    for subscriber_url in self.subscribers[:]:
                        try:
                            subscriber = xmlrpc.client.ServerProxy(subscriber_url)
                            subscriber.notify(insult)
                            print(f"InsultService: Insulto '{insult}' enviado a {subscriber_url}")
                        except Exception as e:
                            print(f"InsultService: Error notificando a {subscriber_url}: {e}")
                            self.subscribers.remove(subscriber_url)
            time.sleep(5)

def run_insult_server():
    server = xmlrpc.server.SimpleXMLRPCServer(("localhost", 8000), allow_none=True)
    insult_service = InsultService()
    server.register_instance(insult_service)
    print("InsultService está funcionando en el puerto 8000...")
    server.serve_forever()

if __name__ == "__main__":
    Process(target=run_insult_server).start()