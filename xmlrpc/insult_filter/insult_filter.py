import xmlrpc.server

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
    server = xmlrpc.server.SimpleXMLRPCServer(("localhost", 8001))
    filter_service = InsultFilter()
    server.register_instance(filter_service)
    print("InsultFilter está funcionando en el puerto 8001...")
    server.serve_forever()

if __name__ == "__main__":
    # Ejecutar el servidor de InsultFilter
    run_filter_server()
