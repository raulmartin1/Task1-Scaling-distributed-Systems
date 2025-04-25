import Pyro4

@Pyro4.expose
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
    Pyro4.Daemon.serveSimple(
        {
            InsultFilter: "example.insultfilter"
        },
        ns=False, port=9091
    )

if __name__ == "__main__":
    run_server()
