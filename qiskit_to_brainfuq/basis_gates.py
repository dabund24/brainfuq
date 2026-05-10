import qiskit as qk
from qiskit.transpiler import Target
from qiskit.circuit.library import (
    XGate,
    CXGate,
    HGate,
    CHGate,
    TGate,
)
from qiskit.circuit import Measure


def to_basis_gates(qc: qk.QuantumCircuit) -> qk.QuantumCircuit:
    """
    Transpile a qiskit circuit to only include the basis gates allowed in brainfuq.

    :param qc: The circuit to transpile
    :return: The transpiled qiskit circuit
    """
    target = Target(num_qubits=qc.num_qubits)

    # important to make transpiler happy
    single_qubit_map = {
        (i,): None
        for i in range(qc.num_qubits)
    }
    two_qubit_map = {
        (i, j): None
        for i in range(qc.num_qubits)
        for j in range(qc.num_qubits)
        if i != j
    }


    target.add_instruction(XGate(), single_qubit_map)
    target.add_instruction(HGate(), single_qubit_map)
    target.add_instruction(TGate(), single_qubit_map)
    target.add_instruction(CXGate(), two_qubit_map)
    target.add_instruction(CHGate(), two_qubit_map)
    target.add_instruction(TGate().control(), two_qubit_map)
    target.add_instruction(Measure(), single_qubit_map)

    return qk.transpile(
        qc,
        target=target,
        optimization_level=0,
    )
