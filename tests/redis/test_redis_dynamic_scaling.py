import random
import subprocess
import time
import os
import signal
import threading
import redis
from math import ceil  # Per arrodonir cap amunt
import matplotlib.pyplot as plt

# Configuracio Redis
client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
queue_name = "insult_queue"  # Cua on s'afegeixen els missatges
processed_set = "missatges_processats"  # Missatges registrats

# Parametres de la formula d'escalat:
# N = (λ × T) / C
MAX_NODES = 50      # Maxim nombre de nodes
MIN_NODES = 2       # Minim nombre de nodes
T = 0.1             # Temps de processament per missatge (segons)
C = 10              # Capacitat d'un node (missatges per segon)

def prepare_environment(num_messages):
    # Neteja les dades anteriors de Redis
    client.delete(queue_name)
    client.delete(processed_set)
    
    insults = [
        "tonto", "bobo", "idiota", "imbecil", "burro",
        "estupido", "torpe", "payaso", "tortuga", "pringao"
    ]
    
    messages = [random.choice(insults) for _ in range(num_messages)]  # Missatges aleatoris d'insults
    client.rpush(queue_name, *messages)
    print(f"S'han inserit {num_messages} insults inicials")
    
def start_node(node_id):
    """Crea un fil que simula un node que processa missatges amb retard T"""
    def process_node():
        while True:
            # Intenta treure un missatge de la cua (espera 1 segon si no hi ha)
            msg = client.blpop(queue_name, timeout=1)
            if msg:
                # Marca el missatge com a processat afegint-lo al conjunt
                client.sadd(processed_set, msg[1])
                # Simula el temps de processament
                time.sleep(T)
    # Crea i inicia un fil daemon per processar missatges
    t = threading.Thread(target=process_node, daemon=True)
    t.start()
    return t

def calculate_needed_nodes():
    """Calcula el nombre de nodes necessaris segons la formula N = (λ × T) / C"""
    current_queue = client.llen(queue_name)  # Obte la mida actual de la cua
    if current_queue == 0:
        return MIN_NODES  # Si no hi ha missatges, retorna minim de nodes
    
    now = time.time()
    # Temps transcorregut des de l'ultima mesura, minim 0.1s per evitar divisio per zero
    elapsed = max(0.1, now - getattr(calculate_needed_nodes, '_last_time', now-1))
    # Taxa d'arribada de missatges (lambda) calculada com diferencia cua dividida pel temps
    lambda_rate = max(0, getattr(calculate_needed_nodes, '_last_queue', current_queue) - current_queue) / elapsed
    
    # Guarda l'estat per la seguent iteracio
    calculate_needed_nodes._last_queue = current_queue
    calculate_needed_nodes._last_time = now
    
    # Aplica la formula
    N = (lambda_rate * T) / C
    
    # Si la taxa lambda es molt baixa pero hi ha missatges pendents, ajusta nodes segons la cua
    if lambda_rate < 0.1 and current_queue > 0:
        N = max(N, ceil((current_queue * T) / 10))
    
    # Retorna un valor limitat entre MIN_NODES i MAX_NODES, arrodonit cap amunt
    return max(MIN_NODES, min(MAX_NODES, ceil(N)))

def dynamic_scaling(total_messages):
    prepare_environment(total_messages)  # Prepara la cua amb els missatges
    
    nodes = []  # Llista per guardar els fils actius (nodes)
    active_nodes = MIN_NODES  # Nombre actual de nodes actius
    
    # Inicialitza els nodes minim
    for i in range(active_nodes):
        nodes.append(start_node(i))
    
    try:
        while True:
            current_queue = client.llen(queue_name)  # Mida cua actual
            N = calculate_needed_nodes()  # Calcula nodes necessaris
            
            now = time.time()
            elapsed = max(0.1, now - getattr(calculate_needed_nodes, '_last_time', now-1))
            lambda_rate = max(0, getattr(calculate_needed_nodes, '_last_queue', current_queue) - current_queue) / elapsed
            
            # Cada segon mostra l'estat amb la λ al final
            if int(now) % 1 == 0:
                print(f"Estat: Cua={current_queue} | Nodes={active_nodes}/{N} | λ={lambda_rate:.2f} msgs/s")
            
            # Si cal, afegeix nodes
            if N > active_nodes:
                for i in range(active_nodes, N):
                    nodes.append(start_node(i))
                active_nodes = N
            
            # Si cal, redueix nodes (no s'atura fil, nomes els descarta de la llista)
            elif N < active_nodes:
                active_nodes = N
                nodes = nodes[:active_nodes]
            
            # Quan la cua esta buida i tenim els minim nodes, acaba el proces
            if current_queue == 0 and active_nodes == MIN_NODES:
                print("Processament completat!")
                break
                
            time.sleep(1)  # Espera abans de tornar a comprovar
            
    except KeyboardInterrupt:
        print("Aturada manual rebuda")
    
    finally:
        print("Neteja final...")
        client.delete(queue_name)
        client.delete(processed_set)

if __name__ == "__main__":
    tests = [2000, 5000, 10000]  # Llistat de carregues a provar
    durations = []  # Per guardar el temps d'execucio de cada prova
    
    for load in tests:
        print(f"\n=== PROVA AMB {load} MISSATGES ===")
        print("Iniciant sistema d'escalat dinamic")
        print("Formula: N = (λ × T) / C")
        print(f"On: T={T}s/msg, C={C} msg/s/node")
        
        start_time = time.time()
        dynamic_scaling(load)  # Executa la prova
        end_time = time.time()
        
        duration = end_time - start_time
        durations.append(duration)  # Guarda la durada
        
        print(f"Prova amb {load} missatges completada en {duration:.2f} segons")
        print("="*50)
        time.sleep(5)  # Pausa entre proves

    # Mostra i desa la grafica amb el rendiment
    plt.figure(figsize=(8,5))
    plt.plot(tests, durations, marker='o')
    plt.title("Temps d'execucio per carrega")
    plt.xlabel("Nombre de missatges")
    plt.ylabel("Temps (segons)")
    plt.grid(True)
    plt.savefig("rendiment_redis_dynamic_scaling.png")
    plt.show()
