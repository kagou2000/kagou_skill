# kagou_skill

一组面向剪映专业版（Jianying Pro）和 CapCut 工作流的本地 Agent 技能。目前包含剪映草稿生成与 SRT 字幕导出两个技能。

## 包含的技能

### `jianying-draft-project`

根据本地媒体、粗剪决定、EDL JSON 和 SRT 字幕生成剪映可识别的草稿项目。

主要能力：

- 从结构化 EDL 创建剪映时间线
- 引用原始视频并保留源素材时间范围
- 可选导入 SRT 字幕轨道
- 生成 `draft_content.json` 和 `draft_meta_info.json`
- 支持生成前的 EDL 校验

### `jianying-srt-export`

通过剪映自动字幕或备用语音识别流程，将视频、音频转换为剪映或 CapCut 可导入的 UTF-8 SRT 字幕。

## 目录结构

```text
.agents/skills/
├── jianying-draft-project/
│   ├── SKILL.md
│   ├── requirements.txt
│   ├── references/
│   └── scripts/
└── jianying-srt-export/
    └── SKILL.md
```

## 安装

克隆仓库：

```bash
git clone git@github.com:kagou2000/kagou_skill.git
cd kagou_skill
```

草稿生成技能使用独立的本地 Python 运行环境。首次使用时运行：

```powershell
python .agents/skills/jianying-draft-project/scripts/check_environment.py
python .agents/skills/jianying-draft-project/scripts/install_dependencies.py
```

依赖会安装到技能目录内的 `.runtime`，该目录不会提交到 Git。

## 草稿生成示例

仅校验 EDL：

```powershell
python .agents/skills/jianying-draft-project/scripts/build_draft.py `
  --edl D:\path\to\rough_cut_edl.json `
  --name demo-draft `
  --validate-only
```

生成带字幕的剪映草稿：

```powershell
python .agents/skills/jianying-draft-project/scripts/build_draft.py `
  --edl D:\path\to\rough_cut_edl.json `
  --srt D:\path\to\subtitles.srt `
  --name demo-draft
```

默认草稿输出目录为：

```text
D:\JianyingPro Drafts\<draft-name>
```

EDL 字段格式和完整工作流请参阅各技能目录中的 `SKILL.md`。

## 使用提醒

- 不要直接修改剪映生成的编码或二进制形式原生草稿。
- 建议始终生成新的草稿目录，并保留原始媒体文件不变。
- 草稿生成后应在剪映专业版中检查媒体链接、视频轨和字幕轨。
- `.runtime`、Python 缓存及本地环境文件已通过 `.gitignore` 排除。

## 已验证环境

- Windows
- Jianying Professional `10.6.0.14057`
- `pyjianyingdraft==0.2.6`

## License

当前仓库尚未指定开源许可证。在添加许可证前，请勿假定代码可用于再分发或商业用途。
