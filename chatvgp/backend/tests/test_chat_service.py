from app.models import Log
from app.services.chat_service import (
    buscar_prestadores,
    extrair_categoria,
    gerar_link_whatsapp,
)
from tests.conftest import criar_categoria, criar_prestador


# ---------- extrair_categoria ----------

def test_encontra_pelo_nome(db):
    cat = criar_categoria(db, "Encanador")
    assert extrair_categoria("preciso de um encanador", db) == cat.id


def test_encontra_pelo_alias(db):
    cat = criar_categoria(db, "Eletricista", aliases="instalação elétrica,tomada,disjuntor")
    assert extrair_categoria("minha tomada queimou", db) == cat.id
    assert extrair_categoria("fazer instalação elétrica nova", db) == cat.id


def test_alias_de_varias_palavras_exige_todas(db):
    criar_categoria(db, "Eletricista", aliases="instalação elétrica")
    assert extrair_categoria("instalação de ar condicionado", db) is None


def test_ignora_acentos_nos_dois_lados(db):
    cat = criar_categoria(db, "Veterinária", aliases="vacina,clínica veterinária")
    assert extrair_categoria("procuro veterinaria", db) == cat.id
    assert extrair_categoria("clinica veterinaria perto", db) == cat.id


def test_escolhe_categoria_com_mais_palavras_em_comum(db):
    # Antes, a primeira categoria do banco com QUALQUER palavra em comum vencia
    criar_categoria(db, "Aluguel Mesas e Cadeiras", ordem=1)
    melhor = criar_categoria(db, "Aluguel de Brinquedos", aliases="pula pula,cama elástica", ordem=2)
    assert extrair_categoria("aluguel de cama elástica", db) == melhor.id


def test_empate_usa_menor_ordem(db):
    criar_categoria(db, "Pintor Residencial", ordem=5)
    primeira = criar_categoria(db, "Pintor Automotivo", ordem=1)
    assert extrair_categoria("preciso de um pintor", db) == primeira.id


def test_sem_categoria_registra_log(db):
    criar_categoria(db, "Encanador")
    assert extrair_categoria("quero comprar pizza", db) is None
    log = db.query(Log).one()
    assert log.tipo == "CATEGORIA_NAO_IDENTIFICADA"
    assert log.pergunta == "quero comprar pizza"


def test_sucesso_registra_log(db):
    criar_categoria(db, "Encanador")
    extrair_categoria("encanador urgente", db)
    log = db.query(Log).one()
    assert log.tipo == "BUSCA_SUCESSO"
    assert log.categoria_encontrada == "Encanador"


# ---------- buscar_prestadores ----------

def test_ordena_premium_depois_verificado_depois_nome(db):
    cat = criar_categoria(db, "Encanador")
    criar_prestador(db, "Zeca", "11900000001", [cat])
    criar_prestador(db, "Ana", "11900000002", [cat])
    criar_prestador(db, "Verificado", "11900000003", [cat], verificado_hurbem=True)
    criar_prestador(db, "Premium", "11900000004", [cat], premium=True)

    nomes = [p["nome"] for p in buscar_prestadores(db, cat.id)]
    assert nomes == ["Premium", "Verificado", "Ana", "Zeca"]


def test_so_retorna_ativos_e_respeita_limite(db):
    cat = criar_categoria(db, "Encanador")
    for i in range(7):
        criar_prestador(db, f"Ativo {i}", f"1190000000{i}", [cat])
    criar_prestador(db, "Pendente", "11911111111", [cat], status="pendente")
    criar_prestador(db, "Inativo", "11922222222", [cat], status="inativo")

    resultado = buscar_prestadores(db, cat.id, limit=5)
    assert len(resultado) == 5
    assert all(p["nome"].startswith("Ativo") for p in resultado)


def test_retorna_descricao_e_nao_retorna_dados_pessoais(db):
    cat = criar_categoria(db, "Encanador")
    criar_prestador(
        db, "Ana", "11900000001", [cat],
        descricao="Atendo 24h", email="ana@exemplo.com", cpf_cnpj="52998224725",
    )
    p = buscar_prestadores(db, cat.id)[0]
    assert p["descricao"] == "Atendo 24h"
    assert "email" not in p
    assert "cpf_cnpj" not in p


# ---------- gerar_link_whatsapp ----------

def test_link_whatsapp_adiciona_codigo_do_pais():
    link = gerar_link_whatsapp("11987654321")
    assert link.startswith("https://wa.me/5511987654321?text=")


def test_link_whatsapp_aceita_numero_formatado():
    assert gerar_link_whatsapp("(11) 98765-4321").startswith("https://wa.me/5511987654321?")


def test_link_whatsapp_nao_duplica_55():
    assert gerar_link_whatsapp("5511987654321").startswith("https://wa.me/5511987654321?")


def test_link_whatsapp_codifica_mensagem():
    link = gerar_link_whatsapp("11987654321")
    assert " " not in link
    assert "Ol%C3%A1" in link  # "Olá" codificado
