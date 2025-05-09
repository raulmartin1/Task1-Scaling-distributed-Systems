import pika
import time

# Connect to RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Declare a queue
queue_name = 'insult_queue'
channel.queue_declare(queue=queue_name)

result_list = "filtered_texts"
censored_words = ["tonto", "bobo", "tortuga"]

def filter_text(text):
    words = text.split()
    filtered = ["CENSORED" if w.lower() in censored_words else w for w in words]
    return " ".join(filtered)

def callback(ch, method, properties, body):    
    insult_text = body.decode()

    if insult_text not in unfiltered_insults:
        unfiltered_insults.append(insult_text)

    filtered_text = filter_text(insult_text)

    if insult_text not in unfiltered_insults:
        filtered_texts.append(filtered_text)
        print(f"InsultFilter: Text filtrat afegit: '{insult_text}'")
    else:
        print(f"InsultFilter: El text filtrat ja es troba a la llista: '{insult_text}'")

filtered_texts = []
unfiltered_insults = [] # Para comprobar si ya se han metido en la lista

def insult_filter():
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    
    print("InsultFilter: Wainting insults...")
    channel.start_consuming()

if __name__ == "__main__":
    insult_filter()