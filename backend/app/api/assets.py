from datetime import datetime
from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.models.asset import Asset
from backend.app.schemas.asset import (
    AssetCreate,
    AssetResponse,
    AssetUpdate,
    AssetListResponse,
)
from backend.app.services.audit_service import (
    serialize_asset,
    write_audit,
)

router = APIRouter()


@router.post(
    "",
    response_model=AssetResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_asset(
    asset_data: AssetCreate,
    db: Session = Depends(get_db),
):

    existing = (
        db.query(Asset)
        .filter(
            Asset.asset_code ==
            asset_data.asset_code
        )
        .first()
    )

    if existing:

        raise HTTPException(
            status_code=409,
            detail="Asset code already exists."
        )


    if asset_data.serial_number:

        existing_serial = (
            db.query(Asset)
            .filter(
                Asset.serial_number ==
                asset_data.serial_number
            )
            .first()
        )

        if existing_serial:

            raise HTTPException(
                status_code=409,
                detail="Serial number already exists."
            )


    asset = Asset(
        **asset_data.model_dump()
    )

    db.add(asset)

    db.flush()

    write_audit(
        db=db,
        action="CREATE",
        asset=asset,
        new_data=serialize_asset(asset),
        description="Asset created.",
    )

    db.commit()

    db.refresh(asset)

    return asset


@router.get(
    "",
    response_model=AssetListResponse,
)
def list_assets(
    search: Optional[str] = Query(None),
    asset_status: Optional[str] = Query(None),
    asset_type: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    owner: Optional[str] = Query(None),
    min_value: Optional[float] = Query(None),
    max_value: Optional[float] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):

    query = db.query(Asset)


    if search:

        search_value = f"%{search.lower()}%"

        query = query.filter(
            or_(
                func.lower(Asset.asset_code).like(search_value),
                func.lower(Asset.name).like(search_value),
                func.lower(Asset.asset_type).like(search_value),
                func.lower(Asset.serial_number).like(search_value),
                func.lower(Asset.location).like(search_value),
                func.lower(Asset.owner).like(search_value),
                func.lower(Asset.description).like(search_value),
            )
        )


    if asset_status:

        query = query.filter(
            func.lower(Asset.status)
            == asset_status.lower()
        )


    if asset_type:

        query = query.filter(
            func.lower(Asset.asset_type)
            == asset_type.lower()
        )


    if location:

        query = query.filter(
            func.lower(Asset.location)
            == location.lower()
        )


    if owner:

        query = query.filter(
            func.lower(Asset.owner)
            == owner.lower()
        )


    if min_value is not None:

        query = query.filter(
            Asset.current_value >= min_value
        )


    if max_value is not None:

        query = query.filter(
            Asset.current_value <= max_value
        )


    total = query.count()


    assets = (
        query
        .order_by(Asset.id.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )


    return {
        "assets": assets,
        "total": total,
    }


@router.get(
    "/{asset_id}",
    response_model=AssetResponse,
)
def get_asset(
    asset_id: int,
    db: Session = Depends(get_db),
):

    asset = (
        db.query(Asset)
        .filter(Asset.id == asset_id)
        .first()
    )

    if not asset:

        raise HTTPException(
            status_code=404,
            detail="Asset not found."
        )

    return asset


@router.put(
    "/{asset_id}",
    response_model=AssetResponse,
)
def update_asset(
    asset_id: int,
    asset_data: AssetUpdate,
    db: Session = Depends(get_db),
):

    asset = (
        db.query(Asset)
        .filter(Asset.id == asset_id)
        .first()
    )

    if not asset:

        raise HTTPException(
            status_code=404,
            detail="Asset not found."
        )


    old_data = serialize_asset(asset)


    update_data = asset_data.model_dump(exclude_unset=True)


    if "asset_code" in update_data:

        duplicate = (
            db.query(Asset)
            .filter(
                Asset.asset_code ==
                update_data["asset_code"],
                Asset.id != asset_id
            )
            .first()
        )

        if duplicate:

            raise HTTPException(
                status_code=409,
                detail="Asset code already exists."
            )


    if "serial_number" in update_data:

        serial = update_data["serial_number"]

        if serial:

            duplicate = (
                db.query(Asset)
                .filter(
                    Asset.serial_number == serial,
                    Asset.id != asset_id
                )
                .first()
            )

            if duplicate:

                raise HTTPException(
                    status_code=409,
                    detail="Serial number already exists."
                )


    for field, value in update_data.items():

        setattr(
            asset,
            field,
            value
        )


    db.flush()


    write_audit(
        db=db,
        action="UPDATE",
        asset=asset,
        old_data=old_data,
        new_data=serialize_asset(asset),
        description="Asset updated.",
    )


    db.commit()

    db.refresh(asset)

    return asset


@router.delete(
    "/{asset_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_asset(
    asset_id: int,
    db: Session = Depends(get_db),
):

    asset = (
        db.query(Asset)
        .filter(Asset.id == asset_id)
        .first()
    )

    if not asset:

        raise HTTPException(
            status_code=404,
            detail="Asset not found."
        )


    old_data = serialize_asset(asset)


    write_audit(
        db=db,
        action="DELETE",
        asset=asset,
        old_data=old_data,
        description="Asset deleted.",
    )


    db.delete(asset)

    db.commit()

    return None


@router.get(
    "/search/advanced",
    response_model=AssetListResponse,
)
def advanced_search(
    q: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
):

    value = f"%{q.lower()}%"


    assets = (
        db.query(Asset)
        .filter(
            or_(
                func.lower(Asset.asset_code).like(value),
                func.lower(Asset.name).like(value),
                func.lower(Asset.asset_type).like(value),
                func.lower(Asset.serial_number).like(value),
                func.lower(Asset.location).like(value),
                func.lower(Asset.owner).like(value),
            )
        )
        .order_by(Asset.id.asc())
        .all()
    )


    return {
        "assets": assets,
        "total": len(assets),
    }


@router.get(
    "/statistics/summary"
)
def asset_statistics(
    db: Session = Depends(get_db),
):

    total = db.query(
        func.count(Asset.id)
    ).scalar() or 0


    active = db.query(
        func.count(Asset.id)
    ).filter(
        func.lower(Asset.status) == "active"
    ).scalar() or 0


    maintenance = db.query(
        func.count(Asset.id)
    ).filter(
        func.lower(Asset.status) == "maintenance"
    ).scalar() or 0


    locations = db.query(
        func.count(
            func.distinct(Asset.location)
        )
    ).scalar() or 0


    owners = db.query(
        func.count(
            func.distinct(Asset.owner)
        )
    ).scalar() or 0


    purchase_value = db.query(
        func.coalesce(
            func.sum(Asset.purchase_value),
            0
        )
    ).scalar()


    current_value = db.query(
        func.coalesce(
            func.sum(Asset.current_value),
            0
        )
    ).scalar()


    return {

        "total_assets": total,

        "active_assets": active,

        "maintenance_assets": maintenance,

        "unique_locations": locations,

        "unique_owners": owners,

        "total_purchase_value":
            float(purchase_value or 0),

        "total_current_value":
            float(current_value or 0),

        "total_value_change":
            float(
                (current_value or 0)
                -
                (purchase_value or 0)
            ),

    }

