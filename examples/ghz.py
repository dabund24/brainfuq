from brainfuq_interpreter.brainfuq_interpreter import BrainfuqInterpreter
from brainfuq_interpreter.brainfuq_simulator import BrainfuqSimulator

N = 10

simulator = BrainfuqSimulator()
interpreter = BrainfuqInterpreter(simulator)

# put q0 in equal superposition
program = "~"

# loop counter
program += "+" * N

# loop body: add a cnot and decrement loop counter
program += "[#}*-]"

interpreter.interpret_program(program)
print(simulator)


# reset interpreter before interpreting the next program
interpreter.reset()