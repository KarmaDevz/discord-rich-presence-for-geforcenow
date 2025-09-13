# 🎮 GeForce Presence — Discord Rich Presence for GeForce NOW

<p align="center">
  <a href="https://github.com/KarmaDevz/discord-rich-presence-for-geforcenow/releases/latest">
    <img src="https://img.shields.io/badge/⬇️%20Download-Latest%20Release-blue?style=for-the-badge" alt="Download Latest Release">
  </a>
</p>

---

<div align="center">

  <img src="assets/discord_status.jpg" alt="Discord Status Example" width="45%">
  <img src="assets/discord_status2.jpg" alt="Discord Status Example" width="45%">

</div>

Tool that shows **REAL Rich Presence** in Discord for the game you’re running in **GeForce NOW**.

---

### Main Features

* Detects the active game in GeForce NOW as **real presence**.
* You can complete **Discord Quests** if the game is available on GFN.
* Optional: Compatible with **Steam Rich Presence**.
* Runs in the background with a tray icon and context menu to **Open Logs** or **Exit the program**.
* Easy installation with the included **Setup**.
* Multi-language support: currently **English (EN)** and **Spanish (ES)**.
* External configuration via `.env` and `config/games_config_merged.json`.

---

## 📦 Installation (Users)

1. Download the installer:

   * `GeForcePresenceSetup.exe` (generated with Inno Setup).

2. Run the installer and follow the wizard.

   * By default, the app is installed in:

     ```text
     %APPDATA%\geforce_presence
     ```
   * Shortcuts are created in the **Start Menu** (and optionally on the Desktop).

> **Note:** The installer is ready and available for download. Check the latest release.

---

## ⚙️ Configuration

The main configuration files are located in `%APPDATA%\geforce_presence`.

### `.env` (example)

```env
CLIENT_ID=1095416975028650046
UPDATE_INTERVAL=10
CONFIG_PATH_FILE=
TEST_RICH_URL=https://steamcommunity.com/dev/testrichpresence
STEAM_COOKIE=
```

* `CLIENT_ID`: Default Discord Rich Presence ID.
* `TEST_RICH_URL`: URL used to fetch rich presence from Steam (optional).
* `STEAM_COOKIE`: `steamLoginSecure` (optional) — improves presence details.
* `CONFIG_PATH_FILE`: Path to the `games_config.json` to be used by default (the installer and app will attempt to create/use `%APPDATA%\geforce_presence\config\games_config_merged.json`).

---

## ▶️ Usage

1. Run the shortcut created by the installer or directly execute:

   ```cmd
   %APPDATA%\geforce_presence\geforce_presence.exe
   ```
2. The application will try to open Discord and GeForce NOW (depending on your configuration).
3. If no `CONFIG_PATH_FILE` is configured, on first launch you will be prompted to select the `games_config.json`.

> **Current behavior**: when selecting the `games_config.json` through the dialog, the app saves the chosen path in `%APPDATA%\geforce_presence\config_path.txt`.

---

## 📜 License
The **GeForce Presence** program is distributed only in compiled format under a binary use license.  
You may use and share it with credit to the author (**KarmaDevz**), but modification or commercial use is not allowed.  
See the [LICENSE](LICENSE) file for more details.

---

## 💬 Credits

* `pypresence` — Discord Rich Presence
* `Pystray` —  Tray Menu
* `Inno Setup` — Installer
* `PyInstaller` — Executable Packaging
