import subprocess 
import time
import multiprocessing
import redis
import random 
import string
import os 
import signal
import threading 
import matplotlib.pyplot as plt 

client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

insult_list = "insult_list"      # Llista d'insults
queue_name = "insult_queue"      # Cola de textos a filtrar
result_list = "filtered_texts"   # Llista de textos filtrats
insults_set = "INSULTS"          # Conjunt d'insults pendents per insult_service

# Funció per netejar dades anteriors de redis
def clear_redis():
    client.delete(insult_list)  # Esborra insults antics
    client.delete(queue_name)   # Esborra texts antics
    client.delete(result_list)  # Esborra texts filtrats antics
    client.delete(insults_set)  # Esborra insults pendents

# Funció per omplir el conjunt INSULTS perquè insult_service pugui consumir insults
def fill_insults_set(n):
    insults = ["tonto", "bobo", "tortuga", "idiota", "imbecil", "burro"]
    for _ in range(n):
        insult = random.choice(insults) + ''.join(random.choices(string.ascii_lowercase, k=3))
        client.sadd(insults_set, insult)
    print(f"Llista INSULTS omplerta amb {n} insults.")

# Funcio per enviar insults a redis des d'un rang de 0 fins a numero de insults per node
def send_insults_range(start, end):
    insults = ["tonto", "bobo", "tortuga", "idiota", "imbecil", "burro"]
    for _ in range(start, end):
        insult = random.choice(insults) + ''.join(random.choices(string.ascii_lowercase, k=3))  # Insult + 3 lletres randoms
        insults_actuals = client.lrange(insult_list, 0, -1)  # Insults actuals a redis
        if insult not in insults_actuals:  # Si insult no es troba repetit
            client.rpush(insult_list, insult)  # Afegir insult a la llista
        time.sleep(0.001)  # Sleep per no saturar el redis

# Funcio per enviar textos a filtrar a la cola Redis des d'un rang de 0 fins a numero de textos per node
def send_texts_range(start, end):
    textos = [
        "Ets un tonto",
        "No siguis bobo",
        "La tortuga és lenta",
        "Ets molt intel·ligent",
        "Aquest text no té insult"
    ]
    for _ in range(start, end):
        text = random.choice(textos)
        client.rpush(queue_name, text)  # Enviar a la cola
        time.sleep(0.001)  # Petita pausa

# Funcio per correr un servei com a procés i imprimir sortida
def launch_service(script_name):
    script_path = os.path.join("redis", script_name)  # Dins la carpeta redis
    proc = subprocess.Popen(
        ["python3", "-u", script_path],        # Executar comanda
        stdout=subprocess.PIPE,                # Capturar sortida
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    # Thread que imprimeix la sortida dels serveis
    def print_output():
        for line in proc.stdout:
            print(f"[{script_name}] {line}", end="", flush=True)
    threading.Thread(target=print_output, daemon=True).start()  # Correr thread daemon
    return proc  # Retornem el proces

# Funcio que termian el servei amb la senyal SIGTERM
def terminate_process(proc):
    if proc.poll() is None:  # Si el proces esta actiu
        os.kill(proc.pid, signal.SIGTERM)  # Enviar senyal per aturar
        proc.wait()  # Esperar que acabi

# Funcio per executar un test amb num_nodes i total_requests
def run_test(num_nodes, total_requests):
    print(f"\n=== Test amb {num_nodes} node(s) i {total_requests} peticions totals ===", flush=True)
    clear_redis()  # Netejar dades anteriors a Redis
    client.rpush(insult_list, "insult inicial")  # Posar insult inicial per activar broadcaster

    # Omplir conjunt INSULTS amb insults per al service
    insults_per_node = total_requests // num_nodes
    for _ in range(num_nodes):
        fill_insults_set(insults_per_node)

    insult_service_procs = []  # Llista per processos insult_service
    insult_filter_procs = []   # Llista per processos insult_filter
    for i in range(num_nodes):
        insult_service_procs.append(launch_service("insult_service.py"))  # Llançar insult_service
        insult_filter_procs.append(launch_service("insult_filter.py"))    # Llançar insult_filter

    time.sleep(2)  # Esperar que s'inicialitzin els serveis

    textos_per_node = total_requests // num_nodes   # Dividir textos per node

    processes = []  # Llista processos enviament
    start_time = time.time()  # Començar comptador temps

    for i in range(num_nodes):
        # Crear procés per enviar insults a rang [0, insults_per_node)
        p_insults = multiprocessing.Process(target=send_insults_range, args=(0, insults_per_node))
        # Crear procés per enviar textos a rang [0, textos_per_node)
        p_texts = multiprocessing.Process(target=send_texts_range, args=(0, textos_per_node))
        processes.append(p_insults)
        processes.append(p_texts)
        p_insults.start()  # Llançar procés insults
        p_texts.start()    # Llançar procés textos

    for p in processes:
        p.join()  # Esperar que acabin tots els processos enviament

    end_time = time.time()  # Temps final enviament

    time.sleep(5)  # Esperar que el filtre acabi de processar

    # Tancar tots els processos serveis
    for p in insult_service_procs + insult_filter_procs:
        terminate_process(p)

    duration = end_time - start_time  # Calcular durada total enviament

    insults_finals = client.lrange(insult_list, 0, -1)           # Llegir insults guardats
    filtered_texts_finals = client.lrange(result_list, 0, -1)    # Llegir textos filtrats guardats

    # Imprimir resum resultats
    print(f"Total insults guardats: {len(insults_finals)}", flush=True)
    print(f"Total textos filtrats: {len(filtered_texts_finals)}", flush=True)
    print(f"Temps total per {num_nodes} node(s): {duration:.2f} segons", flush=True)

    return duration  # Retornar temps del test

# Funcio que executa tests, mostra resultats i la grafica
def main():
    nodes_list = [1, 2, 3]            # Nombres de nodes
    loads = [500, 1000, 2000]         # Càrregues de peticions

    results = {}  # Diccionari per guardar temps: (node, càrrega)

    # Fer els tests per cada combinació de nodes i càrrega
    for load in loads:
        for nodes in nodes_list:
            duration = run_test(nodes, load)  # Executar test
            results[(nodes, load)] = duration  # Guardar temps

    # Mostrar resultats de forma simple per terminal
    print("\nResultats (Temps en segons):")
    print("Nodes\\Carga\t" + "\t".join(str(l) for l in loads))
    for nodes in nodes_list:
        fila = []
        for load in loads:
            fila.append(str(round(results[(nodes, load)], 2)))
        print(f"{nodes}\t\t" + "\t".join(fila))

    # Mostrar speedups de forma simple
    base = results[(1, loads[0])]  # Temps base per 1 node i càrrega més petita
    print("\nSpeedups respecte a 1 node i 500 peticions:")
    for nodes in nodes_list:
        for load in loads:
            speedup = base / results[(nodes, load)]
            print(f"Nodes={nodes}, Càrrega={load}: Speedup={round(speedup, 2)}")

    # Gràfiques: dues subplots, una per temps i una per speedup
    import matplotlib.pyplot as plt
    plt.figure(figsize=(10, 10))  # Ample x alt

    # Gràfica 1: Temps
    plt.subplot(2, 1, 1)  # 2 files, 1 columna, primera
    for load in loads:
        y = [results[(nodes, load)] for nodes in nodes_list]
        plt.plot(nodes_list, y, marker='o', label=f"Càrrega {load}")
    plt.title("Temps total (segons)")
    plt.xlabel("Nombre de nodes")
    plt.ylabel("Temps (segons)")
    plt.grid(True)
    plt.legend()

    # Gràfica 2: Speedups
    plt.subplot(2, 1, 2)  # 2 files, 1 columna, segona
    for load in loads:
        y_speedup = [results[(1, load)] / results[(nodes, load)] for nodes in nodes_list]
        plt.plot(nodes_list, y_speedup, marker='o', label=f"Càrrega {load}")
    plt.title("Speedup respecte a 1 node")
    plt.xlabel("Nombre de nodes")
    plt.ylabel("Speedup")
    plt.grid(True)
    plt.legend()

    plt.tight_layout()
    plt.savefig("rendiment_redis_multiple_node.png")
    plt.show()

if __name__ == "__main__":
    main()
