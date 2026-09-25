import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.models.asset import Asset

DATABASE_URL = "postgresql+psycopg://atul:atul_dev_password@127.0.0.1:5433/atul"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

assets = [
    {
        "asset_code": "ATUL-LAP-001",
        "name": "Executive Laptop",
        "asset_type": "IT Equipment",
        "description": "Primary executive workstation",
        "serial_number": "ATUL-LAP-SN-001",
        "status": "active",
        "location": "Head Office",
        "owner": "ATUL Operations",
        "purchase_value": 125000,
        "current_value": 90000,
    },
    {
        "asset_code": "ATUL-SRV-001",
        "name": "Primary Application Server",
        "asset_type": "Server",
        "description": "Main application server for ATUL platform",
        "serial_number": "ATUL-SRV-SN-001",
        "status": "active",
        "location": "Data Center",
        "owner": "IT Infrastructure",
        "purchase_value": 450000,
        "current_value": 360000,
    },
    {
        "asset_code": "ATUL-NET-001",
        "name": "Core Network Router",
        "asset_type": "Network Equipment",
        "description": "Core network routing device",
        "serial_number": "ATUL-NET-SN-001",
        "status": "active",
        "location": "Network Room",
        "owner": "Network Operations",
        "purchase_value": 175000,
        "current_value": 120000,
    },
    {
        "asset_code": "ATUL-MOB-001",
        "name": "Field Operations Tablet",
        "asset_type": "Mobile Equipment",
        "description": "Tablet used for field asset operations",
        "serial_number": "ATUL-MOB-SN-001",
        "status": "maintenance",
        "location": "Field Operations",
        "owner": "Logistics Team",
        "purchase_value": 65000,
        "current_value": 40000,
    },
    {
        "asset_code": "ATUL-VEH-001",
        "name": "Logistics Vehicle",
        "asset_type": "Vehicle",
        "description": "Vehicle used for asset transportation",
        "serial_number": "ATUL-VEH-SN-001",
        "status": "active",
        "location": "Logistics Hub",
        "owner": "Logistics Operations",
        "purchase_value": 1800000,
        "current_value": 1350000,
    },
]


def main():
    db = SessionLocal()

    try:
        inserted = 0

        for item in assets:
            existing = db.query(Asset).filter(
                Asset.asset_code == item["asset_code"]
            ).first()

            if existing:
                print(f"EXISTS: {item['asset_code']}")
                continue

            asset = Asset(
                **item,
                purchase_date=datetime.utcnow(),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )

            db.add(asset)
            inserted += 1

        db.commit()

        print(f"INSERTED: {inserted}")
        print(f"TOTAL ASSETS: {db.query(Asset).count()}")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()

