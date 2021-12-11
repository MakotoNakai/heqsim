from disqs.physical.basicgate import x_, y_, z_, h_, cnot_
import numpy as np
import time


def apply_x(state, index):
    state_vector = state.vector
    qubit_num = state.qubit_num
    matrix = x_(qubit_num, index)
    state.vector = np.dot(matrix, state_vector)


def apply_y(state, index):
    state_vector = state.vector
    qubit_num = state.qubit_num
    matrix = y_(qubit_num, index)
    state.vector = np.dot(matrix, state_vector)


def apply_z(state, index):
    state_vector = state.vector
    qubit_num = state.qubit_num
    matrix = z_(qubit_num, index)
    state.vector = np.dot(matrix, state_vector)


def apply_h(state, index):
    state_vector = state.vector
    qubit_num = state.qubit_num
    matrix = h_(qubit_num, index)
    state.vector = np.dot(matrix, state_vector)


def apply_cnot(state, control_index, target_index):
    state_vector = state.vector
    qubit_num = state.qubit_num
    matrix = cnot_(qubit_num, control_index, target_index)
    state.vector = np.dot(matrix, state_vector)


def x(state, index, sleep_time, lock):
    if lock is not None:
        lock.acquire()
    apply_x(state, index)
    if lock is not None:
        lock.release()
        time.sleep(sleep_time)


def y(state, index, sleep_time, lock):
    if lock is not None:
        lock.acquire()
    apply_y(state, index)
    if lock is not None:
        lock.release()
        time.sleep(sleep_time)


def z(state, index, sleep_time, lock):
    if lock is not None:
        lock.acquire()
    apply_z(state, index)
    if lock is not None:
        lock.release()
        time.sleep(sleep_time)


def h(state, index, sleep_time, lock):
    if lock is not None:
        lock.acquire()
    apply_h(state, index)
    if lock is not None:
        lock.release()
        time.sleep(sleep_time)


def cnot(state, control_index, target_index, sleep_time, lock):
    if lock is not None:
        lock.acquire()
    apply_cnot(state, control_index, target_index)
    if lock is not None:
        lock.release()
        time.sleep(sleep_time)


def measure(state, index, lock):
    """Measure a qubit
    Args:
        index (int): the index of a qubit that users measure
    """
    # Measurement probability of the measured qubit
    measure_prob = {"0": 0, "1": 0}

    # Pairs of state & its probability amplitude
    state_dict = {}
    for num in range(len(state.vector)):
        comp_basis = bin(num)[2:].zfill(state.qubit_num)
        state_dict[comp_basis] = state.vector[num]

    # Calculate measurement probability of the measured qubit
    for key in list(state_dict.keys()):
        if key[index] == "0":
            measure_prob["0"] += state_dict[key]**2
        else:
            measure_prob["1"] += state_dict[key]**2

    # Perform measurement
    measure_result = np.random.choice(2, 1, p=list(measure_prob.values()))[0]

    # Pairs of each of the updated states & its probability amplitude
    new_state_dict = {}
    for num in range(len(state.vector)):
        comp_basis = bin(num)[2:].zfill(state.qubit_num)
        if comp_basis[index] == str(measure_result):
            comp_basis_list = list(comp_basis)
            del comp_basis_list[index]
            new_comp_basis = "".join(comp_basis_list)
            new_state_dict[new_comp_basis] = state.vector[num]

    # Update each of the probability amplitudes
    prob_list = []
    for key in list(new_state_dict.keys()):
        prob = new_state_dict[key]**2
        prob_list.append(prob)

    for key in list(new_state_dict.keys()):
        new_state_dict[key] *= np.sqrt(1 / sum(prob_list))

    state.vector = np.array(list(new_state_dict.values()))
    state.qubit_num -= 1

    return measure_result


def measure＿(state, index, lock):
    """Measure a qubit
    Args:
        index (int): the index of a qubit that users measure
    """
    # Measurement probability of the measured qubit
    measure_prob = {"0": 0, "1": 0}

    # Pairs of state & its probability amplitude
    state_dict = {}
    for num in range(len(state.vector)):
        comp_basis = bin(num)[2:].zfill(state.qubit_num)
        state_dict[comp_basis] = state.vector[num]

    for key in list(state_dict.keys()):
        if key[index] == "0":
            measure_prob["0"] += state_dict[key]**2
        else:
            measure_prob["1"] += state_dict[key]**2

    measure_result = np.random.choice(2, 1, p=list(measure_prob.values()))[0]

    new_state_dict = {}
    for key in list(state_dict.keys()):
        if key[index] == str(measure_result):
            key_list = list(key)
            del key_list[index]
            new_key = "".join(key_list)
            new_state_dict[new_key] = state_dict[key]

    prob_sum = sum([prob_amp**2 for prob_amp in new_state_dict.values()])
    for key in list(new_state_dict.keys()):
        new_state_dict[key] *= np.sqrt(1 / prob_sum)

    state.vector = list(new_state_dict.values())
    state.qubit_num -= 1
    return measure_result
