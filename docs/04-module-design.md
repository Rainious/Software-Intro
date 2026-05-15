# 模块设计

## 1. 模块划分总览

系统按业务能力和技术边界划分为以下模块：

| 模块 | 所属层 | 核心职责 |
| --- | --- | --- |
| 用户与权限模块 | 后端/前端 | 登录、角色、项目成员、访问控制 |
| 项目管理模块 | 后端/前端 | 项目生命周期、项目仪表盘、归档 |
| 船型与几何模块 | 后端/前端/存储 | 船型参数、几何文件上传、几何预处理 |
| 仿真算例模块 | 后端/前端 | 仿真类型、流体参数、边界条件、控制方程配置 |
| PINN 模型配置模块 | 后端/PINN 引擎 | 网络结构、损失项、采样策略、训练超参数 |
| 任务调度模块 | 后端/Worker/数据库 | 训练、推理、后处理、报告任务管理 |
| PhysicsNeMo 引擎模块 | PINN 引擎 | 物理约束建模、训练、推理和检查点 |
| 结果与可视化模块 | 后端/前端/存储 | 指标、曲线、云图、矢量场、结果对比 |
| 数据集模块 | 后端/存储 | 观测数据、参考 CFD 数据、水池试验数据管理 |
| 报告模块 | 后端/前端/Worker | 报告模板、报告生成、导出 |
| 审计与运维模块 | 后端/基础设施 | 日志、审计、监控、配置、资源状态 |

## 2. 用户与权限模块

### 2.1 功能

- 用户注册、登录、登出、密码重置。
- JWT 或 Session 鉴权。
- 角色管理：管理员、研究人员、设计人员、访客。
- 项目成员管理：项目级权限控制。
- 操作审计。

### 2.2 关键接口

- `POST /api/v1/auth/login`
- `POST /api/v1/auth/logout`
- `GET /api/v1/users/me`
- `POST /api/v1/projects/{project_id}/members`
- `PATCH /api/v1/projects/{project_id}/members/{user_id}`

### 2.3 主要数据表

- `users`
- `roles`
- `user_roles`
- `project_members`
- `audit_logs`

## 3. 项目管理模块

### 3.1 功能

- 创建、编辑、归档、删除项目。
- 项目仪表盘，展示船型数量、算例数量、运行中任务、最新结果。
- 项目标签、描述和可见性。
- 项目级统计信息。

### 3.2 状态

| 状态 | 说明 |
| --- | --- |
| ACTIVE | 正常使用 |
| ARCHIVED | 归档只读 |
| DELETED | 逻辑删除 |

### 3.3 主要数据表

- `projects`
- `project_members`
- `audit_logs`

## 4. 船型与几何模块

### 4.1 功能

- 维护船型基础参数。
- 上传几何文件或参数化几何描述。
- 几何文件元数据管理。
- 几何预处理状态跟踪，例如格式校验、包围盒计算、尺度归一化、采样域生成。
- 支持一个船型关联多个几何版本。

### 4.2 船型参数建议

| 参数 | 说明 |
| --- | --- |
| `length_overall` | 总长 |
| `length_waterline` | 水线长 |
| `beam` | 型宽 |
| `draft` | 吃水 |
| `displacement` | 排水量 |
| `block_coefficient` | 方形系数 |
| `prismatic_coefficient` | 棱形系数 |
| `wetted_surface_area` | 湿表面积 |

### 4.3 几何资产类型

- `STL_MESH`：三角面片几何。
- `OBJ_MESH`：通用三维模型。
- `SECTION_POINTS`：二维截面点集。
- `PARAMETRIC_JSON`：参数化船型描述。
- `DOMAIN_CONFIG`：计算域配置。

### 4.4 主要数据表

- `vessels`
- `geometry_assets`
- `geometry_versions`
- `file_assets`

## 5. 仿真算例模块

### 5.1 功能

- 创建和编辑仿真算例。
- 选择仿真类型和物理模板。
- 配置流体参数、边界条件、初始条件、采样域和输出指标。
- 保存算例模板和配置快照。
- 校验算例完整性。

### 5.2 仿真类型

| 类型 | 说明 | 优先级 |
| --- | --- | --- |
| `CALM_WATER_RESISTANCE` | 静水阻力与绕流流场 | V1 |
| `FLOW_AROUND_HULL` | 船体周围速度/压力分布 | V1 |
| `REGULAR_WAVE_RESPONSE` | 规则波中运动响应简化模型 | V2 |
| `MANEUVERING_SIMPLIFIED` | 简化操纵性模型 | V3 |
| `PARAMETER_SWEEP` | 参数扫描与方案对比 | V2 |
| `DATA_ASSIMILATION` | 观测数据融合 | V2 |

### 5.3 算例状态

| 状态 | 说明 |
| --- | --- |
| DRAFT | 草稿 |
| READY | 配置完整，可提交任务 |
| RUNNING | 有关联任务运行中 |
| COMPLETED | 已产生可用结果 |
| FAILED | 最近一次运行失败 |
| ARCHIVED | 已归档 |

### 5.4 主要数据表

- `simulation_cases`
- `fluid_conditions`
- `boundary_conditions`
- `physics_scenarios`
- `case_snapshots`

## 6. PINN 模型配置模块

### 6.1 功能

- 管理网络结构模板。
- 配置 PhysicsNeMo 所需的节点、约束、采样策略和训练参数。
- 管理损失项权重。
- 保存模型配置版本。
- 校验配置是否与仿真类型匹配。

### 6.2 配置维度

| 维度 | 示例 |
| --- | --- |
| 网络结构 | MLP、Fourier Feature MLP、SIREN |
| 输入变量 | `x, y, z, t, U, Fr, Re` |
| 输出变量 | `u, v, w, p, eta` |
| PDE 约束 | 连续性方程、动量方程、波方程 |
| 边界约束 | 入口速度、出口压力、壁面无滑移、自由液面 |
| 数据约束 | CFD 参考点、水池试验观测点 |
| 优化器 | Adam、LBFGS 或组合策略 |
| 采样策略 | 域内采样、边界采样、自适应残差采样 |

### 6.3 主要数据表

- `pinn_model_configs`
- `pinn_model_versions`
- `loss_terms`
- `training_hyperparameters`

## 7. 任务调度模块

### 7.1 功能

- 创建训练、推理、后处理、报告任务。
- 基于数据库任务表的任务领取、执行和状态跟踪。
- 任务取消、重试、优先级和资源需求描述。
- 任务日志和进度消息。
- 失败原因和异常堆栈保存。

### 7.2 任务类型

| 类型 | 说明 |
| --- | --- |
| TRAINING | PINN 模型训练 |
| INFERENCE | 使用检查点进行推理采样 |
| POSTPROCESS | 计算水动力指标和转换可视化数据 |
| REPORT | 生成报告 |
| GEOMETRY_PREPROCESS | 几何校验和预处理 |

### 7.3 任务状态机

```text
PENDING -> RUNNING -> SUCCEEDED
     |         |
     |         v
     +------> FAILED
     |
     v
   CANCELED
```

### 7.4 主要数据表

- `jobs`
- `job_logs`
- `job_events`
- `training_jobs`
- `simulation_jobs`

### 7.5 后续平台增强

当前版本不依赖 Redis。若后续需要跨节点调度、实时日志推送或更高并发控制，可再引入 Redis + Celery/RQ 或等价方案。

## 8. PhysicsNeMo 引擎模块

### 8.1 功能

- 读取标准化任务配置。
- 构建 PhysicsNeMo 计算图和约束。
- 执行训练循环或调用框架训练器。
- 保存检查点和训练指标。
- 执行推理、采样和结果导出。

### 8.2 输入输出契约

#### 输入

- 算例配置快照。
- 几何资产 URI。
- 物理模板 ID。
- 模型配置快照。
- 数据集 URI，可选。
- 输出目录 URI。

#### 输出

- `metrics.json`：关键指标。
- `loss_history.csv`：损失曲线。
- `checkpoint`：模型检查点。
- `field_data`：流场采样结果。
- `preview_images`：前端预览图。
- `engine_log.txt`：引擎日志。

## 9. 结果与可视化模块

### 9.1 功能

- 保存结果索引和指标。
- 管理结果工件。
- 支持图表和可视化数据按需加载。
- 多算例、多模型版本对比。
- 结果标签和归档。

### 9.2 结果类型

| 类型 | 示例 |
| --- | --- |
| SCALAR_METRIC | 阻力系数、升力系数、平均残差 |
| CURVE | 损失曲线、剖面压力分布 |
| FIELD_2D | 速度云图、压力云图、残差云图 |
| FIELD_3D | 三维速度/压力体数据 |
| VECTOR_FIELD | 速度矢量图 |
| IMAGE | PNG/JPEG 预览图 |
| REPORT | PDF/HTML 报告 |

## 10. 数据集模块

### 10.1 功能

- 上传观测数据和参考数据。
- 数据字段映射和单位说明。
- 数据质量检查，例如缺失值、范围、重复点。
- 数据集版本管理。
- 数据集与算例、损失项关联。

### 10.2 数据来源

- 水池试验。
- 外部 CFD 计算。
- 公开基准算例。
- 传感器或实船试验数据。
- 人工构造验证数据。

## 11. 报告模块

### 11.1 功能

- 根据算例和结果生成报告。
- 支持 HTML 预览和 PDF 导出。
- 支持报告模板。
- 自动包含配置快照、关键指标、图表和结果说明。

### 11.2 报告章节建议

1. 项目与船型信息。
2. 仿真目的与假设。
3. 物理模型与边界条件。
4. PINN 模型配置。
5. 训练过程与收敛情况。
6. 推理结果与关键指标。
7. 对比分析。
8. 局限性与结论。

## 12. 模块依赖关系

```text
前端模块
  -> 后端 API
      -> 领域服务
          -> Repository
          -> Storage
      -> 后台任务执行器
          -> PhysicsNeMo Adapter
              -> PINN Engine
                  -> PhysicsNeMo
```

模块间应通过明确的数据对象或 DTO 通信，避免跨层直接访问实现细节。
