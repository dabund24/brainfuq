import qiskit as qk
from qiskit.circuit.library import QFTGate, TGate
from qiskit_to_brainfuq.qiskit_to_brainfuq import qiskit_to_brainfuq

def test_all_gates():
    qc= qk.QuantumCircuit(2, 1)
    qc.x(1)
    qc.h(1)
    qc.t(0)
    qc.cx(0, 1)
    qc.ch(0, 1)
    qc.append(TGate().control(), [1, 0])
    qc.measure(1, 0)
    bfqc = qiskit_to_brainfuq(qc)
    assert bfqc == ";}*~{#}*{#}~#{;}:{"

def test_qft():
    qc= qk.QuantumCircuit(3)
    qc.append(QFTGate(3), [0, 1, 2])
    qc = qc.decompose()
    bfqc = qiskit_to_brainfuq(qc)
    assert bfqc == "}}~#{;}#{;~}#{{;}#{;}#{;~#}}*#{{*#}}*{{"

def test_bell_state():
    qc = qk.QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure_all()
    bfqc = qiskit_to_brainfuq(qc)
    assert bfqc == "~#}*{:}:{"