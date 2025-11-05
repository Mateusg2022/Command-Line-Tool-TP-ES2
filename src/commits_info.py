from pydriller import Repository
from rich import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

def show_commits_info(repo_url: str):
    console.print(Panel.fit(f"[bold cyan]🔍 Analisando repositório:[/bold cyan] {repo_url}", style="blue"))

    for commit in Repository(repo_url).traverse_commits():
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Arquivo Modificado", style="yellow")

        for file in commit.modified_files:
            table.add_row(file.filename)

        console.print()
        console.print(f"[bold green]Commit:[/bold green] {commit.hash[:10]}")
        console.print(f"[bold]Título:[/bold] {commit.msg}")
        console.print(f"[bold]Autor:[/bold] {commit.author.name}")
        console.print(table)
