from random import randint
import matplotlib.pyplot as plt
import statistics

TIME = 750
NUMBER_OF_PROCESSES = 20
BURST_INTERVAL = [700, 800]

def main():

    processes_burst = generate_processes(NUMBER_OF_PROCESSES, *BURST_INTERVAL)

    fcfs_data = FCFS(processes_burst, T=TIME)
    sjf_data = SJF(processes_burst, T=TIME)
    rr_150_data = RR(processes_burst, 150, T=TIME)
    rr_300_data = RR(processes_burst, 300, T=TIME)
    rr_600_data = RR(processes_burst, 600, T=TIME)
    rr_800_data = RR(processes_burst, 800, T=TIME)

    algorithms = [fcfs_data, sjf_data, rr_150_data, rr_300_data, rr_600_data, rr_800_data]
    names = [data["Algorithm"] for data in algorithms]

    mean_wait_times = [data["Mean Wait Time"] for data in algorithms]
    std_wait_times = [data["Std +/- Wait Time"] for data in algorithms]
    mean_end_times = [data["Mean End Time"] for data in algorithms]
    std_end_times = [data["Std +/- End Time"] for data in algorithms]
    throughputs = [data["Throughput"] for data in algorithms]

    plot_metric(f"Tempo Médio de Espera com {NUMBER_OF_PROCESSES} processos e burst_time de {BURST_INTERVAL[0]} a {BURST_INTERVAL[1]}", "Tempo (ms)", mean_wait_times, names)
    plot_metric(f"Desvio Padrão do Tempo de Espera com {NUMBER_OF_PROCESSES} processos e burst_time de {BURST_INTERVAL[0]} a {BURST_INTERVAL[1]}", "Desvio (ms)", std_wait_times, names)
    plot_metric(f"Tempo Médio de Retorno com {NUMBER_OF_PROCESSES} processos e burst_time de {BURST_INTERVAL[0]} a {BURST_INTERVAL[1]}", "Tempo (ms)", mean_end_times, names)
    plot_metric(f"Desvio Padrão do Tempo de Retorno com {NUMBER_OF_PROCESSES} processos e burst_time de {BURST_INTERVAL[0]} a {BURST_INTERVAL[1]}", "Desvio (ms)", std_end_times, names)
    plot_metric(f"Vazão (Throughput) T = {TIME}ms com {NUMBER_OF_PROCESSES} processos e burst_time de {BURST_INTERVAL[0]} a {BURST_INTERVAL[1]}", "Processos Completados", throughputs, names)

def FCFS(processes_burst: list[int], T: int):
    wait_time = 0
    processes_wait_time = []
    processes_end_time = []
    for burst in processes_burst:
        wait_time += 1
        processes_wait_time.append(wait_time)
        wait_time += burst
        processes_end_time.append(wait_time)

    completed_processes = sum(1 for end_time in processes_end_time if end_time <= T)

    mean_wait_time = statistics.mean(processes_wait_time)
    std_wait_time = (
        statistics.stdev(processes_wait_time) if len(processes_wait_time) > 1 else 0
    )
    mean_end_time = statistics.mean(processes_end_time)
    std_end_time = (
        statistics.stdev(processes_end_time) if len(processes_end_time) > 1 else 0
    )

    return {
        "Algorithm": "FCFS",
        "Mean Wait Time": mean_wait_time,
        "Std +/- Wait Time": std_wait_time,
        "Mean End Time": mean_end_time,
        "Std +/- End Time": std_end_time,
        "Throughput": completed_processes,
    }


def SJF(processes_burst: list[int], T: int):
    sjf_burst = sorted(processes_burst)
    response = FCFS(sjf_burst, T)
    response["Algorithm"] = "SJF"
    return response

def RR(processes_burst: list[int], quantum: int, T: int, print_simulation=False):
    n = len(processes_burst)
    remaining_burst = processes_burst[:]
    wait_times = [0] * n
    end_times = [0] * n
    start_times = [None] * n
    queue = list(range(n))
    time = 0
    steps = []
    
    while queue:
        i = queue.pop(0)
        
        for j in queue:
            wait_times[j] += 1

        if start_times[i] is None:
            start_times[i] = time
            steps.append(f"Processo {i+1} começou a executar em {time} ms")
        
        exec_time = min(quantum, remaining_burst[i])
        time += exec_time
        remaining_burst[i] -= exec_time
        
        if remaining_burst[i] > 0:
            queue.append(i)
        else:
            end_times[i] = time
            steps.append(f"Processo {i+1} terminou em {time} ms")
        
        time += 1

    for i in range(n):
        wait_times[i] = start_times[i] - i

    throughput = sum(1 for t in end_times if t <= T)

    if print_simulation:
        for step in steps:
            print(step)

    mean_wait_time = statistics.mean(wait_times)
    std_wait_time = statistics.stdev(wait_times) if n > 1 else 0
    mean_end_time = statistics.mean(end_times)
    std_end_time = statistics.stdev(end_times) if n > 1 else 0

    return {
        "Algorithm": f"RR_{quantum}",
        "Mean Wait Time": mean_wait_time,
        "Std +/- Wait Time": std_wait_time,
        "Mean End Time": mean_end_time,
        "Std +/- End Time": std_end_time,
        "Throughput": throughput,
    }
    
def generate_processes(n, start, end):
    if end < start:
        raise Exception("O começo não pode ser maior que o final")
    return [randint(start, end) for _ in range(n)]

def plot_metric(title, ylabel, values, names, show_plot=False):
    plt.figure(figsize=(8, 5))
    plt.bar(names, values, color=['blue', 'green', 'orange'])
    plt.title(title)
    plt.ylabel(ylabel)
    plt.xlabel("Algoritmo")
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    if show_plot:
        plt.show()
    plt.savefig(title.replace(" ", ""))

if __name__ == "__main__":
    main()
