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

def plot_performance(num_requests, results):
    labels = list(results.keys())
    insult_service_times = [results[label][0] for label in labels]
    insult_filter_times = [results[label][1] for label in labels]

    x = range(len(labels))
    width = 0.35

    plt.figure(figsize=(10,6))
    plt.bar(x, insult_service_times, width, label='InsultService', color='blue')
    plt.bar([i + width for i in x], insult_filter_times, width, label='InsultFilter', color='red')

    plt.xticks([i + width/2 for i in x], labels)
    plt.ylabel('Tiempo total (segundos)')
    plt.title(f'Tiempo total para {num_requests} peticiones (single node)')
    plt.legend()
    plt.grid(axis='y')

    plt.tight_layout()
    plt.savefig("single_node_performance.png")
    plt.show()

    print("Resumen de tiempos (segundos):")
    for i, label in enumerate(labels):
        print(f"{label}: InsultService={insult_service_times[i]:.4f}, InsultFilter={insult_filter_times[i]:.4f}")

if __name__ == "__main__":
    num_requests = 1000

    ns = Pyro4.locateNS()
    pyro_service_uri = ns.lookup("InsultService")
    pyro_filter_uri = ns.lookup("InsultFilter")

    pyro_service_proxy = Pyro4.Proxy(pyro_service_uri)
    pyro_filter_proxy = Pyro4.Proxy(pyro_filter_uri)

    print(f"Ejecutando stress test para {num_requests} peticiones usando Pyro4 (single node)...")

    pyro_service_time = stress_test_insult_service(pyro_service_proxy, num_requests)
    pyro_filter_time = stress_test_insult_filter(pyro_filter_proxy, num_requests)

    results = {
        "Pyro4": (pyro_service_time, pyro_filter_time),
        # Agrega aquí otras implementaciones cuando las tengas listas
    }

    plot_performance(num_requests, results)
