import pytest
from unittest.mock import MagicMock, patch
from src.commits_info import show_repository_generic_info, show_commits_info

# mock de objetos do PyDriller
class FakeCommit:
    def __init__(self, author, files, branches):
        self.hash = "abc123def456"
        self.msg = "Mensagem de teste"
        self.author = MagicMock()
        self.author.name = author
        self.modified_files = [MagicMock(filename=f) for f in files]
        self.branches = branches

@patch("src.commits_info.console.print")
@patch("src.commits_info.Repository")
def test_show_repository_generic_info(mock_repo, mock_print):
    fake_commits = [
        FakeCommit("Caleb", ["a.py", "b.py"], {"main"}),
        FakeCommit("Jhonatan", ["c.py"], {"main"}),
        FakeCommit("Caleb", ["d.py"], {"dev"}),
    ]
    mock_repo.return_value.traverse_commits.return_value = fake_commits

    show_repository_generic_info("fake_repo_url")

    mock_print.assert_any_call("[bold green]Total de Commits:[/bold green] 3")
    mock_print.assert_any_call("[bold green]Total de Autores:[/bold green] 2")
    mock_print.assert_any_call("[bold green]Total de Branches:[/bold green] 2")

    found_author_table = any("→ Número de commits por autor" in str(call.args[0]) for call in mock_print.call_args_list)
    assert found_author_table


@patch("src.commits_info.console.print")
@patch("src.commits_info.Repository")
def test_show_commits_info(mock_repo, mock_print):
    fake_commits = [
        FakeCommit("Caleb", ["main.py", "utils.py"], {"main"}),
    ]
    mock_repo.return_value.traverse_commits.return_value = fake_commits

    show_commits_info("fake_repo_url")

    mock_print.assert_any_call(f"[bold green]Commit:[/bold green] {fake_commits[0].hash[:10]}")
    mock_print.assert_any_call(f"[bold]Autor:[/bold] Caleb")
