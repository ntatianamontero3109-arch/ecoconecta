from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from typing import Literal

class Register(BaseModel):
    name: str = Field(min_length=3, max_length=120)
    email: str = Field(min_length=5, max_length=200)
    password: str = Field(min_length=8, max_length=100)
    phone: str = Field(min_length=7, max_length=32)
    @field_validator('email')
    @classmethod
    def lower_email(cls, v): return v.strip().lower()

class Login(BaseModel):
    email: str
    password: str

class NewRequest(BaseModel):
    waste_type: Literal['organico','reciclable']
    generator_type: Literal['hogar','unidad_productiva']
    address: str = Field(min_length=6, max_length=240)
    contact: str = Field(min_length=7, max_length=100)
    preferred_schedule: str = Field(min_length=4, max_length=120)
    notes: str = Field(default='', max_length=1000)

class Assign(BaseModel):
    collector_id: int

class Schedule(BaseModel):
    scheduled_at: datetime

class Complete(BaseModel):
    material_kg: float = Field(gt=0, le=10000)

class PointUpdate(BaseModel):
    points_per_kg: int = Field(ge=0, le=10000)

class ArticleInput(BaseModel):
    title: str = Field(min_length=5, max_length=180)
    category: str = Field(min_length=3, max_length=60)
    body: str = Field(min_length=10, max_length=5000)
    published: bool = True
