import threading
from time import sleep
from datetime import datetime
import random

MAX_TIME = 1
NUMBER_OF_PROGRAMMERS = 5

def act(action: str) -> None:
    work_time = random.uniform(0, MAX_TIME)
    print(f"{threading.current_thread().name} vai {action} por {work_time} segundos")
    sleep(random.uniform(0, MAX_TIME))

def work() -> None:
    round = 0
    start = datetime.now()
    while True:
        act("compilar")
        act("descançar")
        round += 1
        if round == 20:
            elapsed = datetime.now() - start
            total_seconds = int(elapsed.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            print(f"{hours:02}:{minutes:02}:{seconds:02}")
            break

threads = []
for i in range(NUMBER_OF_PROGRAMMERS):
    t = threading.Thread(target=work, name=f"Programador {i + 1}")
    threads.append(t)

for t in threads:
    t.start()

for t in threads:
    t.join()

