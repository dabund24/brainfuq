# Brainfuq

Brainfuq brings [classical Brainfuck](https://esolangs.org/wiki/Brainfuck) and [its quantum counterpart](https://esolangs.org/wiki/Quantum_brainfuck) together. Modify both a classical tape of bits using brainfuck operations and a quantum tape of qubits using operations for quantum cicuits.

<details>
<summary>Classical Brainfuck operations</summary>

| Operation | Description                                         |
|----------:|-----------------------------------------------------|
| `>`       | Increment pointer                                   |
| `<`       | Decrement pointer                                   |
| `+`       | Increment byte at pointer                           |
| `-`       | Decrement byte at pointer                           |
| `.`       | Print byte at pointer                               |
| `,`       | Write user input to byte at pointer                 |
| `[`       | Jump past matching ] if byte at pointer is 0        |
| `]`       | Jump back to matching [ if byte at pointer is not 0 |
</details>

<details>
<summary>Quantum Brainfuck operations</summary>

| Operation | Description                                    |
|----------:|------------------------------------------------|
| `}`       | Increment pointer                              |
| `{`       | Decrement pointer                              |
| `*`       | Apply X gate to qubit at pointer               |
| `~`       | Apply H gate to qubit at pointer               |
| `;`       | Apply T gate to qubit at pointer               |
| `:`       | Measure qubit at pointer and print outcome     |
| `#`       | Control next gate on the qubit at pointer      |
| `?`       | Apply next gate only if last measurement was 1 |
</details> 


Read [this report](https://github.com/dabund24/brainfuq/releases/download/submission/main.pdf) for more details.

## Features

- Interpret a Brainfuq program using a simulator with support for arbitratry quantum states
  
  `brainfuq simulate "~,-[#}*-]" -v`

- Translate a Brainfuq program into a qiskit circuit

  `brainfuq to-qiskit -o ghz.qpy "~,-[#}*{:}-]:"`

- Generate a Brainfuq program from a qiskit circuit

  `brainfuq from-qiskit ghz.qpy`

## Usage

**Requirement**:

- `python` $\ge 3.14$

**Setup**:

Create and activate venv:
```
python -m venv . venv & source . venv/bin/activate
```

Install dependencies and CLI:
```
pip install -e .
```

**Running**:

Print CLI help:
```
brainfuq -h
```

For examples of how the interpreter can be used with Python code, see the `examples` directory.

<hr>

By Paul and Daniel