import typer
from src.commits_info import show_commits_info, show_repository_generic_info
from src.loc_analysis import analyze_loc
from src.param_analysis import check_functions_exceed_param_limit

app = typer.Typer(help="Ferramenta CLI para mineração de repositórios de software.")

@app.command()
def commits(repo_url: str):
    """
    Mostra informações dos commits de um repositório.
    """
    typer.echo(f"Analisando commits do repositório: {repo_url}")
    show_commits_info(repo_url)

@app.command()
def loc(repo_url: str, from_commit: str, to_commit: str):
    """
    Analisa a evolução de linhas de código (LOC) entre dois commits.
    """
    typer.echo(f"Analisando LOC do repositório: {repo_url}")
    analyze_loc(repo_url, from_commit, to_commit)

@app.command()
def params(repo_url: str, commit: str):
    """
    Analisa a quantidade de parâmetros das funções em um commit
    """
    typer.echo(f"Analisando quantidade de parâmetros do repositório: {repo_url}")
    check_functions_exceed_param_limit(repo_url, commit)
    
@app.command()
def generic(repo_url: str):
    """
    Mostra informações genéricas de um repositório.
    """
    typer.echo(f"Analisando informações do repositório: {repo_url}")
    show_repository_generic_info(repo_url)

if __name__ == "__main__":
    app()
