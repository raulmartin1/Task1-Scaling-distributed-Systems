import xmlrpc.client
import time
import matplotlib.pyplot as plt
from multiprocessing import Process
from concurrent.futures import ThreadPoolExecutor
import uuid
import logging
import os
import sys

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Ajustar la ruta para importar los módulos de los servicios
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../xmlrpc')))
try:
    from insult_service import run_insult_server
    from insult_filter import run_filter_server
except ImportError as e:
    logging.error(f"Error al importar módulos de servicios: {e}")
    sys.exit(1)

def stress_test_insult_service(num_requests, proxy_url="http://localhost:8000"):
    """Prueba de estrés para InsultService."""
    try:
        proxy = xmlrpc.client.ServerProxy(proxy_url, allow_none=True)
        start_time = time.time()
        
        def send_request(_):
            proxy.add_insult(str(uuid.uuid4()))  # Usamos UUID para evitar duplicados
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            executor.map(send_request, range(num_requests))
        
        end_time = time.time()
        duration = end_time - start_time
        throughput = num_requests / duration if duration > 0 else 0
        logging.info(f"InsultService: {num_requests} solicitudes en {duration:.2f}s, throughput={throughput:.2f} req/s")
        return duration, throughput
    except Exception as e:
        logging.error(f"Error en stress_test_insult_service: {e}")
        return float('inf'), 0

def stress_test_filter_service(num_requests, proxy_url="http://localhost:8001"):
    """Prueba de estrés para InsultFilter."""
    try:
        proxy = xmlrpc.client.ServerProxy(proxy_url, allow_none=True)
        start_time = time.time()
        
        def send_request(_):
            proxy.filter_insults(f"Este es un texto con insulto {uuid.uuid4()}")
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            executor.map(send_request, range(num_requests))
        
        end_time = time.time()
        duration = end_time - start_time
        throughput = num_requests / duration if duration > 0 else 0
        logging.info(f"InsultFilter: {num_requests} solicitudes en {duration:.2f}s, throughput={throughput:.2f} req/s")
        return duration, throughput
    except Exception as e:
        logging.error(f"Error en stress_test_filter_service: {e}")
        return float('inf'), 0

def run_performance_tests(request_counts=[100, 500, 1000, 5000]):
    """Ejecuta pruebas de rendimiento para ambos servicios."""
    insult_times = []
    insult_throughputs = []
    filter_times = []
    filter_throughputs = []
    
    # Iniciar servidores
    insult_process = Process(target=run_insult_server)
    filter_process = Process(target=run_filter_server)
    insult_process.start()
    filter_process.start()
    time.sleep(2)  # Esperar a que los servidores inicien
    
    try:
        for num_requests in request_counts:
            # Prueba InsultService
            duration, throughput = stress_test_insult_service(num_requests)
            insult_times.append(duration)
            insult_throughputs.append(throughput)
            
            # Prueba InsultFilter
            duration, throughput = stress_test_filter_service(num_requests)
            filter_times.append(duration)
            filter_throughputs.append(throughput)
            
            # Limpiar estado para evitar acumulación
            try:
                with xmlrpc.client.ServerProxy("http://localhost:8000", allow_none=True) as proxy:
                    proxy.clear_insults()
                with xmlrpc.client.ServerProxy("http://localhost:8001", allow_none=True) as proxy:
                    proxy.clear_filtered_texts()
            except Exception as e:
                logging.warning(f"Error al limpiar estado: {e}")
    
    finally:
        # Terminar procesos
        insult_process.terminate()
        filter_process.terminate()
    
    return request_counts, insult_times, insult_throughputs, filter_times, filter_throughputs

def plot_results(request_counts, insult_times, insult_throughputs, filter_times, filter_throughputs):
    """Genera gráficos comparativos."""
    # Crear directorio para resultados si no existe
    results_dir = os.path.join(os.path.dirname(__file__), '../../docs/results')
    os.makedirs(results_dir, exist_ok=True)
    
    # Gráfico de tiempo de ejecución
    plt.figure(figsize=(10, 5))
    plt.plot(request_counts, insult_times, marker='o', label='InsultService (add_insult)')
    plt.plot(request_counts, filter_times, marker='s', label='InsultFilter (filter_insults)')
    plt.xlabel('Número de Solicitudes')
    plt.ylabel('Tiempo de Ejecución (segundos)')
    plt.title('Tiempo de Ejecución vs. Número de Solicitudes (XML-RPC)')
    plt.legend()
    plt.grid(True)
    execution_time_path = os.path.join(results_dir, 'xmlrpc_execution_time.png')
    plt.savefig(execution_time_path)
    plt.close()
    logging.info(f"Gráfico guardado: {execution_time_path}")
    
    # Gráfico de throughput
    plt.figure(figsize=(10, 5))
    plt.plot(request_counts, insult_throughputs, marker='o', label='InsultService (add_insult)')
    plt.plot(request_counts, filter_throughputs, marker='s', label='InsultFilter (filter_insults)')
    plt.xlabel('Número de Solicitudes')
    plt.ylabel('Throughput (solicitudes/segundo)')
    plt.title('Throughput vs. Número de Solicitudes (XML-RPC)')
    plt.legend()
    plt.grid(True)
    throughput_path = os.path.join(results_dir, 'xmlrpc_throughput.png')
    plt.savefig(throughput_path)
    plt.close()
    logging.info(f"Gráfico guardado: {throughput_path}")

def main():
    # Ejecutar pruebas
    try:
        request_counts, insult_times, insult_throughputs, filter_times, filter_throughputs = run_performance_tests()
        
        # Imprimir resultados
        print("\nResultados de InsultService:")
        for req, time, throughput in zip(request_counts, insult_times, insult_throughputs):
            print(f"{req} solicitudes: {time:.2f}s, {throughput:.2f} req/s")
        
        print("\nResultados de InsultFilter:")
        for req, time, throughput in zip(request_counts, filter_times, filter_throughputs):
            print(f"{req} solicitudes: {time:.2f}s, {throughput:.2f} req/s")
        
        # Generar gráficos
        plot_results(request_counts, insult_times, insult_throughputs, filter_times, filter_throughputs)
    except Exception as e:
        logging.error(f"Error en main: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
