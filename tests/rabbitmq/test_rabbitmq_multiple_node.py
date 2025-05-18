import subprocess
import time
import multiprocessing
import pika 
import os
import signal
import matplotlib.pyplot as plt

QUEUE_NAME = 'insult_queue'
RABBITMQ_HOST = 'localhost'

def launch_service_silent(script_name):
    # Es llança un proces python en background sense mostrar cap sortida
    return subprocess.Popen(
        ['python3', os.path.join('rabbitmq', script_name)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

def terminate_process(proc):
    # Terminem el proces si encara esta actiu
    if proc.poll() is None:
        os.kill(proc.pid, signal.SIGTERM)
        proc.wait()

def send_insults_range(start, end):
    # Connecta a rabbit i envia insults des de l'index start fins a end-1
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME)

    insults = ["tonto", "bobo", "tortuga", "eres tonto", "eres muy bobo", "eres una tortuga"]

    for i in range(start, end):
        insult = insults[i % len(insults)]  # Selecciona insults ciclicament i el afegim
        channel.basic_publish(exchange='', routing_key=QUEUE_NAME, body=insult)
    connection.close()

def wait_until_queue_empty(queue_name, timeout=120):
    # Espera fins que la cua rabbit estigui buida o fins que s'acabi el timeout
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
    channel = connection.channel()

    start = time.time()
    while True:
        q = channel.queue_declare(queue=queue_name, passive=True)
        count = q.method.message_count
        if count == 0:
            break
        if time.time() - start > timeout:
            print("Timeout esperant que la cua s'esvaiti.")
            break
        time.sleep(0.5)
    connection.close()

def run_test(num_nodes, total_requests):
    # Executa un test amb num_nodes i total_requests
    print("")
    print("Executant test amb nodes:", num_nodes, "i peticions totals:", total_requests)

    insult_service_procs = []
    insult_filter_procs = []
    # Llança els processos insult_service i insult_filter segons el nombre de nodes
    for _ in range(num_nodes):
        insult_service_procs.append(launch_service_silent('insult_service.py'))
        insult_filter_procs.append(launch_service_silent('insult_filter.py'))

    time.sleep(3)  # Esperar que els serveis s'inicialitzin

    insults_per_node = total_requests // num_nodes

    processes = []

    # Mesura el temps d'enviament de tots els insults de forma paral·lela
    start_send = time.time()
    for i in range(num_nodes):
        start_idx = i * insults_per_node
        end_idx = start_idx + insults_per_node
        p = multiprocessing.Process(target=send_insults_range, args=(start_idx, end_idx))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()
    end_send = time.time()

    # Espera que el filtre hagi processat tots els insults (queue buida)
    start_total = start_send
    wait_until_queue_empty(QUEUE_NAME, timeout=300)
    end_total = time.time()

    # Termina tots els processos llançats
    for p in insult_service_procs + insult_filter_procs:
        terminate_process(p)

    total_duration = end_total - start_total
    print(f"Temps total (enviament + filtratge): {total_duration:.2f} segons")

    return total_duration

def main():
    nodes_list = [1, 2, 3] 
    loads = [500, 1000, 2000]

    results = {}

    # Executa el test per totes les combinacions de nodes i carreggues
    for load in loads:
        for nodes in nodes_list:
            duration = run_test(nodes, load)
            results[(nodes, load)] = duration

    print("\nResultats de temps totals (enviament + filtratge):")
    for nodes in nodes_list:
        for load in loads:
            print("Nodes:", nodes, "- Carrega:", load, "- Temps (s):", results[(nodes, load)])

    # Grafica amb dos subplots: un de temps total i un de speedup respecte a 1 node
    plt.subplot(2, 1, 1)
    for load in loads:
        y = [results[(nodes, load)] for nodes in nodes_list]
        plt.plot(nodes_list, y, marker='o', label=f"Carrega {load}")
    plt.title("Temps total (segons)")
    plt.xlabel("Nombre de nodes")
    plt.ylabel("Temps (segons)")
    plt.grid(True)
    plt.legend()

    plt.subplot(2, 1, 2)
    for load in loads:
        y_speedup = [results[(1, load)] / results[(nodes, load)] for nodes in nodes_list]
        plt.plot(nodes_list, y_speedup, marker='o', label=f"Carrega {load}")
    plt.title("Speedup respecte a 1 node")
    plt.xlabel("Nombre de nodes")
    plt.ylabel("Speedup")
    plt.grid(True)
    plt.legend()

    plt.tight_layout()
    plt.savefig("rendiment_rabbitmq_multiple_node.png")
    plt.show()

if __name__ == "__main__":
    main()
