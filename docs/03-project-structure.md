# 项目结构与层级设计

## 1. 设计目标

项目结构需要同时服务于 Web 业务系统、PINN 训练引擎、前端可视化和部署运维。目录划分应保持以下原则：

- 前端、后端、PINN 引擎和基础设施相互独立。
- 后端业务领域按模块聚合，避免所有逻辑堆在控制器中。
- PhysicsNeMo 相关逻辑集中在独立引擎目录和后端适配层中。
- 数据库迁移、配置模板、测试、脚本和文档有清晰位置。
- 未来可以平滑拆分为独立服务，例如模型训练服务或结果可视化服务。

## 2. 推荐项目根目录

```text
pinn-ship-hydro/
  README.md
  .env.example
  docker-compose.yml
  docs/
  backend/
  frontend/
  pinn_engine/
  infra/
  scripts/
  tests/
  data_samples/
  storage/
```

## 3. 完整目录雏形

```text
pinn-ship-hydro/
  README.md
  .env.example
  docker-compose.yml

  docs/
    01-requirements.md
    02-system-architecture.md
    03-project-structure.md
    04-module-design.md
    05-database-design.md
    06-api-and-workflows.md
    07-validation-quality-risk.md
    adr/
      0001-use-physicsnemo.md
      0002-async-training-jobs.md

  backend/
    README.md
    requirements.txt
    pyproject.toml
    migrations/
    app/
      __init__.py
      main.py
      config.py
      extensions.py

      api/
        __init__.py
        v1/
          __init__.py
          auth_routes.py
          project_routes.py
          vessel_routes.py
          geometry_routes.py
          simulation_case_routes.py
          model_config_routes.py
          job_routes.py
          result_routes.py
          dataset_routes.py
          report_routes.py
          admin_routes.py

      core/
        auth.py
        permissions.py
        errors.py
        logging.py
        pagination.py
        validation.py
        security.py

      db/
        session.py
        base.py
        models/
          user.py
          project.py
          vessel.py
          geometry.py
          simulation_case.py
          physics_scenario.py
          pinn_model.py
          job.py
          result.py
          dataset.py
          report.py
          audit_log.py
        repositories/
          user_repository.py
          project_repository.py
          simulation_repository.py
          job_repository.py
          result_repository.py

      domains/
        auth/
          service.py
          schemas.py
        projects/
          service.py
          schemas.py
        vessels/
          service.py
          schemas.py
        geometries/
          service.py
          schemas.py
          validators.py
        simulations/
          service.py
          schemas.py
          physics_templates.py
        pinn_models/
          service.py
          schemas.py
          config_builder.py
        jobs/
          service.py
          schemas.py
          state_machine.py
        results/
          service.py
          schemas.py
          metrics.py
        reports/
          service.py
          renderer.py

      integrations/
        physicsnemo/
          adapter.py
          config_mapper.py
          job_runner_client.py
        storage/
          object_store.py
          local_store.py
        job_runtime/
          job_dispatcher.py
          progress_recorder.py
        visualization/
          tile_generator.py
          vtk_converter.py

      workers/
        training_worker.py
        inference_worker.py
        postprocess_worker.py
        report_worker.py

  pinn_engine/
    README.md
    physics/
      navier_stokes.py
      potential_flow.py
      wave_equations.py
      turbulence_closure.py
    geometries/
      hull_domain.py
      sampling_domain.py
      signed_distance.py
    constraints/
      boundary_conditions.py
      initial_conditions.py
      pde_residuals.py
      data_assimilation.py
    networks/
      mlp.py
      fourier_features.py
      siren.py
    trainers/
      base_trainer.py
      resistance_trainer.py
      wave_response_trainer.py
      maneuvering_trainer.py
    inference/
      field_sampler.py
      section_sampler.py
      force_integrator.py
    postprocess/
      hydrodynamic_coefficients.py
      residual_statistics.py
      result_exporter.py
    configs/
      templates/
        calm_water_resistance.yaml
        regular_wave_response.yaml
        data_assimilation.yaml
    runtime/
      environment.py
      checkpointing.py
      reproducibility.py

  frontend/
    README.md
    package.json
    public/
    src/
      main.jsx
      App.jsx
      routes/
        index.jsx
        protectedRoute.jsx
      api/
        client.js
        authApi.js
        projectApi.js
        simulationApi.js
        jobApi.js
        resultApi.js
      store/
        authStore.js
        projectStore.js
        jobStore.js
      layouts/
        AppLayout.jsx
        ProjectLayout.jsx
      pages/
        LoginPage.jsx
        ProjectListPage.jsx
        ProjectDashboardPage.jsx
        VesselPage.jsx
        GeometryPage.jsx
        SimulationCasePage.jsx
        ModelConfigPage.jsx
        JobMonitorPage.jsx
        ResultViewerPage.jsx
        ComparisonPage.jsx
        ReportPage.jsx
        AdminPage.jsx
      components/
        navigation/
        forms/
        charts/
        viewers/
        tables/
        dialogs/
      features/
        auth/
        projects/
        vessels/
        simulations/
        pinnModels/
        jobs/
        results/
        reports/
      styles/
        tokens.css
        global.css

  infra/
    docker/
      backend.Dockerfile
      frontend.Dockerfile
      worker.Dockerfile
    nginx/
      nginx.conf
    postgres/
      init.sql
    minio/
      README.md
    monitoring/
      prometheus.yml
      grafana-dashboard.json

  scripts/
    dev_backend.ps1
    dev_frontend.ps1
    dev_worker.ps1
    seed_demo_data.py
    export_report_assets.py

  tests/
    backend/
      unit/
      integration/
    pinn_engine/
      physics/
      trainers/
      regression/
    frontend/
      unit/
      e2e/

  data_samples/
    geometries/
    observations/
    benchmark_cases/

  storage/
    .gitkeep
```

## 4. 后端层级设计

### 4.1 API 层

API 层只负责 HTTP 语义：

- 解析请求参数。
- 调用鉴权和权限校验。
- 调用领域服务。
- 返回统一响应结构。
- 不包含复杂业务规则和 PhysicsNeMo 细节。

### 4.2 领域服务层

领域服务层负责业务用例：

- 创建项目、算例、任务和结果。
- 校验对象状态转换是否合理。
- 组装配置快照。
- 协调 Repository、Storage、后台任务执行器和 PhysicsNeMo Adapter。

### 4.3 Repository 层

Repository 层封装数据库访问：

- 提供按 ID、项目、用户、状态等维度的查询。
- 隐藏 ORM 查询细节。
- 统一处理事务边界。

### 4.4 Integration 层

Integration 层封装外部系统或外部框架：

- PhysicsNeMo 适配。
- 对象存储读写。
- 数据库驱动的任务分发与进度记录。
- 可视化文件转换。

### 4.5 Worker 层

Worker 层执行耗时任务：

- 从数据库领取待执行任务 ID。
- 读取数据库配置快照。
- 调用 `pinn_engine` 训练或推理。
- 将日志、指标、工件和状态写回系统。

## 5. 前端层级设计

### 5.1 页面层 Pages

页面层对应业务路由，例如项目列表、算例配置、任务监控和结果查看。

### 5.2 特性层 Features

特性层按业务领域组织状态和组件，避免所有组件进入全局公共目录。

### 5.3 组件层 Components

组件层存放可复用 UI：

- 表单控件。
- 图表组件。
- 结果查看器。
- 表格、弹窗、导航。

### 5.4 API Client 层

统一封装 HTTP 请求、错误处理、Token 注入和分页参数。

## 6. PINN 引擎层级设计

### 6.1 Physics

定义控制方程残差和物理量计算，包括不可压 Navier-Stokes、势流、波方程和扩展湍流项。

### 6.2 Geometries

定义计算域、船体边界、采样域和几何距离函数。

### 6.3 Constraints

封装边界条件、初始条件、观测数据约束、PDE 残差约束和守恒约束。

### 6.4 Networks

封装可选网络结构。初期可通过 PhysicsNeMo 原生组件组合，项目内只保留配置和扩展层。

### 6.5 Trainers

按仿真类型组织训练流程。Trainer 不处理 Web 权限和数据库事务，只接受标准化配置并输出标准化结果。

### 6.6 Inference 与 Postprocess

推理层负责采样和预测，后处理层负责计算工程指标、转换文件格式和生成可视化数据。

## 7. 配置分层

| 配置类型 | 位置 | 示例 |
| --- | --- | --- |
| 环境配置 | `.env` | 数据库连接、存储路径、文件存储配置 |
| 业务配置 | 数据库 | 项目、算例、权限、任务状态 |
| 模型配置 | 数据库 + 快照文件 | 网络结构、损失权重、训练参数 |
| 引擎模板 | `pinn_engine/configs/templates` | 静水阻力、规则波响应 |
| 部署配置 | `infra` | Docker、Nginx、监控 |

## 8. 命名建议

- 数据库表使用复数蛇形命名，例如 `simulation_cases`。
- 后端 Python 包使用小写蛇形命名。
- 前端组件使用 PascalCase。
- API 路径使用复数资源名，例如 `/api/v1/projects/{project_id}/simulation-cases`。
- 任务类型使用固定枚举，例如 `TRAINING`、`INFERENCE`、`POSTPROCESS`、`REPORT`。

## 9. 演进路线

1. 文档阶段：确认需求、架构、模块、数据库和接口边界。
2. 原型阶段：实现用户、项目、算例、训练任务和简单结果展示。
3. 引擎阶段：接入 PhysicsNeMo，跑通一个基准 PINN 算例。
4. 工程化阶段：补权限、数据库驱动的后台任务管理、检查点、报告和可观测性。
5. 扩展阶段：新增仿真类型、可视化能力和资源调度能力。
6. 平台增强阶段：按需引入独立消息队列、实时推送和缓存能力。
