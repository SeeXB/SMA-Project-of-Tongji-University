# 行动导向型辅导系统（Action-Oriented Tutor）原型实现方案

目标：基于 `Flask + Gradio + OpenAI + ChromaDB`，快速构建一个类似 DeepTutor 的行动导向型 AI Tutor 原型，并尽可能利用 GitHub Copilot 进行 “vibe coding”。

系统核心思想：

- 不直接讲解知识
- 不给完整答案
- 不做长篇教学
- 只生成：
  - 行动提示（nudge）
  - 思考刺激（provocation）
  - 微练习（micro-task）
  - 反思问题（reflection）

------

# 一、系统总体架构

## 整体架构

```text
                ┌──────────────────────┐
                │      Gradio UI       │
                │ 上传学习轨迹/对话交互 │
                └─────────┬────────────┘
                          │
                          ▼
                ┌──────────────────────┐
                │      Flask API       │
                │ orchestrator         │
                └─────────┬────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼

┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ TraceIndexer │  │ GapDetector  │  │ NudgeEngine  │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                 │
       ▼                 ▼                 ▼

┌──────────────────────────────────────────┐
│               ChromaDB                   │
│ learning traces / embeddings / concepts  │
└──────────────────────────────────────────┘

                          │
                          ▼
                ┌──────────────────────┐
                │      OpenAI API      │
                │ embeddings + LLM     │
                └──────────────────────┘
```

------

# 二、系统功能设计

------

# 1. Trace Indexer（学习轨迹索引器）

## 功能

解析：

- 学习笔记
- 做题记录
- 错题
- 时间戳
- 练习频率
- 学习停留时间

并建立：

- concept embedding
- concept timeline
- error statistics

------

## 输入

```json
{
  "student_id": "stu001",
  "notes": "...",
  "exercise_logs": [...],
  "error_history": [...],
  "timestamps": [...]
}
```

------

## 输出

```json
{
  "concepts": [
    {
      "name": "gradient descent",
      "mastery": 0.42,
      "last_seen": "2026-05-07",
      "mistake_count": 8
    }
  ]
}
```

------

## Copilot 提示词（核心）

在 VSCode 中创建：

```python
# TODO:
# Build a TraceIndexer class for an AI tutoring system.
# Requirements:
# - Parse student notes, exercise logs, and error history
# - Extract concepts using OpenAI embeddings
# - Store concept vectors in ChromaDB
# - Track timestamps and mistake frequencies
# - Return structured learning-state summaries
# Use clean modular Python design.
```

------

## 推荐实现

### 技术：

- 本地Embedding模型(如 SentenceTransformers)
- ChromaDB semantic indexing

------

## 数据结构

```python
class LearningTrace:
    notes: str
    exercises: list
    errors: list
    timestamps: list
```

------

## ChromaDB collection

```python
collection.add(
    documents=[chunk],
    embeddings=[embedding],
    metadatas=[{
        "concept": concept,
        "mistakes": 3,
        "timestamp": ts
    }]
)
```

------

# 2. Gap Detector（知识缺口检测器）

------

# 功能

识别：

- 高频错误
- 长时间未复习
- 逃避题型
- 概念混淆
- “似懂非懂”状态

------

## 核心思想

Gap ≠ 不会

而是：

```text
high confusion
+ low revisit frequency
+ repeated hesitation
+ weak retrieval
```

------

# 检测指标

## [1] Error Density

$$
ErrorDensity(c)=\frac{Mistakes(c)}{Attempts(c)}
$$

------

## [2] Forgetting Score

genui{"math_block_widget_always_prefetch_v2":{"content":"Retention(c)=e^{-\lambda t}"}}

------

## [3] Avoidance Score

```text
concept mentioned often
BUT practice count very low
```

------

# Gap 输出示例

```json
{
  "weak_concepts": [
    {
      "concept": "backpropagation",
      "reason": "high error + low revisit"
    },
    {
      "concept": "bayes theorem",
      "reason": "avoidance pattern"
    }
  ]
}
```

------

# Copilot 提示词

```python
# TODO:
# Implement a GapDetector module.
# Requirements:
# - Analyze indexed learning traces
# - Detect weak concepts based on:
#   * repeated mistakes
#   * long inactivity
#   * concept avoidance
#   * unstable performance
# - Return ranked learning gaps
# Include scoring heuristics and clean APIs.
```

------

# 3. Nudge Engine（行动刺激引擎）

------

# 功能

生成：

- 微挑战
- 反思问题
- retrieval prompts
- action provocation

禁止：

- 长篇解释
- 完整解答
- lecture-style teaching

------

# Nudge Prompt Engineering

## System Prompt

```text
You are an action-oriented AI tutor.

Never explain concepts directly.
Never provide full solutions.
Never lecture.

Generate only:
- actionable prompts
- thinking provocations
- short retrieval tasks
- reflection questions

The response must:
- be concise
- trigger active thinking
- focus on one weak concept
- avoid encouragement fluff
```

------

## User Prompt 模板

```text
Weak Concept:
{concept}

Reason:
{reason}

Student Context:
{trace_summary}

Generate one targeted nudge.
```

------

# 输出示例

```json
{
  "nudge":
  "Without using notes, write the chain rule path
   from output loss to hidden-layer weights."
}
```

------

# Copilot 提示词

```python
# TODO:
# Build a NudgeEngine for an AI tutoring assistant.
# Requirements:
# - Accept detected weak concepts
# - Generate concise action-oriented nudges
# - No explanations or full solutions
# - Use OpenAI chat completion API
# - Produce retrieval and reflection prompts
# Return JSON-safe outputs.
```


# 三、Flask 后端设计

------

# API 设计

## 上传学习轨迹

```http
POST /upload_trace
```

------

## 分析知识缺口

```http
POST /detect_gap
```

------

## 生成 Nudge

```http
POST /generate_nudge
```

------

# Flask 主路由示例

```python
@app.route("/generate_nudge", methods=["POST"])
def generate_nudge():

    trace = request.json

    indexed = trace_indexer.process(trace)

    gaps = gap_detector.detect(indexed)

    nudge = nudge_engine.generate(gaps)

    return jsonify(nudge)
```

------

# 三、最终建议

对于课程原型：

## 不要追求：

- 完整教育系统
- 超复杂 agent
- 真正长期记忆

------

## 要重点突出：

### 1. Action-Oriented Tutoring

核心创新点。

------

### 2. Learning Trace → Gap → Nudge Pipeline

这是最关键的研究逻辑。

------

### 3. “不解释，只推动思考”

这是区别于普通 ChatBot Tutor 的核心。