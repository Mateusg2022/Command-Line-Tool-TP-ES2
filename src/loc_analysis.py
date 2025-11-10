from pydriller.metrics.process.lines_count import LinesCount
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

def analyze_loc(repo_url: str, from_commit: str, to_commit: str):
    console.print(Panel.fit(
        f"[bold cyan] Analisando evolução de LOC[/bold cyan]\n"
        f"Repositório: [yellow]{repo_url}[/yellow]\n"
        f"De: [green]{from_commit[:10]}[/green] → Até: [green]{to_commit[:10]}[/green]",
        style="blue"
    ))

    metric = LinesCount(
        path_to_repo=repo_url,
        from_commit=from_commit,
        to_commit=to_commit
    )

    added_count = metric.count_added()
    added_max = metric.max_added()
    added_avg = metric.avg_added()

    # total de linhas adicionadas
    console.print("\n[bold underline cyan]→ Total de linhas adicionadas:[/bold underline cyan]")
    table_total = Table(show_header=True, header_style="bold magenta")
    table_total.add_column("Arquivo", style="yellow")
    table_total.add_column("Total", style="green")
    for key, value in added_count.items():
        table_total.add_row(key, str(value))
    console.print(table_total)

    # maximo de linhas adicionadas
    console.print("\n[bold underline cyan]→ Máximo de linhas adicionadas por commit:[/bold underline cyan]")
    table_max = Table(show_header=True, header_style="bold magenta")
    table_max.add_column("Arquivo", style="yellow")
    table_max.add_column("Máximo", style="green")
    table_max.add_column("Média", style="cyan")
    table_max.add_column("Aviso", style="red")
    for key, value in added_max.items():
        warning = ""
        if value > (2 * added_avg[key]):
            warning = "[ALERTA] Commit muito grande!"
        table_max.add_row(key, str(value), str(round(added_avg[key], 2)), warning)
        if warning:
            console.print(warning)
    console.print(table_max)

    # media de linhas adicionadas
    console.print("\n[bold underline cyan]→ Média de linhas adicionadas por commit:[/bold underline cyan]")
    table_avg = Table(show_header=True, header_style="bold magenta")
    table_avg.add_column("Arquivo", style="yellow")
    table_avg.add_column("Média", style="cyan")
    for key, value in added_avg.items():
        table_avg.add_row(key, str(round(value, 2)))
    console.print(table_avg)
