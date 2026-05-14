# Limitazioni e note

Questo documento raccoglie in modo trasparente le limitazioni attuali di DubbingToolkit, le funzionalità non ancora implementate e i comportamenti noti che potrebbero non corrispondere alle aspettative. Il progetto è in sviluppo attivo e queste limitazioni sono destinate a essere risolte progressivamente.

---

## Impostazioni non persistenti

Le impostazioni non vengono salvate tra una sessione e l'altra. Ad ogni avvio il sistema riparte dai valori di default e chiede la lingua dell'interfaccia. Tutte le altre preferenze — provider TTS, voce, modello Whisper, lingue di trascrizione e traduzione — devono essere riselezionate ogni volta. La persistenza delle impostazioni è pianificata come miglioramento futuro.

---

## Nessuna modalità batch

Il flusso è progettato per elaborare un file alla volta. Non è disponibile una modalità per processare automaticamente più file in sequenza. Questa funzionalità è considerata per sviluppi futuri.

---

## Qualità della traduzione

La traduzione usa modelli Helsinki-NLP in esecuzione locale. La qualità può essere inferiore rispetto a servizi cloud di traduzione professionale, specialmente su frasi idiomatiche, termini tecnici o testi con punteggiatura irregolare. È sempre consigliata una verifica manuale del testo tradotto prima di procedere alla sintesi.

---

## Nessuna verifica automatica delle tempistiche

Dopo la traduzione, il testo può risultare più lungo o più corto dell'originale, creando incongruenze con le tempistiche del parlato nel video. Al momento non esiste un sistema automatico di verifica o adattamento. La gestione delle tempistiche richiede intervento manuale sul file SRT tradotto. Un sistema automatico di verifica e adattamento è pianificato come miglioramento futuro.

---

## Trascrizione: rilevamento lingua automatico

Whisper rileva automaticamente la lingua del parlato, ma su audio rumoroso, con accenti marcati o di bassa qualità può commettere errori. In questi casi è necessario specificare manualmente la lingua prima della trascrizione. Un sistema di valutazione della confidenza del rilevamento è pianificato come miglioramento futuro.

---

## Trascrizione: gestione della memoria

File audio molto lunghi vengono caricati interamente in memoria durante la trascrizione. Su sistemi con RAM limitata questo può causare rallentamenti o interruzioni. L'elaborazione a blocchi è pianificata come miglioramento futuro.

---

## WhisperX non integrato

L'ambiente per WhisperX è predisposto ma non ancora integrato nella pipeline principale. Attualmente viene utilizzato esclusivamente Whisper standard.

---

## Sottotitoli non disponibili

La funzione di esportazione sottotitoli è presente nel menu ma non ancora implementata. Selezionandola il sistema non produce output.

---

## Provider TTS aggiuntivi non collegati

Attualmente sono supportati Azure e Google. In futuro è prevista l'integrazione di provider aggiuntivi, tra cui OpenAI ed ElevenLabs.

---

## Traduzione pivot non disponibile

Se la coppia di lingue diretta sorgente→destinazione non è disponibile nei modelli Helsinki-NLP, la traduzione non è possibile. La traduzione via lingua pivot (inglese come intermedio) è pianificata ma non ancora implementata.

---

## Portabilità limitata

Il progetto può essere spostato in un'altra posizione ma richiede la ricostruzione dell'ambiente virtuale dopo ogni spostamento. Non è un sistema completamente portabile.

---

## Elaborazione sequenziale

Le fasi della pipeline vengono eseguite in sequenza. Non è possibile parallelizzare l'elaborazione di più file o eseguire fasi contemporaneamente.