# STYLE-FIRST → A/B → B1/B2（v2.4）

## 不可颠倒的顺序

所有新建 PPT，先理解内容，再**真实生成并展示八张同一正式代表性内容页的不同风格预览**。风格编号选择是第一个必经 Gate。只有风格选定后，才进入 A/B 路由。以前版本的“先问 A/B”已废止。

1. `brief → style_generate → style_await_selection`：八图共用同一正式页的准确文字、事实、尺寸和画幅；预览为八套差异明显的风格，不是 B1/B2 的四四分组。
2. `route`：`gates.style_selected=true`、`selected_style_id=style-XX`、8 张实际展示之后才能路由。若用户先前已明确动画或可编辑性，只记录偏好，风格确认后自动据此路由，避免第二次问。
3. 若需问，原句：“**本次 PPT 是否需要动画效果，或需要后期编辑文字、图形等元素？**” A＝任一需要；B＝两个都不需要。用户可以在看完八图后同时回复风格编号和 A/B，先记风格再写 `workflow_branch`。
4. A 直接执行 `pilot → artwork → approved → build → qa → delivered`；**不重新做八套风格预览**。要编辑但不需动画仍属于 A。
5. B 直接执行 `b_preview → b_await_confirmation → image_generate → image_qa → image_delivered`。B1/B2 分别对**已选同一视觉方向**的**同一页**作画质对照；展示两图后再确认 B1、B2 或 both。绝不把画质对照当成第二次风格选版。

## Gate 与历史兼容

- `schema_version=2.0` 新工程必须按 `style_previews` / `styleboards` / `selected_style_id` / `gates.style_selected` / `gates.branch_selected` 联动。前置阶段 `workflow_branch=null`；进入 route 前不得预先设置 A/B。
- **可提前记偏好，不可提前执行分流。** 若用户一开始就说“要动画”，可记录 `brief.animation_requested=true`，但仍必须真实给八图选风格。
- 已有合法的 v2.3 或更早工程、已确认风格的续作、单纯修订已有 PPT，不强制回溯八图或重问 A/B。
- B1：已确认风格＋相同页面基础提示词，无 Skill 内置画质增强。B2：严格仅追加固定原句，保护用户的动漫、水墨等艺术风格；完整规定见 [B 分支](image-fast-path.md)。
- 同一页 B1/B2 预览不是任意八图的一部分。仍需用户确认后才能生成整套。B 默认每个被选版本 PNG 全套＋ZIP＋纯图片 PPTX。
- A 高保真编辑、按需实际动画、全稿审批和交付规范继续沿用 V2.3，不因共同前置而降标。

更多：[共同 STYLE-FIRST 规范](style-first.md)。
