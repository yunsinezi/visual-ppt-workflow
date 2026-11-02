# Gemini / Antigravity 安装：Visual PPT Workflow

本仓库提供 Agent Skills 工作流，主入口 [SKILL.md](SKILL.md)。它要求宿主有必要的图像生成、PPTX 构建、渲染等工具；**不能把阅读 GitHub 文件当成已安装**。

## Gemini CLI：直接从公开 GitHub 安装

```bash
gemini skills install https://github.com/yunxinzi/visual-ppt-workflow.git
```

启动 Gemini CLI 后用 `/skills list` 查找 `visual-ppt-workflow`，必要时执行 `/skills reload`。安装与激活需经过用户权限确认。

## Gemini 网页版与手机 App：导入 ZIP

Gemini Apps 已支持 Skills，但**仅粘贴 GitHub 链接不等于自动注册持久 Skill**。

1. 在 https://gemini.google.com 打开 `Customize → Skills → Create → Upload`。
2. 下载此仓库源代码，把仓库内的 `SKILL.md`、`references/` 等文件作为 ZIP 根目录重新打包后上传（不要再使用旧名称的 ZIP 文件）。
3. 审核说明并点击创建，确保 Skill 已启用。
4. 在新对话中输入“使用 visual-ppt-workflow 制作 PPT”，或通过 `/` 选择 Skill。

官方目前对 Gemini Apps Skills 的文件、脚本和部分功能有使用限制；不保证在任意对话都能运行 Python、生成可编辑 PPTX 或执行 PowerPoint 实播。应核对实际工具并如实报告。

## Antigravity App/IDE

将本文件夹复制到工作区 `.agents/skills/visual-ppt-workflow/`，或全局 `~/.gemini/config/skills/visual-ppt-workflow/`；按官方文档重载或重新启动，输入 `/visual-ppt-workflow` 或直接提出 PPT 任务。

## 验收清单

- Skill 列表存在 `visual-ppt-workflow`，不是仅能打开 GitHub 页面。
- 激活后可读取 SKILL.md、references 等关联文件。
- 测试“课堂 12 页 PPT”必须**先问 A/B**；选择 A 后才给 8 套真实风格预览；选择 B 则**先用同一页生成 B1/B2 两张独立预览，显示固定选择说明并等待确认**，不可直接批量生产。用户确认默认 both 后才生成两套完整图片，跳过 A 的八套预览、全稿审批和可编辑拆分。
- 必须明确区分纯图片版与真实可编辑 PPTX、结构测试与实播测试。

## Google 官方文档

- https://geminicli.com/docs/cli/skills/
- https://support.google.com/gemini/answer/17094296?hl=en
- https://antigravity.google/docs/skills
