# tests/test_cli.py
from typer.testing import CliRunner
from unittest.mock import patch
import pytest
from main import app

runner = CliRunner()

# -------------------- Testa comando commits --------------------
@patch("main.show_commits_info")
def test_commits_command(mock_show_commits):
    repo_url = "https://github.com/user/repo"
    
    result = runner.invoke(app, ["commits", repo_url])
    
    # Verifica saída no console
    assert f"Analisando commits do repositório: {repo_url}" in result.output
    # Verifica que a função interna foi chamada
    mock_show_commits.assert_called_once_with(repo_url)
    assert result.exit_code == 0

# -------------------- Testa comando loc --------------------
@patch("main.check_function_exceed_limit_size")
def test_loc_command(mock_check_loc):
    repo_url = "https://github.com/user/repo"
    commit_hash = "abc123"
    
    result = runner.invoke(app, ["loc", repo_url, commit_hash])
    
    assert f"Analisando LOC do repositório: {repo_url}" in result.output
    mock_check_loc.assert_called_once_with(repo_url, commit_hash)
    assert result.exit_code == 0

# -------------------- Testa comando params --------------------
@patch("main.check_functions_exceed_param_limit")
def test_params_command_default(mock_check_params):
    repo_url = "https://github.com/user/repo"
    commit_hash = "abc123"
    
    # usa o valor padrao de param_limit=5
    result = runner.invoke(app, ["params", repo_url, commit_hash])
    
    assert f"Analisando quantidade de parâmetros do repositório: {repo_url}" in result.output
    mock_check_params.assert_called_once_with(repo_url, commit_hash, 5)
    assert result.exit_code == 0

@patch("main.check_functions_exceed_param_limit")
def test_params_command_custom_limit(mock_check_params):
    repo_url = "https://github.com/user/repo"
    commit_hash = "abc123"
    param_limit = 10
    
    result = runner.invoke(app, ["params", repo_url, commit_hash, str(param_limit)])
    
    mock_check_params.assert_called_once_with(repo_url, commit_hash, param_limit)
    assert result.exit_code == 0

# -------------------- Testa comando generic --------------------
@patch("main.show_repository_generic_info")
def test_generic_command(mock_show_generic):
    repo_url = "https://github.com/user/repo"
    
    result = runner.invoke(app, ["generic", repo_url])
    
    assert f"Analisando informações do repositório: {repo_url}" in result.output
    mock_show_generic.assert_called_once_with(repo_url)
    assert result.exit_code == 0
