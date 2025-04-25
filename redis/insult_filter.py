import redis
import time

client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

queue_name = "insult_queue"
list_name = "INSULTS"
censored_words = ["tonto", "bobo", "tortuga"]

# Funcio que filtra els imsults i els emmagatzema
def insult_filter():
    print("InsultFilter: Waiting insults...")
    while True:
        task = client.blpop(queue_name, timeout=0) # Espera insult
        if task:
            insult = task[1]

            if insult.lower() in censored_words:    # Si es troba a la llista de censura es censura
                insult = "CENSORED"
            
            if not client.sismember(list_name, insult): # Afegir a la llista si no ha estat afegit (Evitar diplicats)
                client.rpush(list_name, insult)
                print(f"InsultFilter: Insult '{insult}' agreagat")
            else:
                print(f"InsultFilter: Insult '{insult}' ja es troba a la llista")
        time.sleep(1)

if __name__ == "__main__":
    insult_filter()