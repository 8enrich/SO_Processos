import threading
import time
import random
import matplotlib.pyplot as plt
from collections import deque


class RestRoom:
    def __init__(self):
        self.lock = threading.Lock()
        self.state = "empty" 
        self.counts = {"dog": 0, "cat": 0}
        self.history = []

    def _can_enter(self, animal_type):
        return self.state == "empty" or self.state == f"{animal_type}s"

    def _log_state(self):
        timestamp = time.time()
        self.history.append((timestamp, self.counts["dog"], self.counts["cat"]))

    def _enter(self, animal_type):
        self.counts[animal_type] += 1
        self.state = f"{animal_type}s"
        self._log_state()

    def _leave(self, animal_type):
        self.counts[animal_type] -= 1
        if self.counts[animal_type] == 0:
            self.state = "empty"
        self._log_state()

    def enter(self, animal_type, animal_id):
        while True:
            with self.lock:
                if self._can_enter(animal_type):
                    self._enter(animal_type)
                    return
            time.sleep(random.uniform(0.01, 0.05))

    def leave(self, animal_type, animal_id):
        with self.lock:
            self._leave(animal_type)


def simulate_animal(rest_room, animal_type, animal_id):
    rest_room.enter(animal_type, animal_id)
    time.sleep(random.uniform(0.05, 0.2))
    rest_room.leave(animal_type, animal_id)


def generate_random_groups(num_groups=10, min_size=3, max_size=8):
    return [(random.choice(['dog', 'cat']), random.randint(min_size, max_size)) for _ in range(num_groups)]


def interleave_groups(groups):
    dogs = deque([group for group in groups if group[0] == 'dog'])
    cats = deque([group for group in groups if group[0] == 'cat'])
    interleaved = []

    last_type = None
    while dogs or cats:
        if last_type == 'dog':
            if cats:
                interleaved.append(cats.popleft())
                last_type = 'cat'
            elif dogs:
                interleaved.append(dogs.popleft())
        elif last_type == 'cat':
            if dogs:
                interleaved.append(dogs.popleft())
                last_type = 'dog'
            elif cats:
                interleaved.append(cats.popleft())
        else:
            if len(dogs) >= len(cats):
                interleaved.append(dogs.popleft())
                last_type = 'dog'
            else:
                interleaved.append(cats.popleft())
                last_type = 'cat'

    return interleaved


def run_simulation(groups):
    rest_room = RestRoom()
    full_history = []

    for animal_type, group_size in groups:
        threads = [
            threading.Thread(
                target=simulate_animal,
                args=(rest_room, animal_type, f"{animal_type[0]}{i}")
            )
            for i in range(group_size)
        ]

        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        full_history.extend(rest_room.history[len(full_history):])

    return full_history


def plot_history(history, title="Simulação - Protocolo Veterinário"):
    times = [event[0] - history[0][0] for event in history]
    dog_counts = [event[1] for event in history]
    cat_counts = [event[2] for event in history]

    plt.figure(figsize=(14, 7))
    plt.plot(times, dog_counts, label='Cães', linestyle='-', marker='o')
    plt.plot(times, cat_counts, label='Gatos', linestyle='--', marker='x')

    plt.xlabel('Tempo (s)')
    plt.ylabel('Quantidade na sala')
    plt.title(title)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def main():
    random_groups = generate_random_groups()
    print("Grupos gerados:", random_groups)

    interleaved = interleave_groups(random_groups)
    print("Grupos intercalados:", interleaved)

    history = run_simulation(interleaved)
    plot_history(history)


if __name__ == "__main__":
    main()
