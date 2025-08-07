import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import queue
import os
import re
import json
import time
import psutil
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import argostranslate.package
import argostranslate.translate
import yaml
from yaml.representer import SafeRepresenter
from yaml.constructor import SafeConstructor


class TranslatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Minecraft Properties & YAML File Translator by Louis Bryan")
        self.root.geometry("800x750")
        self.root.resizable(True, True)

        # Variables
        self.source_file = tk.StringVar()
        self.output_file = tk.StringVar()
        self.source_lang = tk.StringVar(value="en")
        self.target_lang = tk.StringVar(value="id")
        self.cpu_usage_mode = tk.StringVar(value="percentage")
        self.cpu_percentage = tk.IntVar(value=50)
        self.thread_count = tk.IntVar(value=2)
        self.batch_size = tk.IntVar(value=5)
        self.delay_between_requests = tk.DoubleVar(value=0.3)
        self.file_type = tk.StringVar(value="auto")

        # Translation components
        self.translator = None
        self.translation_thread = None
        self.is_translating = False
        self.log_queue = queue.Queue()

        # Available languages
        self.available_languages = self.get_available_languages()

        self.create_widgets()
        self.setup_logging()

    def get_available_languages(self):
        """Get available language codes and names"""
        try:
            installed_languages = argostranslate.translate.get_installed_languages()
            lang_dict = {}
            for lang in installed_languages:
                lang_dict[lang.code] = lang.name

            # If no languages installed, return empty dict to show fallback languages
            if not lang_dict:
                return self.get_fallback_languages()

            return lang_dict
        except Exception as e:
            print(f"Error getting languages: {e}")
            return self.get_fallback_languages()

    def get_fallback_languages(self):
        """Get fallback language list with popular languages"""
        return {
            # Major World Languages
            "en": "English",
            "zh": "Chinese (Simplified)",
            "es": "Spanish",
            "hi": "Hindi",
            "ar": "Arabic",
            "bn": "Bengali",
            "pt": "Portuguese",
            "ru": "Russian",
            "ja": "Japanese",
            "pa": "Punjabi",
            "de": "German",
            "ko": "Korean",
            "fr": "French",
            "tr": "Turkish",
            "vi": "Vietnamese",
            "ur": "Urdu",
            "it": "Italian",
            "th": "Thai",
            "gu": "Gujarati",
            "pl": "Polish",

            # Southeast Asian Languages
            "id": "Indonesian",
            "ms": "Malay",
            "tl": "Filipino",
            "my": "Burmese",
            "km": "Khmer",
            "lo": "Lao",

            # European Languages
            "nl": "Dutch",
            "sv": "Swedish",
            "da": "Danish",
            "no": "Norwegian",
            "fi": "Finnish",
            "cs": "Czech",
            "sk": "Slovak",
            "hu": "Hungarian",
            "ro": "Romanian",
            "bg": "Bulgarian",
            "hr": "Croatian",
            "sr": "Serbian",
            "sl": "Slovenian",
            "et": "Estonian",
            "lv": "Latvian",
            "lt": "Lithuanian",
            "el": "Greek",
            "he": "Hebrew",

            # Other Popular Languages
            "fa": "Persian",
            "sw": "Swahili",
            "am": "Amharic",
            "yo": "Yoruba",
            "ig": "Igbo",
            "ha": "Hausa",
            "zu": "Zulu",
            "af": "Afrikaans",
            "sq": "Albanian",
            "eu": "Basque",
            "be": "Belarusian",
            "bs": "Bosnian",
            "ca": "Catalan",
            "cy": "Welsh",
            "eo": "Esperanto",
            "ga": "Irish",
            "gl": "Galician",
            "is": "Icelandic",
            "mk": "Macedonian",
            "mt": "Maltese",
            "mn": "Mongolian",
            "ne": "Nepali",
            "si": "Sinhala",
            "ta": "Tamil",
            "te": "Telugu",
            "ml": "Malayalam",
            "kn": "Kannada",
            "or": "Odia",
            "as": "Assamese",
            "mr": "Marathi",
            "sa": "Sanskrit",
            "sd": "Sindhi",
            "ky": "Kyrgyz",
            "kk": "Kazakh",
            "uz": "Uzbek",
            "tg": "Tajik",
            "tk": "Turkmen",
            "az": "Azerbaijani",
            "hy": "Armenian",
            "ka": "Georgian"
        }

    def create_widgets(self):
        """Create GUI widgets"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # File selection section
        self.create_file_section(main_frame)

        # Language selection section
        self.create_language_section(main_frame)

        # CPU/Threading configuration section
        self.create_cpu_section(main_frame)

        # Advanced settings section
        self.create_advanced_section(main_frame)

        # Control buttons
        self.create_control_section(main_frame)

        # Progress and logging section
        self.create_progress_section(main_frame)

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

    def create_file_section(self, parent):
        """Create file selection section"""
        file_frame = ttk.LabelFrame(parent, text="File Selection", padding="10")
        file_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)

        # File type selection
        ttk.Label(file_frame, text="File Type:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        type_frame = ttk.Frame(file_frame)
        type_frame.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))

        ttk.Radiobutton(type_frame, text="Auto-detect", variable=self.file_type, value="auto").pack(side=tk.LEFT)
        ttk.Radiobutton(type_frame, text="Properties", variable=self.file_type, value="properties").pack(side=tk.LEFT,
                                                                                                         padx=(20, 0))
        ttk.Radiobutton(type_frame, text="YAML", variable=self.file_type, value="yaml").pack(side=tk.LEFT, padx=(20, 0))

        # Source file
        ttk.Label(file_frame, text="Source File:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5))
        ttk.Entry(file_frame, textvariable=self.source_file, width=50).grid(row=1, column=1, sticky=(tk.W, tk.E),
                                                                            padx=(0, 5))
        ttk.Button(file_frame, text="Browse", command=self.browse_source_file).grid(row=1, column=2)

        # Output file
        ttk.Label(file_frame, text="Output File:").grid(row=2, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        ttk.Entry(file_frame, textvariable=self.output_file, width=50).grid(row=2, column=1, sticky=(tk.W, tk.E),
                                                                            padx=(0, 5), pady=(5, 0))
        ttk.Button(file_frame, text="Browse", command=self.browse_output_file).grid(row=2, column=2, pady=(5, 0))

    def create_language_section(self, parent):
        """Create language selection section"""
        lang_frame = ttk.LabelFrame(parent, text="Language Settings", padding="10")
        lang_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        lang_frame.columnconfigure(1, weight=1)
        lang_frame.columnconfigure(3, weight=1)

        # Source language
        ttk.Label(lang_frame, text="From:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        source_combo = ttk.Combobox(lang_frame, textvariable=self.source_lang,
                                    values=list(self.available_languages.keys()), state="readonly")
        source_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))

        # Target language
        ttk.Label(lang_frame, text="To:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        target_combo = ttk.Combobox(lang_frame, textvariable=self.target_lang,
                                    values=list(self.available_languages.keys()), state="readonly")
        target_combo.grid(row=0, column=3, sticky=(tk.W, tk.E))

        # Language info
        info_frame = ttk.Frame(lang_frame)
        info_frame.grid(row=1, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(10, 0))

        ttk.Button(info_frame, text="Refresh Languages", command=self.refresh_languages).pack(side=tk.LEFT)
        ttk.Button(info_frame, text="Install Guide", command=self.show_install_info).pack(side=tk.LEFT, padx=(10, 0))

        # Language count label
        lang_count_text = f"Available: {len(self.available_languages)} languages"
        self.lang_count_label = ttk.Label(info_frame, text=lang_count_text, foreground="gray")
        self.lang_count_label.pack(side=tk.RIGHT)

    def create_cpu_section(self, parent):
        """Create CPU/Threading configuration section"""
        cpu_frame = ttk.LabelFrame(parent, text="Performance Settings", padding="10")
        cpu_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        cpu_frame.columnconfigure(1, weight=1)

        # CPU usage mode
        ttk.Label(cpu_frame, text="CPU Usage Mode:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        mode_frame = ttk.Frame(cpu_frame)
        mode_frame.grid(row=0, column=1, sticky=(tk.W, tk.E))

        ttk.Radiobutton(mode_frame, text="Percentage", variable=self.cpu_usage_mode, value="percentage").pack(
            side=tk.LEFT)
        ttk.Radiobutton(mode_frame, text="Thread Count", variable=self.cpu_usage_mode, value="threads").pack(
            side=tk.LEFT, padx=(20, 0))

        # CPU percentage
        ttk.Label(cpu_frame, text="CPU Percentage:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        cpu_frame_control = ttk.Frame(cpu_frame)
        cpu_frame_control.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(5, 0))

        cpu_scale = ttk.Scale(cpu_frame_control, from_=10, to=100, variable=self.cpu_percentage, orient=tk.HORIZONTAL)
        cpu_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        cpu_label = ttk.Label(cpu_frame_control, text="50%")
        cpu_label.pack(side=tk.RIGHT, padx=(10, 0))

        def update_cpu_label(*args):
            cpu_label.config(text=f"{self.cpu_percentage.get()}%")

        self.cpu_percentage.trace('w', update_cpu_label)

        # Thread count
        ttk.Label(cpu_frame, text="Thread Count:").grid(row=2, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        thread_frame = ttk.Frame(cpu_frame)
        thread_frame.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=(5, 0))

        ttk.Spinbox(thread_frame, from_=1, to=psutil.cpu_count(), textvariable=self.thread_count, width=10).pack(
            side=tk.LEFT)
        ttk.Label(thread_frame, text=f"(Max: {psutil.cpu_count()})").pack(side=tk.LEFT, padx=(10, 0))

        # Current CPU info
        cpu_info = f"System: {psutil.cpu_count()} cores, {psutil.cpu_percent()}% usage"
        ttk.Label(cpu_frame, text=cpu_info, foreground="gray").grid(row=3, column=0, columnspan=2, sticky=tk.W,
                                                                    pady=(5, 0))

    def create_advanced_section(self, parent):
        """Create advanced settings section"""
        adv_frame = ttk.LabelFrame(parent, text="Advanced Settings", padding="10")
        adv_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        adv_frame.columnconfigure(1, weight=1)
        adv_frame.columnconfigure(3, weight=1)

        # Batch size
        ttk.Label(adv_frame, text="Batch Size:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        ttk.Spinbox(adv_frame, from_=1, to=50, textvariable=self.batch_size, width=10).grid(row=0, column=1,
                                                                                            sticky=tk.W)

        # Delay between requests
        ttk.Label(adv_frame, text="Delay (seconds):").grid(row=0, column=2, sticky=tk.W, padx=(20, 5))
        ttk.Spinbox(adv_frame, from_=0.1, to=5.0, increment=0.1, textvariable=self.delay_between_requests,
                    width=10).grid(row=0, column=3, sticky=tk.W)

    def create_control_section(self, parent):
        """Create control buttons section"""
        control_frame = ttk.Frame(parent)
        control_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        self.start_button = ttk.Button(control_frame, text="Start Translation", command=self.start_translation)
        self.start_button.pack(side=tk.LEFT)

        self.stop_button = ttk.Button(control_frame, text="Stop Translation", command=self.stop_translation,
                                      state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=(10, 0))

        ttk.Button(control_frame, text="Clear Log", command=self.clear_log).pack(side=tk.RIGHT)
        ttk.Button(control_frame, text="Save Settings", command=self.save_settings).pack(side=tk.RIGHT, padx=(0, 10))
        ttk.Button(control_frame, text="Load Settings", command=self.load_settings).pack(side=tk.RIGHT, padx=(0, 10))

    def create_progress_section(self, parent):
        """Create progress and logging section"""
        progress_frame = ttk.LabelFrame(parent, text="Progress & Logs", padding="10")
        progress_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 0))
        progress_frame.columnconfigure(0, weight=1)
        progress_frame.rowconfigure(1, weight=1)

        # Progress bar
        self.progress = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        # Log area
        self.log_text = scrolledtext.ScrolledText(progress_frame, height=15, state=tk.DISABLED)
        self.log_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    def detect_file_type(self, filename):
        """Auto-detect file type based on extension"""
        ext = os.path.splitext(filename)[1].lower()
        if ext == '.properties':
            return 'properties'
        elif ext in ['.yaml', '.yml']:
            return 'yaml'
        else:
            # Try to detect by content
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if '=' in content and not content.strip().startswith(('---', '- ')):
                        return 'properties'
                    else:
                        return 'yaml'
            except:
                return 'properties'  # Default fallback

    def browse_source_file(self):
        """Browse for source file"""
        filename = filedialog.askopenfilename(
            title="Select Source File",
            filetypes=[
                ("All supported", "*.properties;*.yaml;*.yml"),
                ("Properties files", "*.properties"),
                ("YAML files", "*.yaml;*.yml"),
                ("All files", "*.*")
            ]
        )
        if filename:
            self.source_file.set(filename)
            # Auto-generate output filename
            base, ext = os.path.splitext(filename)
            self.output_file.set(f"{base}_translated{ext}")

    def browse_output_file(self):
        """Browse for output file"""
        filename = filedialog.asksaveasfilename(
            title="Save Translated File As",
            filetypes=[
                ("Properties files", "*.properties"),
                ("YAML files", "*.yaml"),
                ("All files", "*.*")
            ],
            defaultextension=".properties"
        )
        if filename:
            self.output_file.set(filename)

    def refresh_languages(self):
        """Refresh available languages"""
        self.available_languages = self.get_available_languages()

        # Update combobox values
        try:
            # Find and update source language combobox
            for widget in self.root.winfo_children():
                self.update_comboboxes(widget)
        except Exception as e:
            self.log(f"Error updating comboboxes: {e}")

        self.log(f"Languages refreshed - {len(self.available_languages)} languages available")

    def update_comboboxes(self, widget):
        """Recursively update all comboboxes with new language list"""
        try:
            if isinstance(widget, ttk.Combobox):
                current_value = widget.get()
                widget['values'] = list(self.available_languages.keys())
                if current_value in self.available_languages:
                    widget.set(current_value)

            for child in widget.winfo_children():
                self.update_comboboxes(child)
        except:
            pass

    def show_install_info(self):
        """Show language installation information"""
        info = """To install language packages for ArgosTranslate, use the command line:

argos-translate --install-package [source] [target]

Popular language pairs:
• English to Indonesian: argos-translate --install-package en id
• English to Spanish: argos-translate --install-package en es  
• English to French: argos-translate --install-package en fr
• English to German: argos-translate --install-package en de
• English to Chinese: argos-translate --install-package en zh
• English to Japanese: argos-translate --install-package en ja
• English to Korean: argos-translate --install-package en ko
• English to Russian: argos-translate --install-package en ru
• English to Portuguese: argos-translate --install-package en pt
• English to Arabic: argos-translate --install-package en ar

Alternative installation via Python:
import argostranslate.package
argostranslate.package.install_from_path("path/to/package")

Note: Not all language pairs may be available. Check ArgosTranslate 
documentation for complete list of supported languages.

You can also download packages from:
https://www.argosopentech.com/argospm/index/

After installing new languages, click 'Refresh Languages' to update the list."""

        # Create a new window for better display
        info_window = tk.Toplevel(self.root)
        info_window.title("Language Installation Guide")
        info_window.geometry("600x500")
        info_window.resizable(True, True)

        # Create scrollable text widget
        text_frame = ttk.Frame(info_window, padding="10")
        text_frame.pack(fill=tk.BOTH, expand=True)

        info_text = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, height=25, width=70)
        info_text.pack(fill=tk.BOTH, expand=True)
        info_text.insert(tk.END, info)
        info_text.config(state=tk.DISABLED)

        # Close button
        close_button = ttk.Button(info_window, text="Close", command=info_window.destroy)
        close_button.pack(pady=10)

    def calculate_optimal_threads(self):
        """Calculate optimal thread count based on CPU usage setting"""
        if self.cpu_usage_mode.get() == "percentage":
            cpu_cores = psutil.cpu_count()
            target_percentage = self.cpu_percentage.get()
            optimal_threads = max(1, int(cpu_cores * target_percentage / 100))
            return min(optimal_threads, cpu_cores)
        else:
            return self.thread_count.get()

    def setup_logging(self):
        """Setup logging system"""

        def check_log_queue():
            try:
                while True:
                    message = self.log_queue.get_nowait()
                    self.log_text.config(state=tk.NORMAL)
                    self.log_text.insert(tk.END, f"{message}\n")
                    self.log_text.see(tk.END)
                    self.log_text.config(state=tk.DISABLED)
            except queue.Empty:
                pass
            self.root.after(100, check_log_queue)

        check_log_queue()

    def log(self, message):
        """Add message to log"""
        timestamp = time.strftime("%H:%M:%S")
        self.log_queue.put(f"[{timestamp}] {message}")

    def clear_log(self):
        """Clear log text"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)

    def save_settings(self):
        """Save current settings to file"""
        settings = {
            'source_lang': self.source_lang.get(),
            'target_lang': self.target_lang.get(),
            'cpu_usage_mode': self.cpu_usage_mode.get(),
            'cpu_percentage': self.cpu_percentage.get(),
            'thread_count': self.thread_count.get(),
            'batch_size': self.batch_size.get(),
            'delay_between_requests': self.delay_between_requests.get(),
            'file_type': self.file_type.get()
        }

        filename = filedialog.asksaveasfilename(
            title="Save Settings",
            filetypes=[("JSON files", "*.json")],
            defaultextension=".json"
        )

        if filename:
            try:
                with open(filename, 'w') as f:
                    json.dump(settings, f, indent=2)
                self.log(f"Settings saved to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save settings: {e}")

    def load_settings(self):
        """Load settings from file"""
        filename = filedialog.askopenfilename(
            title="Load Settings",
            filetypes=[("JSON files", "*.json")]
        )

        if filename:
            try:
                with open(filename, 'r') as f:
                    settings = json.load(f)

                self.source_lang.set(settings.get('source_lang', 'en'))
                self.target_lang.set(settings.get('target_lang', 'id'))
                self.cpu_usage_mode.set(settings.get('cpu_usage_mode', 'percentage'))
                self.cpu_percentage.set(settings.get('cpu_percentage', 50))
                self.thread_count.set(settings.get('thread_count', 2))
                self.batch_size.set(settings.get('batch_size', 5))
                self.delay_between_requests.set(settings.get('delay_between_requests', 0.3))
                self.file_type.set(settings.get('file_type', 'auto'))

                self.log(f"Settings loaded from {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load settings: {e}")

    def validate_settings(self):
        """Validate current settings"""
        if not self.source_file.get():
            messagebox.showerror("Error", "Please select a source file")
            return False

        if not self.output_file.get():
            messagebox.showerror("Error", "Please specify an output file")
            return False

        if not os.path.exists(self.source_file.get()):
            messagebox.showerror("Error", "Source file does not exist")
            return False

        if self.source_lang.get() not in self.available_languages:
            messagebox.showerror("Error", "Source language not available")
            return False

        if self.target_lang.get() not in self.available_languages:
            messagebox.showerror("Error", "Target language not available")
            return False

        return True

    def start_translation(self):
        """Start translation process"""
        if not self.validate_settings():
            return

        if self.is_translating:
            messagebox.showwarning("Warning", "Translation is already in progress")
            return

        self.is_translating = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

        # Calculate optimal threads
        optimal_threads = self.calculate_optimal_threads()
        self.log(f"Starting translation with {optimal_threads} threads")

        # Determine file type
        if self.file_type.get() == "auto":
            detected_type = self.detect_file_type(self.source_file.get())
            self.log(f"Auto-detected file type: {detected_type}")
        else:
            detected_type = self.file_type.get()

        # Start translation in separate thread
        self.translation_thread = threading.Thread(target=self.run_translation, args=(optimal_threads, detected_type))
        self.translation_thread.daemon = True
        self.translation_thread.start()

    def stop_translation(self):
        """Stop translation process"""
        if self.translator:
            self.translator.stop_translation = True
        self.log("Translation stop requested...")

    def run_translation(self, max_workers, file_type):
        """Run translation process"""
        try:
            if file_type == 'yaml':
                self.translator = YamlTranslatorEngine(
                    source_file=self.source_file.get(),
                    output_file=self.output_file.get(),
                    source_lang=self.source_lang.get(),
                    target_lang=self.target_lang.get(),
                    max_workers=max_workers,
                    batch_size=self.batch_size.get(),
                    delay_between_requests=self.delay_between_requests.get(),
                    log_callback=self.log,
                    progress_callback=self.update_progress
                )
            else:
                self.translator = PropertiesTranslatorEngine(
                    source_file=self.source_file.get(),
                    output_file=self.output_file.get(),
                    source_lang=self.source_lang.get(),
                    target_lang=self.target_lang.get(),
                    max_workers=max_workers,
                    batch_size=self.batch_size.get(),
                    delay_between_requests=self.delay_between_requests.get(),
                    log_callback=self.log,
                    progress_callback=self.update_progress
                )

            self.translator.translate_file()

        except Exception as e:
            self.log(f"Translation error: {e}")
        finally:
            self.is_translating = False
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.progress.config(value=0)

    def update_progress(self, current, total):
        """Update progress bar"""
        if total > 0:
            progress_value = (current / total) * 100
            self.progress.config(value=progress_value)


class BaseTranslatorEngine:
    """Base class for translation engines"""

    def __init__(self, source_file, output_file, source_lang, target_lang,
                 max_workers=2, batch_size=5, delay_between_requests=0.3,
                 log_callback=None, progress_callback=None):
        self.source_file = source_file
        self.output_file = output_file
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.max_workers = max_workers
        self.batch_size = batch_size
        self.delay_between_requests = delay_between_requests
        self.log_callback = log_callback or print
        self.progress_callback = progress_callback or (lambda x, y: None)

        self.stop_translation = False
        self.translation_cache = {}
        self.translation_lock = threading.Lock()

        self.setup_translation()
        self.compile_ignore_patterns()

    def setup_translation(self):
        """Setup translation engine"""
        installed_languages = argostranslate.translate.get_installed_languages()
        self.from_lang = next((lang for lang in installed_languages if lang.code == self.source_lang), None)
        self.to_lang = next((lang for lang in installed_languages if lang.code == self.target_lang), None)

        if not self.from_lang or not self.to_lang:
            raise Exception(f"Language pair {self.source_lang}->{self.target_lang} not available")

        self.translation_engine = self.from_lang.get_translation(self.to_lang)

    def compile_ignore_patterns(self):
        """Compile ignore patterns with fixed Minecraft color code handling"""
        patterns = [
            r'%[^%]*%',  # Placeholder patterns like %player%
            r'<[^<>]*>',  # HTML/XML tags
            r'\{[^{}]*\}',  # JSON/bracket placeholders
            r'\[[^\[\]]*\]',  # Square bracket placeholders
            r'minecraft:[a-zA-Z0-9_]+',  # Minecraft namespaced IDs
            r'\b(sound|particle|block|entity|item|effect|enchantment|potion|biome|dimension)\.[a-zA-Z0-9_.]+\b',
            # Technical terms
            r'[=+\-*/]',  # Math operators
            r'\b[a-zA-Z0-9_]+\.[a-zA-Z0-9_.]+\b',  # Domain-like patterns
            r'https?://\S+',  # URLs
            r'^\d+$',  # Numbers only
            r'^[^\w\s]+$',  # Special characters only
            r'^\w$'  # Single characters
        ]

        self.ignore_patterns = re.compile('|'.join(f'({pattern})' for pattern in patterns))

        # Enhanced split pattern that properly handles Minecraft color codes
        self.split_pattern = re.compile(
            r'('
            r'&[0-9a-fk-or]|'  # Minecraft color codes (& followed by valid color/formatting code)
            r'§[0-9a-fk-or]|'  # Minecraft section sign color codes
            r'%[^%]*%|'  # Placeholder patterns
            r'<[^<>]*>|'  # HTML/XML tags
            r'\{[^{}]*\}|'  # JSON/bracket placeholders
            r'\[[^\[\]]*\]|'  # Square bracket placeholders
            r'minecraft:[a-zA-Z0-9_]+|'  # Minecraft namespaced IDs
            r'https?://\S+|'  # URLs
            r'/\w+|'  # Commands
            r'\b[a-zA-Z0-9_.]+\.[a-zA-Z0-9_.]+\b'  # Domain-like patterns
            r')'
        )

        # Pattern to identify Minecraft color codes specifically
        self.minecraft_color_pattern = re.compile(r'[&§][0-9a-fk-or]')

    def should_ignore(self, text):
        """Check if text should be ignored"""
        if not text or not text.strip() or len(text.strip()) <= 2:
            return True

        # Check if it's a Minecraft color code
        if self.minecraft_color_pattern.fullmatch(text.strip()):
            return True

        return bool(self.ignore_patterns.fullmatch(text.strip()))

    def translate_text(self, text):
        """Translate text with caching"""
        if not text or self.should_ignore(text):
            return text

        text_key = text.strip()
        if text_key in self.translation_cache:
            return self.translation_cache[text_key]

        try:
            with self.translation_lock:
                result = self.translation_engine.translate(text_key)
                if result:
                    self.translation_cache[text_key] = result
                    return result
        except Exception as e:
            self.log_callback(f"Translation error for '{text}': {e}")

        return text

    def translate_complex_text(self, text):
        """Translate complex text by splitting it properly for Minecraft formatting"""
        if self.should_ignore(text):
            return text

        # Split the text while preserving Minecraft color codes and other special patterns
        parts = self.split_pattern.split(text)
        result_parts = []

        i = 0
        while i < len(parts):
            part = parts[i]

            if not part:  # Skip empty parts
                i += 1
                continue

            # Check if this part is a Minecraft color code
            if self.minecraft_color_pattern.fullmatch(part):
                result_parts.append(part)

                # Check if the next part should be attached (no space between color code and text)
                if (i + 1 < len(parts) and
                        parts[i + 1] and
                        not parts[i + 1].startswith(' ') and
                        not self.should_ignore(parts[i + 1])):

                    # Add the color code and translate the next part
                    next_part = parts[i + 1]
                    if next_part and not self.should_ignore(next_part):
                        # Translate the text part that follows the color code
                        translated_part = self.translate_text(next_part)
                        result_parts.append(translated_part)
                        i += 2  # Skip both current and next part
                        continue

                i += 1
                continue

            # Check if this part should be ignored (special patterns, URLs, etc.)
            if self.should_ignore(part):
                result_parts.append(part)
            else:
                # This is regular text that should be translated
                translated_part = self.translate_text(part)
                result_parts.append(translated_part)

            i += 1

        # Join all parts and clean up any double spaces that might have been introduced
        result = ''.join(result_parts)

        # Clean up spacing issues around color codes
        # Remove spaces between color codes and following text
        result = re.sub(r'([&§][0-9a-fk-or])\s+', r'\1', result)

        return result


class PropertiesTranslatorEngine(BaseTranslatorEngine):
    """Translator engine for Properties files"""

    def process_batch(self, lines_batch):
        """Process a batch of lines"""
        if self.stop_translation:
            return []

        results = []
        for line_index, line in lines_batch:
            if self.stop_translation:
                break

            line_stripped = line.strip()
            if not line_stripped or line_stripped.startswith('#'):
                results.append((line_index, line))
                continue

            if '=' in line:
                key, value = line.split('=', 1)
                original_value = value.strip()

                if original_value:
                    translated_value = self.translate_complex_text(original_value)
                    new_line = f"{key.strip()}={translated_value}\n"
                    results.append((line_index, new_line))
                else:
                    results.append((line_index, line))
            else:
                results.append((line_index, line))

        return results

    def translate_file(self):
        """Translate the properties file"""
        self.log_callback(f"Reading properties file: {self.source_file}")

        try:
            with open(self.source_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            raise Exception(f"Failed to read source file: {e}")

        self.log_callback(f"Total lines: {len(lines)}")

        # Prepare lines for processing
        lines_to_process = []
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            if line_stripped and not line_stripped.startswith('#') and '=' in line:
                lines_to_process.append((i, line))

        self.log_callback(f"Lines to process: {len(lines_to_process)}")

        # Create batches
        batches = []
        for i in range(0, len(lines_to_process), self.batch_size):
            batch = lines_to_process[i:i + self.batch_size]
            batches.append(batch)

        self.log_callback(f"Processing {len(batches)} batches with {self.max_workers} workers")

        # Process batches
        translated_results = {}
        processed_batches = 0

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            if self.stop_translation:
                return

            future_to_batch = {
                executor.submit(self.process_batch, batch): i
                for i, batch in enumerate(batches)
            }

            for future in as_completed(future_to_batch):
                if self.stop_translation:
                    break

                try:
                    batch_results = future.result()
                    for line_index, translated_line in batch_results:
                        translated_results[line_index] = translated_line

                    processed_batches += 1
                    self.progress_callback(processed_batches, len(batches))
                    self.log_callback(f"Processed batch {processed_batches}/{len(batches)}")

                    time.sleep(self.delay_between_requests)

                except Exception as e:
                    self.log_callback(f"Batch processing error: {e}")

        if self.stop_translation:
            self.log_callback("Translation stopped by user")
            return

        # Update original lines
        for line_index, translated_line in translated_results.items():
            lines[line_index] = translated_line

        # Save results
        try:
            os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
            with open(self.output_file, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            self.log_callback(f"Translation completed! Saved to: {self.output_file}")
            self.log_callback(f"Cache entries: {len(self.translation_cache)}")
        except Exception as e:
            raise Exception(f"Failed to save output file: {e}")


class YamlTranslatorEngine(BaseTranslatorEngine):
    """Translator engine for YAML files"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Configure YAML to preserve order and formatting
        self.yaml_loader = yaml.SafeLoader
        self.yaml_dumper = yaml.SafeDumper

        # Add custom representer for better output formatting
        def represent_str(dumper, data):
            if '\n' in data:
                return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
            return dumper.represent_scalar('tag:yaml.org,2002:str', data)

        self.yaml_dumper.add_representer(str, represent_str)

    def extract_translatable_strings(self, data, path=""):
        """Extract translatable strings from YAML data structure"""
        translatable_items = []

        if isinstance(data, dict):
            for key, value in data.items():
                current_path = f"{path}.{key}" if path else key
                translatable_items.extend(self.extract_translatable_strings(value, current_path))
        elif isinstance(data, list):
            for i, item in enumerate(data):
                current_path = f"{path}[{i}]"
                translatable_items.extend(self.extract_translatable_strings(item, current_path))
        elif isinstance(data, str):
            # Only translate strings that aren't keys or technical values
            if not self.should_ignore(data) and len(data.strip()) > 2:
                translatable_items.append((path, data))

        return translatable_items

    def set_value_by_path(self, data, path, value):
        """Set value in nested data structure using path"""
        if not path:
            return value

        parts = []
        current = ""
        bracket_depth = 0

        for char in path:
            if char == '[':
                bracket_depth += 1
                if bracket_depth == 1 and current:
                    parts.append(current)
                    current = ""
            elif char == ']':
                bracket_depth -= 1
                if bracket_depth == 0:
                    parts.append(int(current))
                    current = ""
            elif char == '.' and bracket_depth == 0:
                if current:
                    parts.append(current)
                    current = ""
            else:
                current += char

        if current:
            parts.append(current)

        # Navigate to the target location
        current_data = data
        for part in parts[:-1]:
            if isinstance(part, int):
                current_data = current_data[part]
            else:
                current_data = current_data[part]

        # Set the value
        final_key = parts[-1]
        if isinstance(final_key, int):
            current_data[final_key] = value
        else:
            current_data[final_key] = value

    def process_batch(self, strings_batch):
        """Process a batch of translatable strings"""
        if self.stop_translation:
            return []

        results = []
        for path, original_text in strings_batch:
            if self.stop_translation:
                break

            translated_text = self.translate_complex_text(original_text)
            results.append((path, translated_text))

        return results

    def translate_file(self):
        """Translate the YAML file"""
        self.log_callback(f"Reading YAML file: {self.source_file}")

        try:
            with open(self.source_file, 'r', encoding='utf-8') as f:
                yaml_data = yaml.load(f, Loader=self.yaml_loader)
        except Exception as e:
            raise Exception(f"Failed to read YAML file: {e}")

        if yaml_data is None:
            raise Exception("YAML file is empty or invalid")

        # Extract translatable strings
        translatable_strings = self.extract_translatable_strings(yaml_data)
        self.log_callback(f"Found {len(translatable_strings)} translatable strings")

        if not translatable_strings:
            self.log_callback("No translatable strings found")
            return

        # Create batches
        batches = []
        for i in range(0, len(translatable_strings), self.batch_size):
            batch = translatable_strings[i:i + self.batch_size]
            batches.append(batch)

        self.log_callback(f"Processing {len(batches)} batches with {self.max_workers} workers")

        # Process batches
        translation_results = {}
        processed_batches = 0

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            if self.stop_translation:
                return

            future_to_batch = {
                executor.submit(self.process_batch, batch): i
                for i, batch in enumerate(batches)
            }

            for future in as_completed(future_to_batch):
                if self.stop_translation:
                    break

                try:
                    batch_results = future.result()
                    for path, translated_text in batch_results:
                        translation_results[path] = translated_text

                    processed_batches += 1
                    self.progress_callback(processed_batches, len(batches))
                    self.log_callback(f"Processed batch {processed_batches}/{len(batches)}")

                    time.sleep(self.delay_between_requests)

                except Exception as e:
                    self.log_callback(f"Batch processing error: {e}")

        if self.stop_translation:
            self.log_callback("Translation stopped by user")
            return

        # Apply translations to the YAML data
        for path, translated_text in translation_results.items():
            try:
                self.set_value_by_path(yaml_data, path, translated_text)
            except Exception as e:
                self.log_callback(f"Error setting value at path {path}: {e}")

        # Save results
        try:
            os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
            with open(self.output_file, 'w', encoding='utf-8') as f:
                yaml.dump(yaml_data, f, Dumper=self.yaml_dumper, default_flow_style=False,
                          allow_unicode=True, indent=2, sort_keys=False)
            self.log_callback(f"Translation completed! Saved to: {self.output_file}")
            self.log_callback(f"Cache entries: {len(self.translation_cache)}")
        except Exception as e:
            raise Exception(f"Failed to save output file: {e}")


def main():
    try:
        # Check if PyYAML is available
        import yaml
    except ImportError:
        print("Error: PyYAML is required for YAML support.")
        print("Please install it with: pip install PyYAML")
        return

    root = tk.Tk()
    app = TranslatorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()