import argparse
from qiskit import qpy
from brainfuq_interpreter.brainfuq_interpreter import BrainfuqInterpreter
from brainfuq_interpreter.brainfuq_to_qiskit_translator import QiskitBrainfuqInterpreter
from brainfuq_interpreter.brainfuq_simulator import BrainfuqSimulator
from qiskit_to_brainfuq.qiskit_to_brainfuq import qiskit_to_brainfuq


def simulate_brainfuq(program: str, verbose: bool):
    print("Simulating Brainfuq")

    brainfuq_simulator = BrainfuqSimulator()
    interpreter = BrainfuqInterpreter(brainfuq_simulator)
    _, classical_tape = interpreter.interpret_program(program)
    
    if verbose:
        print(f"\nQuantum State:\n{brainfuq_simulator}\n\nClassical tape:\n{classical_tape}")

def translate_to_qiskit(program: str, output_file: str | None):
    print("Translating Brainfuq to Qiskit Circuit")
    
    interpreter = BrainfuqInterpreter(QiskitBrainfuqInterpreter())
    
    qiskit_circuit, _ = interpreter.interpret_program(program)
    print(qiskit_circuit)

    if output_file is not None:
        with open(output_file, "wb") as file:
            qpy.dump(qiskit_circuit, file)
            print(f"Wrote {output_file}")

def translate_from_qiskit(input_file: str):
    print("Translating Qiskit Circuit to Brainfuq")

    with open(input_file, "rb") as handle:
        qc = qpy.load(handle)

    print(qiskit_to_brainfuq(qc[0])) 


def main():
    parser = argparse.ArgumentParser(
        description="""Simulate hybrid Brainfuck/Brainfuq programs or translate them to Qiskit circuits.

Brainfuck Operations operate on a classical tape:
  >  Increment pointer
  <  Decrement pointer
  +  Increment byte at pointer
  -  Decrement byte at pointer
  .  Print byte at pointer
  ,  Write user input to byte at pointer
  [  Jump past matching ] if byte at pointer is 0
  ]  Jump back to matching [ if byte at pointer is not 0

Brainfuq Operations operate on a quantum tape:
  }  Increment pointer
  {  Decrement pointer
  *  Apply X gate to qubit at pointer
  ~  Apply H gate to qubit at pointer
  ;  Apply T gate to qubit at pointer
  :  Measure qubit at pointer and print outcome
  #  Control next gate on the qubit at pointer
  ?  Apply next gate only if last measurement was 1""",
        formatter_class=argparse.RawTextHelpFormatter
    )

    
    subparsers = parser.add_subparsers(dest="command", required=True, help="available subcommands")

    simulate_parser = subparsers.add_parser(
        "simulate",
        help="simulate a brainfuq program. For additional help, run brainfuq simulate -h",
        description="""Simulate a brainfuq program.

Example:
brainfuq simulate "~,-[#}*-]" --verbose
Simulate a GHZ state, where the amount of qubits are read from stdin. Print the quantum state and the contents of the classical tape thereafter""",
        formatter_class=argparse.RawTextHelpFormatter
    )
    simulate_parser.add_argument("program", type=str, help="the brainfuq program string inside quotes")
    simulate_parser.add_argument("-v", "--verbose", action="store_true", help="print the quantum state and classical tape after simulation")

    to_qiskit_parser = subparsers.add_parser(
        "to-qiskit",
        help="translate a brainfuq program into a qiskit circuit and optionally serialize it. For additional help, run brainfuq to-qiskit -h",
        description="""Translate a brainfuq program into a qiskit circuit and optionally serialize it to a qpy file.

Example:
brainfuq to-qiskit -o ghz.qpy "~,-[#}*{:}-]:"
Print a qiskit circuit generating a GHZ state with subsequent measure operations, where the amount of qubits are read from stdin.
Afterwards, serialize the circuit to ghz.qpy""",
        formatter_class=argparse.RawTextHelpFormatter)
    to_qiskit_parser.add_argument("-o", "--output", metavar="filename", help="serialize qiskit circuit to qpy file")
    to_qiskit_parser.add_argument("program", type=str, help="the brainfuq program string inside quotes")

    from_qiskit_parser = subparsers.add_parser(
        "from-qiskit",
        help="translate a serialized qiskit circuit into a brainfuq program (experimental). For additional help, run brainfuq from-qiskit -h",
        description="""Translate a serialized qiskit circuit into a brainfuq program (experimental).

Example:
brainfuq from-qiskit ghz.qpy
Deserialize ghz.py and print a brainfuq translation of the circuit.""",
        formatter_class=argparse.RawTextHelpFormatter)
    from_qiskit_parser.add_argument("filename", type=str, help="the filename of the qpy file to deserialize and translate into brainfuq")

    args = parser.parse_args()

    if args.command == "simulate":
        simulate_brainfuq(args.program, args.verbose)
    elif args.command == "to-qiskit":
        translate_to_qiskit(program=args.program, output_file=args.output)
    elif args.command == "from-qiskit":
        translate_from_qiskit(args.filename)
