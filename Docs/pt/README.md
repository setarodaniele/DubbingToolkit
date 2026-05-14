# DubbingToolkit

> ⚠️ **Aviso**: Esta documentação foi traduzida automaticamente e pode conter erros ou imprecisões. Para uma compreensão detalhada, consulte a versão em [inglês](../en/README.md).

**DubbingToolkit** é um sistema de dublagem híbrido Python + PowerShell que permite transcrever, traduzir e ressintesizar conteúdo de áudio/vídeo em múltiplos idiomas, usando motores TTS profissionais (Azure, Google) e modelos locais de transcrição (Whisper).

---

## Índice da Documentação

| Arquivo | Conteúdo |
|---|---|
| [README.md](README.md) | Esta página — visão geral |
| [instalacao.md](instalacao.md) | Requisitos, configuração inicial e instalação |
| [uso.md](uso.md) | Guia operacional e fluxo de trabalho |
| [arquitetura.md](arquitetura.md) | Estrutura do projeto, módulos e convenções |
| [faq.md](faq.md) | Perguntas frequentes e solução de problemas |
| [limitacoes_e_notas.md](limitacoes_e_notas.md) | Limitações atuais e funcionalidades ainda não implementadas |
| [credenziali_azure.md](credenziali_azure.md) | Configuração de credenciais Azure |
| [credenziali_google.md](credenziali_google.md) | Configuração de credenciais Google |

---

## O Que Faz

O DubbingToolkit orquestra as principais etapas da dublagem — extração de áudio, transcrição, tradução e síntese de voz — reduzindo drasticamente o trabalho manual e centralizando todo o processo em um único pipeline controlado.

1. **Extração de áudio** — Extrai faixas de áudio de arquivos de vídeo via ffmpeg. Pode ser ignorada se você já tiver o áudio.
2. **Transcrição** — Transcreve o áudio no formato SRT via Whisper.
3. **Tradução** — Traduz as legendas SRT para o idioma de destino usando modelos Helsinki-NLP executados localmente, sem dependência de APIs externas.
4. **Síntese de voz (TTS)** — Gera o áudio dublado segmento por segmento via Azure TTS ou Google TTS, depois une os segmentos no arquivo de áudio final.

---

## Idiomas Suportados

A interface do sistema está atualmente disponível em 8 idiomas:

| Código | Idioma |
|---|---|
| `it` | Italiano |
| `en` | Inglês |
| `es` | Espanhol |
| `de` | Alemão |
| `fr` | Francês |
| `pt` | Português |
| `ru` | Russo |
| `zh` | Chinês |

Os idiomas de transcrição e tradução dependem do Whisper e dos modelos Helsinki-NLP disponíveis, respectivamente. Consulte `locale/` para detalhes.

---

## Provedores TTS Suportados Atualmente

- **Azure Cognitive Services Speech** — alta qualidade, vozes neurais, ampla cobertura de idiomas
- **Google Cloud Text-to-Speech** — alternativa confiável com boa variedade de vozes

Ambos os provedores requerem credenciais de API configuradas localmente. Consulte [instalacao.md](instalacao.md).

---

## Ponto de Entrada

O projeto é iniciado a partir de um único arquivo:

```
StartDubbing.bat
```

Todo o restante é orquestrado automaticamente pelo Launcher.

---

## Status do Projeto

O DubbingToolkit está em desenvolvimento ativo. Algumas funcionalidades já estão operacionais no pipeline principal; outras estão planejadas como melhorias futuras (segmentação avançada, pós-processamento de texto, tradução pivot, etc.). Consulte [arquitetura.md](arquitetura.md) para detalhes sobre o status dos módulos.
