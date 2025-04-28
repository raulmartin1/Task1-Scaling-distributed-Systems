import Pyro4

@Pyro4.expose
class InsultFilter:
    def __init__(self):
        self.filtered_texts = []

    # Método para filtrar insultos en un texto
    def filter_insults(self, text, insults):
        for insult in insults:
            text = text.replace(insult, "CENSURADO")
        self.filtered_texts.append(text)
        return text

    # Método para obtener los textos filtrados
    def get_filtered_texts(self):
        return self.filtered_texts

# Función para ejecutar el servidor de InsultFilter
def run_filter_server():
    daemon = Pyro4.Daemon()  # Crea un daemon para el servidor
    ns = Pyro4.locateNS()  # Localiza el nombre del servidor Pyro
    uri = daemon.register(InsultFilter)  # Registra el servicio
    ns.register("example.insultfilter", uri)  # Registra el servicio en el servidor de nombres

    print("InsultFilter está funcionando...")
    daemon.requestLoop()  # Mantiene el servidor en ejecución

if __name__ == "__main__":
    run_filter_server()
