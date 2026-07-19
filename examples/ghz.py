from brainfuq_interpreter.brainfuq_interpreter import BrainfuqInterpreter
from brainfuq_interpreter.brainfuq_simulator import BrainfuqSimulator
from brainfuq_interpreter.brainfuq_to_qiskit_translator import QiskitBrainfuqInterpreter

N = 10

draw = True
output_method = "text" # set to "latex_source" for source code to use in your document

simulator = BrainfuqSimulator()
interpreter = BrainfuqInterpreter(simulator)

# put q0 in equal superposition
program = "~"

# loop counter
program += "+" * (N - 1)

# loop body: add a cnot and decrement loop counter
program += "[#}*-]"

interpreter.interpret_program(program)
print(simulator)

# reset interpreter before interpreting the next program
interpreter.reset()

if draw:
    translation_interpreter = BrainfuqInterpreter(QiskitBrainfuqInterpreter(verbose=False))
    qc, _ = translation_interpreter.interpret_program(program)
    print(qc.draw(output=output_method))
