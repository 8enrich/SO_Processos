import statistics

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


print(FCFS([10, 50, 20, 15, 200, 80, 130, 70, 400], T=100))
print()
print(SJF([200, 50, 20, 15, 80, 130, 70, 400], T=100))

def RR(proccesses: list[int], ):
    pass
