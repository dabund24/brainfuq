import qiskit as qk
import numpy as np
from qiskit.quantum_info import Operator
from qiskit.circuit.library import QFTGate
from qiskit_to_brainfuq.basis_gates import to_basis_gates

def _check_for_circuit(qc: qk.QuantumCircuit):
    qc_transpiled = to_basis_gates(qc)
    _assert_circuit_equivalence(qc, qc_transpiled)
    _assert_only_includes_allowed_gates(qc_transpiled)

def _assert_circuit_equivalence(qc_1: qk.QuantumCircuit, qc_2: qk.QuantumCircuit):
    assert Operator(qc_1).equiv(Operator(qc_2))

def _assert_only_includes_allowed_gates(qc: qk.QuantumCircuit):
    for instr in qc.data:
        assert instr.name in ["x", "h", "t", "cx", "ch", "ct", "measure"]


def test_swap():
    qc = qk.QuantumCircuit(2)
    qc.swap(0,1)
    _check_for_circuit(qc)

def test_p():
    qc = qk.QuantumCircuit(3)
    qc.p(np.pi, 0)
    qc.p(np.pi / 2, 1)
    qc.p(np.pi / 4, 2)
    _check_for_circuit(qc)

def test_cp():
    qc = qk.QuantumCircuit(3)
    qc.cp(np.pi, 0, 1)
    qc.cp(np.pi / 2, 1, 2)
    qc.cp(np.pi / 4, 2, 0)
    _check_for_circuit(qc)

def test_qft():
    qc = qk.QuantumCircuit(3)
    qc.append(QFTGate(3), [0,1,2])
    qc = qc.decompose()
    _check_for_circuit(qc)
