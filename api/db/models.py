from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any, Union

class FarmerCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    location: str

class FarmerLogin(BaseModel):
    email: EmailStr
    password: str

class ChatStartRequest(BaseModel):
    farmer_id: Union[int, str]

class ChatMessageRequest(BaseModel):
    farmer_id: Union[int, str]
    chat_session_id: Union[int, str]
    message: str

class ChatChoiceRequest(BaseModel):
    farmer_id: Union[int, str]
    chat_session_id: Union[int, str]
    message_id: str
    selected_option: str
