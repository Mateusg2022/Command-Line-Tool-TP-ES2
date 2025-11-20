# Command-Line-Tool-TP-ES2

Integrantes do grupo:
  <ul>
    <li>Gabriel Coelho dos Santos</li>
    <li>Joao Correia Costa</li>
    <li>Kayque Meira Siqueira</li>
    <li>Mateus Augusto Gomes </li> 
  </ul>
  
# Explicação do Sistema

Este projeto consiste no desenvolvimento de uma ferramenta de linha de comando (CLI) para auxiliar na identificação de possíveis problemas de manutenção de software em repositórios.

Entre os indicadores analisados, estão:

- Crescimento da quantidade de linhas de código (LOC) ao longo do tempo.

- Estatísticas relacionadas ao histórico do repositório (commits, pull requests, issues).

O sistema poderá realizar uma avaliação automática, identificando situações suspeitas como aumento exagerado de LOC, ou períodos de crescimento descontrolado no repositório.

Assim, a ferramenta servirá como um auxílio para desenvolvedores, professores e pesquisadores que desejam analisar a manutenibilidade de projetos de software.

Para executar o software, primeiro instale as dependências:
`
pip install -r requirements.txt
`

Após isso, utilize o comando a seguir para entender as opções de comandos:
`
python main.py --help
`

Então, para testar, você pode fazer, por exemplo:
`
python main.py commits https://github.com/Mateusg2022/creating-a-testing-framework
`

# Tecnologias

- PyDriller
 – Facilita a extração de métricas de evolução de repositórios Git, como crescimento de linhas de código (LOC) e estatísticas de commits.

- PyGithub
 – Permite acessar dados do GitHub (issues, pull requests, etc.) de forma simples.

- Typer
 – Framework moderno para criar a interface de linha de comando (CLI) do projeto.

- Rich
  - Permite melhor estilização/output das saídas do programa

Essas bibliotecas foram escolhidas por atenderem diretamente aos objetivos de analisar a evolução do código e fornecer uma CLI prática para desenvolvedores e pesquisadores.
