from brainfuq_interpreter.brainfuq_to_qiskit_translator import QiskitBrainfuqInterpreter
from brainfuq_interpreter.brainfuq_interpreter import BrainfuqInterpreter
from qiskit import QuantumCircuit
import numpy as np


def _assert_circuit_equivalence(expected_qiskit: QuantumCircuit, brainfuq: str):
    interpreter = BrainfuqInterpreter(QiskitBrainfuqInterpreter(verbose=False))
    quantum_state, _ = interpreter.interpret_program(brainfuq)

    assert str(expected_qiskit) == str(quantum_state)


def test_all_ops():
    qc = QuantumCircuit(2, 2)
    qc.x(1)
    qc.h(0)
    qc.cx(0, 1)
    qc.ch(1, 0)
    qc.t(1)
    qc.cp(np.pi / 4, 0, 1)
    qc.measure(0, 0)
    qc.measure(1, 1)
    with qc.if_test((qc.clbits[1], 1)):
        qc.x(0)


    _assert_circuit_equivalence(qc, "~}*{#}*#{~};{#};{:?}:{*")

def test_bell_state():
    bell_state_qc = QuantumCircuit(2, 0)
    bell_state_qc.h(0)
    bell_state_qc.cx(0, 1)

    _assert_circuit_equivalence(bell_state_qc, "~#}*")
