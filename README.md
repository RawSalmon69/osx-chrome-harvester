# OSX Chrome Harvester

```bash
 ██████╗ ███████╗██╗  ██╗
██╔═══██╗██╔════╝╚██╗██╔╝
██║   ██║███████╗ ╚███╔╝     █████╗
██║   ██║╚════██║ ██╔██╗     ╚════╝
╚██████╔╝███████║██╔╝ ██╗
 ╚═════╝ ╚══════╝╚═╝  ╚═╝

 ██████╗██╗  ██╗██████╗  ██████╗ ███╗   ███╗███████╗
██╔════╝██║  ██║██╔══██╗██╔═══██╗████╗ ████║██╔════╝
██║     ███████║██████╔╝██║   ██║██╔████╔██║█████╗
██║     ██╔══██║██╔══██╗██║   ██║██║╚██╔╝██║██╔══╝
╚██████╗██║  ██║██║  ██║╚██████╔╝██║ ╚═╝ ██║███████╗
 ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝╚══════╝

██╗  ██╗ █████╗ ██████╗ ██╗   ██╗███████╗███████╗████████╗███████╗██████╗
██║  ██║██╔══██╗██╔══██╗██║   ██║██╔════╝██╔════╝╚══██╔══╝██╔════╝██╔══██╗
███████║███████║██████╔╝██║   ██║█████╗  ███████╗   ██║   █████╗  ██████╔╝
██╔══██║██╔══██║██╔══██╗╚██╗ ██╔╝██╔══╝  ╚════██║   ██║   ██╔══╝  ██╔══██╗
██║  ██║██║  ██║██║  ██║ ╚████╔╝ ███████╗███████║   ██║   ███████╗██║  ██║
╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚══════╝╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝

Author: The Kernel Panic
```

**OSX Chrome Harvester** is a tool designed to silently extract and decrypt saved Chrome passwords from macOS systems. It leverages the macOS Keychain for decryption and transmits the retrieved credentials to a Command-and-Control (C2) server.

Medium Blog Post: [Building OSX Chrome Harvester](https://medium.com/@piyushbhor22/building-osx-chrome-harvester-26513e1cdc3a)

### Features

- Extracts saved Chrome passwords on macOS systems.
- Automatically decrypts passwords using macOS Keychain.
- Sends decrypted passwords to a remote server (C2) silently.
- Ensures minimal disk activity and avoids leaving artifacts.
- Graceful error handling and silent termination upon failure.
- PyInstaller-built executable hides sensitive URLs from basic analysis.

### Requirements

#### Victim Environment

- macOS with Google Chrome installed.
- Python 3.7+ environment if the script isn't precompiled.

#### Attacker Environment

- Python 3.7+ for setup and server-side processing.
- A server capable of receiving and storing JSON data (sample Flask-based server included).

---

### Installation

#### 1. Clone the Repository

```bash
git clone https://github.com/Piyush-Bhor/osx-chrome-harvester.git
cd osx-chrome-harvester
```

#### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 3. Configure the C2 URL

Modify the `C2_URL` variable in the script to point to your server.

#### 4. Compile the Script into an Executable

Use PyInstaller to create a standalone executable:

```bash
pyinstaller --onefile -F osx_chrome_harvester.py
```

The executable will be located in the `/dist` directory.

---

### Usage

#### How It Works

1. Identifies and safely terminates active Chrome processes.
2. Extracts Chrome's "Login Data" SQLite database.
3. Retrieves the Chrome Safe Storage Key from macOS Keychain.
4. Decrypts passwords using AES-128-CBC.
5. Sends decrypted credentials to the configured C2 server.
6. Handles errors silently and transmits them to the server.

#### Example C2 Server Setup

A Flask-based sample server is provided to receive and log decrypted password data.

1. Navigate to the `server` directory and run the Flask server:
   ```bash
   python c2_server.py
   ```
2. Configure the IP and port to match your environment.

---

### JSON Data Format

The tool sends data in the following structure:

```json
{
  "passwords": [
    {
      "url": "https://example.com",
      "username": "user@example.com",
      "password": "decryptedPassword123"
    },
    {
      "url": "https://anotherexample.com",
      "username": "anotheruser@example.com",
      "password": "decryptedPassword456"
    }
  ]
}
```

---

### Notes

- This tool is intended strictly for educational and ethical red team purposes.
- Usage must comply with all local laws and ethical guidelines.

---

### License

This project is licensed under the MIT License. See the [LICENSE](https://github.com/Piyush-Bhor/osx-chrome-harvester?tab=MIT-1-ov-file) file for details.

