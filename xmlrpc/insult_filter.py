import xmlrpc.server
import xmlrpc.client
import queue
import threading
from multiprocessing import Process

class InsultFilter:
    def __init__(self):
        self.filtered_texts = []
        self.work_queue = queue.Queue()
        self.lock = threading.Lock()
        # Conectar a InsultService para obtener insultos
        self.service = xmlrpc.client.ServerProxy('http://localhost:8000')
        self.insults = self.service.get_insults()
        threading.Thread(target=self.process_queue, daemon=True).start()

    def filter_insults(self, text):
        self.work_queue.put(text)
        return True

    def process_queue(self):
        while True:
            text = self.work_queue.get()
            # Actualizar lista de insultos desde InsultService
            self.insults = self.service.get_insults()
            filtered_text = text
            for insult in self.insults:
                filtered_text = filtered_text.replace(insult, "CENSORED")
            with self.lock:
                self.filtered_texts.append(filtered_text)
            print(f"InsultFilter: Texto filtrado: {filtered_text}")
            self.work_queue.task_done()

    def get_filtered_texts(self):
        with self.lock:
            return self.filtered_texts

    def clear_filtered_texts(self):
        with self.lock:
            self.filtered_texts.clear()
            print("InsultFilter: Lista de textos filtrados limpia.")
            return True

def run_filter_server():
    server = xmlrpc.server.SimpleXMLRPCServer(("localhost", 8001), allow_none=True)
    filter_service = InsultFilter()
    server.register_instance(filter_service)
    print("InsultFilter está funcionando en el puerto 8001...")
    server.serve_forever()

if __name__ == "__main__":
    Process(target=run_filter_server).start()