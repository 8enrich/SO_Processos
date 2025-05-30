"""
Google collab relacionado:
    https://colab.research.google.com/drive/1y9QjeIOMFkuAX7P3cKeqNM3ByZEWfG3D?usp=sharing
"""
import threading as th
import time
import logging
from enum import Enum, auto
from typing import Dict, List
from dataclasses import dataclass

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(threadName)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

class Action(Enum):
    WAIT_START = auto()
    WAIT_END = auto()
    COMPILE = auto()
    COMPILE_END = auto()
    REST = auto()
    REST_END = auto()

@dataclass
class Event:
    timestamp: float
    programmer_id: int
    action: Action

class Result:
    def __init__(
        self, num_programmers, total, active,
        idle, cpu_util, counts, min_c, max_c, avg_c
    ):
        self.num_programmers = num_programmers
        self.total = total
        self.active = active
        self.idle = idle
        self.cpu_util = cpu_util
        self.counts = counts
        self.min_c = min_c
        self.max_c = max_c
        self.avg_c = avg_c

class ProgrammerSimulation:
    def __init__(
        self,
        compile_time: float = 0.1,
        rest_time: float = 0.01,
        num_programmers: int = 5,
        db_connections: int = 2,
        compilers: int = 1,
        acquire_db_first: bool = True
    ) -> None:
        if compile_time < 0 or rest_time < 0:
            raise ValueError("compile_time and rest_time must be positive")
        if num_programmers <= 0:
            raise ValueError("num_programmers must be positive")
        if db_connections <= 0:
            raise ValueError("db_connections must be positive")
        if compilers <= 0:
            raise ValueError("compilers must be positive")

        self.compile_time = compile_time
        self.rest_time = rest_time
        self.num_programmers = num_programmers
        self.database = th.Semaphore(db_connections)
        self.compiler = th.Semaphore(compilers)
        self.acquire_db_first = acquire_db_first
        self.threads: List[th.Thread] = []

        self.events: List[Event] = []
        self.stats_lock = th.Lock()
        self.running = th.Event()
        self.running.set()

    def act(self, programmer_id: int, action: Action) -> None:
        ts = time.time()
        with self.stats_lock:
            self.events.append(Event(ts, programmer_id, action))

        if action == Action.COMPILE:
            duration = self.compile_time
        elif action == Action.REST:
            duration = self.rest_time
        else:
            duration = 0
        time.sleep(duration)

        # record end of action
        end_action = Action[f"{action.name}_END"] if action.name in ['COMPILE', 'REST'] else None
        if end_action:
            ts_end = time.time()
            with self.stats_lock:
                self.events.append(Event(ts_end, programmer_id, end_action))

    def programmer(self, pid: int) -> None:
        while self.running.is_set():
            self.act(pid, Action.WAIT_START)
            if self.acquire_db_first:
                with self.database:
                    with self.compiler:
                        self.act(pid, Action.WAIT_END)
                        self.act(pid, Action.COMPILE)
            else:
                with self.compiler:
                    with self.database:
                        self.act(pid, Action.WAIT_END)
                        self.act(pid, Action.COMPILE)
            self.act(pid, Action.REST)

    def start(self) -> None:
        for i in range(self.num_programmers):
            t = th.Thread(target=self.programmer, args=(i+1,), name=f"P-{i+1}")
            self.threads.append(t)
            t.start()

    def stop(self) -> None:
        self.running.clear()
        for t in self.threads:
            t.join()

    def run_for(self, duration: float) -> Result:
        self.start_time = time.time()
        self.start()
        time.sleep(duration)
        self.stop()
        self.end_time = time.time()
        return self.analyze()

    def analyze(self) -> Result:
        total = self.end_time - self.start_time
        compiles: List[tuple] = []
        ongoing: Dict[int, float] = {}
        for ev in sorted(self.events, key=lambda e: e.timestamp):
            if ev.action == Action.COMPILE:
                ongoing[ev.programmer_id] = ev.timestamp
            elif ev.action == Action.COMPILE_END and ev.programmer_id in ongoing:
                compiles.append((ongoing.pop(ev.programmer_id), ev.timestamp))
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

        counts: Dict[int, int] = {}
        for ev in self.events:
            if ev.action == Action.COMPILE:
                counts.setdefault(ev.programmer_id, 0)
                counts[ev.programmer_id] += 1
        min_c = min(counts.values())
        max_c = max(counts.values())
        avg_c = sum(counts.values()) / len(counts)

        return Result(
            self.num_programmers,
            total,
            active,
            idle,
            cpu_util,
            counts,
            min_c,
            max_c,
            avg_c,
        )

def run_experiment(
    compile_time: float,
    rest_time: float,
    num_programmers: int,
    db_connections: int,
    compilers: int,
    duration: float,
    acquire_db_first: bool = True
) -> Result:
    sim = ProgrammerSimulation(
        compile_time=compile_time,
        rest_time=rest_time,
        num_programmers=num_programmers,
        db_connections=db_connections,
        compilers=compilers,
        acquire_db_first=acquire_db_first
    )
    return sim.run_for(duration)

if __name__ == "__main__":
    result = run_experiment(0.1, 0.01, 5, 2, 1, duration=30)
    logger.info(f"CPU Utilization: {result.cpu_util:.2f}%")
    logger.info(f"Compilations per programmer: {result.counts}")
