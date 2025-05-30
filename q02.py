"""
Google collab relacionado:
    https://colab.research.google.com/drive/1y9QjeIOMFkuAX7P3cKeqNM3ByZEWfG3D?usp=sharing
"""
import threading as th
import time
import random
import logging
from enum import Enum, auto
from typing import Dict, List, Tuple, Union

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
    def __init__(
        self,
        max_time: float = 1.0,
        num_programmers: int = 5,
        db_connections: int = 2,
        compilers: int = 1
    ) -> None:
        if max_time <= 0:
            raise ValueError("max_time deve ser positivo")
        if num_programmers <= 0:
            raise ValueError("num_programmers deve ser positivo")
        if db_connections <= 0:
            raise ValueError("db_connections deve ser positivo")
        if compilers <= 0:
            raise ValueError("compilers deve ser positivo")

        self.max_time = max_time
        self.num_programmers = num_programmers
        self.database = th.Semaphore(db_connections)
        self.compiler = th.Semaphore(compilers)
        self.threads: List[th.Thread] = []

        self.events: List[Tuple[float, str, Union[Action, str]]] = []
        self.stats_lock = th.Lock()
        self.running = th.Event()
        self.running.set()

    def __enter__(self) -> "ProgrammerSimulation":
        self.start_time = time.time()
        self.start()
        return self

    def __exit__(self, exc_type, *_) -> bool:
        self.stop()
        self.end_time = time.time()
        self.print_analysis()
        return False

    def act(self, action: Action) -> None:
        start = time.time()
        thread = th.current_thread().name

        with self.stats_lock:
            self.events.append((start, thread, action))

        duration = random.uniform(0, self.max_time)
        time.sleep(duration)

        end = time.time()
        with self.stats_lock:
            self.events.append((end, thread, f"{action.name}_END"))

    def programmer(self) -> None:
        while self.running.is_set():
            with self.compiler:
                with self.database:
                    self.act(Action.COMPILE)
            self.act(Action.REST)

    def start(self) -> None:
        for i in range(self.num_programmers):
            t = th.Thread(target=self.programmer, name=f"P-{i+1}", daemon=True)
            self.threads.append(t)
            t.start()

    def stop(self) -> None:
        self.running.clear()
        for t in self.threads:
            t.join()

    def print_analysis(self):
        total = self.end_time - self.start_time
        # extrai intervalos de compilação
        compiles = []  # list of (start, end)
        ongoing = {}
        for ts, thread, action in sorted(self.events, key=lambda x: x[0]):
            if action == Action.COMPILE:
                ongoing[thread] = ts
            elif action == "COMPILE_END" and thread in ongoing:
                compiles.append((ongoing.pop(thread), ts))
        # unir intervalos
        compiles.sort()
        merged = []
        for s, e in compiles:
            if not merged or s > merged[-1][1]:
                merged.append([s, e])
            else:
                merged[-1][1] = max(merged[-1][1], e)
        active = sum(e - s for s, e in merged)
        idle = total - active
        cpu_util = active / total * 100 if total > 0 else 0

        # fairness
        counts: Dict[str, int] = {}
        for ts, thread, action in self.events:
            if action == Action.COMPILE:
                counts.setdefault(thread, 0)
                counts[thread] += 1
        min_c = min(counts.values())
        max_c = max(counts.values())
        avg_c = sum(counts.values()) / len(counts)

        # impressão dos resultados
        # print(f"Simulação: {self.num_programmers} threads, duração {total:.2f}s")
        # print(f"Tempo ativo (compilando): {active:.2f}s")
        # print(f"Tempo ocioso: {idle:.2f}s")
        # print(f"Utilização da CPU: {cpu_util:.1f}%")
        # print("--- Fairness por thread (número de compilações) ---")
        # for th_n, c in counts.items():
            # print(f"{th_n}: {c}")
        # print(f"Min: {min_c}, Max: {max_c}, Média: {avg_c:.1f}")

        return {
                "num_programmers": self.num_programmers,
                "total": total,
                "active": active,
                "idle": idle,
                "cpu_util": cpu_util,
                "counts": counts,
                "min_c": min_c,
                "max_c": max_c,
                "avg_c": avg_c,
                }

if __name__ == "__main__":
    sim = ProgrammerSimulation(max_time=0.05, num_programmers=5, db_connections=2, compilers=1)
    with sim:
        time.sleep(600)
