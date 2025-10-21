#Para cada arquivo do repositorio - e para um certo 'range' de commits, mostra:
#   total de linhas adicionadas por commit
#   máximo de linhas adicionadas por commit
#   media de linhas adicionadas por commit
from pydriller.metrics.process.lines_count import LinesCount
metric = LinesCount(path_to_repo='https://github.com/Mateusg2022/creating-a-testing-framework',
                    from_commit='1a7c334dbade1cfb007f48798ea1127b817637ae',
                    to_commit='06f062d642838c3d620f5bec55077eaeba072cf2')

added_count = metric.count_added()
added_max = metric.max_added()
added_avg = metric.avg_added()

print('Total lines added per file: {}'.format(added_count), end='\n-\n')
print('Maximum lines added per file: {}'.format(added_max), end='\n-\n')
print('Average lines added per file: {}'.format(added_avg), end='\n-\n')