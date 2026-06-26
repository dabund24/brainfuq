from abc import ABC, abstractmethod
from typing import final

class BrainfuqQuantumInterpreter[T](ABC):
    SUPPORTED_OPS = set('}{*~;#?:')

    def __init__(self, verbose: bool):
        self._verbose = verbose
        self.reset()

    @final
    def reset(self) -> None:
        """
        Public reset API. Resets both base interpreter states 
        and implementation-specific simulator states.
        """
        self._reset_base()
        self._reset_simulator()

    @final
    def _reset_base(self) -> None:
        """
        Resets the core base-class state variables.
        """
        self._quantum_ptr: int = 0
        self._qubit_map: dict[int, int] = {0: 0}
        self._control_qubit_ptr: int | None = None
        self._measurement_control_active = False
        self._next_idx = 1

    @abstractmethod
    def _reset_simulator(self) -> None:
        """
        Subclasses must implement this to reset their own state variables 
        (e.g., state vectors, density matrices, measurement histories).
        """
        pass


    @final
    def __move_right(self) -> None:
        self._quantum_ptr += 1
        if self._quantum_ptr not in self._qubit_map:
            self._qubit_map[self._quantum_ptr] = self._next_idx
            self._next_idx += 1

    @final
    def __move_left(self) -> None:
        self._quantum_ptr -= 1
        if self._quantum_ptr not in self._qubit_map:
            self._qubit_map[self._quantum_ptr] = self._next_idx
            self._next_idx += 1

    @final
    def __x(self) -> None:
        """
        `*` operation. Apply X Gate
        """
        self._apply_x()
        self._control_qubit_ptr = None
        self._measurement_control_active = False

    @abstractmethod
    def _apply_x():
        pass


    @final
    def __h(self) -> None:
        """
        `~` operation. Apply H Gate
        """
        self._apply_h()
        self._control_qubit_ptr = None
        self._measurement_control_active = False

    @abstractmethod
    def _apply_h() -> None:
        pass

    
    @final
    def __t(self) -> None:
        """
        `;` operation. Apply T Gate
        """
        self._apply_t()
        self._control_qubit_ptr = None
        self._measurement_control_active = False

    @abstractmethod
    def _apply_t() -> None:
        pass


    @final
    def __set_control_qubit(self) -> None:
        """
        `#` operation. Set control gate for next operation
        """
        self._control_qubit_ptr = self._quantum_ptr

    @final
    def __set_control_measurement(self) -> None:
        """
        `?` operation. Apply next gate if last measurement was 1
        """
        self._measurement_control_active = True

    
    @abstractmethod
    def _measure(self) -> None:
        """
        `:` operation. Measure the current qubit
        """
        pass

    @final
    def apply_operation(self, op: str):
        """
        apply a quantum brainfuq operation

        :param op: the operation to apply. Must be a single character from SUPPORTED_OPS
        """
        match op:
            case '}':
                self.__move_right()
            case '{':
                self.__move_left()
            case '*':
                self.__x()
            case '~':
                self.__h()
            case ';':
                self.__t()
            case '#':
                self.__set_control_qubit()
            case '?':
                self.__set_control_measurement()
            case ':':
                self._measure()


    @final
    def _return_state(self) -> T:
        """
        return what has been computed so far
        """
        return self.return_state()

    @abstractmethod
    def return_state(self) -> T:
        pass

    @abstractmethod
    def __str__(self):
        pass
        
