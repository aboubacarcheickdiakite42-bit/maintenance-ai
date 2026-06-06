import requests
from sklearn.tree import DecisionTreeClassifier
import matplotlib.pyplot as plt
import os
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

app = FastAPI()

TELEGRAM_TOKEN = "8718574523:AAH1gJwWKb7XjTqP0pBS7hq6qwLtzPrlS5k"

CHAT_ID = "5650384416"

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# ---------------- DATABASE ----------------
DATABASE_URL = "sqlite:///maintenance.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

class MaintenanceRecord(Base):
    __tablename__ = "maintenance"

    id = Column(Integer, primary_key=True, index=True)
    equipment = Column(String)
    history = Column(String)
    diagnosis = Column(String)
    result = Column(String)

Base.metadata.create_all(bind=engine)

# ---------------- MACHINE LEARNING ----------------

X = [
    [60, 5, 3],
    [70, 8, 4],
    [90, 15, 6],
    [95, 18, 7]
]

y = [
    0,
    1,
    2,
    2
]

model = DecisionTreeClassifier()

model.fit(X, y)

# ---------------- TELEGRAM ALERT ----------------

def send_telegram_alert(message):

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": message
    }

    requests.post(url, data=data)
# ---------------- INPUT MODEL ----------------
class Data(BaseModel):
    equipment: str
    history: str
    diagnosis: str

# ---------------- ROUTE HOME ----------------
@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )

# ---------------- ANALYSE IA + SAUVEGARDE ----------------
@app.post("/analyze")
def analyze(data: Data):

    history = data.history.lower()
    diagnosis = data.diagnosis.lower()

    temperature = 78

    vibration_level = 12

    pressure = 5.4

    criticity = "Faible"
    maintenance = "Préventive"
    risk = "Bas"

    if "surchauffe" in diagnosis:
        criticity = "Élevée"
        risk = "Important"

    if "vibration" in history:
        maintenance = "Prédictive"

    if "fuite" in history:
        criticity = "Moyenne"

    if "bruit" in history:
        risk = "Moyen"

    mtbf = 120

    mttr = 4

    availability = ((mtbf - mttr) / mtbf) * 100

    health_score = 85

    risk_score = 20

    if "vibration" in history:
        risk_score += 25

    if "surchauffe" in diagnosis:
        risk_score += 35

    if "fuite" in history:
        risk_score += 15

    if "bruit" in history:
        risk_score += 10

    if risk_score >= 70:
        prediction = "RISQUE DE PANNE CRITIQUE"

    elif risk_score >= 40:
        prediction = "RISQUE DE PANNE MOYEN"

    else:
        prediction = "RISQUE DE PANNE FAIBLE"

    alert = "Aucune alerte"

    if risk_score >= 70:
        alert = "🚨 ALERTE : Intervention immédiate recommandée"

        telegram_message = f"""
🚨 ALERTE MAINTENANCE

Équipement : {data.equipment}

Risque détecté : CRITIQUE

Action recommandée : Intervention immédiate
"""

        send_telegram_alert(telegram_message)

    prediction_ml = model.predict([[temperature, vibration_level, pressure]])[0]

    ml_result = "FAIBLE"

    if prediction_ml == 1:
        ml_result = "MOYEN"

    if prediction_ml == 2:
        ml_result = "CRITIQUE"
    result = f"""
=============================
ANALYSE IA INDUSTRIELLE
=============================

ÉQUIPEMENT : {data.equipment}

CRITICITÉ : {criticity}
RISQUE : {risk}
MAINTENANCE : {maintenance}

MTBF ESTIMÉ : {mtbf} heures

MTTR ESTIMÉ : {mttr} heures

DISPONIBILITÉ : {availability:.2f} %

SCORE SANTÉ MACHINE : {health_score} %S


SCORE DE RISQUE : {risk_score} %

PRÉDICTION IA : {prediction}

ALERTE IA : {alert}


PRÉDICTION MACHINE LEARNING : {ml_result}

=============================

RECOMMANDATIONS :

- Inspection complète
- Analyse vibratoire
- Contrôle thermique
- Vérification composants
- Maintenance adaptée

=============================
"""

    db = SessionLocal()

    new_record = MaintenanceRecord(
        equipment=data.equipment,
        history=data.history,
        diagnosis=data.diagnosis,
        result=result
    )

    db.add(new_record)
    db.commit()
    db.close()

    return {"result": result}

@app.get("/history")
def history(request: Request):

    db = SessionLocal()

    records = db.query(MaintenanceRecord).all()

    total_records = len(records)

    equipments = set()

    high_criticality = 0

    for r in records:

        equipments.add(r.equipment)

        if "Élevée" in r.result:
            high_criticality += 1

    total_equipments = len(equipments)

    labels = ["Criticité élevée", "Autres"]

    values = [
        high_criticality,
        total_records - high_criticality
    ]

    plt.figure(figsize=(5,5))

    plt.pie(values, labels=labels, autopct='%1.1f%%')

    if not os.path.exists("static"):
        os.makedirs("static")

    plt.savefig("static/chart.png")

    plt.close()

    temperature = 78

    vibration_level = 12

    pressure = 5.4

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="history.html",
        context={            "temperature": temperature,
            "vibration_level": vibration_level,
            "pressure": pressure,
            "records": records,
            "total_records": total_records,
            "total_equipments": total_equipments,
            "high_criticality": high_criticality
        }
    )