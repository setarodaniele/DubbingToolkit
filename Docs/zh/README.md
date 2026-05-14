# DubbingToolkit

> ⚠️ **警告**: 此文档已通过自动翻译，可能包含错误或不准确之处。有关详细信息，请参考[英文版本](../en/README.md)。

**DubbingToolkit** 是一个混合 Python + PowerShell 配音系统，能够将音频/视频内容转录、翻译并用多种语言重新合成，使用专业 TTS 引擎（Azure、Google）和本地转录模型（Whisper）。

---

## 文档索引

| 文件 | 内容 |
|---|---|
| [README.md](README.md) | 本页面 — 总体概述 |
| [安装.md](安装.md) | 系统要求、配置和初始设置 |
| [用法.md](用法.md) | 操作指南和工作流程 |
| [架构.md](架构.md) | 项目结构、模块和规范 |
| [faq.md](faq.md) | 常见问题和故障排除 |
| [限制和注意.md](限制和注意.md) | 当前限制和尚未实现的功能 |
| [credenziali_azure.md](credenziali_azure.md) | Azure 凭据配置 |
| [credenziali_google.md](credenziali_google.md) | Google 凭据配置 |

---

## 功能介绍

DubbingToolkit 将配音的主要阶段整合为一体——音频提取、转录、翻译和语音合成——大幅减少手动操作，将整个流程集中在一个受控的管道中。

1. **音频提取** — 通过 ffmpeg 从视频文件中提取音频轨道。如果已有音频文件，此步骤可跳过。
2. **转录** — 通过 Whisper 将音频转录为 SRT 格式。
3. **翻译** — 使用本地运行的 Helsinki-NLP 模型将 SRT 字幕翻译为目标语言，无需依赖外部 API。
4. **文字转语音（TTS）** — 通过 Azure TTS 或 Google TTS 逐段合成配音音频，然后将各段合并为最终音频文件。

---

## 支持的语言

系统界面目前支持 8 种语言：

| 代码 | 语言 |
|---|---|
| `it` | 意大利语 |
| `en` | 英语 |
| `es` | 西班牙语 |
| `de` | 德语 |
| `fr` | 法语 |
| `pt` | 葡萄牙语 |
| `ru` | 俄语 |
| `zh` | 中文 |

转录和翻译支持的语言分别取决于 Whisper 和可用的 Helsinki-NLP 模型。详情请参阅 `locale/` 目录。

---

## 目前支持的 TTS 提供商

- **Azure Cognitive Services Speech** — 高质量神经语音，语言覆盖广泛
- **Google Cloud Text-to-Speech** — 可靠的替代方案，提供多种语音选择

两种提供商均需在本地配置 API 凭据。请参阅 [安装.md](安装.md)。

---

## 入口点

项目通过单个文件启动：

```
StartDubbing.bat
```

其余所有操作均由启动器自动编排。

---

## 项目状态

DubbingToolkit 正处于积极开发中。部分功能已在主管道中运行，其他功能计划作为未来改进（高级分段、文本后处理、中转翻译等）。有关模块状态的详细信息，请参阅 [架构.md](架构.md)。
