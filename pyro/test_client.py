import Pyro4
import threading
import time

@Pyro4.expose
@Pyro4.callback
class SubscriberClient:
    def __init__(self):
        self.daemon = Pyro4.Daemon(host="localhost")
        self.uri = self.daemon.register(self)
        self.thread = threading.Thread(target=self.daemon.requestLoop, daemon=True)
        self.thread.start()
        print(f"SubscriberClient: Demonio iniciado y registrado con URI {self.uri}")

    def notify(self, insult):
        print(f"SubscriberClient: Recibido insulto broadcast: {insult}")

    def get_uri(self):
        return self.uri

if __name__ == "__main__":
    # Creamos y conectamos el cliente al servicio de insultos
    subscriber = SubscriberClient()
    ns = Pyro4.locateNS()
    service_uri = ns.lookup("InsultService")
    insult_service = Pyro4.Proxy(service_uri)

    # Nos suscribimos pasando la URI del objeto remoto para callbacks
    insult_service.add_subscriber(subscriber.get_uri())

    # Prueba de añadir insultos
    insult_service.add_insult("tonto")
    insult_service.add_insult("idiota")
    print("Insultos añadidos:", insult_service.get_insults())

    # Prueba de insertar un insulto repetido
    print("Intentando añadir 'tonto' de nuevo:", insult_service.add_insult("tonto"))
    
    # Filtrado de texto
    print("Probando InsultFilter...")
    ns_filter = ns.lookup("InsultFilter")
    filter_service = Pyro4.Proxy(ns_filter)
    filter_service.clear_filtered_texts()
    filter_service.filter_insults("Eres tonto")
    time.sleep(1)
    print("Textos filtrados:", filter_service.get_filtered_texts())

    print("Esperando broadcasts (20 segundos)...")
    time.sleep(5)

    # Desuscribirse
    insult_service.remove_subscriber(subscriber.get_uri())
    print("Desuscrito.")
