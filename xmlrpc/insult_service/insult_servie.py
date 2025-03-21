import xmlrpc.server
import threading
import random
import time

class InsultService:
    def __init__(self):
        self.insults = []
        self.subscribers = []

    def add_insult(self, insult):
        if insult not in self.insults:
            self.insults.append(insult)
            return True
        return False

    def get_insults(self):
        return self.insults

    def subscribe(self, subscriber):
        self.subscribers.append(subscriber)
        return True

    def broadcast_insults(self):
        while True:
            if self.subscribers:
                insult = random.choice(self.insults)
                for subscriber in self.subscribers:
                    subscriber.notify(insult)
            time.sleep(5)

def run_server():
    server = xmlrpc.server.SimpleXMLRPCServer(("localhost", 8000))
    service = InsultService()
    server.register_instance(service)
    threading.Thread(target=service.broadcast_insults).start()
    server.serve_forever()

if __name__ == "__main__":
    run_server()
