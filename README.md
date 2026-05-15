# PINN 船舶水动力学仿真系统设计文档

本文档集用于系统设计阶段，目标是定义一个基于 PINN 的船舶水动力学仿真系统需求、软件架构、模块边界、数据库模型与项目目录雏形。

## 技术栈约定

- 神经网络与物理约束求解：NVIDIA PhysicsNeMo
- 后端服务：Python Flask
- 前端应用：JavaScript React
- 数据库建议：PostgreSQL
- 后台任务建议：Python Worker + PostgreSQL 任务表
- 文件与结果资产存储建议：对象存储或本地兼容 S3 的 MinIO

当前版本不将 Redis 作为必需基础设施。后续如需更强的任务队列、实时消息推送或跨节点扩展，可再引入 Redis + Celery/RQ 或等价方案。

## 文档目录

1. [需求规格说明](docs/01-requirements.md)
2. [总体软件架构设计](docs/02-system-architecture.md)
3. [项目结构与层级设计](docs/03-project-structure.md)
4. [模块设计](docs/04-module-design.md)
5. [数据库表设计](docs/05-database-design.md)
6. [接口与核心业务流程](docs/06-api-and-workflows.md)
7. [验证、质量与风险设计](docs/07-validation-quality-risk.md)

## 设计范围

本阶段不包含实际编码实现，重点是明确系统边界、业务需求、技术架构和可落地的项目组织方式。后续进入概要设计、详细设计或原型开发时，可在本文档基础上补充 API Schema、数据字典、模型配置模板和前端交互原型。
