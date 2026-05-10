import qiskit as qk
from .basis_gates import to_basis_gates

def qiskit_to_brainfuq(qc: qk.QuantumCircuit) -> str:
    """
    Translate a qiskit circuit to Brainfuq.
    The output produced here is not optimized.

    :param qc: The circuit to translate
    :return: The Brainfuq translation
    """
    qc = to_basis_gates(qc)
    res = ""
    for instr in qc.data:
        if instr.is_controlled_gate():
            res += _parse_control_gate(name=instr.name, control_qubit=instr.qubits[0]._index, target_qubit=instr.qubits[1]._index)
        else:
            res += _parse_regular_gate(name=instr.name, qubit=instr.qubits[0]._index)
    return res

def _parse_regular_gate(name: str, qubit: int) -> str:
    ops = {
        "x": "*",
        "h": "~",
        "t": ";",
        "measure": ":"
    }
    return _op_at_qubit(op=ops[name], qubit=qubit)
    
def _parse_control_gate(name: str, control_qubit: int, target_qubit: int) -> str:
    res = _op_at_qubit(op="#", qubit=control_qubit)

    ops = {
        "cx": "*",
        "ch": "~",
        "ct": ";",
    }
    res += _op_at_qubit(op=ops[name], qubit=target_qubit)

    return res

def _op_at_qubit(op: str, qubit: int) -> str:
    res = "}" * qubit
    res += op
    res += "{" * qubit
    return res
