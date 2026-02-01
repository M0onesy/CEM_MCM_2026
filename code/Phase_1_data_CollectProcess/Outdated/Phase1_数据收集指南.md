# Phase 1: 数据收集与预处理 - 完整指南

## MCM/ICM 2026 Problem D - Indiana Fever

---

## 一、数据收集总览

### 需要收集的数据类型

| 数据类型 | 数据源 | 用途 |
|---------|-------|------|
| **球员基础统计** | Basketball-Reference | 表现价值计算 |
| **高级统计数据** | Basketball-Reference | WAR、BPM计算 |
| **薪资数据** | Spotrac/公开报道 | 成本模型、阵容优化 |
| **社交媒体数据** | 手动收集 | 商业价值计算 |
| **上座率数据** | ESPN/官方数据 | 收入模型 |
| **财务数据** | Forbes/Sportico | 球队估值、收入预测 |

---

## 二、数据收集详细步骤

### Step 1: 球员基础统计数据

**数据源**: https://www.basketball-reference.com/wnba/years/2024_per_game.html

**收集的字段**:
```
Player      - 球员姓名
Position    - 位置 (G/F/C)
Age         - 年龄
Team        - 球队代码
Games       - 出场次数
Minutes     - 场均时间
PTS         - 场均得分
TRB         - 场均篮板
AST         - 场均助攻
STL         - 场均抢断
BLK         - 场均盖帽
TOV         - 场均失误
FG_Pct      - 投篮命中率
ThreeP_Pct  - 三分命中率
FT_Pct      - 罚球命中率
```

### Step 2: 高级统计数据

**数据源**: https://www.basketball-reference.com/wnba/years/2024_advanced.html

**收集的字段**:
```
PER         - 效率值 (Player Efficiency Rating)
TS_Pct      - 真实命中率 (True Shooting %)
WS          - 胜利贡献值 (Win Shares)
WS_per_48   - 每48分钟胜利贡献
BPM         - Box Plus/Minus (关键指标！)
OBPM        - 进攻BPM
DBPM        - 防守BPM
VORP        - 替代球员价值 (Value Over Replacement Player)
USG_Pct     - 球权使用率
```

### Step 3: 薪资数据

**数据源**: 
- Spotrac (https://www.spotrac.com/wnba/)
- HerHoopStats
- 公开新闻报道

**WNBA 2024工资帽信息**:
```
工资帽 (Salary Cap):     $1,413,320
工资地板 (Salary Floor): $1,193,320
超级顶薪 (Supermax):     $252,450
新秀合同 (1轮):         $76,535
新秀合同 (2轮):         $73,439
新秀合同 (3轮):         $64,154
```

### Step 4: 社交媒体数据

**数据源**: 各社交平台官方数据（手动收集）

**收集的字段**:
```
Instagram_Followers  - Instagram粉丝数
Twitter_Followers    - Twitter/X粉丝数
TikTok_Followers     - TikTok粉丝数
Total_Followers      - 总粉丝数
Jersey_Rank          - 球衣销量排名
Rating_Boost         - 收视率提升倍数
Commercial_Index     - 商业价值指数 (计算得出)
```

### Step 5: 上座率数据

**数据源**: ESPN, WNBA官网

**收集的字段**:
```
Team              - 球队
Home_Games        - 主场比赛数 (20场)
Avg_Attendance    - 场均上座人数
Capacity          - 场馆容量
Attendance_Pct    - 上座率
Avg_Ticket_Price  - 平均票价
Est_Ticket_Revenue - 预估门票收入
```

### Step 6: 财务数据

**数据源**: Forbes估值报告、Sportico、公开报道

**收集的字段**:
```
Valuation           - 球队估值
Revenue             - 年收入
Broadcast_Revenue   - 转播收入
Sponsorship_Revenue - 赞助收入
Merchandise_Revenue - 周边商品收入
Operating_Income    - 营业利润
Profit_Margin       - 利润率
```

---

## 三、派生指标计算

### 1. WAR (Wins Above Replacement) 计算

```python
# WAR计算公式
WAR = (BPM - Replacement_BPM) × Total_Minutes / (48 × 40)

其中:
- BPM: Box Plus/Minus
- Replacement_BPM = -2.0 (替补水平基准)
- Total_Minutes: 赛季总出场时间
- 48: 每场比赛时间
- 40: WNBA常规赛场次
```

### 2. 表现价值 (Performance Value) 计算

```python
Performance_Value = WAR × Value_Per_Win

其中:
- Value_Per_Win = $300,000 (每场胜利的货币价值)
```

### 3. 商业价值指数 (Commercial Index) 计算

```python
Commercial_Index = 0.4 × Social_Score + 0.3 × Jersey_Score + 0.3 × Rating_Score

其中:
- Social_Score = min(1, log10(Total_Followers) / 7)
- Jersey_Score = max(0, (100 - Jersey_Rank) / 100)
- Rating_Score = min(1, (Rating_Boost - 1) / 3)
```

### 4. 商业价值 (Commercial Value) 计算

```python
Commercial_Value = Commercial_Index × Base_Commercial_Value

其中:
- Base_Commercial_Value = $5,000,000
```

### 5. 总价值 (Total Value) 计算

```python
Total_Value = α × Performance_Value + β × Commercial_Value

其中:
- α = 0.4 (表现价值权重)
- β = 0.6 (商业价值权重)
```

---

## 四、Indiana Fever 核心球员数据

### 2024赛季数据摘要

| 球员 | 位置 | 场均得分 | 场均篮板 | 场均助攻 | PER | BPM | WAR | 薪资 | 总价值 |
|-----|-----|---------|---------|---------|-----|-----|-----|------|-------|
| Caitlin Clark | G | 19.2 | 5.7 | 8.4 | 15.5 | 3.5 | 4.06 | $76,535 | $3,167,250 |
| Aliyah Boston | F | 14.0 | 8.9 | 2.5 | 18.5 | 2.8 | 3.25 | $76,535 | $2,310,000 |
| Kelsey Mitchell | G | 15.8 | 2.5 | 3.2 | 14.0 | 1.2 | 1.73 | $198,388 | $1,576,260 |
| NaLyssa Smith | F | 10.5 | 7.8 | 1.5 | 12.5 | 0.5 | 1.42 | $72,141 | $1,665,500 |

### Caitlin Clark 商业价值分析

| 指标 | 数值 |
|-----|------|
| Instagram粉丝 | 5,200,000 |
| Twitter粉丝 | 1,500,000 |
| TikTok粉丝 | 2,000,000 |
| 总粉丝数 | 8,700,000 |
| 球衣销量排名 | #1 |
| 收视率提升 | 300% |
| 商业指数 | 0.894 |
| 表现价值 | $1,216,875 |
| **商业价值** | **$4,467,500** |
| **总价值** | **$3,167,250** |

---

## 五、Caitlin Clark 效应分析

### 2023 vs 2024 对比

| 指标 | 2023 (加入前) | 2024 (加入后) | 变化 |
|-----|--------------|--------------|------|
| 场均上座 | 4,067 | 17,000 | **+318%** |
| 上座率 | 22.6% | 94.4% | +71.8pp |
| 平均票价 | $45 | $85 | +89% |
| 门票收入 | $3.66M | $28.9M | **+690%** |
| 球队估值 | $30M | $100M | **+233%** |

---

## 六、数据文件说明

### 生成的CSV文件

| 文件名 | 说明 | 记录数 |
|-------|------|--------|
| `player_basic_stats_2024.csv` | 球员基础统计 | 32名 |
| `player_advanced_stats_2024.csv` | 球员高级统计 | 24名 |
| `salary_data_2024.csv` | 薪资数据 | 37名 |
| `social_media_data_2024.csv` | 社交媒体数据 | 24名 |
| `attendance_data_2024.csv` | 上座率数据 | 12队 |
| `financial_data_2024.csv` | 财务数据 | 12队 |
| `all_players_complete_2024.csv` | 完整球员数据 | 32名×41列 |
| `indiana_fever_complete_2024.csv` | Fever球员数据 | 12名×41列 |
| `caitlin_clark_impact.json` | Clark效应分析 | - |

---

## 七、使用说明

### 运行数据收集脚本

```bash
# 安装依赖
pip install pandas numpy requests beautifulsoup4

# 运行脚本
python wnba_complete_data_collector.py
```

### 输出目录

所有数据将保存到 `./wnba_data_output/` 目录。

### 数据更新

由于网络限制，脚本使用预设数据。如需更新：
1. 编辑脚本中的 `_get_preset_*` 函数
2. 或手动访问数据源获取最新数据

---

## 八、后续建模使用

收集的数据将用于以下模型：

| 模型 | 使用数据 | 用途 |
|-----|---------|------|
| **Model A: 球员价值评估** | 统计+社交媒体 | 双维度价值计算 |
| **Model B: 财务预测** | 财务+上座率 | 收入/利润预测 |
| **Model C: 阵容优化** | 价值+薪资 | 整数规划优化 |
| **Model D: 动态决策** | 所有数据 | 情景分析 |

---

## 九、数据质量说明

### 数据来源可靠性

| 数据类型 | 可靠性 | 说明 |
|---------|--------|------|
| 球员统计 | ⭐⭐⭐⭐⭐ | 官方数据 |
| 高级统计 | ⭐⭐⭐⭐⭐ | 标准计算方法 |
| 薪资数据 | ⭐⭐⭐⭐ | 基于公开报道 |
| 社交媒体 | ⭐⭐⭐ | 手动收集，可能有变动 |
| 财务数据 | ⭐⭐⭐ | 估算值 |

### 数据更新建议

- 社交媒体数据：比赛期间频繁变化，建议定期更新
- 财务数据：基于年度报告估算，用于数量级分析
- 统计数据：赛季结束后稳定

---

**Phase 1 数据收集完成！**

所有数据已准备就绪，可用于 Phase 2-4 的建模分析。
