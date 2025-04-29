# Cursor credit

> Shows remaining credit on Cursor

<p align="center">
  <img src="https://i.imgur.com/nhMB9I1.png">
</p>

---

## 📝 Description

`check.py` is a command-line utility that quickly displays:
- The email of the connected Cursor account
- The number of used and remaining requests on your Cursor account
- Information is automatically extracted from your Cursor configuration files

## ⚙️ Requirements

- Python 3.7 or higher
- The following modules: `colorama`, `requests`
- A Cursor account already connected on your machine (so the config files exist)

## 📦 Installation

1. Clone this repository and move into the project directory:
   ```bash
   git clone https://github.com/DictateurMiro/credit-cursor/
   cd credit-cursor
   ```
2. Or simply copy the `check.py` file to a directory of your choice.

3. Install the required dependencies:
   ```bash
   pip install colorama requests
   ```

## 🚀 Usage

Simply run the script in a terminal:

```bash
python check.py
```

You will see:
- Your Cursor email
- The number of (Fast) requests used/remaining
- The number of (Slow) requests used

## 🖥️ Terminal Integration

To run the command more easily, add an alias to your `.bashrc` or `.zshrc`:

```bash
alias credit='python /path/to/check.py'
```

Reload your terminal, then simply type:

```bash
credit
```

## 💡 Tips

- If the script cannot find your token or email, make sure you are logged in to Cursor on your machine.
- Configuration paths are automatically detected based on your OS (Windows, Mac, Linux).
- Errors are displayed to help with troubleshooting.

## 📄 License

This project is open-source and free to use and modify.
