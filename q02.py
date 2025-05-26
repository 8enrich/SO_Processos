import threading
import time
import random
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

class ProgrammerSimulation:
    def __init__(self, max_time: float = 1.0, num_programmers: int = 5, 
                 db_connections: int = 2, compilers: int = 1):
        self.MAX_TIME = max_time
        self.NUMBER_OF_PROGRAMMERS = num_programmers
        self.database = threading.Semaphore(db_connections)
        self.compiler = threading.Semaphore(compilers)
        self.threads = []
        self.stats = {
            'compilations': 0,
            'rests': 0,
        }

    def act(self, action: str) -> None:
        work_time = random.uniform(0, selfMAX_TIME)
        print(f"{threading.current_thread().name} vai {action} por {work_time} segundos")
        sleep(random.uniform(0, MAX_TIME))

    def programmer(self) -> None:
        while True:
            with compiler:
                with database:
                    act("compilar")
            act("descançar")


def main():
    threads = []
    for i in range(NUMBER_OF_PROGRAMMERS):
        t = threading.Thread(target=programmer, name=f"Programador {i + 1}")
        threads.append(t)

    for t in threads:
        t.start()

    for t in threads:
        t.join()

if __name__ == "__main__":
    main()
