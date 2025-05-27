import threading as th
import time
import random
import logging
from enum import Enum, auto
from typing import Dict, List

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(threadName)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


class Action(Enum):
    COMPILE = auto()
    REST = auto()


class ProgrammerSimulation:
    def __init__(self, max_time: float = 1.0, num_programmers: int = 5, 
                 db_connections: int = 2, compilers: int = 1) -> None:

        if max_time <= 0:
            raise ValueError("max_time deve ser positivo")
        if num_programmers <= 0:
            raise ValueError("num_programmers deve ser positivo") 
        if db_connections <= 0:
            raise ValueError("db_connections deve ser positivo")
        if compilers <= 0:
            raise ValueError("compilers deve ser positivo")

        self.max_time: float = max_time
        self.num_programmers: int = num_programmers
        self.database: th.Semaphore = th.Semaphore(db_connections)
        self.compiler: th.Semaphore = th.Semaphore(compilers)
        self.threads: List[th.Thread] = []

        # Estatísticas
        self.stats_lock: th.Lock = th.Lock()
        self.stats: Dict[Action, int] = {
            Action.COMPILE: 0,
            Action.REST: 0,
        }

        # Event para poder parar
        self.running: th.Event = th.Event()
        self.running.set()

    def __enter__(self) -> "ProgrammerSimulation":
        """Entrada no ContextManager"""
        logger.info("Iniciando Simulação")
        self.start()
        return self

    def __exit__(self, exc_type, *_) -> bool:
        """Saída do ContextManager"""
        logger.info("Finalizando Simulação")
        self.stop()
        self.print_stats()

        if exc_type is KeyboardInterrupt:
            logger.info("Interrupção de Teclado")
            return True
        
        return False

    def act(self, action: Action) -> None:
        """Simula uma ação (action) por um tempo aleatório (work_time) entre 0 e max_time"""
        work_time: float = random.uniform(0, self.max_time)
        thread_name: str = th.current_thread().name

        logger.info(f"{thread_name} vai {action.name} por {work_time:.2f} segundos")
        time.sleep(work_time)

        # Salva a ação
        with self.stats_lock:
            self.stats[action] += 1
            
        logger.info(f"{thread_name} terminou de {action.name}")


    def programmer(self) -> None:
        """Faz Programa e depois descança (ninguém é de ferro) (no caso só compila: Precisa de um compilador e banco de dados)"""
        while self.running.is_set():
            # Acredito que na verdade, faz sentido o recurso mais raro estar como primeiro (o que não é garantido na minha implementação, mas garantido no enunciado do trabalho),
            # pois, é melhor ter o compilador, que tem um, primeiro, uma vez que o contrário causa uma thread ficar com o database "preso" sem poder usar
            with self.compiler:
                with self.database:
                    self.act(Action.COMPILE)

            self.act(Action.REST)


    def start(self) -> None:
        """Inicia as threads da simulação"""
        logger.info(f"Iniciando simulação com {self.num_programmers} programadores")
        logger.info(f"Recursos: {self.compiler._value} compilador(es), {self.database._value} conexão(ões) DB")

        # Cria os threads, daemon faz eles pararem quando o processo principal parar
        for i in range(self.num_programmers):
            t: th.Thread = th.Thread(
                target=self.programmer, 
                name=f"Programador-{i + 1}",
                daemon=True
            )
            self.threads.append(t)
            t.start()

        logger.info("Todas as threads iniciadas")

    def stop(self) -> None:
        """Para as threads da simulação"""
        self.running.clear()
        for t in self.threads:
            t.join()
        
    def print_stats(self) -> None:
        with self.stats_lock:
            logger.info("=== ESTATÍSTICAS ===")
            logger.info(f"Compilações: {self.stats[Action.COMPILE]}")
            logger.info(f"Períodos de descanso: {self.stats[Action.REST]}")


def main():
    with ProgrammerSimulation(
        max_time=1.0,
        num_programmers=5,
        db_connections=2,
        compilers=1
        ):
            time.sleep(20)


if __name__ == "__main__":
    main()
