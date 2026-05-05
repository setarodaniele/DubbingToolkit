# ui_printer.py
from colorama import Style
from core.ui_colors import *

BOX_SEPARATOR = "-" * 28


def print_infobox(lines, status_line=None, status_color=None, warning=None):
    """
    Stampa un infobox standard.

    lines -> lista stringhe principali
    status_line -> stringa stato compatibilità
    status_color -> colore stato
    warning -> stringa warning opzionale
    """

    print()
    print(COLOR_FRAME + BOX_SEPARATOR)

    for line in lines:
        print(COLOR_INFO + line)

    if status_line:
        color = status_color if status_color else COLOR_INFO
        print(color + status_line)

    if warning:
        print(COLOR_WARNING + warning)

    print(COLOR_FRAME + BOX_SEPARATOR + Style.RESET_ALL)

def print_menu_header(title: str):
    """
    Stampa l'intestazione standard di un menu:
    
    ----------------------------
    TITOLO MENU
    ----------------------------
    """
    print()
    print(COLOR_FRAME + BOX_SEPARATOR)
    print(COLOR_INFO + title)
    print(COLOR_FRAME + BOX_SEPARATOR + Style.RESET_ALL)


def print_menu(options_dict):
    """
    options_dict = {
        "1": "Voce menu",
        "2": "Voce menu"
    }
    """
    for key, text in options_dict.items():
        print(COLOR_MENU + f"{key}. {text}")


def print_error(message):
    print(COLOR_ERROR + message + Style.RESET_ALL)


def print_success(message):
    print(COLOR_SUCCESS + message + Style.RESET_ALL)


def print_input(prompt):
    return input(COLOR_INPUT + prompt + Style.RESET_ALL)

def print_info(message):
    """
    Stampa un messaggio informativo standard in colore bianco.
    """
    print(COLOR_INFO + message + Style.RESET_ALL)
