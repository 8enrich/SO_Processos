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

        # Estatísticas, tem seu próprio lock 🔥
        self.stats = {
            Action.COMPILE: 0,
            Action.REST: 0,
            'lock': threading.Lock()
        }

    def act(self, action: Action) -> None:
        """Simula uma ação (action) por um tempo aleatório (work_time) entre 0 e MAX_TIME"""
        work_time = random.uniform(0, self.MAX_TIME)
        thread_name = threading.current_thread().name

        logger.info(f"{thread_name} vai {action} por {work_time:.2f} segundos")
        time.sleep(work_time)

        # Salva a ação
        with self.stats['lock']:
            self.stats[action] += 1
            
        logger.info(f"{thread_name} terminou de {action}")

    def programmer(self) -> None:
        """Faz Programa e depois descança (ninguém é de ferro) (no caso só compila: Precisa de um compilador e banco de dados)"""
        while True:
            # Acredito que na verdade, faz sentido o recurso mais raro estar como primeiro (o que não é garantido na minha implementação, mas garantido no enunciado do trabalho),
            # pois, é melhor ter o compilador, que tem um, primeiro, uma vez que o contrário causa uma thread ficar com o database "preso" sem poder usar
            with self.compiler:
                with self.database:
                    self.act(Action.COMPILE)
            self.act(Action.REST)

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
