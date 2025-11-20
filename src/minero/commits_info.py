from pydriller import Repository
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from itertools import islice

console = Console()

def show_commits_info(repo_url: str):
    console.print(Panel.fit(f"[bold cyan] Analisando repositório:[/bold cyan] {repo_url}", style="blue"))

    for commit in islice(Repository(repo_url).traverse_commits(), 10):
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Arquivo Modificado", style="yellow")

        for file in commit.modified_files:
            table.add_row(file.filename)

        console.print()
        console.print(f"[bold green]Commit:[/bold green] {commit.hash[:10]}")
        console.print(f"[bold]Título:[/bold] {commit.msg}")
        console.print(f"[bold]Autor:[/bold] {commit.author.name}")
        console.print(table)

def show_repository_generic_info(repo_url: str):
    console.print(Panel.fit(f"[bold cyan] Analisando repositório:[/bold cyan] {repo_url}", style="blue"))

    repo = Repository(repo_url)
    total_authors = set()
    total_files = set()
    total_branches = set()
    authors_commit_number = {}
    total_commits = 0

    for commit in repo.traverse_commits():
        total_commits += 1
        total_branches.update(commit.branches)
        total_authors.add(commit.author.name)
        authors_commit_number[commit.author.name] = authors_commit_number.get(commit.author.name, 0) + 1
        for file in commit.modified_files:
            total_files.add(file.filename)
    

    console.print(f"[bold green]Total de Commits:[/bold green] {total_commits}")
    console.print(f"[bold green]Total de Arquivos Modificados:[/bold green] {len(total_files)}")
    console.print(f"[bold green]Total de Autores:[/bold green] {len(total_authors)}")
    console.print(f"[bold green]Total de Branches:[/bold green] {len(total_branches)}")
    console.print("\n[bold underline cyan]→ Número de commits por autor:[/bold underline cyan]")
    table_authors = Table(show_header=True, header_style="bold magenta")
    table_authors.add_column("Autor", style="yellow")
    table_authors.add_column("Número de Commits", style="green")
    for author, count in authors_commit_number.items():
        table_authors.add_row(author, str(count))
    console.print(table_authors)
