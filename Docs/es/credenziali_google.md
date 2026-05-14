> ⚠️ **ADVERTENCIA — Seguridad de las credenciales**
> Nunca compartas este archivo ni lo subas a repositorios públicos. Revócalo inmediatamente si se ve comprometido.

# Configuración de credenciales Google

Guía para obtener las credenciales de Google Cloud Text-to-Speech.

## Archivo de credenciales

```
credentials/google_speech_credentials.json
```

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

## Campos a rellenar

| Campo | Descripción |
|---|---|
| `project_id` | ID del proyecto de Google Cloud |
| `private_key_id` | ID de la clave privada de la cuenta de servicio |
| `private_key` | Clave PEM con cabeceras BEGIN/END |
| `client_email` | Correo electrónico de la cuenta de servicio |
| `client_id` | ID numérico de la cuenta de servicio |
| `client_x509_cert_url` | URL del certificado X509 |

## Cómo obtenerlas

1. [Google Cloud Console](https://console.cloud.google.com)
2. Habilita la **API de Cloud Text-to-Speech**
3. IAM → Cuentas de servicio → Crea una con el rol **Cloud Text-to-Speech Agent**
4. Claves → Crear clave JSON → Descargar
5. Copia el archivo en `credentials/google_speech_credentials.json`

## Notas

- El JSON descargado ya tiene el formato correcto
- La clave privada no puede recuperarse tras su creación
- Nivel gratuito disponible
