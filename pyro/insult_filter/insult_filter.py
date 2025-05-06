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

def run_server():
    Pyro4.Daemon.serveSimple(
        {
            InsultFilter: "example.insultfilter"
        },
        ns=False, port=9091
    )

if __name__ == "__main__":
    run_server()
