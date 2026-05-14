# Limitações e notas

Este documento reúne de forma transparente as limitações atuais do DubbingToolkit, as funcionalidades ainda não implementadas e os comportamentos conhecidos que podem não corresponder às expectativas. O projeto está em desenvolvimento ativo e estas limitações estão destinadas a ser resolvidas progressivamente.

---

## Definições não persistentes

As definições não são guardadas entre sessões. A cada arranque o sistema recomeça com os valores predefinidos e pede o idioma da interface. Todas as outras preferências — provedor TTS, voz, modelo Whisper, idiomas de transcrição e tradução — devem ser selecionadas novamente a cada vez. A persistência das definições está planeada como melhoria futura.

---

## Sem modo em lote

O fluxo está concebido para processar um ficheiro de cada vez. Não existe um modo para processar automaticamente vários ficheiros em sequência. Esta funcionalidade é considerada para desenvolvimentos futuros.

---

## Qualidade da tradução

A tradução usa modelos Helsinki-NLP em execução local. A qualidade pode ser inferior em comparação com serviços de tradução profissional em nuvem, especialmente em frases idiomáticas, termos técnicos ou textos com pontuação irregular. É sempre recomendada uma verificação manual do texto traduzido antes de prosseguir para a síntese.

---

## Sem verificação automática de temporização

Após a tradução, o texto pode ser mais longo ou mais curto do que o original, criando inconsistências com as temporizações da fala no vídeo. De momento não existe um sistema automático de verificação ou adaptação. A gestão das temporizações requer intervenção manual no ficheiro SRT traduzido. Um sistema automático de verificação e adaptação está planeado como melhoria futura.

---

## Transcrição: deteção automática de idioma

O Whisper deteta automaticamente o idioma da fala, mas em áudio com ruído, sotaques acentuados ou de baixa qualidade pode cometer erros. Nestes casos é necessário especificar manualmente o idioma antes da transcrição. Um sistema de avaliação da confiança da deteção está planeado como melhoria futura.

---

## Transcrição: gestão da memória

Ficheiros de áudio muito longos são carregados inteiramente na memória durante a transcrição. Em sistemas com RAM limitada, isto pode causar lentidão ou interrupções. O processamento por blocos está planeado como melhoria futura.

---

## WhisperX não integrado

O ambiente para WhisperX está preparado mas ainda não integrado na pipeline principal. Atualmente é utilizado exclusivamente o Whisper padrão.

---

## Legendas não disponíveis

A função de exportação de legendas está presente no menu mas ainda não implementada. Ao selecioná-la o sistema não produz saída.

---

## Provedores TTS adicionais não ligados

Atualmente são suportados Azure e Google. No futuro está prevista a integração de provedores adicionais, incluindo OpenAI e ElevenLabs.

---

## Tradução pivot não disponível

Se o par de idiomas direto origem→destino não estiver disponível nos modelos Helsinki-NLP, a tradução não é possível. A tradução via idioma pivot (inglês como intermediário) está planeada mas ainda não implementada.

---

## Portabilidade limitada

O projeto pode ser movido para outra localização, mas requer a reconstrução do ambiente virtual após cada deslocação. Não é um sistema completamente portável.

---

## Processamento sequencial

As fases da pipeline são executadas em sequência. Não é possível paralelizar o processamento de vários ficheiros ou executar fases simultaneamente.
