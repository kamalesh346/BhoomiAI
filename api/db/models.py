from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, field_validator


def _validate_email(value: str) -> str:
    email = value.strip()
    if "@" not in email or email.startswith("@") or email.endswith("@"):
        raise ValueError("Invalid email address")
    local_part, domain = email.rsplit("@", 1)
    if not local_part or "." not in domain:
        raise ValueError("Invalid email address")
    return email


class FarmerCreate(BaseModel):
    name: str
    email: str
    password: str
    location: str
    land_size: float = 1.0

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        return _validate_email(value)


class FarmerLogin(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        return _validate_email(value)


class FarmerProfileUpdate(BaseModel):
    name: Optional[str] = None
    land_size: Optional[float] = None
    water_source: Optional[str] = None
    budget: Optional[int] = None
    risk_level: Optional[str] = None
    equipment: Optional[List[str]] = None
    location: Optional[str] = None
    soil_type: Optional[str] = None
    soil_type_distribution: Optional[List[Dict[str, Any]]] = None
    recent_pest_activity: Optional[str] = None
    npk_n: Optional[float] = None
    npk_p: Optional[float] = None
    npk_k: Optional[float] = None
    soil_ph: Optional[float] = None
    language_preference: Optional[str] = None


class PestHistoryCreate(BaseModel):
    pest_name: str
    affected_crop: str
    severity: str
    observation_date: str
    description: Optional[str] = ""


class ChatStartRequest(BaseModel):
    farmer_id: Union[int, str]
    language: Optional[str] = "en"


class ChatMessageRequest(BaseModel):
    farmer_id: Union[int, str]
    chat_session_id: Union[int, str]
    message: str
    language: Optional[str] = "en"


class ChatChoiceRequest(BaseModel):
    farmer_id: Union[int, str]
    chat_session_id: Union[int, str]
    message_id: str
    selected_option: str
    language: Optional[str] = "en"
