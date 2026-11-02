# 文件与状态约定

**分支说明：** 下方含 styleboards/reference/backgrounds/foregrounds 的目录结构仅对 A 适用。B 需要 `project.json`、双预览 `previews/B1.png`、`previews/B2.png`、用户确认状态，以及按选择生成的 `B1/slide-XX.png` 与/或 `B2/slide-XX.png`；双方选择 both 则有两套独立全页图片，不强制建立 A 的目录。见 [B 分支](image-fast-path.md)。

## 推荐项目目录（示例）

```
workspace/<project_id>/
  project.json                  # 唯一事实源（可使用 assets/project-template.json）
  styleboards/01.png ... 08.png
  reference/slide-01.png ...
  assets/backgrounds/*.png
  assets/foregrounds/*.png
  builds/<build_id>/deck.pptx
  builds/<build_id>/deck.pdf
  builds/<build_id>/preview/slide-01.png ...
  builds/<build_id>/qa-report.json
```

素材引用用相对路径；同一构建版本绑定同一 `build_id`。保存每个产物的 SHA-256，禁止拿旧 PDF/图片冒充最新 PPTX 的导出。可选 `manifest` 字段记录 `build_id`, `source_build_id`, `renderer`, `export_timestamp`, `actual_verification`。

## 各模式交付
- `workflow_branch=B`: 先双预览并由用户确认 B1/B2/both，再交付指定的一套或两套有序高清图片；both 需要两个独立版本目录与独立 QA；**必须同时生成 PNG 逐页图集、ZIP、纯图片 PPTX；** PDF 按用户额外要求。无需 A 分层工程包。
- `editable`: 真实可编辑 `.pptx`、静态 `.pdf`、全页预览和总览图；按需可重建素材和动画描述。
- `image`（A 的图片模式或 B）：B 默认同时交付逐页 PNG、ZIP 和纯图片 `.pptx`（PDF 按需），必须明确“不能分层编辑”，禁止夸大。
- `hybrid`: `.pptx` 与按页的编辑性边界表，明确 `flattened` 素材。
- `pdf-only`: PDF 与按需预览，不声称 PPTX 已有。
- `review`: QA报告、已修改文件和差异说明；修改后仍执行受影响页面验证。

## 跨环境运行
工程所需生成/渲染/校验工具因Agent而异。优先使用实际可运行的工具组合；不把某一种Python/PPT生成库写死为工作流必要条件。若某项条件无法满足，精确说明影响范围并给出能诚实交付的产物。

## B v2.2 推荐文件结构

```text
workspace/<project_id>/
  project.json             # workflow_branch=B; b_generation_mode/B 预览与用户确认状态
  previews/B1.png          # 同一正式内容页的 B1（不加 Skill 内置画质约束）
  previews/B2.png          # 同页 B2（追加固定自然真实照片质感约束）
  B1/slide-01.png ...      # 仅 B1 或 both 选项时存在完整图片集
  B2/slide-01.png ...      # 仅 B2 或 both 选项时存在完整图片集
  qa-report.json           # 各版本独立检查结果
```

推荐使用 `assets/image-branch-template.json`（schema 1.3）；`gates.b_previews_generated` 表示两张预览实际生成，`gates.b_variant_confirmed` 表示用户看过预览并批准具体生成范围。不得在确认前为默认 both 预置已批准状态。

## v2.3 单一事实源、检查点、版本隔离

- B 正式交付推荐路径：`builds/<build_id>/B1/slide-01.png`、`B1/images.zip`、`B1/deck-image-only.pptx`（B2 同理）；**两个版本独立哈希、独立 QA 和独立回退标记**。 `artifacts.variant_deliveries.B1/B2` 分别记 `images_dir/images_zip/pptx`；B 的通用 `artifacts.pptx` 不能代替 both 的两套。
- A 正式交付：`artifacts.pptx/pdf/preview_dir/overview_image`，必须基于同一 `build_id`。PDF 不声称包含动画；原生编辑和实播状态另行记录。
- 每个审批 Gate 和每批已完成页面之后**回读** `project.json` 与本批实物路径；记录哈希、源图、QA、`checkpoint.last_saved_at`、`verified_files`、下一任务。仅文件路径字符串不等于存在验证，且沙箱下载链接不是长期持久备份。
- 重入时先查看并验证实物，再恢复最近一次真实通过的节点；对损坏、缺失或不匹配的派生文件按依赖链局部重建。用户已确认的决策不得重新问。
- 修改 B2 一页，仅重制 B2 对应页面、重打该版本 ZIP/PPTX，B1 不自动重制。必要时保留上一套完整有效版本供回滚。
- 文字、字体和安全区最终以真实输出渲染核对：PPTX 图片等比例放置，禁止意外裁切、黑条、黑块和拉伸。
