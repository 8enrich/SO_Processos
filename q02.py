import threading
import time
import random
import logging
from enum import Enum, auto

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

class Action(Enum):
    COMPILE = auto()
    REST = auto()

class ProgrammerSimulation:
    def __init__(self, max_time: float = 1.0, num_programmers: int = 5, 
                 db_connections: int = 2, compilers: int = 1):
        self.MAX_TIME = max_time
        self.NUMBER_OF_PROGRAMMERS = num_programmers
        self.database = threading.Semaphore(db_connections)
        self.compiler = threading.Semaphore(compilers)
        self.threads = []
        self.stats = {
            Action.COMPILE: 0,
            Action.REST: 0,
            'lock': threading.Lock()
        }

    def act(self, action: Action) -> None:
        """executes an action for a random time between 0 and MAX_TIME seconds"""
        work_time = random.uniform(0, self.MAX_TIME)
        thread_name = threading.current_thread().name

        logger.info(f"{thread_name} vai {action} por {work_time:.2f} segundos")
        time.sleep(work_time)

        with self.stats['lock']:
            self.stats[action] += 1
            
        logger.info(f"{thread_name} terminou de {action}")

#    def programmer(self) -> None:
#        while True:
#            with compiler:
#                with database:
#                    act("compilar")
#            act("descançar")

def main():
#    threads = []
#    for i in range(NUMBER_OF_PROGRAMMERS):
#        t = threading.Thread(target=programmer, name=f"Programador {i + 1}")
#        threads.append(t)
#
#    for t in threads:
#        t.start()
#
#    for t in threads:
#        t.join()

if __name__ == "__main__":
    main()
