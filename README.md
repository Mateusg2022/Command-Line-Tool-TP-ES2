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
Essa análise é feita em commits de plataformas de hospedagem de código (é necessário a url do repositorio e/ou a hash do commit).

Entre os indicadores analisados, estão:

- Funções Python que ultrapassam o valor de 200 linhas de código

- Funções Python que ultrapassam a quantidade de 5 parâmetros (valor padrão mas alterável)

- Analisar a Complexidade Cognitiva (métrica quantitativa sobre a complexidade de ler e entender a lógica do código)

O sistema poderá realizar uma avaliação automática, identificando situações suspeitas como aumento exagerado de LOC, ou períodos de crescimento descontrolado no repositório.
O sistema poderá realizar avaliações automáticas sobre métricas de manutenção e evolução de software em commit antes de, por exemplo, o usuário fazer uma aprovação de uma PR.

Assim, a ferramenta servirá como um auxílio para desenvolvedores, professores e pesquisadores que desejam analisar a manutenibilidade de projetos de software.

Para executar o software, primeiro instale as dependências:
`
pip install -r requirements.txt
`

Após isso, utilize o comando a seguir para entender as opções de comandos:
`
python main.py --help
`

# Tecnologias

- PyDriller
  – Facilita a extração de métricas de evolução de repositórios Git, como crescimento de linhas de código (LOC) e estatísticas de commits.

- PyGithub
   – Permite acessar dados do GitHub (issues, pull requests, etc.) de forma simples.

- Typer
 – Framework moderno para criar a interface de linha de comando (CLI) do projeto.

Essas bibliotecas foram escolhidas por atenderem diretamente aos objetivos de analisar a evolução do código e fornecer uma CLI prática para desenvolvedores e pesquisadores.
