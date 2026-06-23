"""
db/storage.py
Gerenciamento da conexão com o PostgreSQL e execução das migrations.
"""

from __future__ import annotations

from pathlib import Path

import asyncpg

from config import (
    DB_DATABASE,
    DB_HOST,
    DB_PASSWORD,
    DB_CONNECT_TIMEOUT,
    DB_POOL_MAX_SIZE,
    DB_POOL_MIN_SIZE,
    DB_PORT,
    DB_STATEMENT_CACHE_SIZE,
    DB_URL,
    DB_USER,
)

# diretório onde ficam os arquivos .sql de migration
MIGRATIONS_DIR = Path(__file__).resolve().parent / "migrations"

# pool de conexões compartilhado pela aplicação - inicializado no lifespan
_pool: asyncpg.Pool | None = None
_pool_error: Exception | None = None


async def init_pool() -> None:
    """
    Cria o pool de conexões com o PostgreSQL e executa as migrations pendentes.
    Deve ser chamado uma única vez na startup da aplicação.
    """
    global _pool, _pool_error

    pool_options = {
        "min_size": DB_POOL_MIN_SIZE,
        "max_size": DB_POOL_MAX_SIZE,
        "timeout": DB_CONNECT_TIMEOUT,
        "statement_cache_size": DB_STATEMENT_CACHE_SIZE,
    }

    try:
        if DB_URL:
            _pool = await asyncpg.create_pool(dsn=DB_URL, **pool_options)
        else:
            _pool = await asyncpg.create_pool(
                host=DB_HOST,
                port=DB_PORT,
                database=DB_DATABASE,
                user=DB_USER,
                password=DB_PASSWORD,
                **pool_options,
            )

        await _run_migrations()
        _pool_error = None
    except Exception as exc:
        _pool = None
        _pool_error = exc
        print(f"[warn] PostgreSQL startup unavailable: {exc}", flush=True)


async def close_pool() -> None:
    """
    Fecha o pool de conexões.
    Deve ser chamado na shutdown da aplicação.
    """
    global _pool

    if _pool is not None:
        await _pool.close()
        _pool = None


def get_pool() -> asyncpg.Pool:
    """
    Retorna o pool de conexões ativo.
    Lança RuntimeError se chamado antes de init_pool().
    """
    if _pool is None:
        detail = f" Erro original: {_pool_error}" if _pool_error else ""
        raise RuntimeError(f"Pool de conexões não inicializado.{detail}")
    return _pool


async def _run_migrations() -> None:
    """
    Executa as migrations ainda não aplicadas, em ordem numérica.
    Controla quais migrations já foram rodadas pela tabela schema_migrations.
    """
    pool = get_pool()

    async with pool.acquire() as conn:
        # garante que a tabela de controle existe
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                versao      TEXT    NOT NULL,
                aplicado_em TEXT    NOT NULL,
                CONSTRAINT pk_schema_migrations PRIMARY KEY (versao)
            )
        """)

        # descobre quais migrations já foram aplicadas
        registros = await conn.fetch("SELECT versao FROM schema_migrations")
        aplicadas = {r["versao"] for r in registros}

        # lê os arquivos .sql em ordem numérica
        arquivos = sorted(MIGRATIONS_DIR.glob("*.sql"))

        for arquivo in arquivos:
            versao = arquivo.stem  # ex: "001_create_safras"

            if versao in aplicadas:
                continue

            sql = arquivo.read_text(encoding="utf-8")
            await conn.execute(sql)
            await conn.execute(
                "INSERT INTO schema_migrations (versao, aplicado_em) VALUES ($1, NOW()::text)",
                versao,
            )
