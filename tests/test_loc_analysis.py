import pytest
from unittest.mock import patch, MagicMock
from src.loc_analysis import analyze_loc


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
    """Verifica se o programa lida graciosamente com exceções."""
    with pytest.raises(Exception, match="Erro ao acessar repositório"):
        analyze_loc("repo", "a"*40, "b"*40)
