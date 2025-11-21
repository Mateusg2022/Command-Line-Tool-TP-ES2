from typing import Optional
import typer
from .commits_info import show_commits_info, show_repository_generic_info
from .loc_analysis import check_function_exceed_limit_size
from .param_analysis import check_functions_exceed_param_limit
from .cognitive_analysis import show_cognitive_analysis
from .code_smells_analysis import check_code_smells

from typing_extensions import Annotated

app = typer.Typer(
    help="Ferramenta CLI para mineração de repositórios de software.",
    add_completion=False
)

@app.command()
def generic(
    repo_url: Annotated[str, typer.Argument(help="URL do repositório a ser analisado.")]
):
    """
    Mostra informações genéricas de um repositório.
    """
    typer.echo(f"Analisando informações do repositório: {repo_url}")
    show_repository_generic_info(repo_url)

@app.command()
def commits(repo_url: Annotated[str, typer.Argument(help="URL do repositório a ser analisado.")]):
    """
    Mostra informações dos commits de um repositório.
    """
    typer.echo(f"Analisando commits do repositório: {repo_url}")
    show_commits_info(repo_url)

@app.command()
def loc(
    repo_url: Annotated[str, typer.Argument(help="URL do repositório a ser analisado.")],
    commit_hash: Annotated[str, typer.Argument(help="Hash do commit a ser analisado.")]
):
    """
    Emite um alerta caso um arquivo .py de um commit tenha funções que excedam 200 linhas
    """
    typer.echo(f"Analisando LOC do repositório: {repo_url}")
    check_function_exceed_limit_size(repo_url, commit_hash)

@app.command()
def params(
    repo_url: Annotated[str, typer.Argument(help="URL do repositório a ser analisado.")],
    commit_hash: Annotated[str, typer.Argument(help="Hash do commit a ser analisado.")],
    param_limit: Annotated[int, typer.Argument(help="Limite do número de parâmetros a ser utilizado.")] = 5
):
    """
    Analisa a quantidade de parâmetros das funções em um commit
    """
    typer.echo(f"Analisando quantidade de parâmetros do repositório: {repo_url}")
    check_functions_exceed_param_limit(repo_url, commit_hash, param_limit)

@app.command()
def cog_analysis(
    repo_url: Annotated[str, typer.Argument(help="URL do repositório a ser analisado.")],
    commit_hash: Annotated[Optional[str], typer.Argument(help="Hash do commit a ser analisado, opcionalmente.")] = None,
    complexity_level_threshold: Annotated[int, typer.Argument(help="Limite de complexidade a ser considerado.")] = 12
):
    """
    Mostra a complexidade cognitiva das funções Python em um commit específico ou nos últimos 10 commits.
    """
    typer.echo(f"Analisando complexidade cognitiva do repositório: {repo_url} no commit: {commit_hash if commit_hash else 'últimos 10 commits'}")
    show_cognitive_analysis(repo_url, commit_hash, complexity_level_threshold)
    
@app.command()
def code_smells(
    repo_url: Annotated[str, typer.Argument(help="URL do repositório a ser analisado.")],
    commit_hash: Annotated[str, typer.Argument(help="Hash do commit a ser analisado.")]
):
    """
    Detecta code smells relacionados à manutenção de software em um commit
    """
    typer.echo(f"Analisando code smells do repositório: {repo_url}")
    check_code_smells(repo_url, commit_hash)

if __name__ == "__main__":
    app()
