> ⚠️ **警告——凭据安全**
> 
> 本文件中的凭据严格属于个人信息，直接与您的账单挂钩。
> 任何获得这些凭据的人都可以以您的名义使用服务，可能产生高额费用。
> 
> - 切勿与任何人分享此文件
> - 不要上传到公共代码仓库（GitHub 等）
> - 不要通过电子邮件或聊天发送
> - 如果凭据丢失或泄露，请立即在提供商门户撤销密钥并生成新密钥

# Azure 凭据配置

本指南介绍如何获取和配置 Azure Cognitive Services Speech 的凭据，这是通过 Azure 提供商进行语音合成的必要条件。

> 未来将提供关于如何创建 Azure 凭据的详细视频指南。

---

## 凭据文件

需要填写的文件为：

```
credentials/azure_speech_credentials.json
```

所需结构如下：

```json
{
  "subscription": "YOUR_AZURE_SPEECH_KEY",
  "region": "YOUR_AZURE_REGION"
}
```

项目中已提供包含此结构的模板文件：

```
credentials/azure_speech_credentials.template.json
```

复制该文件，删除 `.template` 扩展名后重命名，然后填写相应字段。

---

## 必填字段

### `subscription`

Azure Cognitive Services Speech 服务的 API 密钥，可在 Azure 门户中 Speech 资源的**密钥和终结点**部分找到。

### `region`

与资源关联的 Azure 区域（例如 `westeurope`、`eastus`、`northeurope`），必须与创建资源时选择的区域完全一致。

---

## 如何获取凭据

1. 登录 [Azure 门户](https://portal.azure.com)
2. 搜索或创建一个 **Speech**（认知服务）资源
3. 在已创建的资源中，打开**密钥和终结点**部分
4. 复制两个可用密钥之一（`KEY 1` 或 `KEY 2`）——两者均可使用
5. 记录资源的**位置/区域**——对应 `region` 的值

---

## 填写示例

```json
{
  "subscription": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4",
  "region": "westeurope"
}
```

---

## 说明

- Azure 密钥长度为 32 位十六进制字符。
- Speech 服务需要有效套餐（提供带有每月字符限制的免费套餐）。
- 如果凭据无效，系统将在启动 TTS 模块时发出提示。
