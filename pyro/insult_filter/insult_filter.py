import Pyro4

@Pyro4.expose
class InsultFilter:
    def __init__(self):
        self.filtered_texts = []

    # Método para filtrar insultos en un texto
    def filter_insults(self, text, insults):
        print(f"InsultFilter: Filtrando el texto '{text}'...")
        for insult in insults:
            text = text.replace(insult, "CENSURADO")
        self.filtered_texts.append(text)
        print(f"InsultFilter: Texto filtrado: {text}")
        return text

    # Método para obtener los textos filtrados
    def get_filtered_texts(self):
        return self.filtered_texts

    # Método de notificación (como suscriptor)
    def notify(self, insult):
        print(f"InsultFilter ha recibido un nuevo insulto: {insult}")
        # Filtra y procesa el insulto
        self.filter_insults(f"Eres un {insult}", [insult])

# Función para ejecutar el servidor de InsultFilter
def run_filter_server():
    daemon = Pyro4.Daemon()  # Crear el Daemon de Pyro
    ns = Pyro4.locateNS()  # Localizar el Name Server de Pyro
    filter_service = InsultFilter()
    uri = daemon.register(filter_service)  # Registrar InsultFilter
    ns.register("example.insultfilter", uri)  # Registrar en el Name Server con un nombre único

    print("InsultFilter está funcionando...")
    daemon.requestLoop()  # Mantener el servidor funcionando y esperando solicitudes

if __name__ == "__main__":
    run_filter_server()
