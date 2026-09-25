from backend.app.db.database import engine, Base
import backend.app.models

Base.metadata.create_all(bind=engine)

print("DATABASE TABLE CREATION: OK")
print("TABLES:")
for table in Base.metadata.sorted_tables:
    print(" -", table.name)
