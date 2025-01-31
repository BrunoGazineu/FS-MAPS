import subprocess
import json
import ast
import os
import pkg_resources
import pathlib


def ciano_sublinhado(msg):
    return f'\033[4:36m{msg}\033[m'


def amarelo(msg):
    return f'\033[1:33m{msg}\033[m'


def azul_negatigo(msg):
    return f'\033[7:34m{msg}\033[m'


def get_all_imports(directory):
    codings = ["utf-8", "latin-1", "utf-16"]
    all_imports = set()

    for root, _, files in os.walk(directory):

        for file in files:

            if file.endswith(".py"):

                file_path = os.path.join(root, file)

                for coding in codings:

                    try:

                        with open(file_path, "r", encoding=coding) as f:

                            tree = ast.parse(f.read())

                            for node in ast.walk(tree):

                                if isinstance(node, ast.Import):

                                    for alias in node.names:
                                        all_imports.add(alias.name)

                                elif isinstance(node, ast.ImportFrom):

                                    if node.module:
                                        all_imports.add(node.module)

                        break

                    except UnicodeDecodeError:

                        continue

    return all_imports


def Start():
    caminho = input(amarelo('﹛ ? ﹜- Qual o caminho do aquivo do Codigo: '.upper()))
    project_root = rf"{caminho}"

    imports = get_all_imports(project_root)
    installed_packages = {pkg.key for pkg in pkg_resources.working_set}
    unused_packages = installed_packages - imports

    with open('DESINSTALAR.txt', 'w') as novo_arq:

        for package in unused_packages:
            novo_arq.write(package + '\n')

    print('Escreveu em: DESINSTALAR.txt')

    # Verifica se o arquivo .gitignore existe
    gitignore_file = pathlib.Path(".gitignore")
    if gitignore_file.exists():
        # Se o arquivo já existe, adiciona 'DESINSTALAR' na última linha
        with open('.gitignore', 'a') as gitignore:
            gitignore.write('DESINSTALAR.txt\n')
            gitignore.write('INSTALADOS.txt\n')
            gitignore.write('PACOTES_ATUALIZAR.txt\n')
            gitignore.write('ALAGUNS_CODIGOS_Deploy_Limpo.py\n')
            gitignore.write('package.json\n')
    else:
        # Se o arquivo não existe, cria o arquivo e escreve 'DESINSTALAR'
        with open('.gitignore', 'w') as gitignore:
            gitignore.write('DESINSTALAR.txt\n')
            gitignore.write('INSTALADOS.txt\n')
            gitignore.write('PACOTES_ATUALIZAR.txt\n')
            gitignore.write('ALAGUNS_CODIGOS_Deploy_Limpo.py\n')
            gitignore.write('package.json\n')

    print(ciano_sublinhado('Escreveu em: .gitignore'))

    # ⇩ AANALIZE O ARQUIVO DESINSTALAT.txt  SE TUDO OK siga abaixo ⇩
    # ------- Proximos Comandos
    print(f'')
    print(ciano_sublinhado('------- Atualiza o pip do do codigo'))
    # subprocess.run(["pip", "install", "--upgrade", "pip"]) # --> Atualiza o pip do do codigo.

    print(f'')
    print(ciano_sublinhado('Mostra todos modulos instalado via pip'))
    with open("INSTALADOS.txt", "w") as file:
        subprocess.run(["pip", "list", "--not-required", "--format=freeze"], stdout=file, text=True, check=True)
        # --> Mostra tudo instalado via pip

    print(f'')
    print(ciano_sublinhado('vai copiar e tirar ==.. e criar PACOTES_ATUALIZAR.txt'))
    powershell_command = r"(Get-Content INSTALADOS.txt) -replace '==.*$', '' | Out-File -Encoding UTF8 PACOTES_ATUALIZAR.txt"
    subprocess.run(["powershell.exe", "-Command", powershell_command])
    # ---> vai copiar e tirar ==.. e criar PACOTES_ATUALIZAR.txt

    print(f'')
    print(ciano_sublinhado('Atualiza todos os Modulos listados no PACOTES_ATUALIZAR.'))
    subprocess.run(["pip", "install", "--upgrade", "-r", "PACOTES_ATUALIZAR.txt"])
    # ---> Atualiza todos os Modulos listados no PACOTES_ATUALIZAR.

    print(f'')
    print(ciano_sublinhado('Cria um Arquivo requirements.txt com seus arquivos atualizados'))
    # Executar o comando 'pip list' e redirecionar a saída para um arquivo

    with open("requirements.txt", "w") as file:
        process = subprocess.Popen(["pip", "list", "--not-required", "--format=freeze"], stdout=subprocess.PIPE,
                                   universal_newlines=True)

        # Ler a saída do processo linha por linha e escrever no arquivo
        import re
        converted_requirements = {}
        for line in process.stdout:
            file.write(line)
            print(line, end="")  # Imprimir a linha
            match = re.match(r'(\w+)==(\d+\.\d+\.\d+)', line)
            if match:
                package = match.group(1)
                version = match.group(2)
                converted_requirements[package] = f'^{version}'

        process.communicate()  # Aguardar o término do processo
        print('')
        Exec = input(amarelo('﹛ ? ﹜- Deseja criar Executavel [Sim ou Não]: '.upper()))
        # Imprimir o dicionário com quebra de linha após cada vírgula
        formatted_output = json.dumps(converted_requirements, indent=None, separators=(',', ': '))
        formatted_output = formatted_output.replace(',', ',\n')
        print(formatted_output)

        if Exec.lower() != '':
            if Exec.lower()[0] == 's':
                print()
                SEU_NOME = input(amarelo('﹛ ? ﹜- Diga o seu nome: '))
                NOME_PROGRAMA = input(amarelo('﹛ ? ﹜- Diga o nome do Programa: '))
                DESCRIT = input(amarelo('﹛ ? ﹜- Diga a descrição: '))
                IMAGEM_ico = input(amarelo('﹛ ? ﹜- Diga o nome da sua imagem .ICO: '))
                print("criar executaveis:")
                Json = f'''
{{
  "name": "{NOME_PROGRAMA.lower()}",
  "version": "0.1.0",
  "description": "{DESCRIT.capitalize()}",
  "author": "{SEU_NOME.title()}",
  "main": "./build/electron/main.js",
  "scripts": {{
    "dump": "dump-stlite-desktop-artifacts",
    "serve": "NODE_ENV=\\"production\\" electron .",
    "start": "cross-env ELECTRON_START_URL=http://localhost:8501/ electron .",
    "pack": "electron-builder --dir",
    "dist": "electron-builder",
    "postinstall": "electron-builder install-app-deps"
  }},
  "build": {{
    "files": [
      "build/**/*"
    ],
    "directories": {{
      "buildResources": "assets"
    }},
    "win": {{
      "target": "portable",
      "icon": "{IMAGEM_ico}"
    }}
  }},
  "devDependencies": {{
    "@stlite/desktop": "^0.32.0",
    "cross-env": "^6.0.3",
    "electron": "^25.1.1",
    "electron-builder": "^24.4.0"
  }}
}}'''
                with open('package.json', 'w') as novo_arq:
                    novo_arq.write(Json)
                with open('Como_Criar_Executavel', 'w', encoding='utf-8') as novo_arq:
                    novo_arq.write('''

------------------    CRIANDO O EXECUTAVEL

﹛#﹜ - Entre neste Site e baixe o baixe Node.js
https://nodejs.org/en

﹛#﹜ - Depois de ter instaldo:
Abra a pasta do arquivo, e abra o terminal
node -v   | ---> versao

﹛#﹜ - Digite nesta ordem:
npm install   |--> Instala as dependências do projeto listadas no arquivo package.json.

- CRIE PASTA "streamlit_app" e coloque seu app la dentro com o nome streamlit_app.py

npm rum dump streamlit_app -- -r requirements.txt	 |--> Atualiza todos modulos no req.. para o App e se tiver o pandas ou cvs etc... colque dpois do .py

﹛#﹜ - Atualizando e instalando dependência:
npm install @stlite/desktop@latest
npm install cross-env --save-dev
npm install electron --save-dev
npm install electron-builder --save-dev


﹛#﹜ - Abre o Arquivo em Uma tela teste:
Executa um script personalizado chamado serve definido no arquivo package.json, que provavelmente inicia o servidor para o aplicativo.
npm start  (ou)  npm run servewindows  (ou)  npm run serve  (ou)  npx electron .


* atenção se caso tiver problema com o "localhost:3000"!
-entre neste caminho = build/electron/main.js
-e troque = "http://localhost:3000/" por "http://localhost:8502/" ou pela host desejada
-entre no arquivo package.json : e altere  "start": "electron .",  por ' "start": "cross-env ELECTRON_START_URL=http://localhost:8502 electron . '

﹛#﹜ -  E FINALMENTE O EXECUTAVEL:
npm run dist   |--> Executa um script personalizado chamado dist definido no arquivo package.json, que geralmente é usado para criar um pacote de distribuição do aplicativo.

" E só olhar na pasta 'dist' e procurar pelo executavel do seu programa"

﹛#﹜ - Se der algum outro erro:
npm audit	|--> indica os erros
npm audit fix --force	|--> concerta os erros


﹛#﹜ -  Limitações:
A navegação para recursos externos como st.markdown("[link](https://streamlit.io/)")não funciona para segurança. Consulte o nº 445 e informe-nos se houver casos de uso em que você precise usar esses links externos.

--------------------- AQUI VC ENCONTRA MASI DETALHES DA ARVORE DO ARQUI JASON = package.json:
{
  "name": "winter",         # Define o nome do seu aplicativo como "winter".
  "version": "0.1.0",       # Define a versão do seu aplicativo como "0.1.0".
  "description": "My Electron Application",         # Descreve brevemente o seu aplicativo como "My Electron Application".
  "author": "Seu Nome",         # Especifica o autor do aplicativo como "Seu Nome". Substitua por seu nome real.
  "main": "./build/electron/main.js",       # Indica o caminho para o arquivo principal do seu aplicativo, que é "./build/electron/main.js".

  "scripts": {      # Define vários scripts para automatizar tarefas.
    "dump": "dump-stlite-desktop-artifacts",        # Executa o script "dump-stlite-desktop-artifacts".
    "serve": "NODE_ENV="production" electron .",      # Executa o aplicativo em modo de produção.
    "servewindows": "electron .",       # Executa o aplicativo no Windows.
    "start": "cross-env ELECTRON_START_URL=http://localhost:8502 electron .",       # Inicia o aplicativo com a variável de ambiente "ELECTRON_START_URL" definida como "http://localhost:8502".
    "pack": "electron-builder --dir",       # Empacota o aplicativo usando o "electron-builder" no modo de diretório.
    "dist": "electron-builder",         # Empacota o aplicativo usando o "electron-builder" no modo de distribuição.
    "postinstall": "electron-builder install-app-deps"      # Executa o "electron-builder install-app-deps" após a instalação do pacote.
  },
  "build": {        # Configura as opções de compilação e empacotamento do aplicativo.
    "files": [      # Define os arquivos a serem incluídos no pacote final, usando o padrão "build/**/*".
      "build/**/*"
    ],
    "directories": {        # Configura os diretórios relacionados à construção do aplicativo.
      "buildResources": "assets"        # Define o diretório de recursos de construção como "assets".
    },
    "win": {        # Configura as opções específicas para o ambiente Windows.
      "target": "portable",         # Define o tipo de empacotamento como "portable".
      "icon": "assets/icon.ico"         # Especifica o ícone do aplicativo como "assets/icon.ico".
    }
  },
  "devDependencies": {      # Lista as dependências de desenvolvimento do projeto.
    "@stlite/desktop": "^0.22.2",
    "cross-env": "^7.0.3",
    "electron": "^22.0.0",
    "electron-builder": "^23.6.0"
  }
}                    ''')
                print(azul_negatigo(
                    '----------- ATENÇÃO FOI CRIADO UM ARQUIVO CHAMADO "Como_Criar_Executavel" COM TODO PASSO A PASSO! ------------'))
                print(ciano_sublinhado('Escreveu em: package.json'))

    if process.returncode != 0:
        print("Ocorreu um erro ao executar o comando 'pip list'.")
    # ---> Cria um Arquivo requirements.txt com seus arquivos atualizados

    print(f'')
    print(ciano_sublinhado('Instala tudo que foi encontrado no requirements.txt'))
    subprocess.run(["pip", "install", "-r", "requirements.txt"])
    # --> Instala tudo que foi encontrado no requirements.txt
    print(f'')
    Cria = input(amarelo(
        '﹛ ? ﹜- Deseja criar ARQUIVO "packages.txt"?\nO propósito desse arquivo pode variar dependendo do contexto e do objetivo do seu código.\nEm geral, ele pode ser utilizado para armazenar informações atualizadas sobre os pacotes ou para ser usado em etapas subsequentes do processo.\ncomo uma referência para instalar ou atualizar pacotes específicos. [Sim ou Não]: '.upper()))
    if Cria.lower() != '':
        if Cria.lower()[0] == 's':
            powershell_command = r"(Get-Content requirements.txt) -replace '==.*$', '-sdk '  | Out-File -Encoding UTF8 packages.txt"
            subprocess.run(["powershell.exe", "-Command", powershell_command])
            # --> cria arquivo packages.txt

    print(f'')
    print(ciano_sublinhado('Desinstalar todos os pacotes listados no arquivo DESINSTALAR'))
    Exec = input(amarelo(
        '﹛ ? ﹜- Deseja Desisntalar todos o modulos em DESINSTALAR.py \n Geralmente vai desinstalar modulos ou que vc importou \nou que foi instalado automaticamete na criação do ambiente e vc não usa,\n Desinstala [ Sim ou não ]: '.upper()))
    if Exec.lower() != '':
        if Exec.lower()[0] == 's':
            with open("DESINSTALAR.txt", "r") as arquivo:
                pacotes = arquivo.readlines()

            for pacote in pacotes:
                pacote = pacote.strip()
                comando = ["pip", "uninstall", pacote]
                subprocess.run(comando, input="y", text=True)
                # --> Desinstalar todos os pacotes listados no arquivo DESINSTALAR.

    # --> ⇩  Remove arquivo DESINSTALAR.txt , INSTALADOS.txt , DESINSTALAR.txt ⇩
    # Remover DESINSTALAR.txt
    os.remove("DESINSTALAR.txt")

    # Remover INSTALADOS.txt
    os.remove("INSTALADOS.txt")

    # Remover PACOTES_ATUALIZAR.txt
    os.remove("PACOTES_ATUALIZAR.txt")

    os.remove("ALGUNS_CODIGOS_Deploy_Limpo.py")
    '''
    Remove-Item -Path DESINSTALAR.txt
    Remove-Item -Path INSTALADOS.txt
    Remove-Item -Path PACOTES_ATUALIZAR.txt
    Remove-Item -Path ALGUNS_CODIGOS_Deploy_Limpo.py   ---> Só desista-la se não for continuar abaixo

    pip list                            --> Ele sozinho lista todos modulos istalados inclusive  ENV
    pip list --not-required             --> Lista todos modulos instalados por vc sem o ENV
    '''

    # PARA CRIAR UM STREAMILI OU EXECUTAVEL


Start()