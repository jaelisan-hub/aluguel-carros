import psycopg2

DATABASE_URL = "postgresql://locadora_v5d7_user:ZIa4dfq1MOZvXfNXCgW0UcmNZH0sFbMk@dpg-d815iijrjlhs73assr10-a.virginia-postgres.render.com/locadora_v5d7"

conexao = psycopg2.connect(DATABASE_URL)
cursor = conexao.cursor()

# =========================
# CORRIGIR TABELA CLIENTES
# =========================
cursor.execute("""
ALTER TABLE clientes
ADD COLUMN IF NOT EXISTS usuario VARCHAR(200);
""")

# =========================
# CORRIGIR TABELA CARROS
# =========================
cursor.execute("""
ALTER TABLE carros
ADD COLUMN IF NOT EXISTS usuario VARCHAR(200);
""")

# =========================
# CORRIGIR TABELA ALUGUEIS
# =========================
cursor.execute("""
ALTER TABLE alugueis
ADD COLUMN IF NOT EXISTS usuario VARCHAR(200);
""")

conexao.commit()
conexao.close()

print("✅ Banco corrigido com sucesso!")