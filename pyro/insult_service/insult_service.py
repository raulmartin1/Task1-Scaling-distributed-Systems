import Pyro4
import threading
import random
import time

@Pyro4.expose
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
    Pyro4.Daemon.serveSimple(
        {
            InsultService: "example.insultservice"
        },
        ns=False, port=9090
    )

if __name__ == "__main__":
    run_server()
