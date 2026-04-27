import sys
import subprocess

DEPENDENCIAS = [
    "pandas",
    "openpyxl",
    "sqlalchemy",
    "psycopg2-binary",
]

def instalar_dependencias():
    for pacote in DEPENDENCIAS:
        try:
            __import__(pacote.replace("-", "_"))
        except ImportError:
            print(f"Instalando {pacote}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pacote])

instalar_dependencias()


import os
import re
import time
import logging
from functools import wraps
from datetime import datetime

import pandas as pd
from sqlalchemy import create_engine, text


DB_URL = "postgresql+psycopg2://alunos:AlunoFatec@200.19.224.150:5432/atividade2"

OUTPUT_DIR = "output"
LOG_FILE = os.path.join(OUTPUT_DIR, "execucao.log")

os.makedirs(OUTPUT_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


# --- Atividade 4: decorador com log em arquivo ---

def medir_tempo(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        inicio = time.perf_counter()
        resultado = func(*args, **kwargs)
        fim = time.perf_counter()
        duracao = fim - inicio
        logger.info("Funcao '%s' executada em %.6f segundos.", func.__name__, duracao)
        return resultado
    return wrapper


# --- Atividade 1: anonimizacao ---

def anonimizar_nome(nome: str) -> str:
    if not nome:
        return nome
    partes = nome.split()
    partes[0] = partes[0][0] + "*" * (len(partes[0]) - 1)
    return " ".join(partes)


def anonimizar_cpf(cpf: str) -> str:
    if not cpf:
        return cpf
    match = re.match(r"^(\d{3})\.([\d./-]+)$", cpf)
    if match:
        prefixo = match.group(1)
        resto = match.group(2)
        mascara = re.sub(r"\d", "*", resto)
        return f"{prefixo}.{mascara}"
    return cpf[:3] + re.sub(r"\d", "*", cpf[3:])


def anonimizar_email(email: str) -> str:
    if not email or "@" not in email:
        return email
    local, dominio = email.split("@", 1)
    return local[0] + "*" * (len(local) - 1) + "@" + dominio


def anonimizar_telefone(telefone: str) -> str:
    if not telefone:
        return telefone
    digitos = re.sub(r"\D", "", telefone)
    return digitos[-4:] if len(digitos) >= 4 else digitos


def LGPD(row: dict) -> dict:
    anonimizado = dict(row)
    anonimizado["nome"] = anonimizar_nome(row.get("nome", ""))
    anonimizado["cpf"] = anonimizar_cpf(row.get("cpf", ""))
    anonimizado["email"] = anonimizar_email(row.get("email", ""))
    anonimizado["telefone"] = anonimizar_telefone(row.get("telefone", ""))
    return anonimizado


# --- Leitura do banco ---

def carregar_dados(engine) -> pd.DataFrame:
    with engine.connect() as conn:
        df = pd.read_sql(text("SELECT * FROM usuarios;"), conn)
    logger.info("%d registros carregados.", len(df))
    return df


def preparar_dataframe_anonimizado(df: pd.DataFrame) -> pd.DataFrame:
    registros = [LGPD(row) for row in df.to_dict(orient="records")]
    return pd.DataFrame(registros)


def _coluna_nascimento(df: pd.DataFrame) -> str | None:
    candidatas = ["data_nascimento", "nascimento", "birth_date", "birthdate", "dt_nascimento"]
    for col in candidatas:
        if col in df.columns:
            return col
    for col in df.columns:
        if "nasc" in col.lower() or "birth" in col.lower():
            return col
    return None


# --- Atividade 2: exportacao por ano (anonimizado) ---

@medir_tempo
def exportar_por_ano(df_anonimizado: pd.DataFrame) -> None:
    coluna_data = _coluna_nascimento(df_anonimizado)
    if coluna_data is None:
        logger.error("Coluna de data de nascimento nao encontrada.")
        return

    df = df_anonimizado.copy()
    df[coluna_data] = pd.to_datetime(df[coluna_data], errors="coerce")
    df["_ano"] = df[coluna_data].dt.year

    for ano in sorted(df["_ano"].dropna().unique()):
        ano_int = int(ano)
        subdf = df[df["_ano"] == ano_int].drop(columns=["_ano"])
        caminho = os.path.join(OUTPUT_DIR, f"{ano_int}.xlsx")
        subdf.to_excel(caminho, index=False, engine="openpyxl")
        logger.info("Exportado: %s (%d registros)", caminho, len(subdf))


# --- Atividade 3: exportacao todos (nome + cpf sem anonimizacao) ---

@medir_tempo
def exportar_todos(df_original: pd.DataFrame) -> None:
    colunas_faltantes = {"nome", "cpf"} - set(df_original.columns)
    if colunas_faltantes:
        logger.error("Colunas ausentes: %s", colunas_faltantes)
        return

    caminho = os.path.join(OUTPUT_DIR, "todos.xlsx")
    df_original[["nome", "cpf"]].to_excel(caminho, index=False, engine="openpyxl")
    logger.info("Exportado: %s (%d registros)", caminho, len(df_original))


# --- Main ---

def main():
    logger.info("Inicio | %s", datetime.now().isoformat())

    engine = create_engine(DB_URL, echo=False)

    df_original = carregar_dados(engine)
    df_anonimizado = preparar_dataframe_anonimizado(df_original)

    exportar_por_ano(df_anonimizado)
    exportar_todos(df_original)

    logger.info("Fim. Log em: %s", LOG_FILE)


if __name__ == "__main__":
    main()
