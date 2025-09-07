import os
import json
import requests
import urllib.parse

# -----------------------------
# Configuración de rutas
# -----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config_path = os.path.join(BASE_DIR, "config", "games_config.json")

# -----------------------------
# Función para guardar JSON
# -----------------------------
def guardar_json():
    """Guarda el progreso parcial en disco."""
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(juegos_base, f, indent=4, ensure_ascii=False)
    print("💾 Progreso guardado.")

# -----------------------------
# Función para buscar en Steam
# -----------------------------
def buscar_steam_appid_por_nombre(nombre):
    """Consulta Steam Store API para obtener el steam_appid por nombre."""
    try:
        query = urllib.parse.quote(nombre)
        url = f"https://store.steampowered.com/api/storesearch/?term={query}&cc=us"
        resp = requests.get(url, timeout=5)
        data = resp.json()
        if data.get("items"):
            return data["items"][0]["id"]
    except Exception as e:
        print(f"⚠ Error buscando en Steam '{nombre}': {e}")
    return None

# -----------------------------
# Cargar archivo base
# -----------------------------
with open(config_path, "r", encoding="utf-8") as f:
    juegos_base = json.load(f)

# -----------------------------
# Descargar lista pública de Discord
# -----------------------------
url = "https://discord.com/api/v9/applications/detectable"
print("📥 Descargando lista de aplicaciones detectables desde Discord...")
apps_discord = requests.get(url).json()

# Crear índices por steam_appid y nombre
por_steam = {}
por_nombre = {}
steam_por_nombre = {}
exe_por_nombre = {}

for app in apps_discord:
    steam_ids = []
    for sku in app.get("third_party_skus", []):
        if sku.get("distributor") == "steam":
            try:
                steam_ids.append(int(sku.get("id")))
            except (ValueError, TypeError):
                pass

    # Guardar executable_path para Windows
    executable_path = None
    for exe in app.get("executables", []):
        if exe.get("os") == "win32":
            executable_path = exe.get("name")
            break

    for sid in steam_ids:
        por_steam[sid] = app["id"]
    por_nombre[app["name"].lower()] = app["id"]

    if steam_ids:
        steam_por_nombre[app["name"].lower()] = steam_ids[0]
    if executable_path:
        exe_por_nombre[app["name"].lower()] = executable_path

# -----------------------------
# 1️⃣ Completar datos en juegos existentes
# -----------------------------
for juego, datos in juegos_base.items():
    steam_id = datos.get("steam_appid")
    client_id = datos.get("client_id")
    executable_path = datos.get("executable_path")

    # Completar client_id
    if not client_id:
        nuevo_id = None
        if steam_id and steam_id in por_steam:
            nuevo_id = por_steam[steam_id]
        elif juego.lower() in por_nombre:
            nuevo_id = por_nombre[juego.lower()]
        if nuevo_id:
            juegos_base[juego]["client_id"] = nuevo_id
            print(f"✅ Client_id para '{juego}': {nuevo_id}")
            guardar_json()

    # Completar steam_appid
    if not steam_id:
        nuevo_steam = None
        if juego.lower() in steam_por_nombre:
            nuevo_steam = steam_por_nombre[juego.lower()]
        else:
            # 🔍 Buscar en Steam por nombre si Discord no lo tiene
            nuevo_steam = buscar_steam_appid_por_nombre(juego)

        if nuevo_steam:
            juegos_base[juego]["steam_appid"] = nuevo_steam
            print(f"✅ Steam_appid para '{juego}': {nuevo_steam}")
            guardar_json()

    # Completar executable_path
    if not executable_path:
        if juego.lower() in exe_por_nombre:
            juegos_base[juego]["executable_path"] = exe_por_nombre[juego.lower()]
            print(f"✅ Executable_path para '{juego}': {exe_por_nombre[juego.lower()]}")
            guardar_json()

# -----------------------------
# 2️⃣ Agregar juegos nuevos desde Discord
# -----------------------------
for app in apps_discord:
    nombre = app["name"]
    client_id = app["id"]

    # Buscar steam_appid
    steam_id = None
    for sku in app.get("third_party_skus", []):
        if sku.get("distributor") == "steam":
            try:
                steam_id = int(sku.get("id"))
                break
            except (ValueError, TypeError):
                pass

    # Si no está en Discord, buscar en Steam
    if not steam_id:
        steam_id = buscar_steam_appid_por_nombre(nombre)

    # Buscar executable_path
    executable_path = None
    for exe in app.get("executables", []):
        if exe.get("os") == "win32":
            executable_path = exe.get("name")
            break

    if nombre not in juegos_base:
        juegos_base[nombre] = {
            "name": nombre,
            "steam_appid": steam_id,
            "client_id": client_id,
            "executable_path": executable_path
        }
        print(f"➕ Agregado: {nombre} (client_id: {client_id}, steam_appid: {steam_id}, executable_path: {executable_path})")
        guardar_json()

print("\n✅ Actualización completada.")
