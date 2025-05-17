import Pyro4
import time
import random
import matplotlib.pyplot as plt

def stress_test_insult_service(service_proxy, num_requests):
    start = time.time()
    for _ in range(num_requests):
        insult = f"insulto_{random.randint(1, 10000)}"
        service_proxy.add_insult(insult)
        service_proxy.get_insults()
    end = time.time()
    return end - start

def stress_test_insult_filter(filter_proxy, num_requests):
    start = time.time()
    for _ in range(num_requests):
        text = f"Texto con insulto {random.choice(['tonto', 'idiota'])}"
        filter_proxy.filter_insults(text)
        filter_proxy.get_filtered_texts()
    end = time.time()
    return end - start

def run_static_scaling_test(num_nodes_list, total_requests):
    ns = Pyro4.locateNS()
    uri_service = ns.lookup("InsultService")
    uri_filter = ns.lookup("InsultFilter")

    speedups_service = []
    speedups_filter = []
    times_service = []
    times_filter = []

    # Primer test con 1 nodo para referencia de tiempo base
    print(f"Probando 1 nodo con {total_requests} peticiones...")
    service_proxy = Pyro4.Proxy(uri_service)
    filter_proxy = Pyro4.Proxy(uri_filter)

    t1_service = stress_test_insult_service(service_proxy, total_requests)
    t1_filter = stress_test_insult_filter(filter_proxy, total_requests)

    times_service.append(t1_service)
    times_filter.append(t1_filter)

    speedups_service.append(1.0)
    speedups_filter.append(1.0)

    # Tests para 2 y 3 nodos
    for nodes in num_nodes_list[1:]:
        print(f"\nProbando {nodes} nodos con {total_requests} peticiones totales (divididas)...")

        requests_per_node = total_requests // nodes

        total_time_service = 0
        total_time_filter = 0

        # Aquí simulamos múltiples nodos con el mismo proxy, pero dividiendo carga
        for _ in range(nodes):
            total_time_service += stress_test_insult_service(service_proxy, requests_per_node)
            total_time_filter += stress_test_insult_filter(filter_proxy, requests_per_node)

        times_service.append(total_time_service)
        times_filter.append(total_time_filter)

        speedups_service.append(t1_service / total_time_service if total_time_service > 0 else 0)
        speedups_filter.append(t1_filter / total_time_filter if total_time_filter > 0 else 0)

    return num_nodes_list, times_service, times_filter, speedups_service, speedups_filter

def plot_speedup_vs_nodes(num_nodes_list, speedups_service, speedups_filter):
    plt.figure(figsize=(8,6))
    plt.plot(num_nodes_list, speedups_service, marker='o', label='Speedup InsultService')
    plt.plot(num_nodes_list, speedups_filter, marker='o', label='Speedup InsultFilter')
    plt.xlabel('Número de nodos')
    plt.ylabel('Speedup')
    plt.title('Speedup vs Número de nodos (Static Scaling)')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("speedup_static_scaling.png")
    plt.show()

if __name__ == "__main__":
    num_nodes_list = [1, 2, 3]
    total_requests = 1000

    print("Ejecutando análisis de escalabilidad estática con múltiples nodos (Pyro)...")
    nodes, times_service, times_filter, speedups_service, speedups_filter = run_static_scaling_test(num_nodes_list, total_requests)

    print("\nTiempos (segundos) por número de nodos:")
    for n, ts, tf in zip(nodes, times_service, times_filter):
        print(f"Nodos: {n} - InsultService: {ts:.4f}s, InsultFilter: {tf:.4f}s")

    print("\nSpeedups calculados:")
    for n, ss, sf in zip(nodes, speedups_service, speedups_filter):
        print(f"Nodos: {n} - Speedup InsultService: {ss:.4f}, Speedup InsultFilter: {sf:.4f}")

    plot_speedup_vs_nodes(num_nodes_list, speedups_service, speedups_filter)
