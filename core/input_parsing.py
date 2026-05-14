# core/input_parsing.py
"""
Modulo centralizzato per il parsing dei dati utente.
Tutti i numeri e altri input “sensibili” devono passare da qui
per garantire uniformità e indipendenza dal locale del sistema.
"""

def parse_float(raw: str) -> float:
    """
    Converte input utente in float standard.
    Accetta sia ',' che '.' come separatore decimale.
    """
    raw = raw.strip()
    raw = raw.replace(",", ".")
    return float(raw)

def parse_int(raw: str) -> int:
    """
    Converte input utente in int.
    Rimuove spazi e separatori non numerici comuni.
    """
    raw = raw.strip()
    return int(raw)

def is_yes(answer: str, messages) -> bool:
    """Return True if answer matches the locale-defined yes responses.

    Reads YES_SHORT, YES_FULL and GENERAL_YES from the messages object.
    Always call .strip().lower() on input before comparing.
    """
    answer = answer.strip().lower()
    yes_values = {
        getattr(messages, "YES_SHORT", "y").lower(),
        getattr(messages, "YES_FULL", "yes").lower(),
        getattr(messages, "GENERAL_YES", "yes").lower(),
    }
    yes_values.discard("")
    return answer in yes_values


def parse_yes_no(raw: str) -> bool:
    """Legacy helper — does not use locale. Use is_yes(answer, messages) in runtime code."""
    raw = raw.strip().lower()
    if raw in ("s", "y", "yes"):
        return True
    elif raw in ("n", "no"):
        return False
    else:
        raise ValueError(f"Input non valido per yes/no: {raw}")

def parse_choice(raw: str, choices: list) -> str:
    """
    Controlla che l'input sia una delle scelte valide.
    Restituisce l'input standardizzato.
    """
    raw = raw.strip()
    if raw in choices:
        return raw
    raise ValueError(f"Scelta non valida: {raw}. Valide: {choices}")
