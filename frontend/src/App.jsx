import { useEffect, useState } from "react";
import "./App.css";

import jsPDF from "jspdf";
import html2canvas from "html2canvas";

const API_URL = "https://maintenance-backend-jlk6.onrender.com"; 


function App() {
  const [logged, setLogged] = useState(false);

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const [message, setMessage] = useState("");
  const [response, setResponse] = useState("");

  const [history, setHistory] = useState([]);
  const [equipements, setEquipements] = useState([]);

  const [nom, setNom] = useState("");
  const [type, setType] = useState("");
  const [marque, setMarque] = useState("");
  const [localisation, setLocalisation] = useState("");
  const [etat, setEtat] = useState("");

  const [showHistory, setShowHistory] = useState(false);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(false);

  const [time, setTime] = useState(new Date().toLocaleTimeString());

  useEffect(() => {
    loadHistory();
    loadEquipements();

    Notification.requestPermission();

    const interval = setInterval(() => {
      loadEquipements();
    }, 5000);

    const clock = setInterval(() => {
      setTime(new Date().toLocaleTimeString());
    }, 1000);

    return () => {
      clearInterval(interval);
      clearInterval(clock);
    };
  }, []);

  // 📜 HISTORIQUE
  const loadHistory = async () => {
    const res = await fetch(`${API_URL}/history`);
    const data = await res.json();
    setHistory(data);
  };

  // ⚙️ ÉQUIPEMENTS
  const loadEquipements = async () => {
    const res = await fetch(`${API_URL}/equipements`);
    const data = await res.json();
    setEquipements(data);
  };

  // 🤖 CHAT IA
  const sendMessage = async () => {
    setLoading(true);

    const res = await fetch(
      `${API_URL}/chat?message=${encodeURIComponent(message)}`
    );

    const data = await res.json();

    setResponse(data.response);
    loadHistory();
    setMessage("");

    if (Notification.permission === "granted") {
      new Notification("Analyse IA terminée");
    }

    setLoading(false);
  };

  // ➕ AJOUT ÉQUIPEMENT
  const addEquipement = async () => {
    const equipement = {
      nom,
      type,
      marque,
      localisation,
      etat,
    };

    await fetch(`${API_URL}/equipements`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(equipement),
    });

    loadEquipements();

    setNom("");
    setType("");
    setMarque("");
    setLocalisation("");
    setEtat("");
  };

  // ❌ SUPPRESSION (locale seulement)
  const deleteEquipement = async (index) => {
    const updated = [...equipements];
    updated.splice(index, 1);
    setEquipements(updated);
  };

  // 📦 EXPORT JSON
  const exportData = () => {
    const dataStr = JSON.stringify(equipements, null, 2);

    const blob = new Blob([dataStr], {
      type: "application/json",
    });

    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");

    a.href = url;
    a.download = "machines.json";
    a.click();
  };

  // 📄 EXPORT PDF
  const exportPDF = () => {
    const input = document.body;

    html2canvas(input).then((canvas) => {
      const imgData = canvas.toDataURL("image/png");

      const pdf = new jsPDF("p", "mm", "a4");

      const width = 210;
      const height = (canvas.height * width) / canvas.width;

      pdf.addImage(imgData, "PNG", 0, 0, width, height);
      pdf.save("maintenance-report.pdf");
    });
  };

  // 🔐 LOGIN
  if (!logged) {
    return (
      <div className="loginPage">
        <div className="loginBox">
          <h1>🏭 Maintenance IA</h1>

          <input
            placeholder="Utilisateur"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />

          <input
            type="password"
            placeholder="Mot de passe"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          <button
            onClick={() => {
              if (username === "admin" && password === "admin") {
                setLogged(true);
              } else {
                alert("Identifiants incorrects");
              }
            }}
          >
            Connexion
          </button>
        </div>
      </div>
    );
  }

  // 🖥️ INTERFACE
  return (
    <div className="container">
      <div className="sidebar">
        <div className="logo">🏭 MAINTENANCE IA</div>

        <div className="menu">
          <button onClick={() => setShowHistory(!showHistory)}>
            📜 Historique IA
          </button>

          <button onClick={exportData}>📦 Export JSON</button>

          <button onClick={exportPDF}>📄 Export PDF</button>
        </div>
      </div>

      <div className="main">
        <div className="topbar">
          <h1>Maintenance Industrielle IA</h1>
          <div className="live">🟢 LIVE — {time}</div>
        </div>

        <div className="stats">
          <div className="cardStat">
            <h2>Machines</h2>
            <p>{equipements.length}</p>
          </div>

          <div className="cardStat">
            <h2>Historique</h2>
            <p>{history.length}</p>
          </div>

          <div className="cardStat">
            <h2>Serveur</h2>
            <p>ONLINE</p>
          </div>
        </div>

        <div className="chatBox">
          <h2>🤖 Assistant IA</h2>

          <div className="chatInput">
            <input
              value={message}
              placeholder="Décrivez une panne..."
              onChange={(e) => setMessage(e.target.value)}
            />

            <button onClick={sendMessage}>Envoyer</button>
          </div>

          <div className="response">
            {loading ? "🧠 Analyse IA en cours..." : response}
          </div>
        </div>

        <div className="equipementForm">
          <h2>➕ Ajouter un équipement</h2>

          <input placeholder="Nom" value={nom} onChange={(e) => setNom(e.target.value)} />
          <input placeholder="Type" value={type} onChange={(e) => setType(e.target.value)} />
          <input placeholder="Marque" value={marque} onChange={(e) => setMarque(e.target.value)} />
          <input placeholder="Localisation" value={localisation} onChange={(e) => setLocalisation(e.target.value)} />
          <input placeholder="Etat" value={etat} onChange={(e) => setEtat(e.target.value)} />

          <button onClick={addEquipement}>Ajouter équipement</button>
        </div>

        <input
          className="searchBox"
          placeholder="🔍 Rechercher une machine..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />

        <div className="machines">
          {equipements
            .filter((eq) =>
              eq.nom.toLowerCase().includes(search.toLowerCase())
            )
            .map((eq, index) => (
              <div
                key={index}
                className={`machineCard ${
                  eq.health_score < 40
                    ? "critical"
                    : eq.health_score < 70
                    ? "warning"
                    : "good"
                }`}
              >
                <h2>{eq.nom}</h2>

                <p>Type : {eq.type}</p>
                <p>Marque : {eq.marque}</p>
                <p>Localisation : {eq.localisation}</p>
                <p>Etat : {eq.etat}</p>

                <p>🌡 Température : {eq.temperature}</p>
                <p>📈 Vibration : {eq.vibration}</p>
                <p>⚙ Pression : {eq.pression}</p>

                <p>🧠 Score IA : {eq.health_score}%</p>

                <div className="healthBar">
                  <div
                    className="healthFill"
                    style={{ width: `${eq.health_score}%` }}
                  />
                </div>

                <p>🚨 {eq.alert}</p>
                <p>🧠 Recommandation IA : {eq.recommendation}</p>

                <button
                  className="deleteBtn"
                  onClick={() => deleteEquipement(index)}
                >
                  ❌ Supprimer
                </button>
              </div>
            ))}
        </div>

        {showHistory && (
          <div className="history">
            <h2>📜 Historique IA</h2>

            {history.map((item, index) => (
              <div key={index} className="historyItem">
                <p><strong>Question :</strong> {item.question}</p>
                <p><strong>Réponse :</strong> {item.response}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
