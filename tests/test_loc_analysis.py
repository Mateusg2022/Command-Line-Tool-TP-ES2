import textwrap
import pytest
from unittest.mock import patch, MagicMock
from src.loc_analysis import analyze_loc, check_function_sizes, check_function_exceed_limit_size


@pytest.fixture
def mock_linescount():
    """Cria um mock para a classe LinesCount com dados simulados."""
    mock = MagicMock()
    mock.count_added.return_value = {
        "file1.py": 10,
        "file2.py": 20
    }
    mock.max_added.return_value = {
        "file1.py": 15,
        "file2.py": 40
    }
    mock.avg_added.return_value = {
        "file1.py": 5.0,
        "file2.py": 10.0
    }
    return mock


@patch("src.loc_analysis.console.print")
@patch("src.loc_analysis.LinesCount")
def test_analyze_loc_basic(mock_linescount_cls, mock_print, mock_linescount):
    """Verifica se a função chama LinesCount corretamente e imprime os resultados esperados."""
    mock_linescount_cls.return_value = mock_linescount

    repo_url = "https://github.com/test/repo"
    from_commit = "1111111111111111111111111111111111111111"
    to_commit = "2222222222222222222222222222222222222222"

    analyze_loc(repo_url, from_commit, to_commit)

    mock_linescount_cls.assert_called_once_with(
        path_to_repo=repo_url,
        from_commit=from_commit,
        to_commit=to_commit
    )

    mock_linescount.count_added.assert_called_once()
    mock_linescount.max_added.assert_called_once()
    mock_linescount.avg_added.assert_called_once()

    assert mock_print.call_count >= 4


@patch("src.loc_analysis.console.print")
@patch("src.loc_analysis.LinesCount")
def test_analyze_loc_with_large_commit_warning(mock_linescount_cls, mock_print):
    """Verifica se um aviso é mostrado quando um commit é muito grande."""
    mock_instance = MagicMock()
    mock_instance.count_added.return_value = {"file1.py": 10}
    mock_instance.max_added.return_value = {"file1.py": 50}  # > 2x média
    mock_instance.avg_added.return_value = {"file1.py": 10.0}
    mock_linescount_cls.return_value = mock_instance

    analyze_loc("repo", "a"*40, "b"*40)

    # reune todos os argumentos passados ao console.print
    printed_args = [call.args[0] for call in mock_print.call_args_list]

    # converte todos em string (Table, Panel etc.)
    printed_texts = " ".join(str(arg) for arg in printed_args)

    assert "[ALERTA] Commit muito grande!" in printed_texts

@patch("src.loc_analysis.console.print")
@patch("src.loc_analysis.LinesCount", side_effect=Exception("Erro ao acessar repositório"))
def test_analyze_loc_exception_handling(mock_linescount_cls, mock_print):
    """Verifica se o programa lida bem com exceções."""
    with pytest.raises(Exception, match="Erro ao acessar repositório"):
        analyze_loc("repo", "a"*40, "b"*40)
        
#================= Testes unitários da função check_function_sizes =================#

def test_function_exceeds_limit():
    """
    Verifica se uma função com 201 linhas é corretamente detectada.
    """
    
    function_body = "    pass\n" * 200
    source_code = f"def long_function():\n{function_body}"
    # o código fonte final tem 201 linhas
    
    filename = "file_com_funcao_grande.py"
    results = check_function_sizes(source_code, filename)
    
    assert len(results) == 1
    
    result = results[0]
    assert result['function_name'] == 'long_function'
    assert result['line_count'] == 201
    assert result['start_line'] == 1
    assert result['end_line'] == 201 #(linha 1 para 'def' + 200 linhas de 'pass')
    assert result['file_path'] == filename

def test_function_at_or_below_limit():
    """
    Verifica se funções com exatamente 200 linhas (limite) ou 
    199 linhas (ou seja, valor abaixo do limite) NÃO são reportadas.
    """
    
    body_200 = "    pass\n" * 199
    func_200 = f"def borderline_function():\n{body_200}"
    
    body_199 = "    pass\n" * 198
    func_199 = f"def short_function():\n{body_199}"
    
    # juntando as duas no mesmo codigo
    source_code = f"{func_200}\n\n{func_199}"
    results = check_function_sizes(source_code, "file_sem_funcao_grande.py")
    
    # nenhum resultado deve ser retornado
    assert len(results) == 0
    
def test_multiple_mixed_functions_and_async():
    """
    Verifica um arquivo com múltiplas funções (regulares e async),
    reportando apenas as que excedem 200 linhas.
    """
    
    source_code = textwrap.dedent("""
        def short_func(): # 5 linhas
            pass
            pass
            pass
            pass

        # Função longa 1 (210 linhas)
        def very_long_func():
        """) + "    pass\n" * 209 + textwrap.dedent("""

        # Função no limite (200 linhas)
        def border_func():
        """) + "    pass\n" * 199 + textwrap.dedent("""

        # Função longa 2 (Async) (201 linhas)
        async def long_async_func():
        """) + "    pass\n" * 200

    results = check_function_sizes(source_code, "mixed_file.py")
    
    # apenas as duas funções longas devem ser reportadas
    assert len(results) == 2
    
    reported_data = {r['function_name']: r['line_count'] for r in results}
    
    expected_data = {
        'very_long_func': 210,
        'long_async_func': 201
    }
    
    assert reported_data == expected_data
    
    # só garantindo que as outras não estão lá nos resultados
    assert 'short_func' not in reported_data
    assert 'border_func' not in reported_data
    
def test_invalid_syntax_handling():
    """
    Verifica se a função propaga a SyntaxError se o
    código fonte for inválido (o que é esperado do ast.parse).
    """
    invalid_code = "def invalid_function(:"
    
    with pytest.raises(SyntaxError):
        check_function_sizes(invalid_code, "invalid_code.py")

#================= Fixtures para testes de integração da função check_function_exceed_limit_size =================#

@pytest.fixture
def mock_modified_files():
    """
    Cria uma lista de mocks para 'modified_files'.
    basicmanete, essa função serve para simular um commit com um arquivo .py e um arquivo .md.
    """
    
    mock_file_py = MagicMock()
    mock_file_py.filename = "app/main.py"
    mock_file_py.source_code = "def some_python_code():\n    pass"

    mock_file_md = MagicMock()
    mock_file_md.filename = "README.md"
    mock_file_md.source_code = "# Readme"

    return [mock_file_py, mock_file_md]

@pytest.fixture
def mock_repo(mock_modified_files):
    """
    Cria um mock completo do Repository e Commit que retorna
    os modified_files da outra fixture.
    """
    
    # mock do commit
    mock_commit = MagicMock()
    mock_commit.hash = "abc12345"
    mock_commit.modified_files = mock_modified_files
    
    with patch("src.loc_analysis.Repository") as mock_repo_class:
        mock_repo_instance = MagicMock()
        mock_repo_instance.traverse_commits.return_value = [mock_commit]
        mock_repo_class.return_value = mock_repo_instance
        
        # retorna a classe mockada do Repository para podermos fazer asserções nela
        yield mock_repo_class

#================= Testes de integração da função check_function_exceed_limit_size =================#

@patch("src.loc_analysis.check_function_sizes")
@patch("src.loc_analysis.print")
@patch("src.loc_analysis.console.print")
def test_long_function_found_and_reported(mock_console_print, mock_builtin_print, mock_check_sizes, mock_repo):
    """
    Verifica se uma função longa encontrada no arquivo .py é 
    corretamente reportada no console.
    """
    
    # simula que 'check_function_sizes' encontrou uma função longa
    mock_long_result = [{
        'function_name': 'super_long_function',
        'line_count': 250,
        'start_line': 10,
        'end_line': 260,
        'file_path': 'app/main.py'
    }]
    mock_check_sizes.return_value = mock_long_result
    
    repo_url = "https://github.com/test/repo"
    commit_hash = "abc12345"

    check_function_exceed_limit_size(repo_url, commit_hash)

    # verifica se Repository foi chamado corretamente
    mock_repo.assert_called_once_with(repo_url, single=commit_hash)
    
    expected_source = mock_repo.return_value.traverse_commits.return_value[0].modified_files[0].source_code
    mock_check_sizes.assert_called_once_with(expected_source, "app/main.py")
    
    # verifica se o 'print' foi chamado com a mensagem de alerta (fica mais facil se juntar tudo em uma string)
    printed_texts = " ".join([call.args[0] for call in mock_builtin_print.call_args_list])
    
    assert "excedem 200 linhas" in printed_texts
    assert "Função 'super_long_function' tem 250 linhas" in printed_texts


@patch("src.loc_analysis.check_function_sizes")
@patch("src.loc_analysis.print")
@patch("src.loc_analysis.console.print")
def test_no_long_function_found(mock_console_print, mock_builtin_print, mock_check_sizes, mock_repo):
    """
    Verifica se a mensagem "Nenhuma função..." é mostrada quando
    check_function_sizes retorna uma lista vazia.
    """
    
    # simula que 'check_function_sizes' não encontrou nada
    mock_check_sizes.return_value = []
    
    repo_url = "https://github.com/test/repobao"
    commit_hash = "abc12345"

    check_function_exceed_limit_size(repo_url, commit_hash)

    # Verifica se check_function_sizes e o Repository foram chamados
    mock_repo.assert_called_once_with(repo_url, single=commit_hash)
    mock_check_sizes.assert_called_once()
    
    printed_texts = " ".join([call.args[0] for call in mock_builtin_print.call_args_list])
    
    assert "Nenhuma função em 'app/main.py' excede 200 linhas." in printed_texts
    assert "excedem 200 linhas" not in printed_texts # Garantia


@patch("src.loc_analysis.check_function_sizes")
@patch("src.loc_analysis.print")
@patch("src.loc_analysis.console.print")
@patch("src.loc_analysis.Repository") # mock separado, sem a fixture 'mock_repo'
def test_no_python_files_in_commit(mock_repo, mock_console_print, mock_builtin_print, mock_check_sizes):
    """
    Verifica se 'check_function_sizes' NÃO é chamada se o commit
    só contém arquivos não .py.
    """
    # mock de um arquivo
    mock_file_md = MagicMock()
    mock_file_md.filename = "README.md"
    mock_file_md.source_code = "# Readme"
    
    # mock do commit
    mock_commit = MagicMock()
    mock_commit.modified_files = [mock_file_md]
    
    #mock do Repository
    mock_repo_instance = MagicMock()
    mock_repo_instance.traverse_commits.return_value = [mock_commit]
    mock_repo.return_value = mock_repo_instance

    repo_url = "https://github.com/test/repobao"
    commit_hash = "abc12345"

    check_function_exceed_limit_size(repo_url, commit_hash)

    mock_repo.assert_called_once_with(repo_url, single=commit_hash)
    
    # A função de análise NÂO deve ter sido chamada
    mock_check_sizes.assert_not_called()
    
    printed_texts = " ".join([call.args[0] for call in mock_builtin_print.call_args_list])
    
    assert "Nenhuma função" not in printed_texts
    assert "excedem 200 linhas" not in printed_texts