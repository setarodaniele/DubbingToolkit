# Instalação e Configuração

Este guia aborda os requisitos do sistema, a estrutura de credenciais e o processo de configuração inicial do DubbingToolkit.

---

## Requisitos do Sistema

- **Sistema operacional:** Windows com PowerShell 5.1
- **Python:** incluído no projeto — nenhuma instalação no sistema é necessária
  - O Python 3.11 é a versão atualmente utilizada, localizado na pasta `Installation/` e gerenciado internamente.
- **ffmpeg:** incluído em `Tools/ffmpeg-7.1.1-full_build/` — nenhuma instalação separada é necessária
- **Conexão com a internet:** necessária para módulos que acessam recursos externos, incluindo APIs de TTS (Azure, Google) e downloads de modelos de tradução na primeira execução.

---

## Credenciais TTS

As credenciais dos provedores TTS devem ser colocadas na pasta `credentials/`. Os provedores suportados atualmente são Azure e Google, cada um com seu próprio arquivo JSON.

| Arquivo | Provedor |
|---|---|
| `azure_speech_credentials.json` | Azure Cognitive Services Speech |
| `google_speech_credentials.json` | Google Cloud TTS |

Um arquivo de template com a estrutura necessária está disponível para cada provedor:

```
credentials/azure_speech_credentials.template.json
credentials/google_speech_credentials.template.json
```

Copie o arquivo de template, remova a extensão `.template` e preencha suas credenciais no arquivo resultante.

---

## Ambiente Virtual e Dependências Python

Quando o projeto é iniciado, o Launcher gerencia automaticamente a criação e ativação do ambiente virtual, além da instalação das dependências. Nenhuma intervenção manual é necessária em condições normais.

As principais dependências estão listadas em `Scripts/requirements.txt`.

### Reinicialização do Ambiente Virtual

**Reinicialização a partir do projeto** (o projeto deve conseguir iniciar):

Selecione a opção de reinicialização na interface, ou execute diretamente:
```powershell
Scripts/reset_env.ps1
```
Esse script recria o venv e reinstala as dependências automaticamente.

**Reinicialização manual completa** (quando o projeto não inicia):

Delete manualmente a pasta `venv/`. Na próxima inicialização via `StartDubbing.bat`, o Launcher detectará o venv ausente e o recriará automaticamente.

---

## Configuração Inicial

As configurações operacionais do projeto estão em `Settings/`:

| Arquivo | Finalidade |
|---|---|
| `settings.json` | Configuração ativa |
| `settings_default.json` | Configuração de referência (não modificar) |
| `reset.json` | Parâmetros de reinicialização |

### Parâmetros Principais em `settings.json`

- **`interface_lang`** — idioma da interface (ex.: `"it"`, `"en"`, `"es"`)
- Configurações do provedor TTS (provedor ativo, voz selecionada, idioma de destino)
- Parâmetros de transcrição do Whisper (modelo, idioma)

> **Nota:** as configurações não são persistentes entre sessões. Na inicialização, o idioma da interface é solicitado; todas as demais configurações são redefinidas para os valores padrão. A persistência de configurações está planejada como melhoria futura.

---

## Inicialização e Configuração Automática

O usuário inicia o projeto via:

```
StartDubbing.bat
```

O Launcher então executa automaticamente as seguintes etapas, sem intervenção do usuário:

1. Verificação e ativação do runtime Python local
2. Criação ou ativação do ambiente virtual
3. Verificação das credenciais de API
4. Inicialização da interface principal

Se as credenciais estiverem ausentes ou inválidas, o sistema reportará isso no menu antes de conceder acesso às funções TTS.
As demais funções — extração de áudio, transcrição e tradução — não dependem de credenciais e permanecem acessíveis.

---

## Mover o Projeto e Desinstalar

Embora não seja recomendado, o projeto pode ser movido para um local diferente no disco ou para outra máquina, mas após cada movimentação o ambiente virtual deve ser recriado, pois o venv contém caminhos absolutos vinculados à localização original. Procedimento:

1. Delete a pasta `venv/`
2. Inicie `StartDubbing.bat` — o Launcher recriará o venv e reinstalará as dependências

Se o projeto foi instalado via pacote de distribuição, após uma movimentação a entrada em **Aplicativos e Recursos** do Windows não será mais válida. Não é necessário utilizá-la: para desinstalar o projeto, basta deletar a pasta inteira. Nenhum arquivo é gravado fora dela.
