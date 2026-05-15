# 接口与核心业务流程

## 1. API 设计原则

- API 采用 REST 风格，路径以资源为中心。
- 版本前缀使用 `/api/v1`。
- 所有写操作必须鉴权，并执行项目级权限校验。
- 长耗时操作只创建任务并返回 Job ID，不在 HTTP 请求内同步执行。
- 当前版本任务状态更新以数据库任务表和前端轮询为主。
- 列表接口统一支持分页、排序、过滤和关键字搜索。
- 错误响应使用统一结构，便于前端展示和调试。

## 2. 通用响应结构

### 2.1 成功响应

```json
{
  "data": {},
  "meta": {
    "request_id": "req_xxx",
    "timestamp": "2026-05-15T10:00:00Z"
  }
}
```

### 2.2 分页响应

```json
{
  "data": [],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 120
  },
  "meta": {
    "request_id": "req_xxx"
  }
}
```

### 2.3 错误响应

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid simulation configuration",
    "details": []
  },
  "meta": {
    "request_id": "req_xxx"
  }
}
```

## 3. 认证与用户接口

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| POST | `/api/v1/auth/login` | 登录 |
| POST | `/api/v1/auth/logout` | 登出 |
| POST | `/api/v1/auth/refresh` | 刷新 Token |
| GET | `/api/v1/users/me` | 获取当前用户 |
| PATCH | `/api/v1/users/me` | 更新当前用户资料 |
| GET | `/api/v1/roles` | 获取角色列表 |

## 4. 项目接口

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/api/v1/projects` | 项目列表 |
| POST | `/api/v1/projects` | 创建项目 |
| GET | `/api/v1/projects/{project_id}` | 项目详情 |
| PATCH | `/api/v1/projects/{project_id}` | 更新项目 |
| DELETE | `/api/v1/projects/{project_id}` | 删除或归档项目 |
| GET | `/api/v1/projects/{project_id}/dashboard` | 项目仪表盘 |
| GET | `/api/v1/projects/{project_id}/members` | 项目成员列表 |
| POST | `/api/v1/projects/{project_id}/members` | 添加项目成员 |
| PATCH | `/api/v1/projects/{project_id}/members/{user_id}` | 修改成员权限 |
| DELETE | `/api/v1/projects/{project_id}/members/{user_id}` | 移除成员 |

## 5. 船型与几何接口

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/api/v1/projects/{project_id}/vessels` | 船型列表 |
| POST | `/api/v1/projects/{project_id}/vessels` | 创建船型 |
| GET | `/api/v1/vessels/{vessel_id}` | 船型详情 |
| PATCH | `/api/v1/vessels/{vessel_id}` | 更新船型 |
| DELETE | `/api/v1/vessels/{vessel_id}` | 删除或归档船型 |
| GET | `/api/v1/vessels/{vessel_id}/geometries` | 几何资产列表 |
| POST | `/api/v1/vessels/{vessel_id}/geometries` | 上传或创建几何资产 |
| GET | `/api/v1/geometries/{geometry_id}` | 几何详情 |
| POST | `/api/v1/geometries/{geometry_id}/preprocess` | 提交几何预处理任务 |
| GET | `/api/v1/geometries/{geometry_id}/preview` | 获取几何预览数据 |

## 6. 仿真算例接口

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/api/v1/projects/{project_id}/simulation-cases` | 算例列表 |
| POST | `/api/v1/projects/{project_id}/simulation-cases` | 创建算例 |
| GET | `/api/v1/simulation-cases/{case_id}` | 算例详情 |
| PATCH | `/api/v1/simulation-cases/{case_id}` | 更新算例基本信息 |
| POST | `/api/v1/simulation-cases/{case_id}/duplicate` | 复制算例 |
| POST | `/api/v1/simulation-cases/{case_id}/validate` | 校验算例完整性 |
| PATCH | `/api/v1/simulation-cases/{case_id}/fluid-condition` | 更新流体参数 |
| PUT | `/api/v1/simulation-cases/{case_id}/boundary-conditions` | 保存边界条件集合 |
| PUT | `/api/v1/simulation-cases/{case_id}/physics-scenario` | 保存物理场景配置 |
| GET | `/api/v1/simulation-cases/{case_id}/snapshots` | 查看配置快照 |

## 7. PINN 模型配置接口

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/api/v1/simulation-cases/{case_id}/model-configs` | 模型配置列表 |
| POST | `/api/v1/simulation-cases/{case_id}/model-configs` | 创建模型配置 |
| GET | `/api/v1/model-configs/{model_config_id}` | 模型配置详情 |
| PATCH | `/api/v1/model-configs/{model_config_id}` | 更新模型配置 |
| POST | `/api/v1/model-configs/{model_config_id}/validate` | 校验模型配置 |
| POST | `/api/v1/model-configs/{model_config_id}/clone` | 克隆模型配置 |
| GET | `/api/v1/model-configs/{model_config_id}/checkpoints` | 检查点列表 |

## 8. 任务接口

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| POST | `/api/v1/model-configs/{model_config_id}/training-jobs` | 创建训练任务 |
| POST | `/api/v1/simulation-cases/{case_id}/simulation-jobs` | 创建推理/仿真任务 |
| POST | `/api/v1/result-sets/{result_set_id}/postprocess-jobs` | 创建后处理任务 |
| GET | `/api/v1/jobs` | 任务列表 |
| GET | `/api/v1/jobs/{job_id}` | 任务详情 |
| GET | `/api/v1/jobs/{job_id}/logs` | 任务日志 |
| GET | `/api/v1/jobs/{job_id}/events` | 任务事件 |
| POST | `/api/v1/jobs/{job_id}/cancel` | 取消任务 |
| POST | `/api/v1/jobs/{job_id}/retry` | 重试任务 |

## 9. 结果与报告接口

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/api/v1/simulation-cases/{case_id}/result-sets` | 算例结果集列表 |
| GET | `/api/v1/result-sets/{result_set_id}` | 结果集详情 |
| GET | `/api/v1/result-sets/{result_set_id}/artifacts` | 结果工件列表 |
| GET | `/api/v1/result-artifacts/{artifact_id}/data` | 获取结果数据或下载链接 |
| POST | `/api/v1/result-sets/compare` | 多结果对比 |
| POST | `/api/v1/result-sets/{result_set_id}/reports` | 创建报告生成任务 |
| GET | `/api/v1/reports/{report_id}` | 报告详情 |
| GET | `/api/v1/reports/{report_id}/download` | 下载报告 |

## 10. 数据集接口

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/api/v1/projects/{project_id}/datasets` | 数据集列表 |
| POST | `/api/v1/projects/{project_id}/datasets` | 创建数据集 |
| GET | `/api/v1/datasets/{dataset_id}` | 数据集详情 |
| POST | `/api/v1/datasets/{dataset_id}/versions` | 上传数据集版本 |
| GET | `/api/v1/dataset-versions/{version_id}` | 数据集版本详情 |
| POST | `/api/v1/dataset-versions/{version_id}/quality-check` | 数据质量检查 |
| POST | `/api/v1/simulation-cases/{case_id}/datasets` | 关联数据集到算例 |

## 11. 核心业务流程

### 11.1 创建并运行静水阻力算例

```text
用户
  -> 创建项目
  -> 创建船型
  -> 上传船体几何
  -> 几何预处理
  -> 创建静水阻力算例
  -> 配置流体参数、计算域、边界条件
  -> 创建 PINN 模型配置
  -> 校验算例与模型配置
  -> 提交训练任务
  -> 查看训练日志和损失曲线
  -> 选择检查点执行推理
  -> 查看压力场、速度场、阻力系数
  -> 生成报告
```

后端关键动作：

1. 创建 `simulation_cases`、`fluid_conditions`、`boundary_conditions`、`physics_scenarios`。
2. 创建 `pinn_model_configs` 和 `loss_terms`。
3. 训练前创建 `case_snapshots`。
4. 创建 `jobs` 和 `training_jobs`，等待 Worker 领取执行。
5. Worker 写入 `job_logs`、`model_checkpoints`、`result_sets`、`result_artifacts`。

### 11.2 训练任务执行流程

```text
API 接收训练请求
  -> 权限校验
  -> 算例完整性校验
  -> 模型配置校验
  -> 生成配置快照
  -> 创建 Job
  -> Worker 从数据库领取任务
  -> 加载快照与文件资产
  -> 调用 PhysicsNeMo Adapter
  -> 执行训练
  -> 周期性写入日志、进度和损失
  -> 保存检查点和指标
  -> 更新任务状态
```

关键状态变化：

```text
PENDING -> RUNNING -> SUCCEEDED
PENDING -> RUNNING -> FAILED
PENDING -> CANCELED
RUNNING -> CANCELED
```

### 11.3 推理与后处理流程

```text
用户选择检查点
  -> 配置采样方式
  -> 创建推理任务
  -> Worker 加载模型
  -> 生成采样结果
  -> 后处理计算水动力指标
  -> 保存结果文件和索引
  -> 前端加载结果视图
```

常见采样方式：

- 全域规则网格采样。
- 船体附近局部加密采样。
- 指定剖面线采样。
- 指定二维切片采样。
- 时间序列采样。

### 11.4 多方案对比流程

```text
用户选择基准算例
  -> 克隆多个算例
  -> 修改船型参数或工况参数
  -> 批量提交训练/推理任务
  -> 选择结果集
  -> 生成对比视图
  -> 导出对比报告
```

对比指标建议：

- 阻力系数 `C_D`。
- 升力系数 `C_L`。
- 压力系数分布 `C_p`。
- 总损失和各损失项收敛曲线。
- PDE 残差均值、最大值和分位数。
- 与参考数据的 RMSE、MAE、相对误差。

### 11.5 数据同化流程

```text
用户上传观测数据
  -> 数据质量检查
  -> 字段映射和单位确认
  -> 将数据集关联到算例
  -> 在模型配置中启用 DATA loss term
  -> 提交训练任务
  -> 查看物理残差和数据拟合误差
```

## 12. 前端页面流程

### 12.1 页面结构

```text
登录页
  -> 项目列表
      -> 项目仪表盘
          -> 船型管理
          -> 几何资产
          -> 仿真算例
              -> 物理配置
              -> PINN 模型配置
              -> 训练任务
              -> 推理任务
              -> 结果查看
              -> 报告
          -> 数据集
          -> 成员与权限
```

### 12.2 关键页面能力

| 页面 | 核心能力 |
| --- | --- |
| 项目仪表盘 | 概览、最近任务、关键结果、快捷入口 |
| 船型页面 | 参数编辑、几何关联、版本记录 |
| 几何页面 | 上传、预览、预处理状态、错误提示 |
| 算例配置页 | 分步骤配置物理场景和边界条件 |
| 模型配置页 | 网络结构、损失项、训练参数、配置校验 |
| 任务监控页 | 状态、日志、损失曲线、取消/重试 |
| 结果查看页 | 图表、云图、剖面、指标、下载 |
| 对比页面 | 多结果选择、指标对齐、图表对比 |
| 报告页面 | 报告预览、生成、下载 |

## 13. 后端服务调用边界

| 服务 | 可以调用 | 不应直接调用 |
| --- | --- | --- |
| API Route | Domain Service | ORM Model、PhysicsNeMo |
| Domain Service | Repository、Storage、后台任务执行器、Adapter | 前端组件 |
| Repository | ORM/DB Session | PhysicsNeMo |
| Worker | Domain Service、Engine Adapter、Storage | 前端状态 |
| PINN Engine | PhysicsNeMo、本地文件 | Flask Request、用户 Session |

## 14. 错误码建议

| 错误码 | 说明 |
| --- | --- |
| `AUTH_REQUIRED` | 未登录 |
| `PERMISSION_DENIED` | 无权限 |
| `RESOURCE_NOT_FOUND` | 资源不存在 |
| `VALIDATION_ERROR` | 参数校验失败 |
| `CASE_NOT_READY` | 算例配置未完成 |
| `MODEL_CONFIG_INVALID` | 模型配置无效 |
| `JOB_STATE_INVALID` | 任务状态不允许当前操作 |
| `ENGINE_RUNTIME_ERROR` | PhysicsNeMo 引擎执行失败 |
| `STORAGE_ERROR` | 文件存储异常 |
| `DATASET_SCHEMA_ERROR` | 数据集字段或单位不匹配 |

## 15. API 后续详细设计清单

- 为每个请求和响应补充 JSON Schema。
- 明确分页、排序和过滤参数标准。
- 明确文件上传协议，选择表单上传、分片上传或预签名上传。
- 当前版本实时任务进度默认采用轮询；SSE/WebSocket 与 Redis 消息通道列入后续版本。
- 明确前端可视化数据格式和降采样策略。
