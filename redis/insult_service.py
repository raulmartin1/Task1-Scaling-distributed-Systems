import random
import redis
import time

client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
channel_name='insult_channel'
list_name = "INSULTS"

# Funcio per rebre insults i publicar-los al canal
def insult_server():
    while True:
        insult = client.spop(list_name)
        if insult:
            client.publish(channel_name, insult)
            print(f"InsultService: Insult '{insult}' published")
        else:
            print(f"InsultService: No hi ha insults a publicar")

        time.sleep(5) # esperem 5 segons entre cada publicacio

if __name__ == "__main__":
    insult_server()