> ⚠️ **ATENÇÃO — Segurança das credenciais**
> 
> As credenciais contidas neste arquivo são estritamente pessoais e diretamente vinculadas à sua faturação.
> Qualquer pessoa que as obtenha pode usar o serviço às suas custas, potencialmente gerando custos elevados.
> 
> - Nunca compartilhe este arquivo com ninguém
> - Não o carregue em repositórios públicos (GitHub, etc.)
> - Não o envie por e-mail ou chat
> - Em caso de perda ou comprometimento, revogar imediatamente a chave no portal do provedor e gerar uma nova

# Configuração de credenciais Google

Este guia descreve como obter e configurar as credenciais para o Google Cloud Text-to-Speech, necessárias para a síntese de voz via provedor Google.

> No futuro estará disponível um guia em vídeo detalhado sobre como criar as credenciais do Google Cloud.

---

## Arquivo de credenciais

O arquivo a preencher é:

```
credentials/google_speech_credentials.json
```

A estrutura necessária é a seguinte:

```json
{
  "type": "service_account",
  "project_id": "YOUR_PROJECT_ID",
  "private_key_id": "YOUR_PRIVATE_KEY_ID",
  "private_key": "YOUR_PRIVATE_KEY",
  "client_email": "YOUR_CLIENT_EMAIL",
  "client_id": "YOUR_CLIENT_ID",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "YOUR_CLIENT_CERT_URL",
  "universe_domain": "googleapis.com"
}
```

Um arquivo template com esta estrutura já está disponível no projeto:

```
credentials/google_speech_credentials.template.json
```

Copie-o, renomeie-o removendo a extensão `.template` e preencha os campos com os valores da sua conta de serviço.

---

## Campos obrigatórios

Os campos com valor fixo (`type`, `auth_uri`, `token_uri`, `auth_provider_x509_cert_url`, `universe_domain`) não devem ser modificados — são iguais para todas as contas Google Cloud.

Os campos a preencher são:

| Campo | Descrição |
|---|---|
| `project_id` | ID do projeto Google Cloud |
| `private_key_id` | ID da chave privada da conta de serviço |
| `private_key` | Chave privada em formato PEM (incluindo cabeçalhos `-----BEGIN/END PRIVATE KEY-----`) |
| `client_email` | E-mail da conta de serviço (ex. `nome@projeto.iam.gserviceaccount.com`) |
| `client_id` | ID numérico da conta de serviço |
| `client_x509_cert_url` | URL do certificado X509 da conta de serviço |

---

## Como obter as credenciais

1. Aceder à [Google Cloud Console](https://console.cloud.google.com)
2. Criar ou selecionar um projeto existente
3. Ativar a API **Cloud Text-to-Speech** na seção **APIs e serviços**
4. Ir a **IAM e administração → Contas de serviço**
5. Criar uma nova conta de serviço com o papel **Cloud Text-to-Speech Agent** (ou equivalente com acesso TTS)
6. Na aba **Chaves** da conta de serviço, criar uma nova chave em formato **JSON**
7. Descarregar o ficheiro JSON gerado — contém todos os campos necessários já preenchidos
8. Copiar o conteúdo do ficheiro descarregado para `credentials/google_speech_credentials.json`

---

## Notas

- O ficheiro JSON descarregado da Google Cloud Console já está no formato correto e pode ser usado diretamente sem modificações.
- Conserve o ficheiro de forma segura: a chave privada não pode ser recuperada após a criação.
- Em caso de credenciais inválidas ou expiradas, gerar uma nova chave na Console e atualizar o ficheiro.
- O serviço Cloud Text-to-Speech prevê um plano gratuito com limite mensal de caracteres.
