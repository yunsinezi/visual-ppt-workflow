# 发送给支持 Agent Skills 的 Gemini / Codex（复制整段）

请安装或读取 https://github.com/yunxinzi/visual-ppt-workflow 的 **v2.3.0** Skill，入口是根目录 SKILL.md，优先按其 29 项已确认决策执行，不得使用旧版 A/B 路由规则。Gemini CLI 可执行 `gemini skills install https://github.com/yunxinzi/visual-ppt-workflow.git`，如涉及额外安装和权限先征得我的批准；Gemini 网页版必须以 ZIP 导入 Skills，粘贴链接不等于安装。

完成加载后先核实本环境实际可用的生图、PPTX、PDF、文字、文件保存及动画播放工具，如缺失不要冒充具备。每次新建 PPT，若尚未明确要求，请只问我一个组合问题：“本次 PPT 是否需要动画效果，或需要后期编辑文字、图形等元素？”需要任一项走 A，无需两项才走 B。A 需 8 套不同风格预览、完整图稿审批、尽量保真且真正可编辑的 PPTX；如要求动画，必须实装或获得我的降级批准。B 先生成同一页 B1/B2 两张真实对照预览，反复修改两张直至满意，随后由我明确选择仅 B1/仅 B2/同时 both，才能批量。B 默认交付每套 PNG＋ZIP＋纯图片 PPTX，不做分层。按批准的分支执行自适应批次、真实 QA、断点回读和版本一致性，不能假称文件/播放已经验证。
