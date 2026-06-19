from pydantic import BaseModel


class DepartamentoBase(BaseModel):
    nombre: str
    pais: str = "El Salvador"


class DepartamentoCreate(DepartamentoBase):
    pass


class DepartamentoOut(DepartamentoBase):
    id: int

    model_config = {"from_attributes": True}
