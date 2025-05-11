import xmlrpc.server

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
    server = xmlrpc.server.SimpleXMLRPCServer(("localhost", 8001), allow_none=True)  # Habilitar None
    filter_service = InsultFilter()
    server.register_instance(filter_service)
    print("InsultFilter está funcionando en el puerto 8001...")
    server.serve_forever()

if __name__ == "__main__":
    run_filter_server()
