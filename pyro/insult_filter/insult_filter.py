import Pyro4

@Pyro4.expose
class InsultFilter:
    def __init__(self):
        self.filtered_texts = []

    def filter_insults(self, text, insults):
        print(f"InsultFilter: Filtrando el texto '{text}'...")
        for insult in insults:
            text = text.replace(insult, "CENSURADO")
        self.filtered_texts.append(text)
        print(f"InsultFilter: Texto filtrado: {text}")
        return text

    def get_filtered_texts(self):
        return self.filtered_texts

    def notify(self, insult):
        print(f"InsultFilter ha recibido un nuevo insulto: {insult}")
        # Filtra y procesa el insulto
        self.filter_insults(f"Eres un {insult}", [insult])

# Función para ejecutar el servidor de InsultFilter
def run_filter_server():
    daemon = Pyro4.Daemon(host="localhost", port=8001)  # Especifica el puerto 8001
    ns = Pyro4.locateNS()  # Localizar el Name Server
    filter_service = InsultFilter()
    uri = daemon.register(filter_service)  # Registrar InsultFilter
    ns.register("mi.insultfilter", uri)  # Registrar en el Name Server con el nombre 'mi.insultfilter'

    print("InsultFilter está funcionando...")
    daemon.requestLoop()  # Mantener el servidor funcionando

if __name__ == "__main__":
    run_filter_server()
