import numpy as np

# return
def interpret_brainfuq(program: str) -> tuple[dict, dict, dict]:
    
    classical_tape: dict[int, np.uint8] = {0: np.uint8(0)}       # maps position (int) to cell value (int)
    quantum_tape: dict[int, complex] = {0: 1.0} # maps state (int) to amplitude (complex)
    qubit_map: dict[int, int] = {0: 0}         # maps position (int) to bit index (int)

    # quantum tape uses little endian basis states: |q_n ... q_0>
    # 0 amplitudes are implicit

    valid_chars = set("}{*~#?;:><+-.,[]")
    
    for c, char in enumerate(program):
        if char not in valid_chars:
            raise ValueError(f"Syntax Error: Invalid Brainfuq command '{char}' at position {c}")

    del valid_chars

    X_GATE = np.array([[0, 1], [1, 0]])
    H_GATE = np.array([[1, 1], [1, -1]]) / np.sqrt(2)
    T_GATE = np.array([[1, 0], [0, np.exp(1j * np.pi / 4)]])

    quantum_ptr = 0
    next_idx = 1

    # quantum tape pointer to the qubit controlling the next gate - set by '#'
    control_qubit_ptr = None

    # '?': apply next gate only if last measurement yielded 1
    measurement_control_active = False

    last_measured = 0

    classical_ptr = 0

    # index within brainfuq program string
    c = 0

    while(c < len(program)):

        match program[c]:
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

                if not (measurement_control_active and last_measured == 0):
                    apply_gate(quantum_tape, qubit_map, control_qubit_ptr, quantum_ptr, X_GATE)
                
                control_qubit_ptr = None
                measurement_control_active = False

            case '~':
                
                if not (measurement_control_active and last_measured == 0):
                    apply_gate(quantum_tape, qubit_map, control_qubit_ptr, quantum_ptr, H_GATE)
                
                control_qubit_ptr = None
                measurement_control_active = False
            case '#':
                
                control_qubit_ptr = quantum_ptr

            case '?':
                
                measurement_control_active = True

            case ';':

                if not (measurement_control_active and last_measured == 0):
                    apply_gate(quantum_tape, qubit_map, control_qubit_ptr, quantum_ptr, T_GATE)
                
                control_qubit_ptr = None
                measurement_control_active = False

            case ':':

                last_measured = measure_qubit(quantum_tape, qubit_map, quantum_ptr, True)
            
            # classical instructions
            case '>': 
                classical_ptr += 1
                if classical_ptr not in classical_tape:
                    classical_tape[classical_ptr] = np.uint8(0)

            case '<': 
                classical_ptr -= 1
                if classical_ptr not in classical_tape:
                    classical_tape[classical_ptr] = np.uint8(0)

            case '+':
                val = int(classical_tape[classical_ptr])
                classical_tape[classical_ptr] = np.uint8((val + 1) % 256) # avoid implicit upcast

            case '-':
                val = int(classical_tape[classical_ptr])
                classical_tape[classical_ptr] = np.uint8((val - 1) % 256)

            case '.':
                print(classical_tape[classical_ptr])

            case ',':
                classical_tape[classical_ptr] = np.uint8(input("$ "))

            case '[':
                if classical_tape[classical_ptr] == 0:
                    c = classical_cond_jmp(program, c, True)

            case ']':
                if classical_tape[classical_ptr] != 0:
                    c = classical_cond_jmp(program, c, False)

        c += 1

    return classical_tape, quantum_tape, qubit_map
        

def apply_gate(quantum_tape: dict[int, complex], qubit_map: dict[int, int], control_ptr: int, target_ptr: int, gate_matrix: np.ndarray):
    """
    Applies any arbitrary 2x2 quantum gate matrix to the target qubit.
    If the control_ptr is not None the corresponding qubit controls the operation.
    The sparse quantum_tape gets updated in-place.
    """

    if control_ptr is not None and control_ptr == target_ptr:
        raise ValueError("Control qubit and target qubit cannot be the same.")

    if control_ptr is not None:
        control_qubit = qubit_map[control_ptr]
        control_mask = 1 << control_qubit

    target_qubit = qubit_map[target_ptr]
    target_mask = 1 << target_qubit
    
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
        if (state_int & target_mask) == 0:
            state_0 = state_int
            state_1 = state_int ^ target_mask
        else:
            state_1 = state_int
            state_0 = state_int ^ target_mask
        
        if control_ptr is not None and (state_int & control_mask) == 0:
            processed.add(state_0)
            processed.add(state_1)
            continue

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


def measure_qubit(quantum_tape: dict[int, complex], qubit_map: dict[int, int], quantum_ptr: int, verbose: bool = False) -> int:
    """
    Measures the target qubit.
    The quantum_tape is updated in-place.
    The measured value is returned.
    """
    target_qubit = qubit_map[quantum_ptr]
    bit_mask = 1 << target_qubit
    
    prob_0 = 0.0
    for state_int, amplitude in quantum_tape.items():
        
        state_prob = abs(amplitude) ** 2
        
        if (state_int & bit_mask) == 0:
            prob_0 += state_prob
            
    prob_0 = max(0.0, min(1.0, prob_0))
    prob_1 = 1.0 - prob_0

    measured_value = np.random.choice([0, 1], p=[prob_0, prob_1])
    
    chosen_prob = prob_0 if measured_value == 0 else prob_1
    
    normalization_factor = 1.0 / np.sqrt(chosen_prob)

    existing_states = list(quantum_tape.keys())

    for state_int in existing_states:
        
        bit_value = 1 if (state_int & bit_mask) != 0 else 0
        
        if bit_value != measured_value:
            # delete states where the target qubit does not match the measured value
            del quantum_tape[state_int]
        else:
            # normalization
            quantum_tape[state_int] *= normalization_factor

    if verbose:
        print(measured_value)

    return measured_value


def get_quantum_state(quantum_tape, qubit_map):

    output_terms = []

    for state_int, amplitude in quantum_tape.items():
        
        real_part = amplitude.real
        imag_part = amplitude.imag

        has_real = abs(real_part) >= 1e-9
        has_imag = abs(imag_part) >= 1e-9

        if not has_real and not has_imag:
            continue

        spatial_bitstring = get_spatial_bitstring(state_int, qubit_map)

        is_negative = False

        if has_real and has_imag:
            sign_char = "+" if imag_part > 0 else "-"
            amp_str = f"({real_part:.3f} {sign_char} {abs(imag_part):.3f}j)"

        elif has_imag:
            is_negative = imag_part < 0
            abs_imag = abs(imag_part)
            # drop "1.000" prefix for clean 1j / -1j states
            amp_str = "j" if abs(abs_imag - 1.0) < 1e-9 else f"{abs_imag:.3f}j"

        else:
            is_negative = real_part < 0
            abs_real = abs(real_part)
            # drop prefix for clean 1 or -1 basis state
            amp_str = "" if abs(abs_real - 1.0) < 1e-9 else f"{abs_real:.3f}"

        term_str = f"{amp_str} |{spatial_bitstring}⟩"
        
        if is_negative:
            output_terms.append(("- ", term_str))
        else:
            output_terms.append(("+ ", term_str))
    
    if not output_terms:
        return "0"

    final_str = ""
    for i, (sign, term) in enumerate(output_terms):
        if i == 0:
            final_str += f"-{term}" if sign == "- " else term
        else:
            final_str += f" {sign}{term}"

    return final_str


def get_spatial_bitstring(state_int, qubit_map):
    # Sort the tape positions from lowest to highest (e.g., -1, 0, 1)
    sorted_tape_positions = sorted(qubit_map.keys())
    
    bit_chars = []
    for pos in sorted_tape_positions:
        bit_index = qubit_map[pos]
        bit_value = (state_int >> bit_index) & 1
        bit_chars.append(str(bit_value))
        
    return "".join(bit_chars)


def classical_cond_jmp(
    program: str,
    c: int,
    is_to_right: bool
) -> int:
    """
    jump to matching `[` or `]` instruction on classical tape

    :param classical_tape: The classical tape. Is modified in-place!
    :param c: The program counter
    :param is_to_right: Walk to the right? E.g. `True` if `[` is encountered
    :return: The new classical pointer
    """
    sign = 1 if is_to_right else -1
    depth = 1
    while depth > 0:
        c += sign
        if c < 0 or c >= len(program):
            raise SyntaxError("Unmatched brackets '[' or ']' detected.")
        
        if program[c] == '[':
            depth += sign
        elif program[c] == ']':
            depth -= sign

    return c
