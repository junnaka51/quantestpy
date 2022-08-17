from quantestpy import TestCircuit
from qiskit import QuantumCircuit, assemble


def _cvt_qiskit_to_test_circuit(qiskit_circuit: QuantumCircuit) -> TestCircuit:

    qobj = assemble(qiskit_circuit)
    qobj_dict = qobj.to_dict()
    experiments = qobj_dict['experiments'][0]  # [0] changes list into dict.
    gates = experiments['instructions']
    num_qubits = experiments['config']['n_qubits']
    circuit = TestCircuit(num_qubits)

    for gate in gates:
        if len(gate["qubits"]) == 2:
            control_qubit = [gate["qubits"][0]]
            target_qubit = [gate["qubits"][1]]
        else:
            control_qubit = []
            target_qubit = [gate["qubits"][0]]

        # parameter is necessary after implementing parameter in test_circuit.py
        # if "params" in gate:
        #    parameter = gate["params"]
        # else:
        #    parameter = []

        if gate["name"] in ["cx", "cnot"]:
            control_value = [1]
        else:
            control_value = []

        gate_test = dict(name=gate["name"], target_qubit=target_qubit,
                         control_qubit=control_qubit, control_value=control_value)  # , parameter=parameter)
        circuit.add_gate(gate_test)

    return circuit


def _cvt_openqasm_to_test_circuit(qasm: str) -> TestCircuit:
    qiskit_circuit = QuantumCircuit.from_qasm_str(qasm)
    return _cvt_qiskit_to_test_circuit(qiskit_circuit)
