import threading
import time
import random
import matplotlib.pyplot as plt


class RestRoom:
    """
    Sala de repouso compartilhada entre cães e gatos.
    Cães e gatos não podem estar juntos ao mesmo tempo.
    """
    def __init__(self):
        self.lock = threading.Lock()
        self.num_dogs = 0
        self.num_cats = 0
        self.history = []

    def enter_dog(self, dog_id):
        while True:
            with self.lock:
                if self.num_cats == 0:
                    self.num_dogs += 1
                    self._log_state()
                    return
            time.sleep(random.uniform(0.01, 0.05))

    def leave_dog(self, dog_id):
        with self.lock:
            self.num_dogs -= 1
            self._log_state()

    def enter_cat(self, cat_id):
        while True:
            with self.lock:
                if self.num_dogs == 0:
                    self.num_cats += 1
                    self._log_state()
                    return
            time.sleep(random.uniform(0.01, 0.05))

    def leave_cat(self, cat_id):
        with self.lock:
            self.num_cats -= 1
            self._log_state()

    def _log_state(self):
        timestamp = time.time()
        self.history.append((timestamp, self.num_dogs, self.num_cats))


def simulate_animal(rest_room, animal_type, animal_id):
    if animal_type == "dog":
        rest_room.enter_dog(animal_id)
        time.sleep(random.uniform(0.05, 0.2))
        rest_room.leave_dog(animal_id)
    elif animal_type == "cat":
        rest_room.enter_cat(animal_id)
        time.sleep(random.uniform(0.05, 0.2))
        rest_room.leave_cat(animal_id)


def run_interleaved_simulation(group_sizes, first_group='dog'):
    """
    Executa a simulação intercalando grupos de cães e gatos.
    Exemplo de group_sizes: [5, 8, 3, 7] significa 5 cães, depois 8 gatos, depois 3 cães, etc.
    """
    rest_room = RestRoom()
    history = []
    current_group = first_group

    for group_size in group_sizes:
        threads = []
        for i in range(group_size):
            animal_id = f"{current_group[0]}{i}"
            t = threading.Thread(target=simulate_animal, args=(rest_room, current_group, animal_id))
            threads.append(t)

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Adiciona apenas os novos eventos ao histórico
        history.extend(rest_room.history[len(history):])
        current_group = 'cat' if current_group == 'dog' else 'dog'

    return history


def plot_single_simulation(history, title="Simulação com Intercalação de Grupos", filename="grafico_final.png"):
    times = [event[0] - history[0][0] for event in history]
    dogs = [event[1] for event in history]
    cats = [event[2] for event in history]

    plt.figure(figsize=(14, 7))
    plt.plot(times, dogs, label='Cães', linestyle='-', marker='o')
    plt.plot(times, cats, label='Gatos', linestyle='--', marker='x')

    plt.xlabel('Tempo (s)')
    plt.ylabel('Quantidade na sala')
    plt.title(title)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def main():
    # Alternância entre grupos: cães → gatos → cães → gatos...
    group_sizes = [5, 7, 4, 8, 3, 6]  # número de animais por grupo
    history = run_interleaved_simulation(group_sizes, first_group='dog')
    plot_single_simulation(history)


if __name__ == "__main__":
    main()
