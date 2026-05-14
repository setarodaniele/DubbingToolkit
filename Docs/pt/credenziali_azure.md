> ⚠️ **AVISO — Segurança das Credenciais**
>
> As credenciais contidas neste arquivo são estritamente pessoais e diretamente vinculadas ao seu faturamento.
> Qualquer pessoa que as obtenha poderá usar o serviço às suas custas, potencialmente gerando custos significativos.
>
> - Nunca compartilhe este arquivo com ninguém
> - Não o faça upload em repositórios públicos (GitHub, etc.)
> - Não o envie por e-mail ou chat
> - Se perdido ou comprometido, revogue imediatamente a chave no portal do provedor e gere uma nova

# Configuração de Credenciais Azure

Este guia descreve como obter e configurar as credenciais para o Azure Cognitive Services Speech, necessárias para síntese de voz via provedor Azure.

> Um guia em vídeo detalhado sobre como criar credenciais Azure estará disponível no futuro.

---

## Arquivo de Credenciais

O arquivo a ser preenchido é:

```
credentials/azure_speech_credentials.json
```

A estrutura necessária é a seguinte:

```json
{
  "subscription": "YOUR_AZURE_SPEECH_KEY",
  "region": "YOUR_AZURE_REGION"
}
```

Um arquivo de template com esta estrutura já está disponível no projeto:

```
credentials/azure_speech_credentials.template.json
```

Copie-o, renomeie-o removendo a extensão `.template` e preencha os campos.

---

## Campos Necessários

### `subscription`

A chave de API para o serviço Azure Cognitive Services Speech. Pode ser encontrada no portal Azure, na seção **Chaves e Ponto de Extremidade** do recurso de Fala.

### `region`

A região Azure associada ao recurso (ex.: `westeurope`, `eastus`, `northeurope`). Deve corresponder exatamente à região selecionada na criação do recurso.

---

## Como Obter as Credenciais

1. Entre no [portal Azure](https://portal.azure.com)
2. Pesquise ou crie um recurso de **Fala** (Cognitive Services)
3. No recurso criado, abra a seção **Chaves e Ponto de Extremidade**
4. Copie uma das duas chaves disponíveis (`CHAVE 1` ou `CHAVE 2`) — ambas funcionam
5. Anote o **Local/Região** do recurso — este corresponde ao valor de `region`

---

## Exemplo Preenchido

```json
{
  "subscription": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4",
  "region": "westeurope"
}
```

---

## Notas

- As chaves Azure têm 32 caracteres hexadecimais.
- O serviço de Fala requer um plano ativo (um plano gratuito com limite mensal de caracteres está disponível).
- Se as credenciais forem inválidas, o sistema reportará isso quando o módulo TTS for iniciado.
