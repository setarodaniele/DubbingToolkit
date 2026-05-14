> ⚠️ **警告——凭据安全**
> 
> 本文件中的凭据严格属于个人信息，直接与您的账单挂钩。
> 任何获得这些凭据的人都可以以您的名义使用服务，可能产生高额费用。
> 
> - 切勿与任何人分享此文件
> - 不要上传到公共代码仓库（GitHub 等）
> - 不要通过电子邮件或聊天发送
> - 如果凭据丢失或泄露，请立即在提供商门户撤销密钥并生成新密钥

# Google 凭据配置

本指南介绍如何获取和配置 Google Cloud Text-to-Speech 的凭据，这是通过 Google 提供商进行语音合成的必要条件。

> 未来将提供关于如何创建 Google Cloud 凭据的详细视频指南。

---

## 凭据文件

需要填写的文件为：

```
credentials/google_speech_credentials.json
```

所需结构如下：

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

项目中已提供包含此结构的模板文件：

```
credentials/google_speech_credentials.template.json
```

复制该文件，删除 `.template` 扩展名后重命名，然后用您的服务账号值填写各字段。

---

## 必填字段

固定值字段（`type`、`auth_uri`、`token_uri`、`auth_provider_x509_cert_url`、`universe_domain`）无需修改——所有 Google Cloud 账号均相同。

需要填写的字段：

| 字段 | 描述 |
|---|---|
| `project_id` | Google Cloud 项目 ID |
| `private_key_id` | 服务账号私钥 ID |
| `private_key` | PEM 格式的私钥（包含 `-----BEGIN/END PRIVATE KEY-----` 标头） |
| `client_email` | 服务账号电子邮件（例如 `名称@项目.iam.gserviceaccount.com`） |
| `client_id` | 服务账号的数字 ID |
| `client_x509_cert_url` | 服务账号的 X509 证书 URL |

---

## 如何获取凭据

1. 登录 [Google Cloud Console](https://console.cloud.google.com)
2. 创建或选择现有项目
3. 在 **API 和服务**部分启用 **Cloud Text-to-Speech** API
4. 转到 **IAM 和管理 → 服务账号**
5. 创建一个具有 **Cloud Text-to-Speech Agent** 角色（或具有 TTS 访问权限的等效角色）的新服务账号
6. 在服务账号的**密钥**选项卡中，创建一个 **JSON** 格式的新密钥
7. 下载生成的 JSON 文件——其中包含所有已填写的必要字段
8. 将下载文件的内容复制到 `credentials/google_speech_credentials.json`

---

## 说明

- 从 Google Cloud Console 下载的 JSON 文件已经是正确格式，可以直接使用，无需修改。
- 请安全保存该文件：私钥创建后无法恢复。
- 如果凭据无效或已过期，请在 Console 生成新密钥并更新文件。
- Cloud Text-to-Speech 服务提供带有每月字符限制的免费套餐。
