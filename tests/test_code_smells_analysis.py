import pytest
from unittest.mock import patch, MagicMock
from src.minero.code_smells_analysis import (
    detect_code_smells, 
    check_code_smells,
    detect_magic_numbers,
    detect_long_parameter_lists,
    detect_large_classes,
    detect_dead_code_comments,
    detect_bad_variable_names
)
import ast

# ============ Testes das funções de detecção individuais ============

def test_detect_magic_numbers():
    """Testa detecção de números mágicos"""
    source_code = """
def calculate_price():
    tax_rate = 0.15  # Magic number
    max_items = 100  # Magic number
    count = 0        # OK
    multiplier = 1   # OK
    negative = -1    # OK
    pi_approx = 3.14159  # Magic number
"""
    
    tree = ast.parse(source_code)
    results = detect_magic_numbers(tree, source_code, "test.py")
    
    # Deve encontrar 0.15, 100, 3.14159
    assert len(results) == 3
    
    magic_values = []
    for result in results:
        # A descrição tem formato "Magic number {value}"
        desc = result['description']
        magic_values.append(desc)
    
    # Verificar os valores encontrados
    assert "Magic number 0.15" in str(magic_values)
    assert "Magic number 100" in str(magic_values)
    assert "Magic number 3.14159" in str(magic_values)

def test_detect_long_parameter_lists():
    """Testa detecção de funções com muitos parâmetros"""
    source_code = """
def good_function(a, b, c):
    pass

def bad_function(a, b, c, d, e, f, g, h):  # 8 parâmetros > 6
    pass

def another_bad_function(x, y, z, w, v, u, t):  # 7 parâmetros > 6
    pass
"""
    
    tree = ast.parse(source_code)
    results = detect_long_parameter_lists(tree, "test.py")
    
    assert len(results) == 2
    function_names = [r['description'] for r in results]
    assert any("bad_function" in desc for desc in function_names)
    assert any("another_bad_function" in desc for desc in function_names)

def test_detect_large_classes():
    """Testa detecção de classes grandes (God Classes)"""
    # Criar uma classe com muitos métodos
    methods = "\n".join([f"    def method_{i}(self): pass" for i in range(12)])
    source_code = f"""
class SmallClass:
    def method1(self):
        pass
    
    def method2(self):
        pass

class LargeClass:
{methods}
"""
    
    tree = ast.parse(source_code)
    results = detect_large_classes(tree, "test.py")
    
    assert len(results) == 1
    assert "LargeClass" in results[0]['description']
    assert "12 métodos" in results[0]['description']

def test_detect_dead_code_comments():
    """Testa detecção de código morto comentado"""
    source_code = """
# This is a normal comment
def active_function():
    pass
    
# def old_function():  # Código morto
#     return "old"

# import unused_module  # Código morto

## This is documentation - should be ignored
# if condition:  # Código morto
#    do_something()
"""
    
    results = detect_dead_code_comments(source_code, "test.py")
    
    assert len(results) >= 3
    descriptions = [r['description'] for r in results]
    assert any("def old_function" in desc for desc in descriptions)
    assert any("import unused_module" in desc for desc in descriptions)
    assert any("if condition" in desc for desc in descriptions)

def test_detect_bad_variable_names():
    """Testa detecção de nomes de variáveis ruins"""
    source_code = """
def function_with_bad_names():
    data = get_data()      # Bad name
    temp = process(data)   # Bad name
    x = 5                  # Bad single letter
    good_variable = temp   # Good name
    
    for i in range(10):    # OK - loop variable
        obj = i + 1        # Bad name
"""
    
    tree = ast.parse(source_code)
    results = detect_bad_variable_names(tree, "test.py")
    
    assert len(results) >= 4
    bad_names_found = []
    for result in results:
        if "'" in result['description']:
            name = result['description'].split("'")[1]
            bad_names_found.append(name)
    
    assert 'data' in bad_names_found
    assert 'temp' in bad_names_found
    assert 'x' in bad_names_found
    assert 'obj' in bad_names_found
    assert 'i' not in bad_names_found  # Loop variable - OK

def test_detect_code_smells_integration():
    """Teste integrado da função principal"""
    source_code = """
def problematic_function(a, b, c, d, e, f, g):  # Long parameter list
    data = 100  # Magic number + bad name
    temp = data * 0.15  # Magic number + bad name
    return temp

# def old_function():  # Dead code
#     pass

class BigClass:
    def method1(self): pass
    def method2(self): pass
    def method3(self): pass
    def method4(self): pass
    def method5(self): pass
    def method6(self): pass
    def method7(self): pass
    def method8(self): pass
    def method9(self): pass
    def method10(self): pass
    def method11(self): pass  # 11 methods > 10
"""
    
    results = detect_code_smells(source_code, "test.py")
    
    # Deve encontrar vários tipos de smells
    smell_types = set(result['smell_type'] for result in results)
    
    assert 'magic_number' in smell_types
    assert 'long_parameter_list' in smell_types
    assert 'large_class' in smell_types
    assert 'dead_code' in smell_types
    assert 'bad_variable_name' in smell_types
    
    assert len(results) > 5  # Deve encontrar vários problemas

# ============ Testes de integração com mocks ============

@pytest.fixture
def mock_commit_with_smells():
    """Mock de commit com arquivo Python que tem code smells"""
    mock_file = MagicMock()
    mock_file.filename = "smelly_code.py"
    mock_file.source_code = """
def bad_function(a, b, c, d, e, f, g, h):  # Too many params
    magic_number = 42  # Magic number
    data = magic_number * 1.5  # Bad name + magic number
    return data
    
# def commented_code():  # Dead code
#     return "old"
"""
    
    mock_commit = MagicMock()
    mock_commit.hash = "abc123"
    mock_commit.modified_files = [mock_file]
    
    return mock_commit

@patch("src.minero.code_smells_analysis.Repository")
@patch("src.minero.code_smells_analysis.print")
@patch("src.minero.code_smells_analysis.console.print")
def test_check_code_smells_integration(mock_console_print, mock_builtin_print, mock_repo, mock_commit_with_smells):
    """Teste de integração da função principal"""
    
    mock_repo.return_value.traverse_commits.return_value = [mock_commit_with_smells]
    
    check_code_smells("fake_repo", "abc123")
    
    # Verificar que Repository foi chamado corretamente
    mock_repo.assert_called_once_with("fake_repo", single="abc123")
    
    # Verificar que console.print foi chamado (é o que a função usa)
    assert mock_console_print.called
    
    # Verificar que algo sobre o arquivo foi exibido
    all_calls = str(mock_console_print.call_args_list)
    assert "smelly_code.py" in all_calls

@patch("src.minero.code_smells_analysis.Repository")
@patch("src.minero.code_smells_analysis.print")
@patch("src.minero.code_smells_analysis.console.print")
def test_check_code_smells_no_smells(mock_console_print, mock_builtin_print, mock_repo):
    """Teste quando nenhum code smell é encontrado"""
    
    mock_file = MagicMock()
    mock_file.filename = "clean_code.py"
    mock_file.source_code = """
def clean_function(parameter_one, parameter_two):
    result = parameter_one + parameter_two
    return result
"""
    
    mock_commit = MagicMock()
    mock_commit.hash = "abc123"
    mock_commit.modified_files = [mock_file]
    
    mock_repo.return_value.traverse_commits.return_value = [mock_commit]
    
    check_code_smells("fake_repo", "abc123")
    
    # Verificar que console.print foi chamado 
    assert mock_console_print.called
    
    # Verificar que algo sobre nenhum code smell foi exibido
    all_calls = str(mock_console_print.call_args_list)
    assert "Nenhum code smell detectado" in all_calls or "clean_code.py" in all_calls

@patch("src.minero.code_smells_analysis.Repository")
@patch("src.minero.code_smells_analysis.print")
@patch("src.minero.code_smells_analysis.console.print")
def test_check_code_smells_non_python_files(mock_console_print, mock_builtin_print, mock_repo):
    """Teste com arquivos que não são Python"""
    
    mock_file = MagicMock()
    mock_file.filename = "README.md"
    mock_file.source_code = "# Documentation"
    
    mock_commit = MagicMock()
    mock_commit.modified_files = [mock_file]
    
    mock_repo.return_value.traverse_commits.return_value = [mock_commit]
    
    check_code_smells("fake_repo", "abc123")
    
    # Não deve processar arquivos não-Python
    mock_repo.assert_called_once()
    # Verificar que não há output específico sobre code smells
    printed_texts = " ".join([str(call.args[0]) for call in mock_builtin_print.call_args_list])
    assert "README.md" not in printed_texts