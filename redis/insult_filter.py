import redis
import time

client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

queue_name = "insult_queue"
result_list = "filtered_texts"
censored_words = ["tonto", "bobo", "tortuga"]

def filter_text(text):
    words = text.split()
    filtered = ["CENSORED" if w.lower() in censored_words else w for w in words]
    return " ".join(filtered)

# Funcio que filtra els imsults i els emmagatzema
def insult_filter():
    print("InsultFilter: Waiting insults...")
    while True:
        task = client.blpop(queue_name, timeout=0) # Espera insult
        if task:
            insult_text = task[1]
            filtered_text = filter_text(insult_text)

            if filtered_text not in client.lrange(result_list, 0, -1):
                client.rpush(result_list, filtered_text)
                print(f"InsultFilter: Text filtrat agregat: '{filtered_text}'")
            else:
                print(f"InsultFilter: Text filtrat '{filtered_text}' ja es troba a la llista")
            
        time.sleep(0.01)

if __name__ == "__main__":
    insult_filter()