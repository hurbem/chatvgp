from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models import Prestador, PrestadorCategoria, Categoria, Log
from app.schemas.prestador import (
    PrestadorCreate,
    PrestadorUpdate,
    StatusPrestador,
)
from app.utils.security import get_current_admin
from app.utils.validators import normalizar_instagram, normalizar_site

router = APIRouter(prefix="/api/prestadores", tags=["prestadores"])

# Campos que o admin pode apagar (enviar null) no PUT
CAMPOS_LIMPAVEIS = {"email", "cpf_cnpj", "descricao", "instagram", "site", "notas"}


def _apenas_digitos(valor: str) -> str:
    return "".join(filter(str.isdigit, valor or ""))


def _serializar_publico(p: Prestador) -> dict:
    """Dados seguros para exibir publicamente (sem email, CPF/CNPJ ou notas internas de status)."""
    return {
        "id": p.id,
        "nome": p.nome,
        "whatsapp": p.whatsapp,
        "descricao": p.descricao,
        "instagram": p.instagram,
        "site": p.site,
        "notas": p.notas,
        "verificado_hurbem": p.verificado_hurbem,
        "premium": p.premium,
        "categorias": [{"id": c.id, "nome": c.nome} for c in p.categorias],
    }


def _serializar_admin(p: Prestador) -> dict:
    """Todos os dados, apenas para o admin."""
    dados = _serializar_publico(p)
    dados.update({
        "email": p.email,
        "cpf_cnpj": p.cpf_cnpj,
        "status": p.status,
        "criado_em": p.criado_em.isoformat() if p.criado_em else None,
        "atualizado_em": p.atualizado_em.isoformat() if p.atualizado_em else None,
    })
    return dados


def _obter_ou_404(db: Session, prestador_id: int) -> Prestador:
    prestador = db.query(Prestador).filter(Prestador.id == prestador_id).first()
    if not prestador:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prestador não encontrado",
        )
    return prestador


@router.get("")
def listar_prestadores(db: Session = Depends(get_db)):
    """
    Listar prestadores ATIVOS.
    Público (sem autenticação) - não expõe email nem CPF/CNPJ.
    """
    prestadores = (
        db.query(Prestador)
        .filter(Prestador.status == "ativo")
        .order_by(Prestador.nome)
        .all()
    )
    return [_serializar_publico(p) for p in prestadores]


@router.get("/admin/lista")
def listar_prestadores_admin(
    status_filter: Optional[StatusPrestador] = "pendente",
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    """
    Listar prestadores com todos os dados, filtrando por status
    (padrão: 'pendente', ou seja, cadastros aguardando aprovação).
    Admin only (requer token).
    """
    query = db.query(Prestador)
    if status_filter:
        query = query.filter(Prestador.status == status_filter)
    prestadores = query.order_by(Prestador.criado_em.desc()).all()
    return [_serializar_admin(p) for p in prestadores]


@router.get("/admin/{prestador_id}")
def obter_prestador_admin(
    prestador_id: int,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    """Detalhes completos de um prestador (qualquer status). Admin only."""
    return _serializar_admin(_obter_ou_404(db, prestador_id))


@router.get("/{prestador_id}")
def obter_prestador(prestador_id: int, db: Session = Depends(get_db)):
    """
    Obter detalhes públicos de um prestador ativo.
    Público - não expõe email nem CPF/CNPJ.
    """
    prestador = _obter_ou_404(db, prestador_id)
    if prestador.status != "ativo":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prestador não encontrado",
        )
    return _serializar_publico(prestador)


@router.post("", status_code=status.HTTP_201_CREATED)
def criar_prestador(
    prestador: PrestadorCreate,
    db: Session = Depends(get_db),
):
    """
    Cadastrar novo prestador com até 3 categorias.
    Público. O cadastro entra como 'pendente' e só aparece na busca
    depois de aprovado pelo admin (PATCH /{id}/ativar).
    """
    categoria_ids = list(dict.fromkeys(prestador.categoria_ids or []))  # remove duplicados
    if not categoria_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Selecione pelo menos 1 categoria",
        )

    if len(categoria_ids) > 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Máximo 3 categorias por prestador",
        )

    encontradas = db.query(Categoria.id).filter(Categoria.id.in_(categoria_ids)).all()
    faltando = set(categoria_ids) - {c.id for c in encontradas}
    if faltando:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Categoria {sorted(faltando)[0]} não existe",
        )

    whatsapp = _apenas_digitos(prestador.whatsapp)
    if len(whatsapp) not in (10, 11):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="WhatsApp deve ter DDD + número (10 ou 11 dígitos)",
        )

    if prestador.email:
        if db.query(Prestador).filter(Prestador.email == prestador.email).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já cadastrado",
            )

    if db.query(Prestador).filter(Prestador.whatsapp == whatsapp).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="WhatsApp já cadastrado",
        )

    prestador_data = prestador.dict(exclude={"categoria_ids"})
    prestador_data["whatsapp"] = whatsapp
    prestador_data["status"] = "pendente"
    prestador_data["instagram"] = normalizar_instagram(prestador_data.get("instagram"))
    prestador_data["site"] = normalizar_site(prestador_data.get("site"))
    novo_prestador = Prestador(**prestador_data)

    try:
        db.add(novo_prestador)
        db.flush()  # Flush para obter o ID
        for cat_id in categoria_ids:
            db.add(PrestadorCategoria(prestador_id=novo_prestador.id, categoria_id=cat_id))
        db.commit()
    except IntegrityError:
        # Corrida: outro cadastro com o mesmo email/whatsapp/CPF entrou ao mesmo tempo
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Prestador já cadastrado (email, WhatsApp ou CPF/CNPJ repetido)",
        )

    db.refresh(novo_prestador)

    return {
        "id": novo_prestador.id,
        "nome": novo_prestador.nome,
        "status": novo_prestador.status,
        "categorias": [{"id": c.id, "nome": c.nome} for c in novo_prestador.categorias],
        "mensagem": "Cadastro recebido! Ele aparecerá na busca após aprovação.",
    }


@router.put("/{prestador_id}")
def atualizar_prestador(
    prestador_id: int,
    prestador_update: PrestadorUpdate,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    """
    Atualizar prestador existente. Apenas os campos enviados são alterados.
    Para apagar um campo opcional (email, cpf_cnpj, descricao, instagram,
    site, notas), envie null.
    Admin only (requer token).
    """
    prestador = _obter_ou_404(db, prestador_id)

    dados_atualizacao = prestador_update.dict(exclude_unset=True)
    if "instagram" in dados_atualizacao:
        dados_atualizacao["instagram"] = normalizar_instagram(dados_atualizacao["instagram"])
    if "site" in dados_atualizacao:
        dados_atualizacao["site"] = normalizar_site(dados_atualizacao["site"])
    if dados_atualizacao.get("whatsapp"):
        dados_atualizacao["whatsapp"] = _apenas_digitos(dados_atualizacao["whatsapp"])

    for campo, valor in dados_atualizacao.items():
        if valor is None and campo not in CAMPOS_LIMPAVEIS:
            continue  # nome, whatsapp, status etc. não podem ficar vazios
        setattr(prestador, campo, valor)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email, WhatsApp ou CPF/CNPJ já usado por outro prestador",
        )
    db.refresh(prestador)

    return _serializar_admin(prestador)


@router.delete("/{prestador_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_prestador(
    prestador_id: int,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    """
    Deletar prestador.
    Admin only (requer token).
    """
    prestador = _obter_ou_404(db, prestador_id)
    db.delete(prestador)
    db.commit()
    return None


@router.patch("/{prestador_id}/ativar", status_code=status.HTTP_200_OK)
def ativar_prestador(
    prestador_id: int,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    """
    Ativar (aprovar) um prestador pendente ou inativo.
    Admin only (requer token).
    """
    prestador = _obter_ou_404(db, prestador_id)

    if prestador.status == "ativo":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Prestador já está ativo",
        )

    prestador.status = "ativo"
    db.commit()
    db.refresh(prestador)

    return {
        "id": prestador.id,
        "nome": prestador.nome,
        "status": prestador.status,
        "mensagem": f"✅ Prestador '{prestador.nome}' ativado com sucesso!",
    }


@router.post("/{prestador_id}/clique-whatsapp", status_code=status.HTTP_204_NO_CONTENT)
def registrar_clique_whatsapp(
    prestador_id: int,
    db: Session = Depends(get_db),
):
    """
    Registra (na tabela logs) um clique no botão de WhatsApp de um prestador.
    Público (sem autenticação) - chamado pelo frontend ao abrir o link.
    """
    prestador = _obter_ou_404(db, prestador_id)

    novo_log = Log(
        tipo="CLIQUE_WHATSAPP",
        pergunta=prestador.nome,
        categoria_encontrada=str(prestador.id),
    )
    db.add(novo_log)
    db.commit()

    return None
