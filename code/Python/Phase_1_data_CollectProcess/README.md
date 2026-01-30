# WNBA 数据收集与分析系统 (2019-2024)

**MCM/ICM 2026 - Problem D: Professional Sports Team Management**  
**案例研究: Indiana Fever**

---

## 📊 数据集概览

| 指标 | 数值 |
|------|------|
| **时间范围** | 2019-2024 (6个赛季) |
| **总球员记录** | 864条 |
| **唯一球员** | 629人 |
| **球队数** | 12支 |
| **数据字段** | 36个 |

---

## 📁 文件清单

### 数据文件

| 文件名 | 说明 | 格式 |
|--------|------|------|
| `wnba_2019_2024_complete.xlsx` | 完整数据集（多工作表） | Excel |
| `wnba_players_all_seasons.csv` | 球员统计数据 | CSV |
| `wnba_team_financials.csv` | 球队财务数据 | CSV |

### 代码文件

| 文件名 | 说明 |
|--------|------|
| `main.py` | 主程序入口 |
| `wnba_data_scraper.py` | 网络爬虫模块（Basketball-Reference, Spotrac） |
| `wnba_data_generator.py` | 模拟数据生成器（无网络时使用） |

---

## 📋 Excel工作表说明

`wnba_2019_2024_complete.xlsx` 包含以下工作表：

| 工作表 | 内容 |
|--------|------|
| `All_Players` | 全部864条球员记录 |
| `Indiana_Fever` | Fever队球员专项数据 |
| `Star_Players` | 明星球员数据 |
| `Team_Financials` | 12支球队6年财务数据 |
| `Season_Summary` | 各赛季汇总统计 |
| `Top_Scorers` | 得分榜Top 100 |
| `Top_WAR` | WAR值Top 100 |
| `Top_Value` | 综合价值Top 100 |
| `Season_2019` ~ `Season_2024` | 各赛季分表 |

---

## 📊 数据字段详解

### 基础统计字段

| 字段 | 说明 | 类型 |
|------|------|------|
| `player_id` | 球员唯一标识 | string |
| `player` | 球员姓名 | string |
| `season` | 赛季年份 | int |
| `team` | 球队代码 | string |
| `pos` | 位置 (G/G-F/F/F-C/C) | string |
| `age` | 年龄 | int |
| `experience` | NBA经验年数 | int |
| `games` | 出场数 | int |
| `games_started` | 首发数 | int |
| `min_per_game` | 场均时间 | float |
| `pts` | 场均得分 | float |
| `reb` | 场均篮板 | float |
| `ast` | 场均助攻 | float |
| `stl` | 场均抢断 | float |
| `blk` | 场均盖帽 | float |
| `tov` | 场均失误 | float |

### 命中率字段

| 字段 | 说明 |
|------|------|
| `fg_pct` | 投篮命中率 |
| `fg3_pct` | 三分球命中率 |
| `ft_pct` | 罚球命中率 |
| `ts_pct` | 真实命中率 (True Shooting %) |

### 高级统计字段

| 字段 | 说明 | 计算方式 |
|------|------|----------|
| `per` | Player Efficiency Rating | 综合效率值 |
| `usg_pct` | Usage Rate | 球权使用率 |
| `bpm` | Box Plus/Minus | 百回合净效率贡献 |
| `vorp` | Value Over Replacement | 超过替补水平价值 |
| `ws` | Win Shares | 胜场贡献 |
| `ws_48` | Win Shares per 48 min | 每48分钟胜场贡献 |
| `war` | Wins Above Replacement | 超替补胜场值 |

### 薪资与商业字段

| 字段 | 说明 |
|------|------|
| `salary` | 年薪（美元） |
| `instagram_followers` | Instagram粉丝数 |
| `twitter_followers` | Twitter粉丝数 |
| `jersey_rank` | 球衣销量排名 |
| `marketability` | 市场化指数 (1-10) |
| `is_star` | 是否为明星球员 |

### 价值评估字段 (Model A 输出)

| 字段 | 说明 | 公式 |
|------|------|------|
| `performance_value` | 表现价值 ($) | WAR × $300,000 |
| `commercial_value` | 商业价值 ($) | 社交媒体 + 球衣 + 市场化 |
| `total_value` | 综合价值 ($) | 0.4×表现 + 0.6×商业 |

---

## 🏀 关键发现

### Caitlin Clark 效应 (2024)

| 指标 | 数值 | 联盟排名 |
|------|------|---------|
| 场均助攻 | 8.4 | #1 |
| Instagram粉丝 | 520万 | #1 |
| 商业价值 | $4.34M | #1 |
| 球衣销量 | #1 | #1 |

### Indiana Fever 估值增长

| 年份 | 估值 | 同比增长 |
|------|------|---------|
| 2019 | $23.8M | - |
| 2023 | $42.2M | +77% (累计) |
| 2024 | $141.0M | **+234%** |

---

## 🔧 使用方法

### 1. 运行数据生成（无网络）

```bash
python main.py --mode generate --output ./data
```

### 2. 运行网络爬虫（有网络）

```bash
python main.py --mode scrape --output ./data
```

### 3. 指定赛季范围

```bash
python main.py --seasons 2022 2023 2024
```

---

## 📐 核心公式

### WAR (Wins Above Replacement)

$$WAR = \frac{(BPM - BPM_{replacement}) \times MP}{48 \times G_{season}}$$

其中:
- $BPM_{replacement} = -2.0$
- $MP$ = 总出场分钟
- $G_{season}$ = 赛季总场数

### 表现价值

$$V_{performance} = WAR \times VPW$$

其中 $VPW = \$300,000$ (每胜场价值)

### 商业价值

$$V_{commercial} = (Followers_{IG} + Followers_{TW}) \times 0.10 + Jersey\_Value + Market\_Bonus$$

### 综合价值

$$V_{total} = 0.4 \times V_{performance} + 0.6 \times V_{commercial}$$

---

## 📚 数据来源

| 数据类型 | 来源 |
|----------|------|
| 球员统计 | Basketball-Reference |
| 高级数据 | Her Hoop Stats |
| 薪资数据 | Spotrac |
| 社交媒体 | 各平台官方数据 |
| 球队财务 | Forbes, Sportico |

---

## 🔜 下一步

1. **Model A**: 球员价值评估模型
2. **Model B**: 财务预测模型
3. **Model C**: 阵容优化模型
4. **Model D**: 动态决策引擎

---

*MCM/ICM 2026 Team | Generated: 2026-01-30*
