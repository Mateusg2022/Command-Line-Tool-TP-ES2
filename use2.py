#Para cada arquivo do repositorio - e para um certo 'range' de commits, mostra:
#   total de linhas adicionadas por commit
#   máximo de linhas adicionadas por commit
#   media de linhas adicionadas por commit
from pydriller.metrics.process.lines_count import LinesCount
metric = LinesCount(path_to_repo='https://github.com/Mateusg2022/creating-a-testing-framework',
                    from_commit='1a7c334dbade1cfb007f48798ea1127b817637ae',
                    to_commit='06f062d642838c3d620f5bec55077eaeba072cf2')

count = metric.count() # added+removed lines
added_count = metric.count_added()
added_max = metric.max_added()
added_avg = metric.avg_added()

# print('Total lines added per file: {}'.format(added_count), end='\n-\n')
# print('Maximum lines added per file: {}'.format(added_max), end='\n-\n')
#     if added_count >= (2 * added_avg):
#         print('Warning !!! The file ', 'has a commit with more than expected lines added.')
# print('Average lines added per file: {}'.format(added_avg), end='\n-\n')

print("--> Analisando a quantidade total de linhas adicionadas nesse intervalo de commits.")
for key, value in (added_count).items():
    print("File: ", key, " - Count: " , value)
print()

print("--> Analisando a quantidade maxima de linhas adicionadas por um commit do intervalo.")
for key, value in (added_max).items():
    print("File: ", key, " - Count: " , value)
    if value > (2 * added_avg[key]):
        print('\tWarning !!! This file has a commit bigger than the recommended.')
        print('\tCommit size: ', value, ". Commits AVG: ", added_avg[key])
    #se um commit é maior que a metade do total de linhas adicionadas ao longo do tempo
print()

print("--> Analisando a quantidade media de linhas adicionadas nos commits do intervalo.")
for key, value in (added_avg).items():
    print("File: ", key, " - Count: " , value)
print()