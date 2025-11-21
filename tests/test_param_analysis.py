import ast
import pytest
from unittest.mock import MagicMock, patch
from src.minero.param_analysis import check_functions_num_params, check_functions_exceed_param_limit


def test_no_functions():
    source = """
x = 10
y = 20
"""
    result = check_functions_num_params(source, "file.py")
    assert result == []


def test_function_with_few_params():
    source = """
def foo(a, b):
    return a + b
"""
    result = check_functions_num_params(source, "file.py")

    assert result == []


def test_function_with_many_params():
    source = """
def bar(a, b, c, d, e, f):
    pass
"""
    result = check_functions_num_params(source, "file.py")
    assert len(result) == 1
    assert result[0]["function_name"] == "bar"
    assert result[0]["param_count"] == 6


def test_function_ignores_varargs():
    source = """
def baz(a, b, *args, **kwargs):
    pass
"""
    result = check_functions_num_params(source, "file.py")
    #conta apenas args normais
    assert result == []


def test_async_function():
    source = """
async def coro(a, b, c, d, e, f):
    return a + b
"""
    result = check_functions_num_params(source, "file.py")
    assert len(result) == 1
    assert result[0]["function_name"] == "coro"
    assert result[0]["param_count"] == 6


#  TESTES PARA check_functions_exceed_param_limit

class DummyFile:
    def __init__(self, filename, source_code):
        self.filename = filename
        self.source_code = source_code


class DummyCommit:
    def __init__(self, hash_value, files):
        self.hash = hash_value
        self.modified_files = files


def test_check_functions_exceed_param_limit_output(capsys):
    """
    Testa se a função imprime corretamente quando há funções com parâmetros demais.
    """
    dummy_commit = DummyCommit(
        "abc123",
        [
            DummyFile(
                "test_file.py",
                "def f(a, b, c, d, e, f): pass"
            )
        ]
    )

    mock_repo = MagicMock()
    mock_repo.traverse_commits.return_value = [dummy_commit]

    with patch("src.minero.param_analysis.Repository", return_value=mock_repo):
        check_functions_exceed_param_limit("repo", "abc123")

    captured = capsys.readouterr()

    #varios asserts, mas apenas para conferir os output. Todos tem relacao apenas com o comportamento testado
    assert "test_file.py" in captured.out
    assert "f" in captured.out
    assert "mais de 5 parâmetros" in captured.out
    assert "tem 6 parâmetros" in captured.out


def test_skip_non_python_files(capsys):
    dummy_commit = DummyCommit(
        "abc123",
        [
            DummyFile("image.png", "binarydata"),
            DummyFile("test.py", "def a(x, y): pass"),
        ]
    )

    mock_repo = MagicMock()
    mock_repo.traverse_commits.return_value = [dummy_commit]

    with patch("src.minero.param_analysis.Repository", return_value=mock_repo):
        check_functions_exceed_param_limit("repo", "abc123")

    captured = capsys.readouterr()

    assert "image.png" not in captured.out
    assert "test.py" in captured.out
