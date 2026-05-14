# 常见问题与故障排查

---

## 启动与环境

**使用 `StartDubbing.bat` 无法启动项目。**

常见原因是 PowerShell 脚本执行被阻止。
以管理员身份打开 PowerShell 并执行：
```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```
然后重新尝试启动。

---

**虚拟环境损坏或无法激活。**

手动删除项目文件夹内的 `venv/` 目录。下次通过 `StartDubbing.bat` 启动时，Launcher 将检测到 venv 缺失并自动重新创建。

---

**界面出现 `[MISSING: key]` 错误。**

这表示活动本地化文件中缺少某个键。不会阻止使用，但会降低界面可读性。请报告缺失的键以便修复。

---

## 凭据与 API

**系统提示 Azure 凭据无效。**

请确认 `credentials/azure_speech_credentials.json` 包含 `subscription`（API 密钥）和 `region`（例如 `westeurope`）字段。参考 `credentials/azure_speech_credentials.template.json` 了解正确的结构。

---

**系统提示 Google 凭据无效。**

`credentials/google_speech_credentials.json` 必须是启用了 Cloud Text-to-Speech 角色的 GCP 服务账号完整 JSON 文件。请确认文件未被截断或格式错误。

> Azure 和 Google 凭据的创建方法，请参阅本文档同一目录下的专属指南。

---

## 转录

**转录结果不准确或语言识别错误。**

在开始转录前，请通过语言菜单手动指定源语言。可用语言列于语言选择菜单中。

---

**转录速度非常慢。**

速度取决于所选的 Whisper 模型和可用硬件。模型可在开始转录前直接在转录菜单中选择。

| 模型 | 速度 | 质量 |
|---|---|---|
| `tiny` | 极快 | 基础 |
| `base` | 快 | 一般 |
| `small` | 中等 | 良好 |
| `medium` | 慢 | 高 |
| `large` | 极慢 | 最高 |

在没有独立 GPU 的 CPU 上，即使是 `small` 模型处理长文件也可能较慢。

---

**转录因内存错误中断。**

非常长的音频文件全部载入内存时，可能在内存较少的系统上出现问题。请考虑在转录前将音频文件分割为较短的片段。

---

## 翻译

**所需的语言对不可用。**

并非所有语言对都有直接的 Helsinki-NLP 模型。语言选择菜单中列出了支持的语言对。通过中间语言（英语）进行枢轴翻译已规划但尚未实现。

---

**翻译文本包含错误或听起来不自然。**

Helsinki-NLP 模型是机器翻译模型，在惯用语或专业术语上可能产生不准确的结果。文本后处理已规划为未来的改进项目。

---

## TTS 合成

**TTS 生成的音频有停顿或节奏不自然。**

请检查 TTS 菜单中选择的语音。神经语音（Azure Neural、Google WaveNet）的效果明显优于标准语音。可以在开始合成前试听音频示例。

---

**TTS 输出静音或只有噪音。**

用文本编辑器打开 `Translated/` 中已翻译的 SRT 文件，确认其中包含非空文本的有效片段。

---

**消耗监控未更新。**

消耗记录在 `Billing/consumo_tts.json` 中。如果文件被锁定或损坏，请备份后删除，下次使用时将自动重新创建。

---

## 文件与目录

**找不到生成的输出文件。**

每个阶段在其输出目录中创建格式为 `<时间戳>_<文件名>` 的子目录。请在以下位置查找：
- `Audio_Extracted/` — 提取的音频
- `Transcripts/` — SRT 转录文件
- `Translated/` — SRT 翻译文件
- `Dubbed/<PROVIDER>/` — 最终配音音频

每个子目录中的 `_info.txt` 文件记录了处理详情。

---

**我移动了项目，现在无法使用。**

手动删除 `venv/` 目录。下次通过 `StartDubbing.bat` 启动时，Launcher 将在新位置重新创建 venv。

---

## 构建与发布

**API 凭据未包含在发布包中。**

这是正常行为。出于安全原因，Azure 和 Google 凭据从不包含在发布包中。安装后需在每台机器的 `credentials/` 目录中手动添加，参照模板文件的结构填写。

---

## 常规问题

**项目能否在没有网络连接的情况下使用？**

部分可以。转录（Whisper）和翻译（Helsinki-NLP）在下载模型后可离线运行。TTS 合成（Azure、Google）需要网络连接，因为使用的是云端 API。

---

**能否为界面添加新语言？**

可以。新语言将随时间逐步添加。如需申请特定语言，可直接联系项目。希望自行添加的用户需要：

1. 参照现有语言文件的结构，创建 `locale/Active/<语言代码>.json` 文件
2. 在 `locale/System/languages.json` 中添加新语言

两个步骤都必须完成：若缺少第二步，系统将无法识别该语言。

---

**项目是否支持批量处理多个视频？**

目前流程设计为每次处理一个文件。可以依次准备多个文件并逐一处理，但不存在自动批量处理模式。此功能已纳入未来开发计划。
