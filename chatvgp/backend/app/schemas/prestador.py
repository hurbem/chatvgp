from typing import List, Literal, Optional

from pydantic import BaseModel, validator

from app.utils.validators import validar_cpf_cnpj

StatusPrestador = Literal["ativo", "inativo", "pendente"]


def _validar_cpf_cnpj_opcional(v: Optional[str]) -> Optional[str]:
    if v is None or v.strip() == "":
        return None
    if not validar_cpf_cnpj(v):
        raise ValueError("CPF/CNPJ inválido")
    return v


class PrestadorCreate(BaseModel):
    """Cadastro público. Status, premium e verificado são definidos pelo admin."""
    nome: str
    email: Optional[str] = None
    whatsapp: str
    cpf_cnpj: Optional[str] = None
    categoria_ids: List[int]  # de 1 a 3 categorias
    descricao: Optional[str] = None
    instagram: Optional[str] = None
    site: Optional[str] = None
    notas: Optional[str] = None

    _cpf_cnpj = validator("cpf_cnpj", allow_reuse=True)(_validar_cpf_cnpj_opcional)


class PrestadorUpdate(BaseModel):
    """Atualização pelo admin. Só os campos enviados são alterados."""
    nome: Optional[str] = None
    email: Optional[str] = None
    whatsapp: Optional[str] = None
    cpf_cnpj: Optional[str] = None
    descricao: Optional[str] = None
    instagram: Optional[str] = None
    site: Optional[str] = None
    status: Optional[StatusPrestador] = None
    notas: Optional[str] = None
    verificado_hurbem: Optional[bool] = None
    premium: Optional[bool] = None

    _cpf_cnpj = validator("cpf_cnpj", allow_reuse=True)(_validar_cpf_cnpj_opcional)
