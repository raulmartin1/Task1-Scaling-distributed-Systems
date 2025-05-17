import xmlrpc.client
import time
import matplotlib.pyplot as plt
from multiprocessing import Process
from concurrent.futures import ThreadPoolExecutor
import uuid
import os
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Ajustar ruta para importar servicios (modifica según tu estructura)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../xmlrpc')))
try:
    from insult_service import run_insult_server
    from insult_filter import run_filter_server
except ImportError as e:
    logging.error(f"Error al importar módulos de servicios: {e}")
    sys.exit(1)

# Puertos base para cada nodo
INSULT_BASE_PORT = 8000
FILTER_BASE_PORT = 8001

def start_insult_servers(n):
    """Inicia n nodos del InsultService en puertos consecutivos"""
    processes = []
    for i in range(n):
        port = INSULT_BASE_PORT + 2 * i  # 8000, 8002, 8004 ...
        p = Process(target=run_insult_server, args=(), kwargs={"port": port})
        p.start()
        logging.info(f"InsultService nodo {i+1} iniciado en puerto {port}")
        processes.append(p)
    return processes

def start_filter_servers(n):
    """Inicia n nodos del InsultFilter en puertos consecutivos"""
    processes = []
    for i in range(n):
        port = FILTER_BASE_PORT + 2 * i  # 8001, 8003, 8005 ...
        p = Process(target=run_filter_server, args=(), kwargs={"port": port})
        p.start()
        logging.info(f"InsultFilter nodo {i+1} iniciado en puerto {port}")
        processes.append(p)
    return processes

def stop_servers(processes):
    """Termina procesos de servidores"""
    for p in processes:
        p.terminate()
        p.join()

def stress_test_multi_node(num_requests, proxy_ports, method_name):
    """
    Envía num_requests peticiones distribuidas round-robin entre proxies en proxy_ports
    method_name es 'add_insult' o 'filter_insults'
    """
    proxies = [xmlrpc.client.ServerProxy(f"http://localhost:{port}", allow_none=True) for port in proxy_ports]
    start_time = time.time()

    def send_request(i):
        proxy = proxies[i % len(proxies)]
        arg = str(uuid.uuid4()) if method_name == 'add_insult' else f"Texto con insulto {uuid.uuid4()}"
        getattr(proxy, method_name)(arg)

    with ThreadPoolExecutor(max_workers=20) as executor:
        executor.map(send_request, range(num_requests))

    end_time = time.time()
    duration = end_time - start_time
    throughput = num_requests / duration if duration > 0 else 0
    logging.info(f"{method_name} con {len(proxies)} nodos: {num_requests} solicitudes en {duration:.2f}s, throughput={throughput:.2f} req/s")
    return duration, throughput

def clear_states(insult_ports, filter_ports):
    for port in insult_ports:
        try:
            proxy = xmlrpc.client.ServerProxy(f"http://localhost:{port}", allow_none=True)
            proxy.clear_insults()
        except Exception as e:
            logging.warning(f"Error limpiando insultos en puerto {port}: {e}")
    for port in filter_ports:
        try:
            proxy = xmlrpc.client.ServerProxy(f"http://localhost:{port}", allow_none=True)
            proxy.clear_filtered_texts()
        except Exception as e:
            logging.warning(f"Error limpiando textos filtrados en puerto {port}: {e}")

def run_static_scaling_tests(request_count=5000, max_nodes=3):
    insult_times = []
    filter_times = []

    for n_nodes in range(1, max_nodes + 1):
        # Iniciar servidores
        insult_processes = start_insult_servers(n_nodes)
        filter_processes = start_filter_servers(n_nodes)

        # Esperar para que inicien
        time.sleep(3)

        insult_ports = [INSULT_BASE_PORT + 2 * i for i in range(n_nodes)]
        filter_ports = [FILTER_BASE_PORT + 2 * i for i in range(n_nodes)]

        # Limpiar estado antes
        clear_states(insult_ports, filter_ports)

        # Stress test InsultService
        insult_time, _ = stress_test_multi_node(request_count, insult_ports, 'add_insult')
        insult_times.append(insult_time)

        # Stress test InsultFilter
        filter_time, _ = stress_test_multi_node(request_count, filter_ports, 'filter_insults')
        filter_times.append(filter_time)

        # Terminar servidores
        stop_servers(insult_processes)
        stop_servers(filter_processes)

        time.sleep(2)

    return insult_times, filter_times

def plot_static_scaling(request_count, insult_times, filter_times):
    nodes = list(range(1, len(insult_times) + 1))
    # Cálculo speedup
    insult_speedup = [insult_times[0]/t for t in insult_times]
    filter_speedup = [filter_times[0]/t for t in filter_times]

    plt.figure(figsize=(10, 5))
    plt.plot(nodes, insult_times, marker='o', label='InsultService Tiempo')
    plt.plot(nodes, filter_times, marker='s', label='InsultFilter Tiempo')
    plt.xlabel('Número de nodos')
    plt.ylabel('Tiempo (segundos)')
    plt.title(f'Escalabilidad estática - Tiempo de ejecución para {request_count} solicitudes')
    plt.legend()
    plt.grid(True)
    plt.savefig('static_scaling_time.png')
    plt.close()

    plt.figure(figsize=(10, 5))
    plt.plot(nodes, insult_speedup, marker='o', label='InsultService Speedup')
    plt.plot(nodes, filter_speedup, marker='s', label='InsultFilter Speedup')
    plt.xlabel('Número de nodos')
    plt.ylabel('Speedup')
    plt.title(f'Escalabilidad estática - Speedup para {request_count} solicitudes')
    plt.legend()
    plt.grid(True)
    plt.savefig('static_scaling_speedup.png')
    plt.close()

    logging.info("Gráficos guardados: static_scaling_time.png, static_scaling_speedup.png")

def main():
    REQUEST_COUNT = 5000
    insult_times, filter_times = run_static_scaling_tests(request_count=REQUEST_COUNT)
    for i, t in enumerate(insult_times):
        print(f"InsultService con {i+1} nodo(s): {t:.2f} s")
    for i, t in enumerate(filter_times):
        print(f"InsultFilter con {i+1} nodo(s): {t:.2f} s")
    plot_static_scaling(REQUEST_COUNT, insult_times, filter_times)

if __name__ == "__main__":
    main()
