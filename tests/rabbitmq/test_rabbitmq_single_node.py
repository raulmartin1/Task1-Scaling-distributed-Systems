import subprocess
import time
import pika
import os 
import signal
import matplotlib.pyplot as plt

QUEUE_NAME = 'insult_queue'
RABBITMQ_HOST = 'localhost'

def launch_service_silent(script_name):
    # Llançem un proces python per executar un script dins la carpeta 'rabbitmq'
    return subprocess.Popen(
        ['python3', os.path.join('rabbitmq', script_name)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

def terminate_process(proc):
    # Si el proces esta actiu, envia un senyal SIGTERM per finalitzar-lo i espera que acabi
    if proc.poll() is None:
        os.kill(proc.pid, signal.SIGTERM)
        proc.wait()

def send_insults(n):
    # Connecta amb rabbitmq i envia n insults a la cua
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME)

    insults = ["tonto", "bobo", "tortuga", "eres tonto", "eres muy bobo", "eres una tortuga"]

    for i in range(n):
        insult = insults[i % len(insults)]  # Selecciona insults ciclicament
        channel.basic_publish(exchange='', routing_key=QUEUE_NAME, body=insult)

    connection.close()
    print(f"Client: Enviats {n} insults a la cua.", flush=True)

def wait_until_queue_empty(queue_name, timeout=60):
    # Espera fins que la cua rabbitmq estigui buida o fins que s'acabi el timeout
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
    channel = connection.channel()

    start = time.time()
    while True:
        q = channel.queue_declare(queue=queue_name, passive=True)
        count = q.method.message_count
        if count == 0:
            break
        if time.time() - start > timeout:
            print(f"Timeout esperant que la cua {queue_name} s'esvaiti")
            break
        time.sleep(0.5)
    connection.close()

def main():
    loads = [500, 1000, 2000]  # Diferentes carregues d'insults
    times = []

    for n in loads:
        print(f"\n--- Test amb {n} insults enviats ---")

        insult_service_proc = launch_service_silent('insult_service.py')
        insult_filter_proc = launch_service_silent('insult_filter.py')

        time.sleep(3)  # Esperar que els serveis s'inicialitzin

        start_time = time.time()
        send_insults(n)
        wait_until_queue_empty(QUEUE_NAME, timeout=120)  # Timeout major per major carga
        end_time = time.time()

        duration = end_time - start_time
        print(f"Temps enviament + filtratge complet per {n} insults: {duration:.2f} segons")
        times.append(duration)

        terminate_process(insult_service_proc)
        terminate_process(insult_filter_proc)

    plt.figure(figsize=(8,5))
    plt.plot(loads, times, marker='o')
    plt.title("Temps enviament + filtratge insults (sense modificar insult_filter.py)")
    plt.xlabel("Nombre d'insults enviats")
    plt.ylabel("Temps total (segons)")
    plt.grid(True)
    plt.savefig("rendiment_rabbitmq_single_node")
    plt.show()

if __name__ == "__main__":
    main()
