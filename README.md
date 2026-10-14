# travel-planner

AI 旅行规划 Agent：输入空闲时间、预算与偏好，产出精确到航班、酒店、餐厅与每笔开销的完整行程方案，支持对比与对话式修改。

> 学习项目 · 开发中

## 技术栈（规划）

Python 3.12 · FastAPI · LangGraph · PostgreSQL + PostGIS · Redis · DeepSeek/GLM API（OpenAI 兼容）

## 路线图

- [ ] 阶段 0：环境与地基（异步 / Pydantic / 结构化输出）
- [ ] 阶段 1：裸写 Tool-use Agent 内核（不依赖框架）
- [ ] 阶段 2：LangGraph 重构 + 行程编排算法（聚类 / 路径 / 校验器）
- [ ] 阶段 3：RAG 攻略知识库 + MCP 工具化
- [ ] 阶段 4：评测体系 + 可观测性 + 高德真实数据
- [ ] 阶段 5：Web 前端 + 部署
- [ ] 阶段 6：LoRA 微调（需求结构化解析蒸馏）
