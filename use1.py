#mostra a chave hash do commit, a mensagem, o autor e os arquivos modificados

#output exemplo:

# 1a7c3348798ea1127b817637ae
# 2. Classe TestCase
# Mateus
# main.py  has changed

# 7a4e19f310ec4ff7bd53834eed
# 3. Classe TestResult
# Mateus
# TestCase.py  has changed
# TestResult.py  has changed
# main.py  has changed

# [...]


from pydriller import Repository

for commit in Repository('https://github.com/Mateusg2022/creating-a-testing-framework').traverse_commits():
    print()
    print(commit.hash)
    print(commit.msg)
    print(commit.author.name)

    for file in commit.modified_files:
        print(file.filename, ' has changed')
