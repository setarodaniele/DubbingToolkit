# Guia de Uso

Este guia descreve o fluxo de trabalho operacional do DubbingToolkit, desde a preparação dos arquivos de entrada até o áudio dublado final.

---

## Iniciando o Projeto

Dê um duplo clique em `StartDubbing.bat`. O projeto é iniciado e apresenta a interface principal com o menu de gerenciamento de projetos.

---

## Criando e Selecionando um Projeto

Na tela principal, selecione "Gerenciamento de Projetos" (opção 0) e crie um novo projeto. Cada projeto é um espaço de trabalho isolado para um vídeo específico.

Uma vez criado, o projeto é definido como ativo e permanece disponível para operações subsequentes.

---

## Fluxo de Trabalho Operacional

O processo consiste em 4 etapas. Cada etapa pode ser executada individualmente ou como parte do fluxo completo.

| Etapa | Operação               | Pasta de saída                                         |
|-------|------------------------|--------------------------------------------------------|
| 1     | Extração de áudio      | `Workspace/projects/{nome}/audio_extraction/current/` |
| 2     | Transcrição            | `Workspace/projects/{nome}/transcripts/current/`      |
| 3     | Tradução               | `Workspace/projects/{nome}/translated/current/`       |
| 4     | Síntese de voz (TTS)   | `Workspace/projects/{nome}/dubbed/current/`           |

> **Importante:** após a transcrição e após a tradução, recomenda-se uma revisão manual do texto gerado. As correções permitem melhorar a qualidade do áudio final e lidar com possíveis descompassos de timing em relação à fala original.

---

## Preparando a Entrada

### Entrada de Vídeo

Durante a extração de áudio, o sistema apresenta um diálogo de importação que permite:
1. Usar o vídeo de uma localização externa (mantém o caminho original)
2. Copiar o vídeo para o projeto (`Workspace/projects/{nome}/video_input/`)
3. Mover o vídeo para o projeto

Formatos suportados: aqueles manipulados pelo ffmpeg (mp4, mkv, avi, mov, etc.).

### Entrada de Áudio Direta

Se você já tem áudio extraído, durante a transcrição pode selecionar manualmente um arquivo de áudio da pasta `Workspace/projects/{nome}/audio_input/` ou de uma localização externa. Nesse caso, a Etapa 1 — Extração de áudio pode ser omitida.

---

## Etapa 1 — Extração de Áudio

O sistema extrai as faixas de áudio do vídeo via ffmpeg. Todos os arquivos de áudio extraído são salvos em `Workspace/projects/{nome}/audio_extraction/current/` com nomes `track_01.wav`, `track_02.wav`, etc.

Para cada faixa, um arquivo de metadados é gerado automaticamente (`track_XX_metadata.json`) contendo informações sobre codec, taxa de amostragem, duração e outras propriedades.

---

## Etapa 2 — Transcrição

O áudio é transcrito no formato SRT. O idioma falado é detectado automaticamente e pode ser alterado no menu antes de iniciar a transcrição. O resultado é salvo em `Workspace/projects/{nome}/transcripts/current/`.

> **Dica:** antes de prosseguir para a tradução, revise e corrija o texto transcrito. Erros nesta etapa se propagam para todas as etapas subsequentes.

---

## Etapa 3 — Tradução

O arquivo SRT transcrito é traduzido para o idioma de destino. A tradução ocorre inteiramente de forma local. Os modelos necessários são baixados automaticamente na primeira execução para cada par de idiomas. O resultado é salvo em `Workspace/projects/{nome}/translated/current/`.

Se o par de idiomas direto não estiver disponível, a tradução via idioma pivot (inglês como intermediário) está planejada para o futuro.

> **Dica:** revise o texto traduzido antes de iniciar a síntese. Correções manuais permitem lidar com possíveis descompassos de timing em relação à fala original.

---

## Etapa 4 — Síntese de Voz (TTS)

O texto traduzido é sintetizado segmento por segmento via o provedor TTS selecionado. Os segmentos são então unidos no arquivo de áudio final, salvo em `Workspace/projects/{nome}/dubbed/current/`.

### Provedores TTS

O sistema suporta atualmente dois provedores:

- **Azure Cognitive Services Speech** — serviço TTS na nuvem da Microsoft
- **Google Cloud Text-to-Speech** — serviço TTS na nuvem do Google

O provedor e a voz são selecionados diretamente no menu TTS. O sistema inclui uma função dedicada para ouvir amostras de áudio das vozes disponíveis antes de iniciar a síntese.

### Monitoramento de Consumo

Quando o módulo TTS é iniciado, uma estimativa de uso é exibida automaticamente. Para verificar o consumo real, consulte diretamente o painel do seu provedor.

---

## Idioma da Interface

O idioma da interface é selecionado na inicialização e pode ser alterado a qualquer momento no menu de configurações sem reiniciar o projeto.

---

## Gerenciamento de Projetos

### Duplicação

Você pode duplicar um projeto existente para criar uma cópia com um novo nome. Útil para testar variações da mesma fonte.

### Renomear

Um projeto pode ser renomeado a qualquer momento no gerenciamento de projetos. Se o projeto estiver ativo, o ponteiro ativo é atualizado automaticamente.

### Exclusão

Um projeto pode ser excluído. Se a configuração `use_trash` estiver habilitada, o projeto é movido para a Lixeira; caso contrário, é excluído permanentemente.

### Abrir Pasta

Você pode abrir a pasta de um projeto diretamente no Explorer para inspecionar manualmente os arquivos gerados.

---

## Dicas Operacionais

- Use nomes curtos de projeto e arquivo sem espaços ou caracteres especiais para evitar problemas relacionados a caminhos.
- Os arquivos em `Workspace/projects/{nome}/video_input/` nunca são modificados pelo sistema.
- Cada etapa gera metadados (arquivos `.json` ou `_info.txt`): úteis para acompanhar o progresso ou diagnosticar problemas.
- Se o processo for interrompido, você pode retomá-lo a partir da próxima etapa após a já concluída, usando os arquivos nas pastas de saída intermediárias.
- Os arquivos processados em cada etapa são arquivados automaticamente na pasta `archive/` dessa etapa para preservar o histórico.
