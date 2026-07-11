from .brainfuq_quantum_interpreter import BrainfuqQuantumInterpreter
from typing import override, Literal
import numpy as np

class BrainfuqSimulator(BrainfuqQuantumInterpreter[tuple[dict[int, complex], dict[int, int]]]):
    """
    Simulate Brainfuq
    """

    X_GATE = np.array([[0, 1], [1, 0]])
    H_GATE = np.array([[1, 1], [1, -1]]) / np.sqrt(2)
    T_GATE = np.array([[1, 0], [0, np.exp(1j * np.pi / 4)]])

    def __init__(self, verbose=True):
        super().__init__(verbose)

    @override
    def _reset_simulator(self):
        self.__quantum_tape: dict[int, complex] = {0: 1.0}
        """
        maps state to amplitude.
        quantum tape uses little endian basis states: |q_n> ... q_0>.
        0 amplitudes are implicit.
        """

        self.__last_measured: Literal[0, 1] = 0
        """
        result of the last measurement
        """

    @override
    def _apply_x(self):
        self.__apply_gate(self.X_GATE)

    @override
    def _apply_h(self):
        self.__apply_gate(self.H_GATE)

    @override
    def _apply_t(self):
        self.__apply_gate(self.T_GATE)

    def __apply_gate(self, gate_matrix: np.ndarray) -> None:
        """
        Applies any arbitrary 2x2 quantum gate matrix to the target qubit.
        If the control_ptr is not None the corresponding qubit controls the operation.
        The sparse quantum_tape gets updated in-place.
        """
            
        if self._control_qubit_ptr is not None and self._control_qubit_ptr == self._quantum_ptr:
            raise ValueError("Control qubit and target qubit cannot be the same.")        

        if self._measurement_control_active and self.__last_measured == 0:
            return

        if self._control_qubit_ptr is not None:
            control_qubit = self._qubit_map[self._control_qubit_ptr]
            control_mask = 1 << control_qubit

        target_qubit = self._qubit_map[self._quantum_ptr]
        target_mask = 1 << target_qubit

        m00, m01 = gate_matrix[0, 0], gate_matrix[0, 1]
        m10, m11 = gate_matrix[1, 0], gate_matrix[1, 1]

        # track processed states to avoid double-processing pairs
        existing_states = list(self.__quantum_tape.keys())
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

            if self._control_qubit_ptr is not None and (state_int & control_mask) == 0:
                processed.add(state_0)
                processed.add(state_1)
                continue

            amp_0 = self.__quantum_tape.get(state_0, 0.0)
            amp_1 = self.__quantum_tape.get(state_1, 0.0)

            new_amp_0 = m00 * amp_0 + m01 * amp_1
            new_amp_1 = m10 * amp_0 + m11 * amp_1

            if abs(new_amp_0) > 1e-9:
                self.__quantum_tape[state_0] = new_amp_0
            elif state_0 in self.__quantum_tape:
                del self.__quantum_tape[state_0]

            if abs(new_amp_1) > 1e-9:
                self.__quantum_tape[state_1] = new_amp_1
            elif state_1 in self.__quantum_tape:
                del self.__quantum_tape[state_1]

            processed.add(state_0)
            processed.add(state_1)

    @override
    def _measure(self):
        target_qubit = self._qubit_map[self._quantum_ptr]
        bit_mask = 1 << target_qubit

        prob_0 = 0.0
        for state_int, amplitude in self.__quantum_tape.items():

            state_prob = abs(amplitude) ** 2

            if (state_int & bit_mask) == 0:
                prob_0 += state_prob

        prob_0 = max(0.0, min(1.0, prob_0))
        prob_1 = 1.0 - prob_0

        self.__last_measured = np.random.choice([0, 1], p=[prob_0, prob_1])

        chosen_prob = prob_0 if self.__last_measured == 0 else prob_1

        normalization_factor = 1.0 / np.sqrt(chosen_prob)

        existing_states = list(self.__quantum_tape.keys())

        for state_int in existing_states:

            bit_value = 1 if (state_int & bit_mask) != 0 else 0

            if bit_value != self.__last_measured:
                # delete states where the target qubit does not match the measured value
                del self.__quantum_tape[state_int]
            else:
                # normalization
                self.__quantum_tape[state_int] *= normalization_factor

        if self._verbose:
            print(self.__last_measured)

    @override
    def return_state(self):
        return self.__quantum_tape, self._qubit_map

    def __str__(self):
        output_terms = []

        for state_int, amplitude in self.__quantum_tape.items():

            spatial_bitstring = self.__get_spatial_bitstring(state_int, self._qubit_map)

            if isinstance(amplitude, complex):
                # Format complex numbers as (a + bj) if they have a significant complex component
                amp_str = f"{amplitude.real:.3f}" if abs(amplitude.imag) < 1e-9 else f"({amplitude.real:.3f} + {amplitude.imag:.3f}j)"
            else:
                amp_str = f"{amplitude:.3f}"

            output_terms.append(f"{amp_str} |{spatial_bitstring}⟩")
        
        return " + ".join(output_terms)
    

    def __get_spatial_bitstring(self, state_int, qubit_map):
        """
        Sort the tape positions from lowest to highest (e.g., -1, 0, 1)
        """
        sorted_tape_positions = sorted(qubit_map.keys())

        bit_chars = []
        for pos in sorted_tape_positions:
            bit_index = qubit_map[pos]
            bit_value = (state_int >> bit_index) & 1
            bit_chars.append(str(bit_value))

        return "".join(bit_chars)

