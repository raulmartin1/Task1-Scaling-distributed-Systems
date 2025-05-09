import pika
import random
import time

# Connect to RabbitMQ

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

queue_name = 'insult_queue'
channel.queue_declare(queue=queue_name)

list_name = "INSULTS"
insults = ["tonto", "bobo", "tortuga", "eres tonto", "eres muy bobo", "eres una tortuga"]

def insult_server():
    print("InsultService: Publishing random insults every 5 seconds...")

    while True:
        insult = random.choice(insults)
        # Enviamos el insulto a la cola
        channel.basic_publish(exchange='',
                              routing_key=queue_name,
                              body=insult)
        
        print(f"InsultService: Insult '{insult}' published")
        
        time.sleep(5)  # Esperamos 5 segundos entre cada publicacion

if __name__ == "__main__":
    insult_server()