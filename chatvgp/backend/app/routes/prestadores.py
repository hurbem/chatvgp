from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Prestador, PrestadorCategoria, Categoria
from app.schemas.prestador import (
    PrestadorCreate,
    PrestadorUpdate,
    PrestadorResponse,
)
from app.utils.security import get_current_admin

router = APIRouter(prefix="/api/prestadores", tags=["prestadores"])

@router.get("")
def listar_prestadores(
    status_filter: str = "ativo",
    db: Session = Depends(get_db),
):
    """
    Listar prestadores com scores calculados.
    Público (sem autenticação).
    """
    query = db.query(Prestador)

    if status_filter:
        query = query.filter(Prestador.status == status_filter)

    prestadores = query.all()

    result = []
    for p in prestadores:
        result.append({
            "id": p.id,
            "nome": p.nome,
            "whatsapp": p.whatsapp,
            "instagram": p.instagram,
            "site": p.site,
            "status": p.status,
            "notas": p.notas,
            "criado_em": p.criado_em.isoformat() if p.criado_em else None,
            "categorias": [{"id": c.id, "nome": c.nome} for c in p.categorias],
        })

    return result

@router.get("/{prestador_id}")
def obter_prestador(prestador_id: int, db: Session = Depends(get_db)):
    """
    Obter detalhes de um prestador com score.
    Público.
    """
    prestador = db.query(Prestador).filter(Prestador.id == prestador_id).first()

    if not prestador:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prestador não encontrado",
        )

    return {
        "id": prestador.id,
        "nome": prestador.nome,
        "email": prestador.email,
        "whatsapp": prestador.whatsapp,
        "cpf_cnpj": prestador.cpf_cnpj,
        "descricao": prestador.descricao,
        "instagram": prestador.instagram,
        "site": prestador.site,
        "status": prestador.status,
        "notas": prestador.notas,
        "criado_em": prestador.criado_em.isoformat() if prestador.criado_em else None,
        "atualizado_em": prestador.atualizado_em.isoformat() if prestador.atualizado_em else None,
        "verificado_hurbem": prestador.verificado_hurbem,
        "premium": prestador.premium,
        "categorias": [{"id": c.id, "nome": c.nome} for c in prestador.categorias],
    }

@router.post("", status_code=status.HTTP_201_CREATED)
def criar_prestador(
    prestador: PrestadorCreate,
    db: Session = Depends(get_db),
):
    """
    Criar novo prestador com até 3 categorias.
    Público (sem autenticação para MVP/testes).
    """
    # Validar categoria_ids
    categoria_ids = prestador.categoria_ids
    if not categoria_ids or len(categoria_ids) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Selecione pelo menos 1 categoria",
        )

    if len(categoria_ids) > 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Máximo 3 categorias por prestador",
        )

    # Validar se categorias existem
    for cat_id in categoria_ids:
        cat = db.query(Categoria).filter(Categoria.id == cat_id).first()
        if not cat:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Categoria {cat_id} não existe",
            )

    # Validar se já existe com mesmo email ou whatsapp
    if prestador.email:
        existing_email = db.query(Prestador).filter(Prestador.email == prestador.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já cadastrado",
            )

    existing_whatsapp = db.query(Prestador).filter(Prestador.whatsapp == prestador.whatsapp).first()
    if existing_whatsapp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="WhatsApp já cadastrado",
        )

    # Criar prestador com status 'ativo' por padrão
    prestador_data = prestador.dict(exclude={"categoria_ids"})
    prestador_data['status'] = 'ativo'
    novo_prestador = Prestador(**prestador_data)
    db.add(novo_prestador)
    db.flush()  # Flush para obter o ID

    # Adicionar categorias
    for cat_id in categoria_ids:
        pc = PrestadorCategoria(prestador_id=novo_prestador.id, categoria_id=cat_id)
        db.add(pc)

    db.commit()
    db.refresh(novo_prestador)

    return {
        "id": novo_prestador.id,
        "nome": novo_prestador.nome,
        "whatsapp": novo_prestador.whatsapp,
        "email": novo_prestador.email,
        "cpf_cnpj": novo_prestador.cpf_cnpj,
        "status": novo_prestador.status,
        "categorias": [{"id": c.id, "nome": c.nome} for c in novo_prestador.categorias],
        "criado_em": novo_prestador.criado_em.isoformat() if novo_prestador.criado_em else None,
    }

@router.put("/{prestador_id}")
def atualizar_prestador(
    prestador_id: int,
    prestador_update: PrestadorUpdate,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    """
    Atualizar prestador existente.
    Admin only (requer token).
    """
    prestador = db.query(Prestador).filter(Prestador.id == prestador_id).first()

    if not prestador:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prestador não encontrado",
        )

    # Atualizar apenas campos não-None
    dados_atualizacao = prestador_update.dict(exclude_unset=True)
    for campo, valor in dados_atualizacao.items():
        if valor is not None:
            setattr(prestador, campo, valor)

    db.commit()
    db.refresh(prestador)

    return {
        "id": prestador.id,
        "nome": prestador.nome,
        "whatsapp": prestador.whatsapp,
        "status": prestador.status,
        "notas": prestador.notas,
        "criado_em": prestador.criado_em.isoformat() if prestador.criado_em else None,
    }

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
    prestador = db.query(Prestador).filter(Prestador.id == prestador_id).first()

    if not prestador:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prestador não encontrado",
        )

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
    Ativar um prestador (mudar status de 'inativo' para 'ativo').
    Admin only (requer token).
    """
    prestador = db.query(Prestador).filter(Prestador.id == prestador_id).first()

    if not prestador:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prestador não encontrado",
        )

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
