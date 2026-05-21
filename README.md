# Atalho Médico

Aplicativo desktop para Windows, feito em Python, para expandir atalhos de texto em conteúdos médicos pré-cadastrados. A primeira versão funciona offline e salva a biblioteca em JSON local.

## Sobre

Este aplicativo foi criado por um médico de PSF para uso próprio na rotina da atenção primária.

Não foi feito por uma empresa de software nem por um programador profissional. Foi desenvolvido com ajuda de IA, em estilo "vibecoding", a partir de uma necessidade bem prática: diminuir o tempo gasto digitando evoluções e organizar melhor os textos do prontuário.

O app não toma decisões clínicas, não substitui o médico e não é um dispositivo médico validado. Todo texto gerado deve ser revisado antes de ser copiado para o prontuário.

## O que o MVP faz

- Cadastra, edita, exclui e lista atalhos.
- Busca por atalho, título, categoria ou conteúdo.
- Expande atalhos globais automaticamente assim que o atalho ativo é reconhecido.
- Permite pausar e reativar a expansão.
- Mantém um ícone na bandeja do Windows.
- Importa e exporta a biblioteca em JSON.
- Mantém apenas um buffer curto dos últimos caracteres digitados e não salva histórico de digitação.

## Instalação

### Versão instalável

Baixe o instalador da página de Releases do GitHub, execute `AtalhoMedicoSetup.exe` e siga as instruções. O instalador copia o aplicativo para a pasta local do usuário e cria atalhos no Menu Iniciar e na Área de Trabalho.

### Desenvolvimento

Crie e ative um ambiente virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Instale as dependências:

```powershell
pip install -r requirements.txt
```

Execute:

```powershell
python main.py
```

Para abrir sem janela de terminal, use o lançador:

```powershell
.\abrir_atalho_medico.vbs
```

Durante o desenvolvimento, se as alterações parecerem não surtir efeito, use:

```powershell
.\reiniciar_atalho_medico.bat
```

Se quiser ver mensagens de erro no terminal, use o lançador de diagnóstico:

```powershell
.\rodar_atalho_medico.bat
```

## Uso

1. Abra o aplicativo.
2. Cadastre atalhos começando com ponto, como `.rcr`.
3. Deixe a expansão ativa.
4. Em qualquer campo de texto do Windows, digite o atalho.

Exemplo:

```text
.rcr
```

Expande para:

```text
Ritmo cardíaco regular em 2 tempos, bulhas normofonéticas, sem sopros audíveis.
```

## Observações importantes

- O app não usa internet, login, nuvem, banco de dados ou IA.
- A biblioteca local fica em `atalho_medico/data/snippets.json`.
- A captura global pode exigir permissões elevadas em alguns ambientes Windows.
- Ao clicar no `X`, escolha entre fechar o aplicativo, enviar para a bandeja ou cancelar.
- Na bandeja, a expansão continua ativa enquanto o aplicativo estiver rodando.

## Formato do JSON

```json
[
  {
    "atalho": ".rcr",
    "titulo": "Ritmo cardíaco regular",
    "categoria": "Exame físico",
    "texto": "Ritmo cardíaco regular em 2 tempos, bulhas normofonéticas, sem sopros audíveis.",
    "ativo": true
  }
]
```
