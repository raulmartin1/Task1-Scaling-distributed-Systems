import Pyro4

@Pyro4.expose
class InsultService:
    def __init__(self):
        # Lista de insultos predeterminados
        self.insults = [
            "tonto", "idiota", "estúpido", "imbécil", "bobo", 
            "morón", "burro", "papanatas", "pelmazo", "torpe", 
            "bestia", "bruto"
        ]

    # Método para añadir un insulto
    def add_insult(self, insult):
        if insult not in self.insults:
            self.insults.append(insult)
            print(f"InsultService: Insulto '{insult}' agregado.")
            return True
        print(f"InsultService: El insulto '{insult}' ya está en la lista.")
        return False  # El insulto ya estaba en la lista

    # Método para obtener la lista de insultos
    def get_insults(self):
        return self.insults

def run_server():
    Pyro4.Daemon.serveSimple(
        {
            InsultService: "example.insultservice"
        },
        ns=False, port=9090
    )

if __name__ == "__main__":
    run_server()
