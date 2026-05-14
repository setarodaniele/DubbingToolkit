> ⚠️ **ADVERTENCIA — Seguridad de las credenciales**
> Las credenciales son estrictamente personales y están vinculadas a tu facturación. Cualquier persona con acceso podría usar el servicio a tu cargo.
> - Nunca compartas este archivo
> - Nunca lo subas a repositorios públicos
> - Nunca lo envíes por correo electrónico o chat
> - Si se ve comprometido, revócalo inmediatamente desde el portal del proveedor

# Configuración de credenciales Azure

Guía para obtener y configurar las credenciales de Azure Cognitive Services Speech.

> En el futuro estará disponible una guía en vídeo detallada.

## Archivo de credenciales

```
credentials/azure_speech_credentials.json
```

```json
{
  "subscription": "YOUR_AZURE_SPEECH_KEY",
  "region": "YOUR_AZURE_REGION"
}
```

Plantilla: `credentials/azure_speech_credentials.template.json`

## Campos obligatorios

- **`subscription`**: clave de API del portal de Azure → **Claves y punto de conexión**
- **`region`**: región de Azure (p. ej. `westeurope`, `eastus`, `northeurope`)

## Cómo obtener las credenciales

1. [Portal de Azure](https://portal.azure.com)
2. Crea un recurso **Speech** (Cognitive Services)
3. Abre **Claves y punto de conexión**
4. Copia la CLAVE 1 o la CLAVE 2
5. Anota la región

## Ejemplo

```json
{
  "subscription": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4",
  "region": "westeurope"
}
```

## Notas

- 32 caracteres hexadecimales
- Nivel gratuito disponible con límite mensual de caracteres
- Las credenciales no válidas se detectan al iniciar el TTS
