# Mini-Projeto-2-LP2
# LGPD — Anonimização e Exportação de Dados

Projeto desenvolvido para a disciplina de Engenharia de Dados. O script conecta a um banco PostgreSQL, aplica anonimização de dados pessoais conforme a LGPD e exporta os registros em arquivos Excel organizados por ano de nascimento.

---

## Estrutura do Projeto

```
.
├── LGPD.py
├── requirements.txt
└── output/
    ├── execucao.log
    ├── todos.xlsx
    ├── 1990.xlsx
    ├── 1991.xlsx
    └── ...
```

---

## Requisitos

- Python 3.10 ou superior
- Acesso à rede do banco de dados

As dependências são instaladas automaticamente na primeira execução. Caso prefira instalar manualmente:

```bash
pip install -r requirements.txt
```

---

## Como Executar

```bash
python LGPD.py
```

Na primeira execução o script instala as dependências ausentes e cria a pasta `output/` automaticamente.

---

## Atividades Implementadas

### Atividade 1 — Anonimização

Aplicada em memória sobre todos os registros lidos do banco antes de qualquer exportação.

| Campo | Regra | Exemplo |
|---|---|---|
| `nome` | Mantém a primeira letra da primeira palavra | `Olivia Araújo` → `O***** Araújo` |
| `cpf` | Mantém os três primeiros dígitos | `237.615.809-59` → `237.*** ***-**` |
| `email` | Mantém a primeira letra antes do `@` | `nuneserick@example.com` → `n*********@example.com` |
| `telefone` | Retorna apenas os quatro últimos dígitos | `+55 (011) 9483-6810` → `6810` |

### Atividade 2 — Exportação por Ano

Gera um arquivo `.xlsx` por ano de nascimento dentro da pasta `output/`, contendo os dados anonimizados.

```
output/
├── 1990.xlsx
├── 1991.xlsx
└── ...
```

### Atividade 3 — Exportação Unificada

Gera o arquivo `output/todos.xlsx` com todos os registros, contendo apenas as colunas `nome` e `cpf` **sem anonimização**.

### Atividade 4 — Log de Tempo de Execução

O decorador `@medir_tempo` é aplicado nas funções de exportação das Atividades 2 e 3. O tempo de execução de cada função é registrado no arquivo `output/execucao.log`.

Exemplo de entrada no log:

```
2024-06-01 10:32:45 | INFO | Funcao 'exportar_por_ano' executada em 1.234567 segundos.
2024-06-01 10:32:46 | INFO | Funcao 'exportar_todos' executada em 0.087321 segundos.
```

---

## Banco de Dados

| Parâmetro | Valor |
|---|---|
| Host | `200.19.224.150` |
| Porta | `5432` |
| Banco | `atividade2` |
| Usuário | `alunos` |
| Tabela | `usuarios` |

---

## Dependências

| Pacote | Uso |
|---|---|
| `pandas` | Manipulação e exportação dos dados |
| `openpyxl` | Geração dos arquivos `.xlsx` |
| `sqlalchemy` | Conexão com o banco PostgreSQL |
| `psycopg2-binary` | Driver do PostgreSQL |
