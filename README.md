Berikut adalah `README.md` yang cocok untuk project GitHub kamu berdasarkan isi dari `main.py` yang telah kamu berikan:

---

````markdown
# Minecraft Properties & YAML File Translator by Louis Bryan

A graphical desktop application for translating Minecraft `.properties` and `.yaml` configuration files using [Argos Translate](https://www.argosopentech.com/). This tool supports multi-threaded translation with fine control over CPU usage and translation batching, optimized for handling formatting like Minecraft color codes and nested YAML structures.

---

## ✨ Features

- 🖼️ User-friendly GUI with file and language selection
- 🔄 Auto-detect or manually select file type: `.properties` or `.yaml`
- 🧠 Intelligent translation that preserves:
  - Minecraft color codes (`&a`, `§c`, etc.)
  - Placeholders (`%player%`, `{variable}`, `<tag>` etc.)
- 🌐 Built-in support for [Argos Translate](https://www.argosopentech.com/)
- 🧵 Multi-threaded translation with CPU usage control
- 📦 Batch processing & adjustable delay between requests
- 💾 Save/load translation settings for reuse
- 📈 Real-time progress bar and logging output
- 📘 Helpful install guide and language management tools
- 🗃️ Supports over 70+ languages (based on installed Argos Translate packages)

---

## 🧑‍💻 Installation

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/minecraft-translator-gui.git
cd minecraft-translator-gui
````

2. **Install dependencies**

Make sure you have Python 3.8 or higher installed.

```bash
pip install -r requirements.txt
```

Required packages:

* `argostranslate`
* `PyYAML`
* `psutil`
* `tqdm`

Or install manually:

```bash
pip install argostranslate pyyaml psutil tqdm
```

3. **Install Argos Translate Language Packages**

Download and install translation packages (e.g., English → Indonesian):

```bash
argos-translate --install-package en id
```

See available packages here: [Argos Packages Index](https://www.argosopentech.com/argospm/index/)

---

## 🚀 Usage

Run the translator GUI:

```bash
python main.py
```

Then:

1. Choose a source `.properties` or `.yaml` file
2. Select output path
3. Select language pair (e.g., `en` → `id`)
4. Adjust performance settings (optional)
5. Click `Start Translation`

You can also save your settings as `.json` and reload them later.

---

## 📷 Screenshots

> *Add screenshots here of the GUI in use, before and after translation.*

---

## 🧠 How It Works

* Properties and YAML files are parsed and traversed.
* Translatable text is filtered out using smart patterns (ignores placeholders, formatting, etc.)
* Translations are batched and sent using Argos Translate with optional multithreading.
* Translations are cached to avoid redundant work.
* YAML structure is preserved using custom loader/dumper logic.

---

## 📂 File Support

| File Type        | Support | Notes                                |
| ---------------- | ------- | ------------------------------------ |
| `.properties`    | ✅       | Java-based key-value config format   |
| `.yaml` / `.yml` | ✅       | Supports nested structures and lists |

---

## 🛠 Advanced Settings

* **Batch Size**: Number of strings to translate at once
* **Delay**: Seconds to wait between batches
* **CPU Usage Mode**:

  * By percentage (e.g., 50% of all cores)
  * Fixed thread count (e.g., 4 threads)

---

## 💬 Language Support

The app can display all Argos Translate-installed languages. If no language is installed, it shows fallback languages.

To install more:

```bash
argos-translate --install-package en ja  # English to Japanese
```

Click `Refresh Languages` in the GUI after installing.

## 📦 Packaging (Optional)

To convert the app to `.exe` (Windows):

```bash
pip install pyinstaller
pyinstaller main.py --noconsole --onefile
```

## 📄 License

MIT License

## 👤 Author

**Louis Bryan**

> Minecraft enthusiast & AI student with a focus on language tech.

## ⭐️ Star the repo if this helped your Minecraft translation workflow!


Kalau kamu ingin, aku juga bisa buatin versi Bahasa Indonesia dari README ini. Mau?
```
