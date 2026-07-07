import numpy as np

class BrainfuqClassicalInterpreter:
    SUPPORTED_OPS = set('><+-.,[]')

    def __init__(self):
        self.reset()

    def reset(self):
        self.__classical_tape: dict[int, np.uint8] = {0: np.uint8(0)}
        self.__classical_ptr = 0

    def apply_operation(self, program: str, pc: int) -> int:
        """
        apply a classical brainfuq operation

        :param program: the brainfuq program
        :param pc: the current program counter
        :return: the new program counter after applying the operation at pc
        """
        op = program[pc]

        match op:
            case '>': 
                self.__classical_ptr += 1
                if self.__classical_ptr not in self.__classical_tape:
                    self.__classical_tape[self.__classical_ptr] = np.uint8(0)

            case '<': 
                self.__classical_ptr -= 1
                if self.__classical_ptr not in self.__classical_tape:
                    self.__classical_tape[self.__classical_ptr] = np.uint8(0)

            case '+':
                val = int(self.__classical_tape[self.__classical_ptr])
                self.__classical_tape[self.__classical_ptr] = np.uint8((val + 1) % 256)

            case '-':
                val = int(self.__classical_tape[self.__classical_ptr])
                self.__classical_tape[self.__classical_ptr] = np.uint8((val - 1) % 256)

            case '.':
                print(self.__classical_tape[self.__classical_ptr])

            case ',':
                self.__classical_tape[self.__classical_ptr] = np.uint8(input("$ "))

            case '[':
                if self.__classical_tape[self.__classical_ptr] == 0:
                    return self.classical_cond_jmp(program, pc, True)

            case ']':
                if self.__classical_tape[self.__classical_ptr] != 0:
                    return self.classical_cond_jmp(program, pc, False)
                
        return pc

    def classical_cond_jmp(
        self,
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


    def return_state(self) -> dict[int, np.uint8]:
        return self.__classical_tape