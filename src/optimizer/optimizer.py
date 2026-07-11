import re

def optimize_brainfuq(bfqc: str) -> str:
    """
    Optimize the length of a Brainfuq program

    :param bfqc: The program to optimize
    :return: The optimized Brainfuq program
    """

    while True:
        optimized_bfqc = _fixpoint_optimizations(bfqc)
        if optimized_bfqc == bfqc: # fixpoint reached
            break
        bfqc = optimized_bfqc

    return bfqc

def _fixpoint_optimizations(bfqc: str) -> str:
    def _remove_repeated_pointer_moves(bfqc: str) -> str:
        bfqc = bfqc.replace("}{", "")
        return bfqc.replace("{}", "")

    bfqc = _remove_repeated_pointer_moves(bfqc)
    return bfqc
