# Instagram ADB Follow Bot 📱🤖

A simple Python script that uses ADB and `pure-python-adb` to **automate following Instagram users** via Android device, based on a list of usernames provided in a text file.

---

## 📦 Features

- 🔌 Connects to Android via ADB (Wi-Fi or USB)
- 🔍 Opens Instagram profiles using URLs
- 🤖 Automates tapping the **Follow** button
- 📂 Reads usernames from an editable `usernames.txt` file
- 🎲 Can randomly pick users to follow

---

## 🚀 Requirements

- Python 3.7+
- Android device with:
  - USB Debugging enabled
  - Instagram installed and logged in
- [`pure-python-adb`](https://pypi.org/project/pure-python-adb/)

---

## 🛠 Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/instagram-adb-bot.git
cd instagram-adb-bot

# (Recommended) Create a virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt
