import numpy as np

# return
def interpret_brainfuq(input: str) -> tuple[dict, dict, dict]:
    
    classical_tape: dict[int, int] = {}       # maps position (int) to cell value (int)
    quantum_tape: dict[int, complex] = {0: 1.0} # maps state (int) to amplitude (complex)
    qubit_map: dict[int, int] = {0: 0}         # maps position (int) to bit index (int)

    # quantum tape uses little endian basis states: |q_n ... q_0>
    # 0 amplitudes are implicit

    valid_chars = set("}{*~#?;:><+-.,[]")
    
    for c, char in enumerate(input):
        if char not in valid_chars:
            raise ValueError(f"Syntax Error: Invalid Brainfuq command '{char}' at position {c}")

    del valid_chars

    X_GATE = np.array([[0, 1], [1, 0]])
    H_GATE = np.array([[1, 1], [1, -1]]) / np.sqrt(2)
    T_GATE = np.array([[1, 0], [0, np.exp(1j * np.pi / 4)]])

    quantum_ptr = 0
    next_idx = 1

    classical_ptr = 0

    # index within brainfuq input string
    c = 0

    while(c < len(input)):

        match input[c]:
            # quantum instructions
            case '}': 
                quantum_ptr += 1
                if quantum_ptr not in qubit_map:
                    qubit_map[quantum_ptr] = next_idx
                    next_idx += 1
            case '{':
                quantum_ptr -= 1
                if quantum_ptr not in qubit_map:
                        qubit_map[quantum_ptr] = next_idx
                        next_idx += 1
            case '*':
                apply_single_qubit_gate(quantum_tape, qubit_map, quantum_ptr, X_GATE)
            case '~':
                apply_single_qubit_gate(quantum_tape, qubit_map, quantum_ptr, H_GATE)
            case '#': pass
            case '?': pass
            case ';':
                apply_single_qubit_gate(quantum_tape, qubit_map, quantum_ptr, T_GATE)
            case ':': pass
            # classical instructions
            case '>': 
                classical_ptr += 1
            case '<': 
                classical_ptr -= 1
            case '+': pass
            case '-': pass
            case '.': pass
            case ',': pass
            case '[': pass
            case ']': pass
        
        c += 1

    return classical_tape, quantum_tape, qubit_map
        

def apply_single_qubit_gate(quantum_tape: dict[int, complex], qubit_map: dict[int, int], quantum_ptr: int, gate_matrix: np.ndarray) -> dict[int, complex]:
    """
    Applies any arbitrary 2x2 quantum gate matrix to the target qubit.
    Updates the sparse quantum_tape in-place.
    """
    target_qubit = qubit_map[quantum_ptr]
    bit_mask = 1 << target_qubit
    
    m00, m01 = gate_matrix[0, 0], gate_matrix[0, 1]
    m10, m11 = gate_matrix[1, 0], gate_matrix[1, 1]
    
    # track processed states to avoid double-processing pairs
    existing_states = list(quantum_tape.keys())
    processed = set()
    
    for state_int in existing_states:
        if state_int in processed:
            continue
            
        # state_0 = x0y
        # state_1 = x1y
        if (state_int & bit_mask) == 0:
            state_0 = state_int
            state_1 = state_int ^ bit_mask
        else:
            state_1 = state_int
            state_0 = state_int ^ bit_mask
        
        amp_0 = quantum_tape.get(state_0, 0.0)
        amp_1 = quantum_tape.get(state_1, 0.0)
        
        new_amp_0 = m00 * amp_0 + m01 * amp_1
        new_amp_1 = m10 * amp_0 + m11 * amp_1
        
        if abs(new_amp_0) > 1e-9:
            quantum_tape[state_0] = new_amp_0
        elif state_0 in quantum_tape:
            del quantum_tape[state_0]
            
        if abs(new_amp_1) > 1e-9:
            quantum_tape[state_1] = new_amp_1
        elif state_1 in quantum_tape:
            del quantum_tape[state_1]
            
        processed.add(state_0)
        processed.add(state_1)
        
    return quantum_tape


def get_quantum_state(quantum_tape, qubit_map):

    output_terms = []

    for state_int, amplitude in quantum_tape.items():
        
        spatial_bitstring = get_spatial_bitstring(state_int, qubit_map)

        if isinstance(amplitude, complex):
            # Format complex numbers as (a + bj) if they have a significant complex component
            amp_str = f"{amplitude.real:.3f}" if abs(amplitude.imag) < 1e-9 else f"({amplitude.real:.3f} + {amplitude.imag:.3f}j)"
        else:
            amp_str = f"{amplitude:.3f}"

        output_terms.append(f"{amp_str} |{spatial_bitstring}⟩")
    
    return " + ".join(output_terms)


def get_spatial_bitstring(state_int, qubit_map):
    # Sort the tape positions from lowest to highest (e.g., -1, 0, 1)
    sorted_tape_positions = sorted(qubit_map.keys())
    
    bit_chars = []
    for pos in sorted_tape_positions:
        bit_index = qubit_map[pos]
        bit_value = (state_int >> bit_index) & 1
        bit_chars.append(str(bit_value))
        
    return "".join(bit_chars)
