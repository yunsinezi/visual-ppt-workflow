# 附带脚本与边界

脚本均使用 Python 3.10+，除图像对比脚本外只依赖标准库。

- `scripts/validate_skill.py`: 检查 Agent Skills 元信息、内部相对链接和基础目录结构；不代表平台官方认证。
- `scripts/validate_project.py`: 检查 project.json schema、A/B 分支选择与对应阶段门槛、素材映射，属于**声明一致性检查**，不等于用户真的确认过。B 模板见 `assets/image-branch-template.json`（schema 1.3）。新建 B 必须经双预览确认 Gate，脚本检查所声明的 B1/B2 图片、提示词来源和每版本 QA；但仅凭路径字段仍不能证明图片真的存在或预览真的被用户看到。
- `scripts/audit_pptx.py`: 解析 PPTX ZIP/XML，统计页面对象、文本框、图片和动画结构；可标记整页一图与空白。无法证明图片真透明、字体匹配、背景无残影、在 WPS 可编辑或动画可播放。
- `scripts/compare_renders.py`: 比较两张等尺寸渲染图，输出绝对误差热力图与MAE。需要 `Pillow`（可 `pip install Pillow`）；视觉数值只辅助人审。

示例：

```bash
python scripts/validate_skill.py .
python scripts/validate_project.py assets/project-template.json
python scripts/validate_project.py assets/image-branch-template.json
python scripts/audit_pptx.py path/to/deck.pptx --mode editable --json build/audit.json
python scripts/compare_renders.py reference/slide-01.png builds/run-01/preview/slide-01.png --heatmap build/heatmap-01.png
```

未包含任何生成模型 API key，未绑定特定商业供应商，外部工具的版权、权限、价格和限额由使用者自行管理。

## v2.3 自主选型／成本许可／能力分层

- 不绑定图像模型与生成库，依据环境自由组合并验证；不可用时先换可靠工具，若需要新权限/付费/安装须征求用户同意。
- 图片清晰度、字体兼容、授权、PPTX 实际打开/编辑、动画实播不在静态脚本覆盖范围。自动化验证成功**不代表**视觉、编辑性和播放验收成功。
- 修改该 Skill 时运行静态检查与单元测试；重大版本还须实际制作受影响分支的样例并提供证据，否则在升级报告中标“实战未验证”。
