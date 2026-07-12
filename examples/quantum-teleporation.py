from brainfuq_interpreter.brainfuq_interpreter import BrainfuqInterpreter
from brainfuq_interpreter.brainfuq_simulator import BrainfuqSimulator

# Quantum Teleportation Circuit

# Initialize q0: psi = |-⟩
program = "~;;;;"

# Set up shared bell state between q1 and q2
program += "}~#}*"

# Entangle psi with bell state: cnot q0 q1
program += "{{#}*"

# Apply h gate on q0
program += "{~"

# Measure q1 and apply x gate on q2 if measurement yielded 1
program += "}:?}*"

# Measure q0 and apply z gate on q2 if measurement yielded one
# Simulate z gate by 4 t gates
program += "{{:?}};"
program += "{{:?}};"
program += "{{:?}};"
program += "{{:?}};"

simulator = BrainfuqSimulator()
interpreter = BrainfuqInterpreter(simulator)
interpreter.interpret_program(program)

print(simulator)