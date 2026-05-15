import qiskit as qk
import numpy as np
from qiskit.transpiler import Target
from qiskit.circuit.library import (
    XGate,
    CXGate,
    HGate,
    CHGate,
    TGate,
    CPhaseGate,
    PhaseGate,
)
from qiskit.circuit import Measure

def to_basis_gates(qc: qk.QuantumCircuit) -> qk.QuantumCircuit:
    """
    Transpile a qiskit circuit to only include the basis gates allowed in brainfuq.

    :param qc: The circuit to transpile
    :return: The transpiled qiskit circuit
    """
    qc_without_param_instructions = _replace_param_instructions(qc)

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
        qc_without_param_instructions,
        target=target,
        optimization_level=0,
    )

def _replace_param_instructions(qc: qk.QuantumCircuit):
    """
    Handle gates with parameters. Transpiler is too dumb for them
    """
    res = qc.copy_empty_like()
        
    for instr in qc.data:
        gate = instr.operation
        qubits = instr.qubits
        
        if isinstance(gate, PhaseGate):
            if np.isclose(float(gate.params[0]), np.pi):
                res.t(qubits[0])
                res.t(qubits[0])
                res.t(qubits[0])
                res.t(qubits[0])
                continue
            if np.isclose(float(gate.params[0]), np.pi / 2):
                res.t(qubits[0])
                res.t(qubits[0])
                continue
            if np.isclose(float(gate.params[0]), np.pi / 4):
                res.t(qubits[0])
                continue
            else:
                raise Exception("Cannot represent P gate with θ ∉ { π/2, π/4 } in qiskit basis")

        elif isinstance(gate, CPhaseGate):
            ct = TGate().control()
            if np.isclose(float(gate.params[0]), np.pi):
                res.append(ct, [qubits[0], qubits[1]])
                res.append(ct, [qubits[0], qubits[1]])
                res.append(ct, [qubits[0], qubits[1]])
                res.append(ct, [qubits[0], qubits[1]])
                continue
            if np.isclose(float(gate.params[0]), np.pi / 2):
                res.append(ct, [qubits[0], qubits[1]])
                res.append(ct, [qubits[0], qubits[1]])
                continue
            if np.isclose(float(gate.params[0]), np.pi / 4):
                res.append(ct, [qubits[0], qubits[1]])
                continue
            else:
                raise Exception("Cannot represent controlled P gate with θ ∉ { π/2, π/4 } in qiskit basis")

        res.append(instr)

    return res