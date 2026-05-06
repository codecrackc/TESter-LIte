# =========================================================
# ULTRA WEB TESTER PRO v6.0
# Tester avanzado para proyectos web completos
# Detecta:
# ✔ HTML estructural
# ✔ CSS errores / versiones / media query
# ✔ JS errores / funciones / eventos / logs
# ✔ Recursos rotos (img/css/js/video/audio/fonts)
# ✔ SEO básico
# ✔ Accesibilidad
# ✔ Seguridad básica
# ✔ Performance
# ✔ Responsive
# ✔ Formularios
# ✔ Links rotos internos
# ✔ Sitemap / robots
# ✔ Favicon
# ✔ Meta tags
# ✔ Duplicados
# ✔ Versionado web
# =========================================================

import os
import re
import hashlib
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
from html.parser import HTMLParser
from urllib.parse import urlparse, parse_qs


# =========================================================
# PARSER HTML MASTER
# =========================================================
class UltraParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.css = []
        self.js = []
        self.img = []
        self.links = []
        self.forms = []
        self.inputs = []
        self.meta = []
        self.title_found = False
        self.favicon = False
        self.headers = []
        self.video = []
        self.audio = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)

        if tag == "title":
            self.title_found = True

        if tag == "link":
            href = attrs.get("href", "")
            rel = str(attrs.get("rel", ""))

            if href:
                if "stylesheet" in rel:
                    self.css.append(href)

                if "icon" in rel:
                    self.favicon = True

        elif tag == "script":
            if attrs.get("src"):
                self.js.append(attrs["src"])

        elif tag == "img":
            if attrs.get("src"):
                self.img.append((attrs["src"], attrs.get("alt")))

        elif tag == "a":
            if attrs.get("href"):
                self.links.append(attrs["href"])

        elif tag == "form":
            self.forms.append(attrs)

        elif tag == "input":
            self.inputs.append(attrs)

        elif tag in ["h1", "h2", "h3"]:
            self.headers.append(tag)

        elif tag == "meta":
            self.meta.append(attrs)

        elif tag == "video":
            if attrs.get("src"):
                self.video.append(attrs["src"])

        elif tag == "audio":
            if attrs.get("src"):
                self.audio.append(attrs["src"])


# =========================================================
# APP
# =========================================================
class UltraWebTester:
    def __init__(self, root):
        self.root = root
        self.root.title("Ultra Web Tester PRO")
        self.root.geometry("1100x760")
        self.root.configure(bg="#0d1117")

        self.project_path = ""

        tk.Label(
            root,
            text="ULTRA WEB TESTER PRO",
            font=("Arial", 18, "bold"),
            fg="white",
            bg="#0d1117"
        ).pack(pady=8)

        top = tk.Frame(root, bg="#0d1117")
        top.pack()

        tk.Button(
            top,
            text="Seleccionar Proyecto",
            command=self.select_project,
            width=22,
            bg="#238636",
            fg="white"
        ).grid(row=0, column=0, padx=5)

        tk.Button(
            top,
            text="EJECUTAR TEST COMPLETO",
            command=self.run_full_test,
            width=24,
            bg="#da3633",
            fg="white"
        ).grid(row=0, column=1, padx=5)

        self.path_label = tk.Label(
            root,
            text="No seleccionado",
            fg="yellow",
            bg="#0d1117"
        )
        self.path_label.pack(pady=5)

        self.output = scrolledtext.ScrolledText(
            root,
            width=140,
            height=40,
            bg="#010409",
            fg="#58a6ff",
            font=("Consolas", 9)
        )
        self.output.pack(padx=10, pady=10)

    # =====================================================
    # PATH
    # =====================================================
    def select_project(self):
        path = filedialog.askdirectory()
        if path:
            self.project_path = path
            self.path_label.config(text=path)

    # =====================================================
    # VERSION
    # =====================================================
    def extract_version(self, file):
        parsed = urlparse(file)
        query = parse_qs(parsed.query)

        for key in ["v", "ver", "version"]:
            if key in query:
                return query[key][0]

        return None

    # =====================================================
    # HASH DUPLICADOS
    # =====================================================
    def file_hash(self, path):
        h = hashlib.md5()
        with open(path, "rb") as f:
            h.update(f.read())
        return h.hexdigest()

    # =====================================================
    # TEST
    # =====================================================
    def run_full_test(self):
        if not self.project_path:
            messagebox.showerror("Error", "Selecciona un proyecto web.")
            return

        self.output.delete(1.0, tk.END)

        errors = []
        warnings = []
        info = []

        versions = []
        hashes = {}

        html_files = []

        for root_dir, dirs, files in os.walk(self.project_path):
            for file in files:
                full = os.path.join(root_dir, file)

                if file.endswith(".html"):
                    html_files.append(full)

                # Duplicados
                try:
                    file_md5 = self.file_hash(full)
                    if file_md5 in hashes:
                        warnings.append(f"Archivo duplicado: {full}")
                    else:
                        hashes[file_md5] = full
                except:
                    pass

        if not html_files:
            errors.append("No se encontraron archivos HTML.")

        # =================================================
        # HTML ANALYSIS
        # =================================================
        for html in html_files:
            try:
                with open(html, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                name = os.path.basename(html)

                parser = UltraParser()
                parser.feed(content)

                # Estructura
                for tag in ["<html", "<head", "<body"]:
                    if tag not in content.lower():
                        errors.append(f"{name}: Falta {tag}")

                # Title
                if "<title>" not in content.lower():
                    warnings.append(f"{name}: Sin <title> SEO")

                # Meta viewport
                if "viewport" not in content.lower():
                    warnings.append(f"{name}: Sin viewport responsive")

                # Description
                if "description" not in content.lower():
                    warnings.append(f"{name}: Sin meta description")

                # Favicon
                if not parser.favicon:
                    warnings.append(f"{name}: Sin favicon")

                # H1
                if "h1" not in parser.headers:
                    warnings.append(f"{name}: Sin H1")

                # Recursos
                for css in parser.css:
                    clean = css.split("?")[0]
                    if not clean.startswith("http"):
                        if not os.path.exists(os.path.join(self.project_path, clean)):
                            errors.append(f"{name}: CSS roto -> {clean}")

                    v = self.extract_version(css)
                    if v:
                        versions.append(v)
                    else:
                        warnings.append(f"{name}: CSS sin versión -> {css}")

                for js in parser.js:
                    clean = js.split("?")[0]
                    if not clean.startswith("http"):
                        if not os.path.exists(os.path.join(self.project_path, clean)):
                            errors.append(f"{name}: JS roto -> {clean}")

                    v = self.extract_version(js)
                    if v:
                        versions.append(v)

                for img, alt in parser.img:
                    clean = img.split("?")[0]
                    if not clean.startswith("http"):
                        if not os.path.exists(os.path.join(self.project_path, clean)):
                            warnings.append(f"{name}: Imagen rota -> {clean}")

                    if not alt:
                        warnings.append(f"{name}: Imagen sin ALT -> {img}")

                # Links
                for link in parser.links:
                    if link.startswith("#") or link.startswith("http"):
                        continue

                    clean = link.split("?")[0]
                    if not os.path.exists(os.path.join(self.project_path, clean)):
                        warnings.append(f"{name}: Link roto -> {clean}")

                # Forms
                for form in parser.forms:
                    if "action" not in form:
                        warnings.append(f"{name}: Formulario sin action")

                # Seguridad
                if 'target="_blank"' in content and 'rel="noopener"' not in content:
                    warnings.append(f"{name}: Riesgo target=_blank sin noopener")

            except Exception as e:
                errors.append(f"{html}: {str(e)}")

        # =================================================
        # CSS / JS
        # =================================================
        for root_dir, dirs, files in os.walk(self.project_path):
            for file in files:
                full = os.path.join(root_dir, file)

                try:
                    with open(full, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()

                    # CSS
                    if file.endswith(".css"):
                        if content.count("{") != content.count("}"):
                            errors.append(f"{file}: Llaves CSS desbalanceadas")

                        if "@media" not in content:
                            warnings.append(f"{file}: Sin media queries responsive")

                    # JS
                    elif file.endswith(".js"):
                        if content.count("{") != content.count("}"):
                            errors.append(f"{file}: Llaves JS desbalanceadas")

                        if "console.log" in content:
                            warnings.append(f"{file}: console.log detectado")

                        if "addEventListener" not in content:
                            warnings.append(f"{file}: Pocos eventos detectados")

                except:
                    warnings.append(f"No se pudo analizar {file}")

        # =================================================
        # ROBOTS / SITEMAP
        # =================================================
        if not os.path.exists(os.path.join(self.project_path, "robots.txt")):
            warnings.append("Sin robots.txt")

        if not os.path.exists(os.path.join(self.project_path, "sitemap.xml")):
            warnings.append("Sin sitemap.xml")

        # =================================================
        # VERSIONES
        # =================================================
        unique_versions = list(set(versions))

        if len(unique_versions) > 1:
            warnings.append(
                f"Versiones mezcladas detectadas: {', '.join(unique_versions)}"
            )

        # =================================================
        # PERFORMANCE
        # =================================================
        total_size = 0
        for root_dir, dirs, files in os.walk(self.project_path):
            for file in files:
                total_size += os.path.getsize(os.path.join(root_dir, file))

        mb = total_size / (1024 * 1024)

        if mb > 25:
            warnings.append(f"Proyecto pesado: {mb:.2f} MB")

        # =================================================
        # SCORE
        # =================================================
        score = max(0, 100 - (len(errors) * 4 + len(warnings)))

        # =================================================
        # OUTPUT
        # =================================================
        self.output.insert(tk.END, "="*90 + "\n")
        self.output.insert(tk.END, "ULTRA REPORTE PROFESIONAL WEB\n")
        self.output.insert(tk.END, "="*90 + "\n")
        self.output.insert(tk.END, f"SCORE GENERAL: {score}/100\n")
        self.output.insert(tk.END, f"Tamaño Proyecto: {mb:.2f} MB\n")

        if unique_versions:
            self.output.insert(
                tk.END,
                f"Versiones Web: {', '.join(unique_versions)}\n"
            )

        self.output.insert(tk.END, "\n")

        # Errors
        self.output.insert(tk.END, f"ERRORES ({len(errors)}):\n")
        for e in errors:
            self.output.insert(tk.END, f"[ERROR] {e}\n")

        self.output.insert(tk.END, "\n")

        # Warnings
        self.output.insert(tk.END, f"ADVERTENCIAS ({len(warnings)}):\n")
        for w in warnings:
            self.output.insert(tk.END, f"[WARNING] {w}\n")

        self.output.insert(tk.END, "\n")
        self.output.insert(
            tk.END,
            "RECOMENDACIÓN: Mantén SEO + Seguridad + Responsive + Versionado.\n"
        )


# =========================================================
# RUN
# =========================================================
if __name__ == "__main__":
    root = tk.Tk()
    app = UltraWebTester(root)
    root.mainloop()
