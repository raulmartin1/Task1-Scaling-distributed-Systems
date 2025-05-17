import Pyro4
import queue
import threading

@Pyro4.expose
class InsultFilter:
    def __init__(self):
        self.filtered_texts = []
        self.lock = threading.Lock()
        self.work_queue = queue.Queue()

    def filter_insults(self, text):
        self.work_queue.put(text)
        return True

    def get_filtered_texts(self):
        with self.lock:
            return list(self.filtered_texts)

    def clear_filtered_texts(self):
        with self.lock:
            self.filtered_texts.clear()
            return True

    def process(self):
        while True:
            text = self.work_queue.get()
            filtered = text
            with self.lock:
                for insult in ["tonto", "idiota"]:  # Asumimos que los insultos se proporcionan así
                    filtered = filtered.replace(insult, "CENSORED")
                self.filtered_texts.append(filtered)
            self.work_queue.task_done()

def run_filter_server():
    daemon = Pyro4.Daemon(host="localhost", port=9094)
    ns = Pyro4.locateNS()
    uri = daemon.register(InsultFilter())
    ns.register("InsultFilter", uri)
    print("InsultFilter está funcionando en el puerto 9094...")
    filtro = daemon.objectsById[uri.object]
    t = threading.Thread(target=filtro.process, daemon=True)
    t.start()
    daemon.requestLoop()

if __name__ == "__main__":
    run_filter_server()
