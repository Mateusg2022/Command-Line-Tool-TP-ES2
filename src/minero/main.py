import typer
from src.minero.commits_info import show_commits_info, show_repository_generic_info
from src.minero.loc_analysis import check_function_exceed_limit_size
from src.minero.param_analysis import check_functions_exceed_param_limit

from typing_extensions import Annotated

app = typer.Typer(help="Ferramenta CLI para mineração de repositórios de software.")

@app.command()
def commits(repo_url: str):
    """
    Mostra informações dos commits de um repositório.
    """
    typer.echo(f"Analisando commits do repositório: {repo_url}")
    show_commits_info(repo_url)

@app.command()
def loc(repo_url: str, commit_hash: str):
    """
    Emite um alerta caso um arquivo .py de um commit tenha funções que excedam 200 linhas
    """
    typer.echo(f"Analisando LOC do repositório: {repo_url}")
    check_function_exceed_limit_size(repo_url, commit_hash)

@app.command()
def params(repo_url: str, commit: str, param_limit: Annotated[int, typer.Argument()] = 5):
    """
    Analisa a quantidade de parâmetros das funções em um commit
    """
    typer.echo(f"Analisando quantidade de parâmetros do repositório: {repo_url}")
    check_functions_exceed_param_limit(repo_url, commit, param_limit)
    
@app.command()
def generic(repo_url: str):
    """
    Mostra informações genéricas de um repositório.
    """
    typer.echo(f"Analisando informações do repositório: {repo_url}")
    show_repository_generic_info(repo_url)

if __name__ == "__main__":
    app()
