from datetime import datetime
from pydantic import BaseModel, ConfigDict


class AssetBase(BaseModel):
    asset_code: str
    name: str
    asset_type: str
    description: str | None = None
    serial_number: str | None = None
    status: str = "active"
    location: str | None = None
    owner: str | None = None
    purchase_date: datetime | None = None
    purchase_value: float | None = None
    current_value: float | None = None
    asset_metadata: dict | None = None


class AssetCreate(AssetBase):
    pass


class AssetUpdate(BaseModel):
    asset_code: str | None = None
    name: str | None = None
    asset_type: str | None = None
    description: str | None = None
    serial_number: str | None = None
    status: str | None = None
    location: str | None = None
    owner: str | None = None
    purchase_date: datetime | None = None
    purchase_value: float | None = None
    current_value: float | None = None
    asset_metadata: dict | None = None


class AssetResponse(AssetBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class AssetListResponse(BaseModel):
    assets: list[AssetResponse]
    total: int
