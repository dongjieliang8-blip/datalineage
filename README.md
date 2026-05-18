# DataLineage

Multi-agent data lineage tracking and impact analysis pipeline.

## Overview

DataLineage uses 4 specialized agents to scan data sources, map dependencies, analyze change impacts, and check compliance:

```
Lineage Scanner -> Dependency Mapper -> Impact Analyzer -> Compliance Checker
```

## Install

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Run full pipeline
python -m src.main scan --input ./demo/sample_data/schema.yaml

# Map dependencies only
python -m src.main map --input ./demo/sample_data/schema.yaml

# Analyze impact of schema changes
python -m src.main impact --input ./demo/sample_data/schema.yaml --target users

# Check compliance
python -m src.main compliance --input ./demo/sample_data/schema.yaml
```

---

多 Agent 协作数据血缘追踪与影响分析流水线。

## 概述

DataLineage 使用 4 个专业 Agent 协作完成数据血缘追踪、依赖映射、影响分析和合规检查。

## 安装

```bash
pip install -r requirements.txt
```

## 使用

```bash
# 运行完整流水线
python -m src.main scan --input ./demo/sample_data/schema.yaml

# 仅映射依赖关系
python -m src.main map --input ./demo/sample_data/schema.yaml

# 分析 Schema 变更影响
python -m src.main impact --input ./demo/sample_data/schema.yaml --target users

# 合规检查
python -m src.main compliance --input ./demo/sample_data/schema.yaml
```
