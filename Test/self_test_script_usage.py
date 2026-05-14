# =========================================================
# self_test_script_usage.py
# Analizza quali script Python sono effettivamente utilizzati
# a partire da Regista.py
# =========================================================

import os
import ast
from collections import defaultdict

# ---------------------------------------------------------
# Funzione per leggere tutti gli import da un file Python
# ---------------------------------------------------------
def get_imports(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            tree = ast.parse(f.read(), filename=file_path)
        except SyntaxError:
            return set()
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module.split(".")[0])
    return imports

# ---------------------------------------------------------
# Funzione ricorsiva per tracciare gli script utilizzati
# ---------------------------------------------------------
def find_used_scripts(script_name, all_scripts, visited):
    if script_name in visited:
        return
    visited.add(script_name)
    file_path = all_scripts.get(script_name)
    if not file_path:
        return
    imports = get_imports(file_path)
    for imp in imports:
        # considera solo gli script presenti nella cartella
        if imp in all_scripts:
            find_used_scripts(imp, all_scripts, visited)

# ---------------------------------------------------------
# Entry point
# ---------------------------------------------------------
if __name__ == "__main__":
    # Cartella corrente (dove è inserito questo script)
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Trova tutti gli script Python nella cartella
    all_scripts = {}
    for fname in os.listdir(base_dir):
        if fname.endswith(".py") and fname != os.path.basename(__file__):
            name = os.path.splitext(fname)[0]
            all_scripts[name] = os.path.join(base_dir, fname)

    # Punto di partenza: Regista.py
    start_script = "Regista"

    used_scripts = set()
    find_used_scripts(start_script, all_scripts, used_scripts)

    # Determina gli script non utilizzati
    all_script_names = set(all_scripts.keys())
    unused_scripts = all_script_names - used_scripts

    # ---------------------------------------------------------
    # Stampa risultati sintetici
    # ---------------------------------------------------------
    print("\n=== Script Python utilizzati ===")
    for s in sorted(used_scripts):
        print(f"- {s}.py")

    print("\n=== Script Python probabilmente non utilizzati ===")
    for s in sorted(unused_scripts):
        print(f"- {s}.py")

    # ---------------------------------------------------------
    # Costruzione della mappa "chi importa chi"
    # ---------------------------------------------------------
    imported_by = defaultdict(list)
    for script_name, path in all_scripts.items():
        imports = get_imports(path)
        for imp in imports:
            if imp in all_scripts:
                imported_by[imp].append(script_name)

    # ---------------------------------------------------------
    # Stampa dettagli per gli script utilizzati (allineato come richiesto)
    # ---------------------------------------------------------
    print("\n=== Dettaglio import degli script utilizzati ===")

    # Calcola lunghezza massima del nome + '.py'
    max_len = max(len(s) + 3 for s in used_scripts)  # 3 caratteri per ".py"

    for s in sorted(used_scripts):
        callers = imported_by.get(s, [])
        if callers:
            callers_text = ", ".join(sorted(callers))
        else:
            callers_text = "nessuno (entry point principale)"
        # Nome + .py attaccato, poi spazi per allineare la parte successiva
        print(f"- {s}.py{(' ' * (max_len - (len(s) + 3)))} è importato da: {callers_text}")

    print("\n[INFO] Controllo completato.")


