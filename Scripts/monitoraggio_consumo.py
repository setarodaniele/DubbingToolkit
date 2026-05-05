# monitoraggio_consumo.py

import locale
import os
import json
from datetime import datetime
import threading

# Definire il lock a livello di modulo o di classe
json_lock = threading.Lock()

try:
    locale.setlocale(locale.LC_ALL, 'it_IT.UTF-8')
except locale.Error:
    locale.setlocale(locale.LC_ALL, 'Italian_Italy.1252')

def get_mese_precedente(mese_str, passi=1):
    anno, mese = map(int, mese_str.split('-'))
    for _ in range(passi):
        if mese == 1:
            anno -= 1
            mese = 12
        else:
            mese -= 1
    return f"{anno}-{mese:02d}"

class ConsumoTTS:
    def __init__(self, franchigia=1_000_000, prezzo_per_1k_char=16.0, motore="google"):
        self.franchigia = franchigia
        self.prezzo_per_1k_char = prezzo_per_1k_char
        self.motore = motore
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        billing_dir = os.path.join(base_dir, 'Billing')
        os.makedirs(billing_dir, exist_ok=True)
        self.file_save = os.path.join(billing_dir, 'consumo_tts.json')
        self.data_oggi = datetime.now().strftime("%Y-%m")
        self.dati = self.carica()

        # Assicuriamoci che sia un dizionario valido
        if not isinstance(self.dati, dict):
            self.dati = {}

        # Inizializza i motori presenti e aggiunge eventuali motori nuovi
        motori_standard = ["google", "azure", "elevenlabs"]
        for key in motori_standard:
            if key not in self.dati or not isinstance(self.dati[key], dict):
                self.dati[key] = {self.data_oggi: 0}

        # Assicuriamoci che anche eventuali motori extra siano inizializzati per i mesi mancanti
        for motore_attuale in self.dati:
            for mese in [
                self.data_oggi,
                get_mese_precedente(self.data_oggi, 1),
                get_mese_precedente(self.data_oggi, 2)
            ]:
                if mese not in self.dati[motore_attuale]:
                    self.dati[motore_attuale][mese] = 0

        self.pulisci_mesi_vecchi()
        self.salva()

    def carica(self):
        if os.path.exists(self.file_save):
            try:
                with open(self.file_save, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def salva(self):
        with open(self.file_save, 'w', encoding='utf-8') as f:
            json.dump(self.dati, f, indent=2, ensure_ascii=False)
    
    '''
    vecchia funzione per backup
    def aggiungi_caratteri(self, n):
        if n < 0:
            raise ValueError("Numero di caratteri non può essere negativo.")
        self.dati[self.motore][self.data_oggi] = self.dati[self.motore].get(self.data_oggi, 0) + n
        self.salva()
        '''
    def aggiungi_caratteri(self, n: int):
        if n < 0:
            raise ValueError("Numero di caratteri non può essere negativo.")

        mese_corrente = self.data_oggi
        motore = self.motore

        # Acquisisci il lock prima di leggere/aggiornare/scrivere il JSON
        with json_lock:
            prev_count = self.dati[motore].get(mese_corrente, 0)
            new_count = prev_count + n

            # Debug compatto come richiesto
            print(f"DEBUG [{motore}] ({mese_corrente}) Caratteri: ora={prev_count} | nuovi={n} | Tot={new_count}")

            self.dati[motore][mese_corrente] = new_count
            self.salva()




    def percentuale_consumo(self):
        return (self.dati[self.motore].get(self.data_oggi, 0) / self.franchigia) * 100

    def costo_stimato(self):
        extra = max(0, self.dati[self.motore].get(self.data_oggi, 0) - self.franchigia)
        return (extra / 1000) * self.prezzo_per_1k_char / 100

    def report_sintesi(self):
        usati = self.dati[self.motore].get(self.data_oggi, 0)
        return (
            f"{self.motore.capitalize()}: {locale.format_string('%d', usati, grouping=True)} caratteri "
            f"({locale.format_string('%.1f', self.percentuale_consumo(), grouping=True)}% franchigia)"
        )

    def report_completo(self):
        usati = self.dati[self.motore].get(self.data_oggi, 0)
        return (
            f"Motore: {self.motore}\n"
            f"Caratteri usati (mese {self.data_oggi}): {locale.format_string('%d', usati, grouping=True)}\n"
            f"Franchigia: {locale.format_string('%d', self.franchigia, grouping=True)}\n"
            f"Percentuale consumata: {locale.format_string('%.2f', self.percentuale_consumo(), grouping=True)}%\n"
            f"Costo stimato: €{locale.format_string('%.2f', self.costo_stimato(), grouping=True)}"
        )

    def pulisci_mesi_vecchi(self):
        mesi_necessari = set([
            self.data_oggi,
            get_mese_precedente(self.data_oggi, 1),
            get_mese_precedente(self.data_oggi, 2)
        ])
        for motore_attuale in self.dati:
            mesi_presenti = list(self.dati[motore_attuale].keys())
            for mese in mesi_presenti:
                if mese not in mesi_necessari:
                    print(f"DEBUG: elimino mese vecchio {mese} per motore {motore_attuale}")
                    del self.dati[motore_attuale][mese]

    def stampa_storico(self):
        mesi_ordinati = sorted([
            self.data_oggi,
            get_mese_precedente(self.data_oggi, 1),
            get_mese_precedente(self.data_oggi, 2)
        ], reverse=True)
        print(f"→ Storico ultimi due mesi precedenti per '{self.motore}':")
        for mese in mesi_ordinati:
            val = self.dati[self.motore].get(mese, 0)
            print(f"   {mese}: {locale.format_string('%d', val, grouping=True)} caratteri")
