import math
from typing import Optional
from qiskit import QuantumCircuit
from typing import override
from .brainfuq_interpreter import BrainfuqQuantumInterpreter

class QiskitBrainfuqInterpreter(BrainfuqQuantumInterpreter[QuantumCircuit]):
    """
    Qiskit implementation of the Brainfuq Quantum Interpreter.
    Compiles Brainfuq tapes into qiskit.QuantumCircuit objects.
    """
    
    @override
    def _reset_simulator(self) -> None:
        # History of operations: (op_type, target_idx, control_idx, classical_control_idx)
        self._operations: list[tuple[str, int, Optional[int], Optional[int]]] = []
        self._num_cbits: int = 0
        """
        The amount of measures happening in a circuit
        """

        self._last_cbit: Optional[int] = None
        """
        The last classical bit a measure operation was written to
        """

    def _get_op_context(self) -> tuple[int, Optional[int], Optional[int]]:
        """
        Helper method to resolve the current target, quantum control, 
        and classical control pointers.
        """
        target = self._qubit_map[self._quantum_ptr]
        
        control = None
        if self._control_qubit_ptr is not None:
            control = self._qubit_map[self._control_qubit_ptr]
            
        c_control = None
        if self._measurement_control_active:
            if self._last_cbit is None:
                raise RuntimeError("Attempted to apply a measurement-controlled gate, but no measurements have occurred yet.")
            c_control = self._last_cbit
            
        return target, control, c_control

    @override
    def _apply_x(self) -> None:
        self._operations.append(("x", *self._get_op_context()))

    @override
    def _apply_h(self) -> None:
        self._operations.append(("h", *self._get_op_context()))

    @override
    def _apply_t(self) -> None:
        self._operations.append(("t", *self._get_op_context()))

    @override
    def _measure(self) -> None:
        target = self._qubit_map[self._quantum_ptr]
        cbit = self._num_cbits
        self._num_cbits += 1
        self._last_cbit = cbit
        
        self._operations.append(("measure", target, None, cbit))

    def __append_regular_op_to_qiskit_circuit(self, qc: QuantumCircuit, op_type: str, target: int, control: Optional[int]) -> None:
        """
        Apply a non-measure operation to `qc`
        """
        if op_type == "x":
            qc.cx(control, target) if control is not None else qc.x(target)
        elif op_type == "h":
            qc.ch(control, target) if control is not None else qc.h(target)
        elif op_type == "t":
            qc.cp(math.pi / 4, control, target) if control is not None else qc.t(target)
        else:
            raise ValueError(f"Unknown operation type: {op_type}")


    @override
    def return_state(self) -> QuantumCircuit:
        num_qubits = len(self._qubit_map)
        qc = QuantumCircuit(num_qubits, self._num_cbits)
        
        for op_type, target, control, c_control in self._operations:
            
            if op_type == "measure":
                qc.measure(target, c_control)
                continue
                
            # Apply classical measurement conditioning if active
            if c_control is not None:
                with qc.if_test((qc.clbits[c_control], 1)):
                    self.__append_regular_op_to_qiskit_circuit(qc, op_type, target, control)
            else:
                self.__append_regular_op_to_qiskit_circuit(qc, op_type, target, control)
  
        return qc

    @override
    def __str__(self) -> str:
        return str(self.return_state().draw())
