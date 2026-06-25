from .brainfuq_quantum_interpreter import BrainfuqQuantumInterpreter
from .brainfuq_classical_interpreter import BrainfuqClassicalInterpreter

class BrainfuqInterpreter[T]:
    def __init__(self, quantum_interpreter: BrainfuqQuantumInterpreter[T]):
        self.__quantum_interpreter = quantum_interpreter
        self.__classical_interpreter = BrainfuqClassicalInterpreter()

    def reset(self):
        self.__quantum_interpreter.reset()
        self.__classical_interpreter.reset()
                
    def interpret_program(self, program: str) -> T:
        for i, op in enumerate(program):
            if op not in BrainfuqQuantumInterpreter.SUPPORTED_OPS and op not in BrainfuqClassicalInterpreter.SUPPORTED_OPS:
                raise ValueError(f"Syntax Error: Invalid Brainfuq command '{op}' at position {i}")

        pc = 0
        while(pc < len(program)):
            op = program[pc]
            if op in BrainfuqQuantumInterpreter.SUPPORTED_OPS:
                self.__quantum_interpreter.apply_operation(op)
            else:
                pc = self.__classical_interpreter.apply_operation(program, pc)

            pc += 1

        return self.__quantum_interpreter.return_state()
