from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Prestador, PrestadorCategoria, Categoria
from app.schemas.prestador import (
    PrestadorCreate,
    PrestadorUpdate,
    PrestadorResponse,
    PrestadorComScore,
)
from app.services.ranking_service import calcular_stats_prestador
from app.utils.security import verify_token

router = APIRouter(prefix="/api/prestadores", tags=["prestadores"])

def verificar_admin(authorization: str = None) -> bool:
    """
    Middleware simples: valida se tem token válido.
    Para MVP, aceita qualquer token não-vazio.
    Em produção: usar JWT properly.
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticação necessário",
        )
    return True

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
        # Calcular score agregado de todos os feedbacks
        # Se condominio_id foi filtrado, usa esse; senão calcula agregado
        from app.models import Feedback

        if condominio_id:
            # Se foi especificado um condomínio, calcula score para ele
            stats = calcular_stats_prestador(db, p.id, condominio_id)
        else:
            # Senão, usa agregado de todos os feedbacks
            feedbacks = db.query(Feedback).filter(Feedback.prestador_id == p.id).all()
            if feedbacks:
                # Calcula agregado simples
                total = len(feedbacks)
                qualidade_media = sum(f.qualidade for f in feedbacks) / total if feedbacks else 0
                material_acertou = sum(1 for f in feedbacks if f.material_estimativa == "Acertou") / total if feedbacks else 0
                prazo_cumprido = sum(1 for f in feedbacks if f.prazo_manteve) / total if feedbacks else 0
                custo_mantido = sum(1 for f in feedbacks if f.custo_manteve) / total if feedbacks else 0

                score_final = (material_acertou * 2) + (prazo_cumprido * 1.5) + (custo_mantido * 1.5) + qualidade_media

                class Stats:
                    pass
                stats = Stats()
                stats.score_final = round(score_final, 2)
                stats.total_feedbacks = total
                stats.qualidade_media = round(qualidade_media, 1)
                stats.material_acertou_pct = round(material_acertou, 2)
                stats.prazo_cumprido_pct = round(prazo_cumprido, 2)
                stats.custo_mantido_pct = round(custo_mantido, 2)
            else:
                stats = None

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
            "score_final": stats.score_final if stats else 0,
            "feedback_count": stats.total_feedbacks if stats else 0,
            "qualidade_media": stats.qualidade_media if stats else None,
            "material_acertou_pct": stats.material_acertou_pct if stats else None,
            "prazo_cumprido_pct": stats.prazo_cumprido_pct if stats else None,
            "custo_mantido_pct": stats.custo_mantido_pct if stats else None,
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

    from app.models import Feedback

    # Calcular score agregado
    feedbacks = db.query(Feedback).filter(Feedback.prestador_id == prestador.id).all()
    if feedbacks:
        total = len(feedbacks)
        qualidade_media = sum(f.qualidade for f in feedbacks) / total
        material_acertou = sum(1 for f in feedbacks if f.material_estimativa == "Acertou") / total
        prazo_cumprido = sum(1 for f in feedbacks if f.prazo_manteve) / total
        custo_mantido = sum(1 for f in feedbacks if f.custo_manteve) / total

        score_final = (material_acertou * 2) + (prazo_cumprido * 1.5) + (custo_mantido * 1.5) + qualidade_media

        class Stats:
            pass
        stats = Stats()
        stats.score_final = round(score_final, 2)
        stats.total_feedbacks = total
        stats.qualidade_media = round(qualidade_media, 1)
        stats.material_acertou_pct = round(material_acertou, 2)
        stats.prazo_cumprido_pct = round(prazo_cumprido, 2)
        stats.custo_mantido_pct = round(custo_mantido, 2)
    else:
        stats = None

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
        "score_final": stats.score_final if stats else 0,
        "feedback_count": stats.total_feedbacks if stats else 0,
        "qualidade_media": stats.qualidade_media if stats else None,
        "material_acertou_pct": stats.material_acertou_pct if stats else None,
        "prazo_cumprido_pct": stats.prazo_cumprido_pct if stats else None,
        "custo_mantido_pct": stats.custo_mantido_pct if stats else None,
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
    authorization: str = Header(None),
):
    """
    Atualizar prestador existente.
    Admin only (requer token).
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticação necessário",
        )

    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Scheme inválido. Use: Authorization: Bearer <token>",
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Formato de Authorization inválido",
        )

    from app.utils.security import verify_token
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
        )

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
    authorization: str = Header(None),
):
    """
    Deletar prestador.
    Admin only (requer token).
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticação necessário",
        )

    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Scheme inválido. Use: Authorization: Bearer <token>",
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Formato de Authorization inválido",
        )

    from app.utils.security import verify_token
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
        )

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
):
    """
    Ativar um prestador (mudar status de 'inativo' para 'ativo').
    Público - sem autenticação para facilitar aprovação.
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
