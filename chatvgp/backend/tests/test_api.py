"""Testes das rotas: autenticação, privacidade e fluxo de aprovação."""
from app.models import Prestador
from tests.conftest import criar_categoria, criar_prestador

CPF_VALIDO = "52998224725"


# ---------- Login ----------

def test_login_com_admin_password(client):
    resp = client.post("/api/auth/login", json={"senha": "senha-de-teste-admin"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_com_secret_key_nao_funciona_mais(client):
    resp = client.post("/api/auth/login", json={"senha": "chave-de-teste"})
    assert resp.status_code == 401


def test_login_bloqueia_apos_5_tentativas_por_minuto(client):
    for _ in range(5):
        assert client.post("/api/auth/login", json={"senha": "errada"}).status_code == 401
    assert client.post("/api/auth/login", json={"senha": "errada"}).status_code == 429


# ---------- Privacidade ----------

def test_rotas_publicas_nao_expoem_email_nem_cpf(client, db):
    cat = criar_categoria(db, "Encanador")
    p = criar_prestador(db, "Ana", "11900000001", [cat], email="ana@x.com", cpf_cnpj=CPF_VALIDO)

    detalhe = client.get(f"/api/prestadores/{p.id}").json()
    lista = client.get("/api/prestadores").json()
    for dados in (detalhe, lista[0]):
        assert "email" not in dados
        assert "cpf_cnpj" not in dados


def test_rota_publica_esconde_pendentes_e_inativos(client, db):
    cat = criar_categoria(db, "Encanador")
    pend = criar_prestador(db, "Pendente", "11900000001", [cat], status="pendente")
    criar_prestador(db, "Inativo", "11900000002", [cat], status="inativo")

    assert client.get("/api/prestadores").json() == []
    assert client.get(f"/api/prestadores/{pend.id}").status_code == 404
    # parâmetro antigo não deve mais liberar outros status
    assert client.get("/api/prestadores?status_filter=pendente").json() == []


def test_lista_admin_exige_token_e_mostra_tudo(client, db, admin_headers):
    cat = criar_categoria(db, "Encanador")
    criar_prestador(db, "Ana", "11900000001", [cat], status="pendente", cpf_cnpj=CPF_VALIDO)

    assert client.get("/api/prestadores/admin/lista").status_code == 401
    lista = client.get("/api/prestadores/admin/lista", headers=admin_headers).json()
    assert lista[0]["cpf_cnpj"] == CPF_VALIDO


# ---------- Cadastro e aprovação ----------

def test_cadastro_entra_pendente_e_so_aparece_apos_aprovacao(client, db, admin_headers):
    cat = criar_categoria(db, "Encanador")
    resp = client.post("/api/prestadores", json={
        "nome": "Novo", "whatsapp": "(11) 98765-4321", "categoria_ids": [cat.id],
    })
    assert resp.status_code == 201
    assert resp.json()["status"] == "pendente"
    novo_id = resp.json()["id"]
    assert db.get(Prestador, novo_id).whatsapp == "11987654321"  # salvo só com dígitos

    busca = client.post("/api/chat/buscar", json={"pergunta": "encanador"}).json()
    assert busca["total_resultados"] == 0

    assert client.patch(f"/api/prestadores/{novo_id}/ativar", headers=admin_headers).status_code == 200
    busca = client.post("/api/chat/buscar", json={"pergunta": "encanador"}).json()
    assert busca["total_resultados"] == 1


def test_cadastro_publico_nao_pode_se_autoaprovar(client, db):
    cat = criar_categoria(db, "Encanador")
    resp = client.post("/api/prestadores", json={
        "nome": "Esperto", "whatsapp": "11987654321", "categoria_ids": [cat.id],
        "status": "ativo", "premium": True, "verificado_hurbem": True,
    })
    p = db.get(Prestador, resp.json()["id"])
    assert p.status == "pendente"
    assert not p.premium
    assert not p.verificado_hurbem


def test_cadastro_whatsapp_duplicado_retorna_mensagem_clara(client, db):
    cat = criar_categoria(db, "Encanador")
    criar_prestador(db, "Ana", "11987654321", [cat])
    resp = client.post("/api/prestadores", json={
        "nome": "Outra", "whatsapp": "(11) 98765-4321", "categoria_ids": [cat.id],
    })
    assert resp.status_code == 400
    assert resp.json()["detail"] == "WhatsApp já cadastrado"


# ---------- Atualização ----------

def test_put_permite_apagar_campos_opcionais(client, db, admin_headers):
    cat = criar_categoria(db, "Encanador")
    p = criar_prestador(db, "Ana", "11900000001", [cat], instagram="https://www.instagram.com/ana/")

    resp = client.put(f"/api/prestadores/{p.id}", json={"instagram": None, "nome": None},
                      headers=admin_headers)
    assert resp.status_code == 200
    db.refresh(p)
    assert p.instagram is None
    assert p.nome == "Ana"  # campo obrigatório não é apagado


def test_put_rejeita_status_invalido(client, db, admin_headers):
    cat = criar_categoria(db, "Encanador")
    p = criar_prestador(db, "Ana", "11900000001", [cat])
    resp = client.put(f"/api/prestadores/{p.id}", json={"status": "qualquer"}, headers=admin_headers)
    assert resp.status_code == 422
