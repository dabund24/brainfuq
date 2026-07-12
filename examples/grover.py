from brainfuq_interpreter.brainfuq_interpreter import BrainfuqInterpreter
from brainfuq_interpreter.brainfuq_simulator import BrainfuqSimulator

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import grover_operator

from qiskit_to_brainfuq import qiskit_to_brainfuq

N = 5

# set to False to output evolved statevector (incl. aux. qubits)
measure = True 

def linear_exact_one_oracle(N: int) -> QuantumCircuit:
    """
    Produces a Phase Oracle for N-bit AND (i.e. only solution: 11...1) with N-2 auxiliary qubits.
    """
    num_ancillas = N - 2
    qc = QuantumCircuit(N + num_ancillas)
    
    # example for N = 5
    qc.ccx(0, 1, N) # ccx(0, 1, 5)
    for i in range(num_ancillas - 1): # i = 0, 1
        # i=0: ccx(2, 5, 6)
        # i=1: ccx(3, 6, 7)
        qc.ccx(2 + i, N + i, N + i + 1)
        
    # last main qubit is factored into the phase inversion target
    qc.cz(N - 1, N + num_ancillas - 1) # cz(4, 7)
    
    # uncomputation
    for i in reversed(range(num_ancillas - 1)):
        qc.ccx(2 + i, N + i, N + i + 1)
    qc.ccx(0, 1, N)
    
    return qc

oracle = linear_exact_one_oracle(N)
operator = grover_operator(oracle=oracle, reflection_qubits=list(range(N))).decompose()

# do not increae optimization_level as qiskit_to_brainfuq translator can not handle it
operator = transpile(operator, basis_gates=['h', 'x', 't', 'cx', 'tdg'], optimization_level=0)
brainfuq_grover_operator = qiskit_to_brainfuq.qiskit_to_brainfuq(operator)

print(f"Brainfuq program length of single Grover Operator: {len(brainfuq_grover_operator)}")

brainfuq_program = ""

# initialize equal superposition
for _ in range(N - 1):
    brainfuq_program += "~}"
brainfuq_program += "~"
for _ in range(N - 1):
    brainfuq_program += "{"

search_space_size = 2 ** N
optimal_iterations = np.floor(np.pi / (4 * np.arcsin((1 / search_space_size) ** 0.5))).astype(int)

# set up loop counter
brainfuq_program += "+" * optimal_iterations

# loop body containing application of grover operator
brainfuq_program += "[" + brainfuq_grover_operator + "-]"

simulator = BrainfuqSimulator()
interpreter = BrainfuqInterpreter(simulator)

if measure:
    # measure and print to stdout
    for i in range(N - 1):
        brainfuq_program += ":}"
    brainfuq_program += ":"

interpreter.interpret_program(brainfuq_program)

if not measure:
    print(simulator) # print evolved statevector

# reset interpreter before interpreting the next program
interpreter.reset()