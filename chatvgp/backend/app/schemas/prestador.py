from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime
from app.utils.validators import validar_cpf_cnpj

class CategoriaBase(BaseModel):
    id: int
    nome: str

class PrestadorBase(BaseModel):
    nome: str
    email: Optional[str] = None
    whatsapp: str
    cpf_cnpj: Optional[str] = None
    categoria_ids: List[int]  # Nova: lista de até 3 categorias
    descricao: Optional[str] = None
    instagram: Optional[str] = None
    site: Optional[str] = None
    status: str = "ativo"
    notas: Optional[str] = None

    @validator("cpf_cnpj")
    def validar_cpf_cnpj_campo(cls, v):
        if v is None or v.strip() == "":
            return None
        if not validar_cpf_cnpj(v):
            raise ValueError("CPF/CNPJ inválido")
        return v

class PrestadorCreate(PrestadorBase):
    pass

class PrestadorUpdate(BaseModel):
    nome: Optional[str] = None
    whatsapp: Optional[str] = None
    cpf_cnpj: Optional[str] = None
    descricao: Optional[str] = None
    instagram: Optional[str] = None
    site: Optional[str] = None
    status: Optional[str] = None
    notas: Optional[str] = None

    @validator("cpf_cnpj")
    def validar_cpf_cnpj_campo(cls, v):
        if v is None or v.strip() == "":
            return None
        if not validar_cpf_cnpj(v):
            raise ValueError("CPF/CNPJ inválido")
        return v

class PrestadorResponse(BaseModel):
    id: int
    nome: str
    email: Optional[str] = None
    whatsapp: str
    cpf_cnpj: Optional[str] = None
    descricao: Optional[str] = None
    instagram: Optional[str] = None
    site: Optional[str] = None
    status: str
    notas: Optional[str] = None
    criado_em: datetime
    atualizado_em: datetime
    verificado_hurbem: bool = False
    premium: bool = False
    categorias: List[CategoriaBase] = []
