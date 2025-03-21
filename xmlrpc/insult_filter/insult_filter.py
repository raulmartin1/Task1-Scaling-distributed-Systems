import xmlrpc.server

class InsultFilter:
    def __init__(self):
        self.filtered_texts = []

    def filter_insults(self, text, insults):
        for insult in insults:
            text = text.replace(insult, "CENSORED")
        self.filtered_texts.append(text)
        return text

    def get_filtered_texts(self):
        return self.filtered_texts

def run_server():
    server = xmlrpc.server.SimpleXMLRPCServer(("localhost", 8001))
    service = InsultFilter()
    server.register_instance(service)
    server.serve_forever()

if __name__ == "__main__":
    run_server()
