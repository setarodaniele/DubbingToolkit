# Perguntas Frequentes e Solução de Problemas

---

## Inicialização e Ambiente

**O projeto não inicia com `StartDubbing.bat`.**

Uma causa comum é a execução de scripts PowerShell estar bloqueada.
Abra o PowerShell como administrador e execute:
```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```
Em seguida, tente iniciar novamente.

---

**O venv parece corrompido ou não consegue ser ativado.**

Delete manualmente a pasta `venv/` dentro da pasta do projeto. Na próxima inicialização via `StartDubbing.bat`, o Launcher detectará o venv ausente e o recriará automaticamente.

---

**Erro `[MISSING: key]` na interface.**

Isso indica que uma chave está ausente do arquivo de localização ativo. Não é um erro bloqueante, mas reduz a clareza da interface. Reporte a chave ausente para que seja corrigida.

---

## Credenciais e API

**O sistema reporta credenciais Azure inválidas.**

Verifique que `credentials/azure_speech_credentials.json` contém os campos `subscription` (chave de API) e `region` (ex.: `westeurope`). Use `credentials/azure_speech_credentials.template.json` como referência para a estrutura correta.

---

**O sistema reporta credenciais Google inválidas.**

`credentials/google_speech_credentials.json` deve ser o arquivo JSON completo de uma conta de serviço GCP com a função Cloud Text-to-Speech habilitada. Verifique se o arquivo não está truncado ou malformado.

> Guias dedicados para criar credenciais Azure e Google estão disponíveis na mesma pasta desta documentação.

---

## Transcrição

**A transcrição produz resultados imprecisos ou no idioma errado.**

Especifique manualmente o idioma de origem pelo menu de idiomas antes de iniciar a transcrição. Os idiomas disponíveis estão listados no menu de seleção de idioma.

---

**A transcrição é muito lenta.**

A velocidade depende do modelo Whisper selecionado e do hardware disponível. O modelo é selecionado diretamente no menu de transcrição antes de iniciar o processo.

| Modelo | Velocidade | Qualidade |
|---|---|---|
| `tiny` | Muito alta | Básica |
| `base` | Alta | Razoável |
| `small` | Média | Boa |
| `medium` | Baixa | Alta |
| `large` | Muito baixa | Máxima |

Em CPU sem GPU dedicada, mesmo o modelo `small` pode ser lento em arquivos longos.

---

**A transcrição para com um erro de memória.**

Arquivos de áudio muito longos carregados inteiramente na RAM podem causar problemas em sistemas com memória limitada. Considere dividir o arquivo de áudio em segmentos menores antes de transcrever.

---

## Tradução

**O par de idiomas desejado não está disponível.**

Nem todos os pares de idiomas têm um modelo Helsinki-NLP disponível diretamente. Os pares suportados estão listados no menu de seleção de idioma. A tradução via idioma pivot (inglês como intermediário) está planejada, mas ainda não implementada.

---

**O texto traduzido contém erros ou soa pouco natural.**

Os modelos Helsinki-NLP são modelos de tradução automática e podem produzir imprecisões, especialmente em expressões idiomáticas, termos técnicos ou texto com pontuação irregular. O pós-processamento de texto está planejado como melhoria futura.

---

## Síntese TTS

**O TTS gera áudio com pausas ou ritmo artificiais.**

Verifique a voz selecionada no menu TTS. Vozes neurais (Azure Neural, Google WaveNet) produzem resultados significativamente melhores do que vozes padrão. Você pode ouvir amostras de áudio antes de iniciar a síntese.

---

**A saída do TTS é silenciosa ou contém apenas ruído.**

Abra o arquivo SRT traduzido em `Translated/` com um editor de texto e verifique que ele contém segmentos válidos com texto não vazio.

---

**O monitoramento de uso não está sendo atualizado.**

O uso é registrado em `Billing/consumo_tts.json`. Se o arquivo parecer bloqueado ou corrompido, faça um backup dele, delete-o, e ele será recriado automaticamente no próximo uso.

---

## Arquivos e Pastas

**Não consigo encontrar a saída gerada.**

Cada etapa cria uma subpasta com o formato `<timestamp>_<nome_do_arquivo>` em seu diretório de saída. Procure em:
- `Audio_Extracted/` para o áudio extraído
- `Transcripts/` para as transcrições SRT
- `Translated/` para as traduções SRT
- `Dubbed/<PROVIDER>/` para o áudio dublado final

O arquivo `_info.txt` em cada subpasta mostra os detalhes do processamento.

---

**Movi o projeto e agora ele não funciona mais.**

Delete manualmente a pasta `venv/`. Na próxima inicialização via `StartDubbing.bat`, o Launcher recriará o venv no novo local.

---

## Build e Distribuição

**As credenciais de API não estão incluídas no pacote de distribuição.**

Este é o comportamento correto. As credenciais Azure e Google nunca são incluídas no pacote por razões de segurança. Elas devem ser colocadas manualmente na pasta `credentials/` em cada máquina após a instalação, seguindo a estrutura dos arquivos de template.

---

## Perguntas Gerais

**É possível usar o projeto sem conexão com a internet?**

Parcialmente. A transcrição (Whisper) e a tradução (Helsinki-NLP) funcionam offline após os modelos terem sido baixados. A síntese TTS (Azure, Google) requer conexão com a internet, pois usa APIs na nuvem.

---

**É possível adicionar novos idiomas à interface?**

Sim. Novos idiomas serão adicionados progressivamente ao longo do tempo. Para solicitar um idioma específico, entre em contato diretamente com o projeto. Quem quiser adicioná-lo de forma independente deve:

1. Criar o arquivo `locale/Active/<código_do_idioma>.json` seguindo a estrutura dos outros arquivos de idioma existentes
2. Adicionar o novo idioma em `locale/System/languages.json`

Ambas as etapas são necessárias: sem a segunda, o idioma não será reconhecido pelo sistema.

---

**O projeto suporta processamento em lote de múltiplos vídeos?**

Atualmente o fluxo de trabalho é projetado para um arquivo por vez. Você pode preparar vários arquivos e processá-los em sequência, mas não há modo automático de processamento em lote. Essa funcionalidade está sendo considerada para desenvolvimento futuro.
