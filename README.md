# Visual PPT Workflow · 完整版 V2.4

> 通过真实 8 张风格预览、选版后 A/B 分流，生成高质量 PPT。与 [骨干高速版](https://github.com/yunsinezi/visual-ppt-fast) 是**同一 GitHub 账号下两个独立的仓库**。

[核心 SKILL.md](SKILL.md) · [前置八图和分流规则](references/style-first.md) · [详细 B1/B2 规则](references/image-fast-path.md) · [Gemini 安装说明](INSTALL_GEMINI.md) · [English](README_EN.md)

## 唯一正确的新建流程

**理解内容 → 8 张同一正式内容页的不同风格预览 → 展示并由用户选中 1 张 → A/B 分流 → 正式制作 → QA → 交付。**

必须实际生成、展示八张**各自独立的完整风格图**，不是单张拼贴后切片、同图滤镜，也不是“B1 4 张＋B2 4 张”。如用户开始就说明要动画或可编辑，可提前记录偏好，但**不得提前启动 A/B、跳过八图**。已确认风格的续作或已有稿件修订，不强行重跑。

选风格后，才按是否要求动画或逐项编辑决定：
- **A：需要任一项。** 复用已经确认的风格，执行 PILOT → ARTWORK（全套定稿用户审批）→ REBUILD（普通文字真正可编辑、需要动效时实装动画）→ VERIFY → DELIVER。**不再重新生成第二轮八套风格。** 交付可编辑 PPTX、静态 PDF、逐页预览和总览。
- **B：两项均不需要。** 在已选定的同一风格下，实际生成 B1/B2 两张**仅画质附加限制不同**的预览供确认（不是再次选风格），确认仅 B1、仅 B2 或 both 后才生成整套。每个选定版本默认交付完整 PNG、ZIP 和纯图片 PPTX，不提供逐元素编辑或动画。

## 固定 B2 画质附加句

> 画面保持干净自然的真实照片质感：不要数字噪点与彩色噪点，不要颗粒覆盖，不要过度锐化，不要 HDR 与油腻高光，不要蜡质表面，不要脏灰色调，不要假细节与压缩伪影。

与 B1 相比，B2 **只在共享基础提示词后附加该句**；若已选风格是动漫、水墨、插画等，不可强行改成摄影作品。

## 安装

Gemini CLI 支持安装仓库的环境中：

```bash
gemini skills install https://github.com/yunsinezi/visual-ppt-workflow.git
```

请以仓库的 `SKILL.md` 为入口，并读取 `references/`。纯聊天引用 GitHub URL 不等于实际安装，详情见 [安装说明](INSTALL_GEMINI.md)。

## 自动化检查

```bash
python3 scripts/validate_skill.py .
python3 scripts/validate_project.py assets/style-first-template.json
python3 scripts/validate_project.py assets/project-template.json
python3 scripts/validate_project.py assets/image-branch-template.json
python3 -m unittest discover -s tests -v
```

v2.4 的新建工程使用 `assets/style-first-template.json`（schema 2.0）；旧的 A/B 模板只用于兼容早期续作和回归测试。结构校验不会证明真实出图、字体许可、PPTX 实际可编辑性或 PowerPoint/WPS 动画实播；必须用宿主工具另行验证。

## 高质量保障

实际图片与 PPTX 画幅保持一致、文本清晰、安全区域合理；按内容页布局保持设计语言统一但不死板；生成失败优先局部修复、阶段性回读验证和保存文件；所有下载链接必须指向实际已存在的产物。

MIT License.
