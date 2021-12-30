
class BellPairManager:
    """A class for module that manages qubit indices in each bell pair"""

    def __init__(self):
        """Create a new Bell pair manager"""
        self.remote_cnot_manager = {}

    def add_new_info(self, remote_cnot_info):
        """Add information about a new Bell pair

        Args:
            remote_cnot_info (dict): information about a new Bell pair
                                    e.g.
                                    {
                                        "id": a remote cnot id,
                                        "qubit_indices": [q_control, q_target]
                                    }
        """
        remote_cnot_id = remote_cnot_info["id"]
        qubit_indices = remote_cnot_info["qubit_indices"]
        self.remote_cnot_manager[remote_cnot_id] = qubit_indices

    def get_info(self):
        """Return the content of this remote CNOT manager

        Returns:
            dict: dict that maps a remote CNOT id to qubit indices involved in that remote CNOT
        """
        return self.remote_cnot_manager

    def get_control_index(self, remote_cnot_id):
        """Return the index of the control qubit in the particular remote CNOT

        Args:
            remote_cnot_id (int): a remote CNOT id

        Returns:
            int: the index of the control qubit in the particular remote CNO
        """
        index_list = self.remote_cnot_manager[remote_cnot_id]
        control_index = index_list[0]
        self.update(control_index)
        return control_index

    def get_target_index(self, remote_cnot_id):
        """Return the index of the target qubit in the particular remote CNOT

        Args:
            remote_cnot_id (int): a remote CNOT id

        Returns:
            int: the index of the target qubit in the particular remote CNO
        """
        index_list = self.remote_cnot_manager[remote_cnot_id]
        target_index = index_list[0]
        self.update(target_index)
        return target_index

    def update(self, index):
        """Remove the given index from the remote CNOT manager

        Args:
            index (int): qubit index to remove
        """
        key = -1
        for key_ in list(self.remote_cnot_manager.keys()):
            if index in self.remote_cnot_manager[key_]:
                key = key_
        self.remote_cnot_manager[key].remove(index)

        key_list = list(self.remote_cnot_manager.keys())
        key_index = key_list.index(key)
        remaining_key_list = key_list[key_index:]

        for remaining_key in remaining_key_list:
            self.remote_cnot_manager[remaining_key] = [index - 1 for index in self.remote_cnot_manager[remaining_key]]
