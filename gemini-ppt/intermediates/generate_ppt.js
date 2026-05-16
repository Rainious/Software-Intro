const pptxgen = require("pptxgenjs");

const COLORS = {
    PRIMARY: "065A82",    // Deep Blue
    SECONDARY: "1C7293",  // Teal
    ACCENT: "21295C",     // Midnight
    LIGHT_BG: "F8FAFC",   // Off-white/Slate-50
    TEXT: "1E293B",       // Slate-800
    WHITE: "FFFFFF",
    MUTED: "64748B",      // Slate-500
    LIGHT_TEAL: "E0F2F1"  // Very light teal for contrast
};

let pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.title = "船舶水动力学仿真系统 (PINN) 需求与架构设计";

// Helper: Add background and header to content slides
function addContentSlide(pres, title) {
    let slide = pres.addSlide();
    slide.background = { color: COLORS.LIGHT_BG };
    
    // Header bar
    slide.addShape(pres.shapes.RECTANGLE, {
        x: 0, y: 0, w: "100%", h: 0.8, fill: { color: COLORS.PRIMARY }
    });
    
    // Title
    slide.addText(title, {
        x: 0.5, y: 0, w: 9, h: 0.8,
        fontSize: 28, color: COLORS.WHITE, bold: true, valign: "middle", margin: 0
    });
    
    return slide;
}

// Slide 1: Title Slide
let s1 = pres.addSlide();
s1.background = { color: COLORS.ACCENT };
s1.addText("基于 PINN 的船舶水动力学仿真系统\n需求与架构设计汇报", {
    x: 0.5, y: 1.2, w: 9, h: 2.2,
    fontSize: 42, color: COLORS.WHITE, bold: true, align: "center", margin: 0
});
s1.addText("探索 AI 在工业水动力仿真中的应用", {
    x: 0.5, y: 3.4, w: 9, h: 0.5,
    fontSize: 22, color: COLORS.LIGHT_TEAL, italic: true, align: "center"
});
s1.addText("汇报人：软件工程系学生团队", {
    x: 0.5, y: 4.6, w: 9, h: 0.5,
    fontSize: 18, color: COLORS.WHITE, align: "center"
});
s1.addShape(pres.shapes.LINE, {
    x: 2.5, y: 4.1, w: 5, h: 0, line: { color: COLORS.SECONDARY, width: 2 }
});

// Slide 2: Background & Pain Points
let s2 = addContentSlide(pres, "项目背景与行业痛点");
s2.addText([
    { text: "行业痛点：", options: { bold: true, color: COLORS.PRIMARY, breakLine: true } },
    { text: "• 前处理复杂：网格划分耗时数天甚至数周", options: { bullet: true, breakLine: true } },
    { text: "• 计算资源高：传统 CFD 对计算集群要求极高", options: { bullet: true, breakLine: true } },
    { text: "• 迭代周期长：难以及时响应快速的设计变更", options: { bullet: true, breakLine: true } },
    { text: " ", options: { breakLine: true } },
    { text: "技术破局点：PINN (物理信息神经网络)", options: { bold: true, color: COLORS.PRIMARY, breakLine: true } },
    { text: "• 将 N-S 方程作为物理约束引入神经网络训练", options: { bullet: true, breakLine: true } },
    { text: "• 无网格计算：显著降低前处理与网格划分难度", options: { bullet: true, breakLine: true } },
    { text: "• 应用优势：快速参数扫描、逆问题求解与代理模型", options: { bullet: true } }
], { x: 0.6, y: 1.1, w: 6.2, h: 4, fontSize: 18, color: COLORS.TEXT });

s2.addShape(pres.shapes.RECTANGLE, {
    x: 7.0, y: 1.2, w: 2.5, h: 3.8, fill: { color: COLORS.WHITE },
    shadow: { type: "outer", color: "000000", opacity: 0.1, blur: 10, offset: 4, angle: 135 }
});
s2.addText("PINN 工作流优势", { x: 7.0, y: 1.4, w: 2.5, h: 0.5, align: "center", bold: true, color: COLORS.SECONDARY, fontSize: 18 });
s2.addText("1. 物理驱动\n2. 算力优化\n3. 快速响应", { x: 7.0, y: 2.2, w: 2.5, h: 2, fontSize: 18, align: "center", color: COLORS.TEXT });

// Slide 3: Goals & Boundaries
let s3 = addContentSlide(pres, "系统建设目标与边界");
s3.addText("核心目标", { x: 0.6, y: 1.2, w: 4, h: 0.5, fontSize: 22, bold: true, color: COLORS.PRIMARY });
s3.addText([
    { text: "构建一个可扩展、可复现的 Web 化 PINN 仿真平台", options: { bullet: true, breakLine: true } },
    { text: "服务于水动力研究、船型设计及工程教学", options: { bullet: true } }
], { x: 0.6, y: 1.8, w: 4.4, h: 1.5, fontSize: 17, color: COLORS.TEXT });

s3.addText("系统边界", { x: 5.4, y: 1.2, w: 4, h: 0.5, fontSize: 22, bold: true, color: COLORS.PRIMARY });
s3.addTable([
    [{ text: "包含范围", options: { bold: true, fill: { color: COLORS.PRIMARY }, color: COLORS.WHITE } }, { text: "不包含范围", options: { bold: true, fill: { color: COLORS.MUTED }, color: COLORS.WHITE } }],
    ["算例管理、物理配置", "复杂 CAD 建模能力"],
    ["PhysicsNeMo 训练调度", "替代高保真工业 CFD"],
    ["流场可视化、报告导出", "大规模 HPC 集群集成"]
], { x: 5.4, y: 1.8, w: 4, h: 3.2, fontSize: 15, border: { pt: 1, color: "E2E8F0" }, align: "center", valign: "middle" });

// Slide 4: System Architecture
let s4 = addContentSlide(pres, "总体架构设计 (解耦与分层)");
const archX = 0.5, archY = 1.2, archW = 9, layerH = 0.7, gap = 0.2;
const layers = [
    { name: "表现层 (React + JavaScript)", color: "0EA5E9" },
    { name: "API 与业务层 (Python Flask)", color: "065A82" },
    { name: "任务调度层 (PostgreSQL Worker)", color: "1C7293" },
    { name: "仿真计算引擎 (NVIDIA PhysicsNeMo)", color: "21295C" }
];
layers.forEach((layer, i) => {
    s4.addShape(pres.shapes.RECTANGLE, {
        x: archX, y: archY + i * (layerH + gap), w: archW, h: layerH,
        fill: { color: layer.color }, line: { color: COLORS.WHITE, width: 1 }
    });
    s4.addText(layer.name, {
        x: archX, y: archY + i * (layerH + gap), w: archW, h: layerH,
        fontSize: 20, color: COLORS.WHITE, bold: true, align: "center", valign: "middle"
    });
});
s4.addText("关键设计：分离交互业务与长耗时物理训练任务，确保 Web 体验流畅。", {
    x: 0.5, y: 4.8, w: 9, h: 0.5, fontSize: 16, color: COLORS.MUTED, italic: true, align: "center"
});

// Slide 5: Business Flow
let s5 = addContentSlide(pres, "核心业务流程闭环");
const flowSteps = ["1. 资产准备", "2. 物理配置", "3. 模型配置", "4. 异步执行", "5. 结果分析"];
flowSteps.forEach((step, i) => {
    s5.addShape(pres.shapes.RECTANGLE, {
        x: 0.5 + i * 1.9, y: 1.5, w: 1.6, h: 2.2, fill: { color: COLORS.WHITE },
        line: { color: COLORS.SECONDARY, width: 2 }
    });
    s5.addText(step, {
        x: 0.5 + i * 1.9, y: 1.6, w: 1.6, h: 0.5,
        fontSize: 18, bold: true, color: COLORS.PRIMARY, align: "center"
    });
});
s5.addText("上传船型几何\n自动化预处理", { x: 0.5, y: 2.3, w: 1.6, h: 1, fontSize: 15, align: "center" });
s5.addText("定义流体参数\n设置边界条件", { x: 2.4, y: 2.3, w: 1.6, h: 1, fontSize: 15, align: "center" });
s5.addText("选择网络结构\n分配损失权重", { x: 4.3, y: 2.3, w: 1.6, h: 1, fontSize: 15, align: "center" });
s5.addText("提交训练任务\nWorker 队列调度", { x: 6.2, y: 2.3, w: 1.6, h: 1, fontSize: 15, align: "center" });
s5.addText("生成流场云图\n导出对比报告", { x: 8.1, y: 2.3, w: 1.6, h: 1, fontSize: 15, align: "center" });
for (let i = 0; i < 4; i++) {
    s5.addShape(pres.shapes.LINE, {
        x: 2.15 + i * 1.9, y: 2.6, w: 0.2, h: 0, line: { color: COLORS.MUTED, width: 2 }
    });
}

// Slide 6: Module Design
let s6 = addContentSlide(pres, "领域模块设计亮点");
const modules = [
    { title: "前端视图模块", desc: "聚焦实时监控与多维度结果可视化展示" },
    { title: "Flask API 模块", desc: "鉴权、快照生成、避免请求长连接阻塞" },
    { title: "Worker 调度模块", desc: "隔离 GPU 训练任务与 CPU 后处理任务" },
    { title: "引擎适配层", desc: "屏蔽框架底层迭代，降低业务系统耦合度" }
];
modules.forEach((mod, i) => {
    const x = i < 2 ? 0.6 : 5.2, y = i % 2 === 0 ? 1.4 : 3.4;
    s6.addShape(pres.shapes.RECTANGLE, {
        x: x, y: y, w: 4.2, h: 1.6, fill: { color: COLORS.WHITE }, line: { color: COLORS.PRIMARY, width: 1 }
    });
    s6.addText(mod.title, { x: x + 0.2, y: y + 0.1, w: 3.8, h: 0.5, fontSize: 19, bold: true, color: COLORS.PRIMARY });
    s6.addText(mod.desc, { x: x + 0.2, y: y + 0.7, w: 3.8, h: 0.8, fontSize: 17, color: COLORS.TEXT });
});

// Slide 7: DB & Traceability
let s7 = addContentSlide(pres, "数据库与实验可追踪性");
s7.addText("科研级数据追踪机制", { x: 0.6, y: 1.2, w: 4.6, h: 0.5, fontSize: 22, bold: true, color: COLORS.PRIMARY });
s7.addText([
    { text: "配置快照 (Snapshot) 机制：", options: { bold: true, breakLine: true, color: COLORS.SECONDARY } },
    { text: "任务启动即锁定所有参数，确保实验过程 100% 可复现。", options: { breakLine: true } },
    { text: "模型版本与检查点管理：", options: { bold: true, breakLine: true, color: COLORS.SECONDARY } },
    { text: "自动化追踪最优检查点，支持多版本迭代对比。" }
], { x: 0.6, y: 1.8, w: 4.6, h: 3, fontSize: 17, color: COLORS.TEXT });

s7.addShape(pres.shapes.RECTANGLE, { x: 5.6, y: 1.2, w: 3.8, h: 3.8, fill: { color: COLORS.ACCENT, transparency: 5 } });
s7.addText("数据存储架构", { x: 5.6, y: 1.4, w: 3.8, h: 0.5, color: COLORS.WHITE, bold: true, align: "center", fontSize: 20 });
s7.addText("结构化元数据 (PostgreSQL)\n· 用户权限 / 算例元数据\n· 任务状态 / 配置索引\n\n大容量资产 (MinIO/S3)\n· 几何文件 / 模型权重\n· 仿真结果 / PDF 报告", {
    x: 5.8, y: 2.1, w: 3.4, h: 2.5, color: COLORS.WHITE, fontSize: 16, align: "center", valign: "middle"
});

// Slide 8: QA & Physics Validation
let s8 = addContentSlide(pres, "质量保证与物理验证");
s8.addText("全方位保障仿真结果的可信度", { x: 0.5, y: 1.0, w: 9, h: 0.5, fontSize: 22, bold: true, color: COLORS.PRIMARY, align: "center" });
const qaCols = [
    { title: "软件工程验证", items: ["状态机流转严谨校验", "基于项目的成员隔离", "防止数据误删的软删除"] },
    { title: "物理科学验证", items: ["物理残差 (PDE) 分布监控", "全局/局部质量守恒评估", "基准算例 A/B/C 分级制度"] }
];
qaCols.forEach((col, i) => {
    s8.addShape(pres.shapes.RECTANGLE, {
        x: 0.6 + i * 4.6, y: 1.6, w: 4.2, h: 3.4, fill: { color: COLORS.WHITE },
        line: { color: i === 0 ? COLORS.SECONDARY : COLORS.PRIMARY, width: 2 }
    });
    s8.addText(col.title, { x: 0.6 + i * 4.6, y: 1.8, w: 4.2, h: 0.5, fontSize: 19, bold: true, align: "center", color: COLORS.PRIMARY });
    s8.addText(col.items.map(it => "• " + it).join("\n"), {
        x: 0.8 + i * 4.6, y: 2.5, w: 3.8, h: 2, fontSize: 17, color: COLORS.TEXT
    });
});

// Slide 9: Summary & Roadmap
let s9 = addContentSlide(pres, "总结与演进路线");
s9.addText("核心价值：融合现代 Web 技术与深度学习，加速工业水动力研发流程。", {
    x: 0.6, y: 1.0, w: 8.8, h: 0.5, fontSize: 19, bold: true, color: COLORS.PRIMARY, align: "center"
});
s9.addChart(pres.charts.BAR, [{
    name: "阶段重点", labels: ["V1 原型", "V2 工程化", "V3 扩展", "V4 平台"], values: [1, 2, 3, 4]
}], {
    x: 0.5, y: 1.6, w: 9, h: 3.2, barDir: "col", showLegend: false,
    chartColors: [COLORS.SECONDARY, COLORS.PRIMARY, COLORS.ACCENT, "0EA5E9"],
    valGridLine: { style: "none" }, catAxisLabelColor: COLORS.MUTED
});
s9.addText("V1: 核心链路闭环 | V2: 协作对比与报告 | V3: 复杂波动模型 | V4: 弹性算力调度", {
    x: 0.5, y: 5.0, w: 9, h: 0.4, fontSize: 16, color: COLORS.PRIMARY, align: "center", bold: true
});

// Slide 10: Q&A
let s10 = pres.addSlide();
s10.background = { color: COLORS.ACCENT };
s10.addText("感谢各位的聆听与指导！", {
    x: 0.5, y: 1.8, w: 9, h: 1.2, fontSize: 48, color: COLORS.WHITE, bold: true, align: "center", margin: 0
});
s10.addText("欢迎交流与提问 (Q & A)", {
    x: 0.5, y: 3.2, w: 9, h: 0.5, fontSize: 26, color: COLORS.LIGHT_TEAL, align: "center"
});

pres.writeFile({ fileName: "船舶水动力学仿真系统汇报.pptx" }).then(fileName => {
    console.log("Created file: " + fileName);
});
