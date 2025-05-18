import subprocess
import time 
import multiprocessing
import redis 
import random  # Per triar insults/textos aleatoris
import string  # Per generar cadenes aleatòries
import os  # Per gestionar rutes de fitxers
import signal  # Per enviar senyals a processos (terminar-los)
import threading  # Per fer threads que imprimeixin la sortida dels processos
import matplotlib.pyplot as plt  # Per fer gràfiques

client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

insult_list = "insult_list"      # Llista d'insults registrats
queue_name = "insult_queue"      # Cola per textos a filtrar
result_list = "filtered_texts"   # Llista de textos filtrats
insults_set = "INSULTS"          # Conjunt d'insults pendents pel insult_service

# Funció per esborrar les dades anteriors de redis per netejar l'entorn
def clear_redis():
    client.delete(insult_list)      # Esborra insults antics
    client.delete(queue_name)       # Esborra texts antics
    client.delete(result_list)      # Esborra texts filtrats antics
    client.delete(insults_set)      # Esborra insults pendents

# Funció per omplir la llista INSULTS amb insults perquè insult_service pugui consumir-los
def fill_insults_set(n):
    insults = ["tonto", "bobo", "tortuga", "idiota", "imbecil", "burro"]
    for _ in range(n):
        insult = random.choice(insults) + ''.join(random.choices(string.ascii_lowercase, k=3))
        client.sadd(insults_set, insult)
    print(f"Llista INSULTS (conjunt pendents) omplerta amb {n} insults.")

# Funció per registrar insults a insult_list, per visibilitat de quants s'han processat/desat
def send_insults_list(n):
    insults = ["tonto", "bobo", "tortuga", "idiota", "imbecil", "burro"]
    count = 0
    for _ in range(n):
        insult = random.choice(insults) + ''.join(random.choices(string.ascii_lowercase, k=3))
        insults_actuals = client.lrange(insult_list, 0, -1)
        if insult not in insults_actuals:
            client.rpush(insult_list, insult)
            count += 1
        time.sleep(0.005)  # Sleep per no saturar redis
    print(f"Client insults registrats a insult_list: {count}")

# Funció per enviar textos a filtrar a la cola de Redis (n textos)
def send_texts_to_filter(n):
    textos = [
        "Ets un tonto",
        "No siguis bobo",
        "La tortuga és lenta",
        "Ets molt intel·ligent",
        "Aquest text no té insult"
    ]
    count = 0  # Comptador de textos enviats
    for _ in range(n):
        text = random.choice(textos)  # Text aleatori
        client.rpush(queue_name, text)  # Afegir text a la cola per filtrar
        count += 1
        time.sleep(0.005)  # Petita pausa
    print(f"Client textos enviats a filtrar: {count}", flush=True)  # Mostrar quantitat enviada

# Funció per llançar un servei Python com a procés
def launch_service(script_name):
    script_path = os.path.join("redis", script_name)  # Ruta del fitxer script dins carpeta 'redis'
    proc = subprocess.Popen(
        ["python3","-u" ,script_path],
        stdout=subprocess.PIPE,  # Capturar la sortida per anar mostrant el que es filtra
        stderr=subprocess.STDOUT,  # Redirigir stderr a stdout
        text=True,
        bufsize=1,
    )
    # Thread per imprimir la sortida de cada proces(Filter y Service)
    def print_output():
        for line in proc.stdout:
            print(f"[{script_name}] {line}", end="", flush=True)
    threading.Thread(target=print_output, daemon=True).start()
    return proc  # Retorna el proces per poder controlar-lo despres

# Funcio per tancar un proces enviant senyal SIGTERM
def terminate_process(proc):
    if proc.poll() is None:  # Si el proces està actiu
        os.kill(proc.pid, signal.SIGTERM)  # Enviar senyal de terminacio
        proc.wait()  # Esperem que es tanqui

# Funció que executa el test complet amb un nombre concret de peticions (texts a filtrar)
def run_test(num_requests):
    print(f"\n--- Test amb {num_requests} peticions ---", flush=True)
    clear_redis()  # Netejar redis abans de començar
    
    fill_insults_set(num_requests)  # Omplir la llista INSULTS perquè insult_service pugui començar a publicar
    
    send_insults_list(num_requests)  # Registrar insults a insult_list (només per visibilitat)

    client.rpush(insult_list, "insult inicial")  # Posem un insult al principi perque el servei que envia insults pugui començar a treballar

    # Llançar serveis insult_service.py i insult_filter.py com processos
    insult_service_proc = launch_service("insult_service.py")
    insult_filter_proc = launch_service("insult_filter.py")

    time.sleep(2)  # Esperar 2 segons que s'inicialitzin els serveis

    # Crear procés per enviar textos paral·lelament
    p2 = multiprocessing.Process(target=send_texts_to_filter, args=(num_requests,))

    start_time = time.time()  # Començar mesura de temps
    p2.start()
    p2.join()  # Esperar que finalitzin els processos enviadors
    end_time = time.time()  # Temps final

    time.sleep(5)  # Sleep de 5 segons per a que el insult_filter acabi de processar missatges

    # Obtenir llistes finals d'insults i textos filtrats de redis
    insults_in_set = client.scard(insults_set)           # Quants insults pendents queden
    insults_registered = client.llen(insult_list)        # Quants insults ha registrat el client
    filtered_texts_finals = client.llen(result_list)     # Quants textos filtrats hi ha

    # Mostrar estadístiques finals
    print(f"Insults pendents a INSULTS: {insults_in_set}")
    print(f"Insults registrats a insult_list: {insults_registered}")
    print(f"Total textos filtrats: {filtered_texts_finals}")

    # Terminar els serveis
    terminate_process(insult_service_proc)
    terminate_process(insult_filter_proc)

    duration = end_time - start_time  # Calcular durada total enviament
    print(f"Temps total per {num_requests} peticions: {duration:.2f} segons", flush=True)
    return duration

# Funció principal que executa tests per diferents carregues i fa una gràfica
def main():
    peticions = [100, 500, 1000, 2000]  # Carregues de peticions
    temps = []  # Llista temps resultants

    for n in peticions:
        temps.append(run_test(n))  # Executar test per cada nombre de peticions i guardar el temps

    # Crear i mostrar la grafica de rendiment
    plt.figure(figsize=(8,5))
    plt.plot(peticions, temps, marker='o')
    plt.title("Rendiment InsultService + InsultFilter (Single-node)")
    plt.xlabel("Nombre de peticions")
    plt.ylabel("Temps total (segons)")
    plt.grid(True)
    plt.savefig("rendiment_redis_single_node.png")  # Guardar la grafica a fitxer
    plt.show()

if __name__ == "__main__":
    main()
