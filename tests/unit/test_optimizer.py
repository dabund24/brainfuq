from optimizer.optimizer import optimize_brainfuq

def test_simple():
    bfqc = "}}{{}{}*}}{:}}"
    optimized_bfqc = optimize_brainfuq(bfqc)
    assert optimized_bfqc == "}*}:}}"

def test_qft():
    bfqc = "}}~#{;}#}{{;~}#{{}}{{;}#{}{{{}{}}{}}{;}#{;~#}}*#{{*#}}*{{}}{}}"
    optimized_bfqc = optimize_brainfuq(bfqc)
    assert optimized_bfqc == "}}~#{;}#{;~}#{{;}#{;}#{;~#}}*#{{*#}}*}"

