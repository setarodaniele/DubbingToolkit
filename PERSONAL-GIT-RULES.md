# Personal Git Rules

## Filosofia di lavoro

La storia di lavoro locale è **personale e privata**. Include tentativi, errori, cambi di direzione, refactoring intermedi — tutto quello che serve per arrivare alla soluzione finale.

Online (GitHub) vogliamo mostrare solo il **risultato finale pulito**, senza esporre i passaggi intermedi non necessari.

---

## Regola principale: Squash prima di Push

**Prima di fare push su `main` o su un branch remoto, squasha tutti i commit intermedi in uno solo.**

Questo significa:
- ✅ Localmente mantieni tutta la storia (nel branch di lavoro)
- ✅ Online vedono solo il commit finale pulito e ben descritto
- ✅ Privacy mantenuta sulla tua storia di sviluppo

---

## Come fare: Procedura step-by-step

### 1. Crea un branch di lavoro (facoltativo ma consigliato)
```powershell
git checkout -b feature/my-work
```

### 2. Fai tutti i commit che vuoi, senza preoccuparti
```powershell
git commit -m "tentativo 1"
git commit -m "fix bug"
git commit -m "refactor"
git commit -m "final touches"
```

### 3. Prima di pushare, squasha i commit
Se hai fatto 4 commit:
```powershell
git rebase -i HEAD~4
```

Oppure se lavori su un branch di feature:
```powershell
git rebase -i main
```

### 4. Nella finestra che si apre:
- La prima riga lasciala come `pick`
- Le altre righe cambia `pick` in `squash` (oppure `s`)
- Salva e chiudi

Esempio:
```
pick a1b2c3d tentativo 1
squash b2c3d4e fix bug
squash c3d4e5f refactor
squash d4e5f6g final touches
```

### 5. Nel messaggio finale, scrivi una descrizione pulita e completa
```
Update documentation: reference new Workspace/projects structure

Complete documentation updates for alpha release:
- All 8 language usage guides updated
- Architecture documentation synchronized
- Project-based Workspace model documented
```

### 6. Fai il push
```powershell
git push origin main
```

---

## Risultato

**Online (GitHub):**
```
a1b2c3d Update documentation: reference new Workspace/projects structure
```
(Un commit pulito, ben descritto, professionale)

**Localmente (il tuo branch di lavoro):**
```
a1b2c3d tentativo 1
b2c3d4e fix bug
c3d4e5f refactor
d4e5f6g final touches
```
(Tutta la storia preservata se ti serve consultarla)

---

## Quando applicare questa regola

- ✅ Prima di ogni push su `main`
- ✅ Prima di push su branch ufficiali
- ❌ Non necessario per branch temporanei personali
- ❌ Non necessario per push su feature branches private (dipende dal workflow)

---

## Note importanti

- **Rebase interattivo è non-distruttivo**: Se sbagli, puoi sempre annullare con `git reflog`
- **La storia locale non viene mai persa**: Il rebase modifica solo come appare online
- **Commit message importanti**: Scrivi sempre un messaggio chiaro nel commit finale squashato
- **Quando in dubbio**: Fai il squash prima di pushare su un branch "pubblico" (main, release, etc.)

---

## Esempio pratico dal progetto

Quando abbiamo aggiornato la documentazione, avremmo potuto fare così:

```powershell
# Crea branch di lavoro
git checkout -b docs/workspace-updates

# Fai i commit (non preoccuparti della storia)
git commit -m "fix pt docs"
git commit -m "fix de docs"
git commit -m "fix ru docs"
git commit -m "fix zh docs"
git commit -m "fix architettura"

# Prima di pushare, squasha
git rebase -i main

# Risultato: 1 commit pulito online
# "Update remaining usage guides to reference Workspace/projects/{name} structure"
```

---

**Questa è una convenzione personale. Seguirla mantiene il repository pulito e la tua storia di lavoro privata.**
