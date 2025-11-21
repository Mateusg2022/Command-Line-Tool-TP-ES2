# Minero - A Command-Line-Tool

Trabalho Prático da disciplina de Engenharia de Software 2
Professor: André Hora
UFMG

Integrantes do grupo:
  <ul>
    <li>Gabriel Coelho dos Santos</li>
    <li>Joao Correia Costa</li>
    <li>Kayque Meira Siqueira</li>
    <li>Mateus Augusto Gomes</li> 
  </ul>
  
# Explicação do Sistema e do objetivo

Este projeto consiste no desenvolvimento de uma ferramenta de linha de comando (CLI) para auxiliar na identificação de possíveis problemas de manutenção de software em repositórios.
Essa análise é feita em commits de plataformas de hospedagem de código (é necessário a url do repositorio e/ou a hash do commit).

Entre os indicadores analisados, estão:

- Funções Python que ultrapassam o valor de 200 linhas de código

- Funções Python que ultrapassam a quantidade de 5 parâmetros (valor padrão mas alterável)

- Analisar a Complexidade Cognitiva (métrica quantitativa sobre a complexidade de ler e entender a lógica do código)

O sistema poderá realizar avaliações automáticas sobre métricas de manutenção e evolução de software em commits. Pode ser útil como uma segunda verificação antes de, por exemplo, o usuário fazer uma aprovação de uma PR.

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
  - Facilita a extração de métricas de evolução de repositórios Git, como crescimento de linhas de código (LOC) e estatísticas de commits.

- Typer
  - Framework moderno para criar a interface de linha de comando (CLI) do projeto.

- Rich
  - Biblioteca python para adicionar cores, estilos e formatação para saídas de texto no terminal.
