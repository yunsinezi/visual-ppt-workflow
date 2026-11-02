# V2.4 共同 STYLE-FIRST Gate 与状态结构

## 必须先发生的三个动作

- **准备同一正式内容页**：确定 `style_previews.slide_id/shared_copy/aspect_ratio`，8 张预览不得各自换文案。字体、构图、图像语言等显著不同，禁止只是换色。
- **真实生成并展示** 8 张独立 PNG：`styleboards/style-01.png` … `styleboards/style-08.png`。使用真实图片，不得以声明路径或拼贴切分代替；展示完用户才选风格。
- **用户选择编号**：`selected_style_id` 必须来自上述 8 个选项，`gates.style_selected=true` 才能进入 `route`。已提前记录的 A/B 喜好到此之后才能生效。

## 新建工程状态机（schema 2.0）

```text
brief
style_generate
style_await_selection  [8 images generated + presented; wait for user]
route                  [style selected; ask or apply A/B]
A: pilot → artwork → approved → build → qa → delivered
B: b_preview → b_await_confirmation → image_generate → image_qa → image_delivered
```

- `brief/style_generate/style_await_selection/route` 阶段 `workflow_branch=null`，`gates.branch_selected=false`。在八图完成之前不允许 `gates.style_selected=true`。
- `style_await_selection` 必须有八图和展示声明，但是只有**真实图片与用户确认**才能证明 Gate；JSON 声明不等于证据。
- `route` 只能在 `selected_style_id`、八图和展示记录合法时进入；用户可与选风格一起给 A/B，先保存风格选择再启用分支。
- 进入 A/B 执行阶段 `workflow_branch` 才为 A/B，必须有 `gates.branch_selected=true`；不可绕开原本的 B1/B2 二级确认或 A 全稿批准。
- A/B 都复用同一个 `design_spec` 与选中的风格，页构图可变化而核心视觉语言一致。重要 A 需要的额外封面实验不得变成第二个八图 Gate。
- 旧版 schema 1.1/1.2/1.3 按原有状态继续，不能被 v2.4 的新 Gate 强制打断。

## 降本提速和可审计性

风格八张图无依赖，可适当并发；用户选风格和 B1/B2 确认必须串行。所有预览原图和版本保存在文件系统、云盘或工作区，临时渲染不能冒充永久可恢复文件。QA 记录应区分结构检查、实际图像检验、实际可编辑测试和实播检查。

示例工程：[STYLE-FIRST 空白模板](../assets/style-first-template.json)。
