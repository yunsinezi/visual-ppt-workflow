# Visual PPT Workflow v2.3.0

**高质量 PPT Agent Skill：由用户审核的 29 项执行规则，A/B 分支、双预览、强质量门禁与可恢复交付。**

[Skill 主规范](SKILL.md) · [29 项决策矩阵](references/upgrade-policy-v2.3.md) · [Gemini 安装说明](INSTALL_GEMINI.md) · [English](README_EN.md)

## 先选择是否需要动画或逐元素编辑

新建 PPT 只问一个问题：

> **本次 PPT 是否需要动画效果，或需要后期编辑文字、图形等元素？**

- **A：其中任何一项需要。** 依次 DEFINE → EXPLORE（8 套真正不同的图稿，普通 8 张/重要 16 张）→ PILOT → ARTWORK（用户确认全部定稿）→ REBUILD（视觉保真、普通文字可编辑、按需真实动画）→ VERIFY → DELIVER。
- **B：两者都不需要。** 先**独立真实生成**同一代表页的 B1（无 Skill 附加画质句）与 B2（同基础提示词仅追加固定画质句）两张预览；用户不满意可共同调整基线并重做两张。两图展示后由用户确认 B1、B2 或 both，之后才批量生成。

B2 追加句原文，不得改变：

> 画面保持干净自然的真实照片质感：不要数字噪点与彩色噪点，不要颗粒覆盖，不要过度锐化，不要 HDR 与油腻高光，不要蜡质表面，不要脏灰色调，不要假细节与压缩伪影。

B2 在动漫、水墨等题材中保持用户指定风格，不强制变摄影图。

**A 默认交付：可编辑 PPTX＋静态 PDF＋逐页预览＋总览图**；工程素材按需。需要动画时必须尽力真实实装；不能未经同意降级为说明表或静态版。

**B 默认交付：每个选定版本的高清 PNG 全套＋ZIP＋纯图片 PPTX**；`both` 是两套完整且独立 QA 的成品，图片版不能逐元素修改或承载原生动画；PDF 按需。

## 执行质量要求

用同一 `project.json` 保存用户确认、每批状态、文件哈希及 `build_id`；中断恢复核对真实文件，不重造已验收内容。重要数据与学术事实严格核验。图稿符合统一视觉语言但各页有创意差异。字体兼顾审美/许可/跨平台兼容；重要文字和数据位于安全区，背景允许出血；B 普通展示目标不低于 1080P，重要大屏优先 4K。最终实物检查黑块、错字、空页、错位、拉伸及导出差异。

Agent 可自主使用工具、调整并发与切换修复方案，但安装授权/付费/敏感权限/关键功能降级需用户批准。**脚本静态检查不能代替真实 PPTX 编辑或动画实播。**

## 安装

Gemini CLI：

```bash
gemini skills install https://github.com/yunxinzi/visual-ppt-workflow.git
```

Gemini 网页版按 [安装说明](INSTALL_GEMINI.md) 将仓库以 SKILL.md 在根目录的 ZIP 导入 Skills；仅发送 GitHub 链接不等于已安装。其他 Agent 使用兼容的 Skill 目录，明确检测其支持的图片/PPTX/实播能力。

## 自动化测试

```bash
python3 scripts/validate_skill.py .
python3 scripts/validate_project.py assets/project-template.json
python3 scripts/validate_project.py assets/image-branch-template.json
python3 -m unittest discover -s tests -v
```

测试验证目录/状态/规则约束，不虚称验证了实物视觉质量。重大流程升级要求额外真实生成受影响分支的 PPT 作为集成验证；未运行需明确披露。

MIT License.
