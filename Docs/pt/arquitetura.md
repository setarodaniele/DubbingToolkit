# Arquitetura e referência técnica

Este documento descreve a estrutura interna do projeto, os módulos principais, as convenções de desenvolvimento e o estado dos componentes. Destina-se principalmente a quem contribui para o desenvolvimento ou quer entender o funcionamento interno do sistema.

---

## Estrutura de pastas

```
DubbingToolkit/
├── Audio_Extracted/        Saída de extração de áudio (subpastas por arquivo)
├── Audio_Input/            Áudio de entrada direto
├── Billing/                Monitoramento de consumo e custos TTS
├── core/                   Módulos de suporte Python compartilhados
├── credentials/            Credenciais de API (excluídas do Git)
├── Dubbed/                 Saída TTS final (por provedor)
├── Installation/           Runtimes Python locais (3.10, 3.11)
├── installer/              Sistema de build e empacotamento
├── locale/                 Localização e gerenciamento de idiomas
│   ├── Active/             Arquivos JSON de idioma ativos (it, en, es, de, fr, pt, ru, zh)
│   └── System/             Metadados de idiomas (Whisper, idiomas suportados)
├── Logs/                   Logs operacionais
├── ps/                     Módulos PowerShell (logging, mensagens)
├── Repository/             Recursos compartilhados e modelos locais
├── Scripts/                Scripts operacionais e módulos Python
│   └── maintenance/        Scripts de manutenção e pipeline de localização
├── Settings/               Configuração ativa e de referência
├── Subtitles/              Legendas (a implementar)
├── Temp/                   Arquivos temporários
├── Tools/                  Binários externos (ffmpeg)
├── Transcripts/            Transcrições SRT (subpastas por arquivo)
├── Translated/             Traduções SRT (subpastas por arquivo)
├── venv/                   Ambiente virtual Python principal
├── Video_Input/            Vídeos fonte (nunca modificados)
└── voices/                 Vozes TTS disponíveis e amostras de áudio
```

---

## Cadeia de inicialização

```
StartDubbing.bat
  └→ Scripts/Launcher.ps1
       Ativa venv, configura UTF-8, log, carregamento de idioma
         └→ Scripts/Regista.py
              Menu principal e orquestração da pipeline
```

O Launcher gerencia: seleção do runtime Python local (`Installation/`), criação/ativação do venv, configuração do sistema de log, carregamento do idioma da interface.

`Regista.py` é o coordenador central: apresenta o menu ao usuário e delega a execução aos módulos específicos para cada fase.

---

## Pipeline operacional

| Fase | Módulo | Entrada → Saída |
|---|---|---|
| 1 — Extração de áudio | `Scripts/estrai_tracce.py` | `Video_Input/` → `Audio_Extracted/<ts>/` |
| 2 — Transcrição | `Scripts/trascrivi_audio.py` | `Audio_Extracted/` ou `Audio_Input/` → `Transcripts/<ts>/` (SRT) |
| 3 — Tradução | `Scripts/traduci_testo.py` | `Transcripts/` → `Translated/<ts>/` (SRT) |
| 4 — TTS | `Scripts/tts_menu.py` | `Translated/` → `Dubbed/` (MP3/WAV) |

`tts_menu.py` delega para `tts_azure.py` ou `tts_google.py` conforme o provedor ativo.

---

## Módulos core (`core/`)

Estes módulos são compartilhados por toda a pipeline. Não devem ser chamados diretamente pelo usuário.

### `messages.py`
Sistema centralizado de mensagens localizadas. Lê `Settings/settings.json` → campo `interface_lang` → carrega `locale/Active/<lang>.json`.

Uso nos scripts:
```python
from core.messages import Messages
msg = Messages()
print(msg._("chave_mensagem"))
```

As chaves ausentes produzem o fallback `[MISSING: chave]` e não causam travamentos. Todas as chaves ausentes devem ser corrigidas antes do lançamento.

### `credentials_manager.py`
Carregamento e validação centralizada das credenciais de API. É o único ponto do projeto autorizado a ler os arquivos em `credentials/`. Nenhum outro módulo deve acessar esses arquivos diretamente.

### `api_check.py`
Verifica a validade das credenciais antes de permitir o acesso ao menu TTS. É invocado automaticamente ao entrar no menu TTS.

### `ui_printer.py` + `ui_colors.py`
Funções para saída no console com formatação e cores. Todos os scripts devem usar estes módulos em vez de `print()` direto, para garantir consistência visual.

### `utils_tts.py`
Utilitários compartilhados para parsing de SRT, usados por ambos os backends TTS.

### `file_selector.py`
Interface para seleção de arquivos via menu interativo.

### `input_parsing.py`
Parsing e validação de entradas do usuário.

---

## Módulos Scripts principais

### `Regista.py`
Orquestrador principal. Gerencia o menu de nível superior e coordena a execução das fases da pipeline. Ponto de entrada Python da aplicação.

### `estrai_tracce.py`
Extração de trilhas de áudio de vídeos via ffmpeg. Gera uma subpasta em `Audio_Extracted/` com os arquivos de áudio e o arquivo `_info.txt`.

### `trascrivi_audio.py`
Transcrição de áudio via Whisper (ou WhisperX, quando integrado). Saída em formato SRT em `Transcripts/`.

### `traduci_testo.py`
Tradução de SRT via modelos Helsinki-NLP MarianMT em execução local. Saída em `Translated/`.

### `tts_dubbing.py` / `tts_menu.py`
Coordenação da pipeline TTS. `tts_menu.py` é a interface do usuário; `tts_dubbing.py` gerencia o fluxo de geração e fusão de segmentos.

### `tts_azure.py` / `tts_google.py`
Backends TTS específicos por provedor. Geram os segmentos de áudio e os salvam em `Dubbed/<PROVIDER>/`.

### `tts_merge.py`
Fusão e sincronização dos segmentos de áudio TTS no arquivo final.

### `tts_config_manager.py`
Gerenciamento de configurações TTS: provedor ativo, voz selecionada, parâmetros de síntese.

### `info_manager.py`
Leitura e escrita do arquivo `project_info.json` nas subpastas com timestamp. Garante a rastreabilidade do estado entre as fases.

### `settings_manager.py`
Leitura, validação e acesso às configurações em `Settings/settings.json`.

### `monitoraggio_consumo.py`
Acesso thread-safe ao registro de consumo TTS em `Billing/consumo_tts.json`.

### `menu_lingue.py` / `menu_lingue_tts.py`
Seleção de idiomas para transcrição/tradução e para a pipeline TTS.

### `menu_voices.py`
Seleção e configuração de vozes TTS pela interface.

### `backup_utils.py`
Gerenciamento de backups e histórico de arquivos gerados.

---

## Sistema de localização

### Estrutura

```
locale/
├── Active/              Arquivos de idioma ativos (runtime)
│   ├── it.json
│   ├── en.json
│   ├── es.json
│   ├── de.json
│   ├── fr.json
│   ├── pt.json
│   ├── ru.json
│   └── zh.json
└── System/
    ├── languages.json           Idiomas conceitualmente suportados
    └── whisper_languages.json   Idiomas suportados pelo Whisper
```

### Regras

- Todas as mensagens da interface Python devem usar `core/messages.py`.
- Todos os arquivos em `locale/Active/` devem ser sincronizados: uma chave presente em `it.json` deve existir em todos os outros arquivos de idioma.
- As chaves ausentes produzem `[MISSING: key]` em tempo de execução — não são permitidas em ambiente estável.
- PowerShell usa `ps/Messages.psm1` (sistema equivalente, separado).

### Pipeline de manutenção de localização

Em `Scripts/maintenance/translation/` está disponível uma pipeline completa para gerenciar os arquivos de idioma:

| Script | Função |
|---|---|
| `LocaleKeyAnalyzer.ps1` | Análise de chaves ausentes e inconsistências entre arquivos |
| `LocaleTranslator.ps1` | Tradução automática com proteção de placeholders |
| `Validate-LocaleJson.ps1` | Validação de estrutura e integridade JSON |
| `Fix-LocaleDuplicates.ps1` | Correção de chaves duplicadas |
| `Clean-LocaleUnusedKeys.ps1` | Remoção de chaves não utilizadas |
| `Extract-Placeholders.ps1` | Extração e mapeamento de placeholders |
| `Protect-Placeholders.ps1` | Proteção de placeholders durante tradução automática |

---

## Configuração (`Settings/settings.json`)

Campos principais:

```json
{
  "interface_lang": "it",
  "model": "small",
  "Transcript_Audio_Spoken_Lang": "it",
  "Translation_Target_Lang": "en",
  "Dubbing_Lang": "en"
}
```

| Campo | Descrição |
|---|---|
| `interface_lang` | Idioma da interface do usuário |
| `model` | Modelo Whisper a usar (`tiny`, `base`, `small`, `medium`, `large`) |
| `Transcript_Audio_Spoken_Lang` | Idioma falado no áudio fonte |
| `Translation_Target_Lang` | Idioma de destino para tradução |
| `Dubbing_Lang` | Idioma para síntese TTS |

---

## Gerenciamento de vozes TTS

As vozes disponíveis são catalogadas em `voices/`:

| Arquivo | Conteúdo |
|---|---|
| `voices_azure.json` | Vozes Azure filtradas e prontas para uso |
| `voices_azure_complete.json` | Catálogo completo Azure |
| `voices_google.json` | Vozes Google filtradas |
| `voices_google_complete.json` | Catálogo completo Google |
| `voices_index.json` | Índice unificado de todas as vozes (Azure + Google) com metadados |

As amostras de áudio das vozes (para audição) estão em `voices/voices_output/<provider>/<LANG-CODE>/<voice>.mp3`, se geradas via `Scripts/VoicesRepository.py`.

Para atualizar o catálogo de vozes dos provedores:
```bash
voices/fetch_azure_voices.py
voices/fetch_google_voices.py
```

---

## Sistema de build e distribuição

O projeto inclui um sistema de empacotamento em `installer/`:

```powershell
installer/build.ps1
```

As regras de inclusão/exclusão estão em:

| Arquivo | Propósito |
|---|---|
| `build_include.json` | O que copiar, onde e em que modalidade |
| `build_exclude.json` | Lista negra global (todas as modalidades) |
| `build_exclude_test.json` | Lista negra adicional apenas em modo TEST (Python runtime, ffmpeg, voices) |
| `build_protected.json` | Caminhos copiados literalmente — as regras de exclusão são ignoradas |
| `build_empty_dirs.json` | Pastas vazias a criar no pacote |

Parâmetros disponíveis:
```powershell
.\build.ps1              # menu interativo (opções 1/2/3)
.\build.ps1 -Test        # build leve sem componentes pesados
.\build.ps1 -Production  # build completa com confirmação
.\build.ps1 -DryRun      # simulação sem escrever arquivos
```

A saída vai para `installer/build_payload/`. Os arquivos de credenciais reais nunca são incluídos no build — apenas os arquivos `*.template.json`.

---

## Convenções de desenvolvimento

### Nomenclatura

| Elemento | Convenção |
|---|---|
| Pastas (novas) | `minúsculo_underscore` |
| Módulos Python | `minúsculo_underscore.py` |
| Classes | `CamelCase` |
| Funções e variáveis | `minúsculo_underscore` |
| Scripts de teste | prefixo `test_` obrigatório |

### Estrutura dos scripts

Todos os scripts devem seguir a estrutura numerada definida na Seção 6 de `RecapDubbing.txt`:

```
# 1. IMPORTS / DEPENDENCIES
# 2. CONFIGURATION – Paths, settings, constants
# 3. UTILITIES – Helper functions
# 4. CORE LOGIC – Main processing
# 5. MAIN EXECUTION – Entry point
```

Cada script deve incluir um cabeçalho padrão com nome, descrição, entrada, saída e notas operacionais. Os comentários no código devem ser em inglês.

### Mensagens

- Nenhuma string codificada nos módulos de runtime.
- Todas as mensagens provêm dos arquivos JSON de localização via `core/messages.py` (Python) ou `ps/Messages.psm1` (PowerShell).
- Exceção: scripts de bootstrap e scripts de manutenção podem usar saída não localizada.

### Caminhos

Todos os caminhos devem ser relativos à raiz do projeto. Nenhum caminho absoluto nos módulos de runtime.

### Arquivos gerados

Cada fase da pipeline que gera arquivos cria uma subpasta com formato:
```
<timestamp>_<nome_arquivo_de_entrada>
```
e inclui um arquivo `_info.txt` com metadados do processamento.

---

## Estado dos componentes

| Componente | Estado |
|---|---|
| Extração de áudio | ✅ Operacional |
| Transcrição Whisper | ✅ Operacional |
| Tradução Helsinki-NLP | ✅ Operacional |
| TTS Azure | ✅ Operacional |
| TTS Google | ✅ Operacional |
| Interface multilíngue (8 idiomas) | ✅ Operacional |
| Monitoramento de consumo TTS | ✅ Operacional |
| Sistema de build/packaging | ✅ Operacional |
| Legendas (menu opção 5) | ⚠️ Stub — não implementado |
| Segmentação avançada | ⚠️ Placeholder — não na pipeline |
| WhisperX | ⚠️ Venv preparado, não integrado |
| TTS OpenAI / ElevenLabs | ⚠️ Credenciais presentes, não conectados ao menu |
| Tradução pivot (idioma intermediário) | 🔲 Planejado |
| Pós-processamento de texto (Tradução→TTS) | 🔲 Planejado |
| Modelo baseado em projeto (pasta única por projeto) | 🔲 Refatoração futura |
