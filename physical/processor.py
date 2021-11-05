from physical.circuit import PhysicalCircuit
from device.connection import Connection
import asyncio
import numpy as np
import time
import ray


@ray.remote
class QuantumProcessor(object):
    """A class of a single quantum processor"""

    def __init__(self, detail):
        """Define a quantum processor

        Attributes:
            name (str): the name
            qubit_num (int): the number of qubits
            gates (list[QuantumGate]): the list of quantum gates
            pc (QuantumCircuit): the quantum circuit

        """
        self.id = detail["id"]
        self.qubit_num = detail["qubit_num"]
        self.execution_time = detail["execution_time"]
        self.pc = detail["physical_circuit"]
        self.gates = []

        self.cluster = None
        self.connection_list = []

    def get_id(self):
        """Return the processor id

        Returns:
            str: the name of a quantum processor
        """
        return self.id

    def get_gates(self):
        """Return the quantum gate list

        Returns:
            list[QuantumGate]: List of quantum gates
        """
        return self.gates

    def get_qubit_num(self):
        """Return the number of qubits

        Returns:
            int: the number of qubits on a quantum processor
        """
        return self.qubit_num

    def get_state(self):
        """Retreive the current quantum state

        Returns:
            np.array: the state vector
        """
        return self.pc.state

    def set_gates(self, gates):
        """Give the gate list to the quantum processor

        Args:
            gates (list[QuantumGate]): the new list of quantum gates
        """
        self.gates = gates

    def set_cluster(self, cluster):
        """Give the time for applying each gate

        Args:
            cluster (list(QuantumProcessor)): List of quantum processors
        """
        self.cluster = cluster

    def set_connection_list(self, connection_list):
        """Give the time for applying each gate

        Args:
            cluster (list(QuantumProcessor)): List of quantum processors
        """
        self.connection_list = connection_list

    def wait(self):
        time.sleep(self.execution_time)

    def x(self, idx):
        """Apply an X gate

        Args:
            idx (int): The index of qubit that X gate is applied to
        """
        self.pc.px(idx)
        self.wait()

    def y(self, idx):
        """Apply an Y gate

        Args:
            idx (int): The index of qubit that Y gate is applied to
        """
        self.pc.py(idx)
        self.wait()

    def z(self, idx):
        """Apply an Z gate

        Args:
            idx (int): The index of qubit that Z gate is applied to
        """
        self.pc.pz(idx)
        self.wait()

    def h(self, idx):
        """Apply an H gate

        Args:
            idx (int): The index of qubit that H gate is applied to
        """
        self.pc.ph(idx)
        self.wait()

    def cx(self, control_idx, target_idx):
        """Apply an CNOT gate

        Args:
            control_idx (int): The index of controlled qubit
            target_idx (int): The index of target qubit
        """
        self.pc.pcx(control_idx, target_idx)
        self.wait()

    def execute(self):
        """Execute the quantum gates in the given gate list"""
        for gate in self.gates:

            if gate.name == "X":
                self.x(gate.index)

            elif gate.name == "Y":
                self.y(gate.index)

            elif gate.name == "Z":
                self.z(gate.index)

            elif gate.name == "H":
                self.h(gate.index)

            elif gate.name == "CNOT":
                self.cx(gate.index, gate.target_index)

            elif gate.name == "RemoteCNOT":
                conn = self.connection_list[gate.id]
                try:
                    conn.send_message(gate.id)
                    ack = conn.get_ack()
                except ray.util.queue.Full:
                    message = conn.get_message()
                    conn.send_ack("ack")

    def add_new_zero(self, num, new_index):
        """Insert zero to arbitrary position of a binary string

        E.g. insert 0 to the 2nd digit of 010 → 0010

        Args:
            num (int): the number
            new_index ([type]): the index of a new zero

        Returns:
            str: the binary string with an additional zero
        """
        string = bin(num)[2:].zfill(self.qubit_num)
        string_list = list(string)
        string_list.insert(new_index, '0')
        new_string = "".join(string_list)
        return new_string

    def add_qubit(self, new_index):
        """Update the quantum state by adding another qubit

        Args:
            new_index (int): the index of the new qubit
        """
        state_dict = {}
        for idx in range(len(self.pc.state)):
            new_idx = self.add_new_zero(idx, new_index)
            state_dict[new_idx] = self.pc.state[idx]

        new_state = [0 for idx in range(2**(self.qubit_num + 1))]
        for key in list(state_dict.keys()):
            new_idx = int(key, 2)
            new_state[new_idx] = state_dict[key]
        self.pc.state = new_state

    def measure(self, idx):
        """Measure a qubit
        Args:
            idx (int): the index of a qubit that users measure
        """
        # Create a probability list
        prob = [prob_amp**2 for prob_amp in self.state]
        prob_dict = {}
        for state_ in range(len(prob)):
            prob_dict[format(state_, 'b').zfill(self.qubit_num)] = prob[state_]

        # Get a measured outcome
        measure_prob = [0, 0]
        for state_ in list(prob_dict.keys()):
            if state_[idx] == "0":
                measure_prob[0] += prob_dict[state_]
            else:
                measure_prob[1] += prob_dict[state_]
        measure_result = np.random.choice(range(2), 1, p=measure_prob)[0]

        # Update a previous state dict (state: probability amplitude)
        state_dict = {}
        for state_ in range(len(prob)):
            index = format(state_, 'b').zfill(self.ubit_num)
            state_dict[index] = self.state[state_]

        new_state_dict = {}
        for state_ in list(state_dict.keys()):
            if state_[idx] == str(measure_result):
                state_list = list(state_)
                del state_list[idx]
                new_state = "".join(state_list)
                new_state_dict[new_state] = state_dict[state_]

        new_prob = [prob_amp**2 for prob_amp in list(new_state_dict.values())]
        for state_ in list(new_state_dict.keys()):
            new_state_dict[state_] *= np.sqrt(1 / sum(new_prob))

        new_state = np.array(list(new_state_dict.values()))
        self.state = new_state
        return measure_result
