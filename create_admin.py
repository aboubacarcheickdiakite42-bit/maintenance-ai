from database.db import SessionLocal, Base, engine
from database.models import User
import hashlib

Base.metadata.create_all(bind=engine)

db = SessionLocal()

admin = User(
    username="admin",
    password=hashlib.sha256("admin123".encode()).hexdigest(),
    is_admin=True
)

db.add(admin)
db.commit()
db.close()

print("Admin créé")