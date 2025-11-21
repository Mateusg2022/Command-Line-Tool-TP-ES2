import ast
import pytest
from unittest.mock import patch

from src.minero.cognitive_analysis import (
    CognitiveComplexityVisitor,
    analyze_functions_in_source,
    FunctionComplexity,
    show_cognitive_analysis,
)

#testando o visitor 

@pytest.mark.parametrize("source_code, expected_complexity, description", [
    # Caso Base
    ("def func(): pass", 0, "Função vazia deve ser 0"),
    
    # Estruturas de Controle Simples (+1)
    ("def func():\n if True: pass", 1, "If simples"),
    ("def func():\n for x in y: pass", 1, "For simples"),
    ("def func():\n while True: pass", 1, "While simples"),
    ("def func():\n with open(x): pass", 1, "With simples"),
    
    # Estruturas de Fluxo (+1)
    ("def func():\n return", 1, "Return conta como +1"),
    ("def func():\n if True:\n  return", 2, "If (+1) + Return (+1)"),
    
    # Operadores Booleanos (+1 para cada operador extra)
    ("def func():\n if a and b: pass", 2, "If (+1) + 1 'and' (+1)"),
    ("def func():\n if a and b and c: pass", 3, "If (+1) + 2 'and' (+2)"),
    ("def func():\n if a or b: pass", 2, "If (+1) + 1 'or' (+1)"),
    
    # Aninhamento (Nesting)
    # Nível 0: If (+1)
    # Nível 1: If aninhado (+1 base + 1 penalidade de nesting)
    # Total: 3
    ("""
def func():
    if a:
        if b:
            pass
    """, 3, "If aninhado (1 + (1+1))"),

    # Aninhamento Profundo
    # If (+1) -> Nesting 0
    #  For (+2) -> Nesting 1 (1 base + 1 penalidade)
    #   If (+3) -> Nesting 2 (1 base + 2 penalidade)
    # Total: 6
    ("""
def func():
    if a:
        for x in y:
            if z:
                pass
    """, 6, "Aninhamento triplo"),
    
    # Try / Except
    # Try (+1)
    # Except (+1)
    # Total: 2
    ("""
def func():
    try:
        a()
    except:
        b()
    """, 2, "Try/Except simples"),
    
    # Else (não deve adicionar complexidade em if/try, apenas o bloco interno)
    ("""
def func():
    if a:
        pass
    else:
        pass
    """, 1, "Else não soma, só o If conta"),
])

def test_cognitive_complexity_calculation(source_code, expected_complexity, description):
    """testa a lógica de cálculo do visitor para vários cenários."""
    results = analyze_functions_in_source(source_code, "test.py")
    assert len(results) == 1
    assert results[0].complexity == expected_complexity, f"Falha em: {description}"

def test_simple_if_increases_complexity():
    """testa se um simples if aumenta a complexidade cognitiva"""
    source = """
def f():
    if True:
        pass
"""
    tree = ast.parse(source)
    func = tree.body[0]

    visitor = CognitiveComplexityVisitor()
    visitor.visit(func)

    # if sem boolop, complexidade = 1 (nível 0)
    assert visitor.complexity == 1


def test_nested_if_complexity():
    """testa se ifs aninhados aumentam a complexidade cognitiva corretamente"""
    source = """
def f():
    if True:
        if True:
            pass
"""
    tree = ast.parse(source)
    func = tree.body[0]

    visitor = CognitiveComplexityVisitor()
    visitor.visit(func)

    # primeiro if: 1
    # segundo if: 1 + nesting(1) = 2
    assert visitor.complexity == 3


def test_boolop_in_if_condition():
    """testa se operadores booleanos na condição if aumentam a complexidade"""
    source = """
def f():
    if a and b and c:
        pass
"""
    tree = ast.parse(source)
    func = tree.body[0]

    visitor = CognitiveComplexityVisitor()
    visitor.visit(func)

    # if = 1
    # boolop (and x2) = 2
    assert visitor.complexity == 3


def test_flow_statements_add_complexity():
    """testa se instruções de fluxo aumentam a complexidade"""
    source = """
def f():
    if True:
        return 1
"""
    tree = ast.parse(source)
    func = tree.body[0]

    visitor = CognitiveComplexityVisitor()
    visitor.visit(func)

    # if = 1
    # return = +1
    assert visitor.complexity == 2

def test_syntax_error_handling(capsys):
    """testa se o código lida com erros de sintaxe sem quebrar."""
    code = "def func( broken code"
    results = analyze_functions_in_source(code, "test.py")
    
    # deve retornar lista vazia e imprimir erro no console
    assert results == []
    captured = capsys.readouterr()
    assert "Erro ao parsear test.py" in captured.out

def test_multiple_functions_in_file():
    """Testa se o analisador pega múltiplas funções no mesmo arquivo."""
    code = """
def a():
    if True: pass

def b():
    if True:
        if True: pass
    """
    results = analyze_functions_in_source(code, "test.py")
    assert len(results) == 2
    assert results[0].function_name == "a"
    assert results[0].complexity == 1
    assert results[1].function_name == "b"
    assert results[1].complexity == 3
    
# ==========================================================
# === TESTE analyze_functions_in_source =====================
# ==========================================================

def test_analyze_functions_returns_expected_data():
    source = """
def f():
    if True:
        pass

def g():
    for i in range(3):
        pass
"""
    results = analyze_functions_in_source(source, "arquivo.py")

    assert len(results) == 2
    assert all(isinstance(r, FunctionComplexity) for r in results)

    names = {r.function_name for r in results}
    assert names == {"f", "g"}


def test_analyze_functions_invalid_code():
    broken = "def f(:"
    results = analyze_functions_in_source(broken, "arq.py")

    assert results == []


#pequeno teste de integração
@pytest.fixture
def fake_commit():
    """Cria um commit falso com dois arquivos python."""
    class FakeModifiedFile:
        def __init__(self, filename, code):
            self.filename = filename
            self.source_code = code

    class FakeCommit:
        def __init__(self):
            self.hash = "abc123"
            self.msg = "commit fake"
            self.modified_files = [
                FakeModifiedFile("a.py", "def x():\n    pass"),
                FakeModifiedFile("b.py", "def y():\n    if True:\n        pass"),
            ]

    return FakeCommit()


@patch("src.minero.cognitive_analysis.Repository")
def test_show_cognitive_analysis_runs_without_errors(mock_repo, fake_commit, capsys):
    """Testa se show_cognitive_analysis roda sem erros com um repositório mockado."""
    
    mock_repo.return_value.traverse_commits.return_value = [fake_commit]

    # Executa a função
    show_cognitive_analysis("http://fake.repo", commit_hash="abc123")

    captured = capsys.readouterr()

    # verifica que o commit foi exibido
    assert "abc123" in captured.out
    # verifica que as duas funções foram listadas
    assert "x" in captured.out
    assert "y" in captured.out
