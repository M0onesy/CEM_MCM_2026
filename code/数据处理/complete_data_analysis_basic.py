"""
ICM Problem D: Indiana Fever 决策支持系统
完整数据处理与分析代码

数据来源:
- final_data.xlsx: 比赛数据、球员统计、上座率数据
- 补充数据.docx: 薪资帽、球队估值、CBA规则
"""

import pandas as pd
import numpy as np
from docx import Document
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# 第一部分：数据加载与预处理
# =============================================================================

class DataLoader:
    """数据加载器"""
    
    def __init__(self, excel_path, docx_path):
        self.excel_path = excel_path
        self.docx_path = docx_path
        self.data = {}
        
    def load_excel_data(self):
        """加载Excel数据"""
        xlsx = pd.ExcelFile(self.excel_path)
        
        # Sheet1: BPM历史数据 (2000-2022)
        self.data['bpm_history'] = pd.read_excel(xlsx, sheet_name='Sheet1')
        
        # Sheet2: 上座率历史数据 (2008-2024)
        self.data['attendance_history'] = pd.read_excel(xlsx, sheet_name='Sheet2')
        
        # Sheet3: 比赛详情数据 (2003-2025)
        self.data['game_details'] = pd.read_excel(xlsx, sheet_name='Sheet3')
        
        # Sheet4: 2024赛季汇总统计
        self.data['season_2024'] = pd.read_excel(xlsx, sheet_name='Sheet4')
        
        print("✓ Excel数据加载完成")
        print(f"  - BPM历史: {len(self.data['bpm_history'])} 条记录")
        print(f"  - 上座率历史: {len(self.data['attendance_history'])} 条记录")
        print(f"  - 比赛详情: {len(self.data['game_details'])} 条记录")
        print(f"  - 2024赛季: {len(self.data['season_2024'])} 名球员")
        
        return self.data
    
    def load_supplementary_data(self):
        """加载补充数据（从docx解析或直接定义）"""
        
        # 由于docx格式复杂，直接定义关键数据
        self.data['cba_rules'] = {
            'salary_cap_2024': 1463200,
            'salary_cap_2025': 1507100,
            'salary_floor_2025': 1261440,
            'max_salary_2025': 214466,
            'supermax_2025': 249244,
            'rookie_min_2025': 66079,
            'veteran_min_2025': 78831,
            'league_avg_salary': 102249,
            'roster_min': 11,
            'roster_max': 12,
            'cap_growth_rate': 0.03
        }
        
        # 球员薪资数据 (Spotrac + CBA估算)
        self.data['player_salaries'] = {
            'Kelsey Mitchell': {'salary': 249244, 'type': 'Supermax'},
            'Natasha Howard': {'salary': 214466, 'type': 'Max'},
            'Aliyah Boston': {'salary': 78831, 'type': 'Rookie'},
            'Caitlin Clark': {'salary': 78066, 'type': 'Rookie'},
            'NaLyssa Smith': {'salary': 78831, 'type': 'Rookie'},
            'Lexie Hull': {'salary': 75643, 'type': 'Rookie'},
            'Katie Lou Samuelson': {'salary': 102249, 'type': 'Veteran'},
            'Temi Fagbenle': {'salary': 102249, 'type': 'Veteran'},
            'Erica Wheeler': {'salary': 78831, 'type': 'Veteran Min'},
            'Kristy Wallace': {'salary': 78831, 'type': 'Veteran Min'},
            'Damiris Dantas': {'salary': 102249, 'type': 'Veteran'},
            'Grace Berger': {'salary': 72455, 'type': 'Rookie'}
        }
        
        # 球队估值数据 (Sportico)
        self.data['team_valuations'] = {
            'indiana_fever': {
                '2024': {'valuation': 90_000_000, 'revenue': 9_100_000},
                '2025': {'valuation': 335_000_000, 'revenue': 34_000_000}
            },
            'league_avg': {
                '2024': {'valuation': 96_000_000},
                '2025': {'valuation': 269_000_000}
            }
        }
        
        # 扩张计划
        self.data['expansion_plans'] = [
            {'city': 'Golden State', 'year': 2025, 'fee': 50_000_000, 'distance_from_indy': 2180},
            {'city': 'Toronto', 'year': 2026, 'fee': 50_000_000, 'distance_from_indy': 592},
            {'city': 'Portland', 'year': 2026, 'fee': 75_000_000, 'distance_from_indy': 2175},
            {'city': 'Cleveland', 'year': 2028, 'fee': 250_000_000, 'distance_from_indy': 264},
            {'city': 'Detroit', 'year': 2029, 'fee': 250_000_000, 'distance_from_indy': 290},
            {'city': 'Philadelphia', 'year': 2030, 'fee': 250_000_000, 'distance_from_indy': 647}
        ]
        
        print("✓ 补充数据加载完成")
        return self.data


# =============================================================================
# 第二部分：数据清洗与特征工程
# =============================================================================

class DataProcessor:
    """数据处理器"""
    
    def __init__(self, data):
        self.data = data
        self.processed = {}
        
    def process_player_stats_2024(self):
        """处理2024赛季球员统计数据"""
        
        # 从Sheet3提取Indiana Fever 2024赛季数据
        df = self.data['game_details']
        
        # 筛选Indiana Fever 2024赛季常规赛数据
        fever_2024 = df[
            (df['team_abbr'] == 'IND') & 
            (df['season'] == 2024) & 
            (df['season_type'] == 2)  # 常规赛
        ].copy()
        
        # 按球员聚合统计
        player_stats = fever_2024.groupby('player').agg({
            'game_id': 'nunique',  # 比赛场次
            'starter': 'sum',       # 首发次数
            'minutes': 'sum',       # 总分钟数
            'points': 'sum',        # 总得分
            'rebounds': 'sum',      # 总篮板
            'assists': 'sum',       # 总助攻
            'steals': 'sum',        # 总抢断
            'blocks': 'sum',        # 总盖帽
            'turnovers': 'sum',     # 总失误
            'plus_minus': 'sum'     # 总正负值
        }).reset_index()
        
        player_stats.columns = ['Player', 'G', 'GS', 'MIN', 'PTS', 'REB', 'AST', 
                                'STL', 'BLK', 'TOV', 'PM']
        
        # 计算场均数据
        player_stats['MPG'] = player_stats['MIN'] / player_stats['G']
        player_stats['PPG'] = player_stats['PTS'] / player_stats['G']
        player_stats['RPG'] = player_stats['REB'] / player_stats['G']
        player_stats['APG'] = player_stats['AST'] / player_stats['G']
        player_stats['SPG'] = player_stats['STL'] / player_stats['G']
        player_stats['BPG'] = player_stats['BLK'] / player_stats['G']
        player_stats['TOPG'] = player_stats['TOV'] / player_stats['G']
        
        # 筛选主要球员（至少出场20场）
        player_stats = player_stats[player_stats['G'] >= 20].copy()
        
        self.processed['player_stats_2024'] = player_stats
        print(f"✓ 2024赛季球员统计处理完成: {len(player_stats)} 名球员")
        
        return player_stats
    
    def process_attendance_data(self):
        """处理上座率数据"""
        
        df = self.data['game_details']
        
        # 筛选Indiana Fever主场比赛
        home_games = df[
            (df['team_abbr'] == 'IND') & 
            (df['home_away'] == 'home') &
            (df['season'] == 2024) &
            (df['season_type'] == 2)
        ].copy()
        
        # 去重（每场比赛只保留一条记录）
        home_games_unique = home_games.drop_duplicates(subset=['game_id'])
        
        attendance_summary = {
            'total_home_games': len(home_games_unique),
            'avg_attendance': home_games_unique['attendance'].mean(),
            'max_attendance': home_games_unique['attendance'].max(),
            'min_attendance': home_games_unique['attendance'].min(),
            'total_ticket_revenue_proxy': home_games_unique['ticket_revenue_proxy'].sum(),
            'total_gameday_revenue_proxy': home_games_unique['gameday_revenue_proxy'].sum()
        }
        
        self.processed['attendance_2024'] = attendance_summary
        self.processed['home_games_2024'] = home_games_unique
        
        print(f"✓ 上座率数据处理完成: {attendance_summary['total_home_games']} 场主场比赛")
        print(f"  - 场均上座: {attendance_summary['avg_attendance']:.0f} 人")
        
        return attendance_summary
    
    def process_team_performance(self):
        """处理球队战绩数据"""
        
        df = self.data['game_details']
        
        # Indiana Fever 2024赛季所有比赛结果
        fever_games = df[
            (df['team_abbr'] == 'IND') & 
            (df['season'] == 2024) &
            (df['season_type'] == 2)
        ].drop_duplicates(subset=['game_id'])
        
        wins = fever_games['team_winner'].sum()
        total_games = len(fever_games)
        
        team_performance = {
            'wins': int(wins),
            'losses': total_games - int(wins),
            'total_games': total_games,
            'win_pct': wins / total_games if total_games > 0 else 0,
            'avg_points_scored': fever_games['team_score'].mean(),
            'avg_points_allowed': fever_games['opponent_team_score'].mean()
        }
        
        self.processed['team_performance_2024'] = team_performance
        
        print(f"✓ 球队战绩处理完成: {team_performance['wins']}-{team_performance['losses']}")
        print(f"  - 胜率: {team_performance['win_pct']:.1%}")
        
        return team_performance


# =============================================================================
# 第三部分：模型计算
# =============================================================================

class ModelCalculator:
    """模型计算器"""
    
    def __init__(self, processed_data, raw_data):
        self.processed = processed_data
        self.raw = raw_data
        self.results = {}
        
    # =========================================================================
    # Model A: 球员价值评估模型
    # =========================================================================
    
    def calculate_player_value(self):
        """
        计算球员总价值
        Total_Value = α × Performance_Value + β × Commercial_Value
        其中 α = 0.4, β = 0.6
        """
        
        player_stats = self.processed['player_stats_2024'].copy()
        salaries = self.raw['player_salaries']
        
        # 参数设置
        ALPHA = 0.4  # 表现价值权重
        BETA = 0.6   # 商业价值权重
        WAR_MONETARY_VALUE = 500000  # 每WAR价值 $0.5M
        REPLACEMENT_LEVEL = -2.0  # 替代球员水平
        SEASON_MINUTES_BENCHMARK = 2400  # 赛季分钟基准
        
        # 收入增量用于商业价值归因
        revenue_2024 = self.raw['team_valuations']['indiana_fever']['2025']['revenue']
        revenue_2023 = self.raw['team_valuations']['indiana_fever']['2024']['revenue']
        revenue_increase = revenue_2024 - revenue_2023  # $24.9M增量
        
        results = []
        
        for _, row in player_stats.iterrows():
            player_name = row['Player']
            
            # Step 1: 计算Per-36数据
            mpg = row['MPG']
            if mpg > 0:
                ppg_per36 = row['PPG'] / mpg * 36
                rpg_per36 = row['RPG'] / mpg * 36
                apg_per36 = row['APG'] / mpg * 36
                topg_per36 = row['TOPG'] / mpg * 36
            else:
                ppg_per36 = rpg_per36 = apg_per36 = topg_per36 = 0
            
            # Step 2: 估算BPM
            # BPM_est = 0.86×PPG_per36 + 0.68×RPG_per36 + 0.89×APG_per36 - 0.79×TOPG_per36 - 2.0
            est_bpm = (0.86 * ppg_per36 + 0.68 * rpg_per36 + 
                       0.89 * apg_per36 - 0.79 * topg_per36 - 2.0)
            
            # Step 3: 计算WAR
            # WAR = (BPM - Replacement_Level) × MIN / Season_Minutes_Benchmark
            total_minutes = row['MIN']
            est_war = (est_bpm - REPLACEMENT_LEVEL) * total_minutes / SEASON_MINUTES_BENCHMARK
            
            # Step 4: 计算表现价值
            performance_value = est_war * WAR_MONETARY_VALUE
            
            # Step 5: 计算商业价值（收入归因）
            # 根据球员知名度和市场影响力分配
            if 'Clark' in player_name:
                commercial_attribution = 0.70  # Clark获得70%的收入增量归因
            elif 'Boston' in player_name:
                commercial_attribution = 0.07
            elif 'Mitchell' in player_name:
                commercial_attribution = 0.03
            else:
                commercial_attribution = 0.02  # 其他球员平分剩余
            
            commercial_value = revenue_increase * commercial_attribution
            
            # Step 6: 计算总价值
            total_value = ALPHA * performance_value + BETA * commercial_value
            
            # 获取薪资数据
            salary_info = salaries.get(player_name, {'salary': 78831, 'type': 'Unknown'})
            salary = salary_info['salary']
            
            # 计算价值效率
            value_salary_ratio = total_value / salary if salary > 0 else 0
            
            results.append({
                'Player': player_name,
                'G': row['G'],
                'MIN': total_minutes,
                'MPG': mpg,
                'PPG': row['PPG'],
                'RPG': row['RPG'],
                'APG': row['APG'],
                'TOPG': row['TOPG'],
                'PPG_per36': ppg_per36,
                'RPG_per36': rpg_per36,
                'APG_per36': apg_per36,
                'TOPG_per36': topg_per36,
                'Est_BPM': est_bpm,
                'Est_WAR': est_war,
                'Salary': salary,
                'Salary_Type': salary_info['type'],
                'Performance_Value': performance_value,
                'Commercial_Value': commercial_value,
                'Total_Value': total_value,
                'Value_Salary_Ratio': value_salary_ratio
            })
        
        df_results = pd.DataFrame(results)
        df_results = df_results.sort_values('Total_Value', ascending=False)
        
        self.results['player_values'] = df_results
        
        print("\n" + "="*80)
        print("MODEL A: 球员价值评估结果")
        print("="*80)
        print(f"\n公式: Total_Value = {ALPHA} × Performance_Value + {BETA} × Commercial_Value")
        print(f"WAR货币价值: ${WAR_MONETARY_VALUE:,}/WAR")
        print(f"收入增量用于归因: ${revenue_increase:,.0f}")
        
        # 打印结果摘要
        print("\n球员价值排名 (前10):")
        print("-"*100)
        for i, row in df_results.head(10).iterrows():
            print(f"{row['Player']:<20} | WAR: {row['Est_WAR']:>6.2f} | "
                  f"薪资: ${row['Salary']:>9,} | "
                  f"表现价值: ${row['Performance_Value']:>10,.0f} | "
                  f"商业价值: ${row['Commercial_Value']:>12,.0f} | "
                  f"总价值: ${row['Total_Value']:>12,.0f} | "
                  f"效率: {row['Value_Salary_Ratio']:>6.1f}x")
        
        return df_results
    
    # =========================================================================
    # Model B: 财务预测模型
    # =========================================================================
    
    def calculate_financial_forecast(self):
        """
        财务预测模型
        Profit = Total_Revenue - Total_Costs
        """
        
        # 使用Sportico实际收入数据
        actual_revenue = self.raw['team_valuations']['indiana_fever']['2025']['revenue']
        
        # 收入结构分解
        revenue_structure = {
            'Media Rights': actual_revenue * 0.275,
            'Ticket Revenue': actual_revenue * 0.325,
            'Sponsorship': actual_revenue * 0.275,
            'Merchandise': actual_revenue * 0.125
        }
        
        # 成本结构（基于行业标准，成本占收入70-80%）
        cost_ratio = 0.75
        total_costs = actual_revenue * cost_ratio
        
        # 详细成本分解
        total_salaries = sum(s['salary'] for s in self.raw['player_salaries'].values())
        cost_structure = {
            'Player Salaries': total_salaries,
            'Operations': actual_revenue * 0.25,
            'Arena Costs': actual_revenue * 0.15,
            'Marketing': actual_revenue * 0.10,
            'Travel': actual_revenue * 0.044,
            'Other': total_costs - (total_salaries + actual_revenue * (0.25 + 0.15 + 0.10 + 0.044))
        }
        
        # 利润计算
        profit = actual_revenue - total_costs
        profit_margin = profit / actual_revenue
        
        # 情景分析
        scenarios = [
            {'name': 'Best Case (Finals)', 'prob': 0.05, 'rev_mult': 1.30, 'cost_mult': 1.10},
            {'name': 'Optimistic (Top 4)', 'prob': 0.20, 'rev_mult': 1.15, 'cost_mult': 1.05},
            {'name': 'Base Case', 'prob': 0.55, 'rev_mult': 1.00, 'cost_mult': 1.00},
            {'name': 'Pessimistic', 'prob': 0.12, 'rev_mult': 0.85, 'cost_mult': 0.95},
            {'name': 'Catastrophic (Clark Injury)', 'prob': 0.08, 'rev_mult': 0.60, 'cost_mult': 0.90}
        ]
        
        scenario_results = []
        expected_profit = 0
        
        for s in scenarios:
            s_revenue = actual_revenue * s['rev_mult']
            s_cost = total_costs * s['cost_mult']
            s_profit = s_revenue - s_cost
            weighted_contrib = s['prob'] * s_profit
            expected_profit += weighted_contrib
            
            scenario_results.append({
                'Scenario': s['name'],
                'Probability': s['prob'],
                'Revenue': s_revenue,
                'Costs': s_cost,
                'Profit': s_profit,
                'Weighted_Contribution': weighted_contrib
            })
        
        financial_results = {
            'actual_revenue': actual_revenue,
            'revenue_structure': revenue_structure,
            'total_costs': total_costs,
            'cost_structure': cost_structure,
            'profit': profit,
            'profit_margin': profit_margin,
            'scenarios': pd.DataFrame(scenario_results),
            'expected_profit': expected_profit
        }
        
        self.results['financial'] = financial_results
        
        print("\n" + "="*80)
        print("MODEL B: 财务预测结果")
        print("="*80)
        print(f"\n总收入 (Sportico 2025): ${actual_revenue:,.0f}")
        print("\n收入结构:")
        for k, v in revenue_structure.items():
            print(f"  {k}: ${v:,.0f} ({v/actual_revenue:.1%})")
        
        print(f"\n总成本: ${total_costs:,.0f} (收入的{cost_ratio:.0%})")
        print("\n成本结构:")
        for k, v in cost_structure.items():
            print(f"  {k}: ${v:,.0f}")
        
        print(f"\n利润: ${profit:,.0f}")
        print(f"利润率: {profit_margin:.1%}")
        
        print("\n情景分析:")
        print("-"*80)
        for _, row in pd.DataFrame(scenario_results).iterrows():
            print(f"{row['Scenario']:<30} | 概率: {row['Probability']:.0%} | "
                  f"利润: ${row['Profit']:>12,.0f}")
        print(f"\n期望利润 E[Profit]: ${expected_profit:,.0f}")
        
        return financial_results
    
    # =========================================================================
    # Model E: 资本结构优化 (WACC最小化)
    # =========================================================================
    
    def calculate_capital_structure(self):
        """
        资本结构优化模型
        WACC = (E/V) × r_e + (D/V) × r_d × (1-T)
        """
        
        # 参数设置
        valuation = self.raw['team_valuations']['indiana_fever']['2025']['valuation']
        risk_free_rate = 0.045
        market_risk_premium = 0.055
        unlevered_beta = 1.0
        tax_rate = 0.21
        
        # 不同杠杆水平下的WACC计算
        debt_ratios = [0.0, 0.1, 0.2, 0.3, 0.4]
        
        results = []
        for d_v in debt_ratios:
            e_v = 1 - d_v
            debt = valuation * d_v
            equity = valuation * e_v
            
            # 杠杆Beta
            levered_beta = unlevered_beta * (1 + (1 - tax_rate) * (d_v / e_v)) if e_v > 0 else unlevered_beta
            
            # 股权成本 (CAPM)
            cost_of_equity = risk_free_rate + levered_beta * market_risk_premium
            
            # 债务成本 (随杠杆增加而上升)
            base_debt_cost = 0.06
            debt_spread = d_v * 0.08  # 杠杆溢价
            cost_of_debt = base_debt_cost + debt_spread
            
            # WACC
            wacc = e_v * cost_of_equity + d_v * cost_of_debt * (1 - tax_rate)
            
            results.append({
                'D/V': d_v,
                'Debt': debt,
                'Equity': equity,
                'Levered_Beta': levered_beta,
                'Cost_of_Equity': cost_of_equity,
                'Cost_of_Debt': cost_of_debt,
                'WACC': wacc
            })
        
        df_results = pd.DataFrame(results)
        
        # 找到最优资本结构
        optimal_idx = df_results['WACC'].idxmin()
        optimal = df_results.loc[optimal_idx]
        
        capital_structure_results = {
            'valuation': valuation,
            'parameters': {
                'risk_free_rate': risk_free_rate,
                'market_risk_premium': market_risk_premium,
                'unlevered_beta': unlevered_beta,
                'tax_rate': tax_rate
            },
            'analysis': df_results,
            'optimal': {
                'debt_ratio': optimal['D/V'],
                'wacc': optimal['WACC'],
                'debt': optimal['Debt'],
                'equity': optimal['Equity']
            }
        }
        
        self.results['capital_structure'] = capital_structure_results
        
        print("\n" + "="*80)
        print("MODEL E: 资本结构优化结果")
        print("="*80)
        print(f"\n球队估值: ${valuation:,.0f}")
        print(f"无风险利率: {risk_free_rate:.1%}")
        print(f"市场风险溢价: {market_risk_premium:.1%}")
        print(f"无杠杆Beta: {unlevered_beta}")
        
        print("\n不同杠杆水平下的WACC:")
        print("-"*80)
        for _, row in df_results.iterrows():
            print(f"D/V: {row['D/V']:.0%} | "
                  f"Debt: ${row['Debt']:>12,.0f} | "
                  f"Equity: ${row['Equity']:>12,.0f} | "
                  f"β_L: {row['Levered_Beta']:.2f} | "
                  f"r_e: {row['Cost_of_Equity']:.2%} | "
                  f"r_d: {row['Cost_of_Debt']:.2%} | "
                  f"WACC: {row['WACC']:.2%}")
        
        print(f"\n最优资本结构: D/V = {optimal['D/V']:.0%}, WACC = {optimal['WACC']:.2%}")
        
        return capital_structure_results
    
    # =========================================================================
    # Model F: 球员潜力预测
    # =========================================================================
    
    def calculate_player_projections(self):
        """
        球员潜力预测模型
        Performance(age) = Peak_Performance × f(age, position)
        """
        
        # 年龄因子表（后卫）
        guard_age_factors = {
            22: 0.78, 23: 0.80, 24: 0.88, 25: 0.94,
            26: 0.98, 27: 1.00, 28: 1.02, 29: 1.03,
            30: 1.03, 31: 1.00, 32: 0.97, 33: 0.90, 34: 0.80
        }
        
        # 核心球员预测
        players_to_project = [
            {'name': 'Caitlin Clark', 'current_age': 23, 'current_war': 14.83, 'position': 'G'},
            {'name': 'Aliyah Boston', 'current_age': 23, 'current_war': 12.35, 'position': 'F'},
            {'name': 'Kelsey Mitchell', 'current_age': 29, 'current_war': 11.64, 'position': 'G'}
        ]
        
        projections = []
        
        for player in players_to_project:
            current_factor = guard_age_factors.get(player['current_age'], 0.90)
            peak_war = player['current_war'] / current_factor
            
            for year_offset in range(6):  # 2025-2030
                future_age = player['current_age'] + year_offset
                future_factor = guard_age_factors.get(future_age, 0.80)
                projected_war = peak_war * future_factor
                
                # 90%置信区间
                ci_low = projected_war * 0.75
                ci_high = projected_war * 1.15
                
                projections.append({
                    'Player': player['name'],
                    'Year': 2025 + year_offset,
                    'Age': future_age,
                    'Age_Factor': future_factor,
                    'Projected_WAR': projected_war,
                    'CI_Low': ci_low,
                    'CI_High': ci_high,
                    'Peak_WAR': peak_war
                })
        
        df_projections = pd.DataFrame(projections)
        
        self.results['player_projections'] = df_projections
        
        print("\n" + "="*80)
        print("MODEL F: 球员潜力预测结果")
        print("="*80)
        
        for player in players_to_project:
            print(f"\n{player['name']} (现年{player['current_age']}岁):")
            print(f"  当前WAR: {player['current_war']:.2f}")
            print(f"  估计巅峰WAR: {player['current_war'] / guard_age_factors.get(player['current_age'], 0.90):.2f}")
            print("\n  5年预测:")
            player_proj = df_projections[df_projections['Player'] == player['name']]
            for _, row in player_proj.iterrows():
                print(f"    {row['Year']} (年龄{row['Age']}): WAR {row['Projected_WAR']:.2f} "
                      f"[90% CI: {row['CI_Low']:.2f} - {row['CI_High']:.2f}]")
        
        return df_projections
    
    # =========================================================================
    # Model G: 联盟扩张影响分析
    # =========================================================================
    
    def calculate_expansion_impact(self):
        """
        扩张影响分析模型
        Market_Overlap = f(distance, population, demographics)
        Revenue_Impact = Market_Overlap × Base_Revenue × Impact_Factor
        """
        
        expansion_plans = self.raw['expansion_plans']
        current_revenue = self.raw['team_valuations']['indiana_fever']['2025']['revenue']
        
        # 距离-影响函数参数
        def calculate_market_overlap(distance):
            """基于距离计算市场重叠度"""
            if distance < 300:
                return 0.50 - (distance / 300) * 0.10  # 300英里内高重叠
            elif distance < 600:
                return 0.30 - ((distance - 300) / 300) * 0.20
            elif distance < 1000:
                return 0.10 - ((distance - 600) / 400) * 0.08
            else:
                return 0.02  # 远距离最小影响
        
        results = []
        
        for plan in expansion_plans:
            distance = plan['distance_from_indy']
            market_overlap = calculate_market_overlap(distance)
            
            # 收入影响估计
            revenue_impact_pct = market_overlap * 0.10  # 最大影响为市场重叠的10%
            revenue_impact = current_revenue * revenue_impact_pct
            
            # 风险等级
            if distance < 300:
                risk_level = 'HIGH'
            elif distance < 600:
                risk_level = 'MODERATE'
            else:
                risk_level = 'LOW'
            
            results.append({
                'City': plan['city'],
                'Year': plan['year'],
                'Expansion_Fee': plan['fee'],
                'Distance_Miles': distance,
                'Market_Overlap': market_overlap,
                'Revenue_Impact_Pct': revenue_impact_pct,
                'Revenue_Impact': revenue_impact,
                'Risk_Level': risk_level
            })
        
        df_results = pd.DataFrame(results)
        df_results = df_results.sort_values('Revenue_Impact_Pct', ascending=False)
        
        self.results['expansion_impact'] = df_results
        
        print("\n" + "="*80)
        print("MODEL G: 联盟扩张影响分析结果")
        print("="*80)
        print(f"\nIndiana Fever 当前收入: ${current_revenue:,.0f}")
        
        print("\n扩张城市影响排名:")
        print("-"*100)
        for _, row in df_results.iterrows():
            print(f"{row['City']:<15} | {row['Year']} | "
                  f"距离: {row['Distance_Miles']:>5}mi | "
                  f"市场重叠: {row['Market_Overlap']:.1%} | "
                  f"收入影响: {row['Revenue_Impact_Pct']:.1%} (${row['Revenue_Impact']:>10,.0f}) | "
                  f"风险: {row['Risk_Level']}")
        
        return df_results


# =============================================================================
# 第四部分：报告生成
# =============================================================================

class ReportGenerator:
    """报告生成器"""
    
    def __init__(self, results, processed_data, raw_data):
        self.results = results
        self.processed = processed_data
        self.raw = raw_data
        
    def generate_summary_statistics(self):
        """生成汇总统计"""
        
        summary = {
            'data_overview': {
                'total_games_analyzed': self.processed.get('team_performance_2024', {}).get('total_games', 0),
                'players_evaluated': len(self.results.get('player_values', [])),
                'seasons_covered': '2024'
            },
            'key_findings': {
                'top_player': self.results['player_values'].iloc[0]['Player'] if 'player_values' in self.results else 'N/A',
                'top_player_value': self.results['player_values'].iloc[0]['Total_Value'] if 'player_values' in self.results else 0,
                'expected_profit': self.results.get('financial', {}).get('expected_profit', 0),
                'optimal_wacc': self.results.get('capital_structure', {}).get('optimal', {}).get('wacc', 0),
                'highest_risk_expansion': self.results['expansion_impact'].iloc[0]['City'] if 'expansion_impact' in self.results else 'N/A'
            }
        }
        
        return summary
    
    def export_to_excel(self, output_path):
        """导出结果到Excel"""
        
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # 球员价值
            if 'player_values' in self.results:
                self.results['player_values'].to_excel(
                    writer, sheet_name='Player_Values', index=False
                )
            
            # 财务情景
            if 'financial' in self.results:
                self.results['financial']['scenarios'].to_excel(
                    writer, sheet_name='Financial_Scenarios', index=False
                )
            
            # 资本结构
            if 'capital_structure' in self.results:
                self.results['capital_structure']['analysis'].to_excel(
                    writer, sheet_name='Capital_Structure', index=False
                )
            
            # 球员预测
            if 'player_projections' in self.results:
                self.results['player_projections'].to_excel(
                    writer, sheet_name='Player_Projections', index=False
                )
            
            # 扩张影响
            if 'expansion_impact' in self.results:
                self.results['expansion_impact'].to_excel(
                    writer, sheet_name='Expansion_Impact', index=False
                )
        
        print(f"\n✓ 结果已导出到: {output_path}")
    
    def generate_markdown_report(self, output_path):
        """生成Markdown格式报告"""
        
        report = []
        
        # 标题
        report.append("# ICM Problem D 数据分析与模型计算报告")
        report.append("\n## Indiana Fever 2025赛季决策支持系统")
        report.append("\n---\n")
        
        # 数据概览
        report.append("## 1. 数据概览\n")
        team_perf = self.processed.get('team_performance_2024', {})
        attendance = self.processed.get('attendance_2024', {})
        
        report.append(f"- 分析赛季: 2024")
        report.append(f"- 球队战绩: {team_perf.get('wins', 0)}-{team_perf.get('losses', 0)} ({team_perf.get('win_pct', 0):.1%})")
        report.append(f"- 主场比赛: {attendance.get('total_home_games', 0)} 场")
        report.append(f"- 场均上座: {attendance.get('avg_attendance', 0):,.0f} 人\n")
        
        # Model A 结果
        report.append("## 2. 球员价值评估 (Model A)\n")
        report.append("| 球员 | WAR | 薪资 | 表现价值 | 商业价值 | 总价值 | 效率 |")
        report.append("|------|-----|------|---------|---------|--------|------|")
        
        if 'player_values' in self.results:
            for _, row in self.results['player_values'].head(10).iterrows():
                report.append(
                    f"| {row['Player']} | {row['Est_WAR']:.2f} | "
                    f"${row['Salary']:,} | ${row['Performance_Value']:,.0f} | "
                    f"${row['Commercial_Value']:,.0f} | ${row['Total_Value']:,.0f} | "
                    f"{row['Value_Salary_Ratio']:.1f}x |"
                )
        report.append("")
        
        # Model B 结果
        report.append("\n## 3. 财务预测 (Model B)\n")
        financial = self.results.get('financial', {})
        report.append(f"- 总收入: ${financial.get('actual_revenue', 0):,.0f}")
        report.append(f"- 总成本: ${financial.get('total_costs', 0):,.0f}")
        report.append(f"- 利润: ${financial.get('profit', 0):,.0f}")
        report.append(f"- 利润率: {financial.get('profit_margin', 0):.1%}")
        report.append(f"- 期望利润: ${financial.get('expected_profit', 0):,.0f}\n")
        
        # Model E 结果
        report.append("\n## 4. 资本结构优化 (Model E)\n")
        capital = self.results.get('capital_structure', {}).get('optimal', {})
        report.append(f"- 最优负债比率: {capital.get('debt_ratio', 0):.0%}")
        report.append(f"- 最优WACC: {capital.get('wacc', 0):.2%}\n")
        
        # Model G 结果
        report.append("\n## 5. 扩张影响分析 (Model G)\n")
        report.append("| 城市 | 年份 | 距离 | 收入影响 | 风险等级 |")
        report.append("|------|------|------|---------|---------|")
        
        if 'expansion_impact' in self.results:
            for _, row in self.results['expansion_impact'].iterrows():
                report.append(
                    f"| {row['City']} | {row['Year']} | {row['Distance_Miles']}mi | "
                    f"{row['Revenue_Impact_Pct']:.1%} | {row['Risk_Level']} |"
                )
        
        # 写入文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report))
        
        print(f"✓ Markdown报告已生成: {output_path}")


# =============================================================================
# 主程序
# =============================================================================

def main():
    """主函数"""
    
    print("="*80)
    print("ICM Problem D: Indiana Fever 决策支持系统")
    print("完整数据处理与分析")
    print("="*80)
    
    # 1. 数据加载
    print("\n[1/5] 加载数据...")
    loader = DataLoader(
        excel_path='/mnt/user-data/uploads/final_data.xlsx',
        docx_path='/mnt/user-data/uploads/补充数据.docx'
    )
    raw_data = loader.load_excel_data()
    loader.load_supplementary_data()
    raw_data = loader.data
    
    # 2. 数据处理
    print("\n[2/5] 数据预处理...")
    processor = DataProcessor(raw_data)
    processor.process_player_stats_2024()
    processor.process_attendance_data()
    processor.process_team_performance()
    processed_data = processor.processed
    
    # 3. 模型计算
    print("\n[3/5] 模型计算...")
    calculator = ModelCalculator(processed_data, raw_data)
    calculator.calculate_player_value()
    calculator.calculate_financial_forecast()
    calculator.calculate_capital_structure()
    calculator.calculate_player_projections()
    calculator.calculate_expansion_impact()
    results = calculator.results
    
    # 4. 报告生成
    print("\n[4/5] 生成报告...")
    reporter = ReportGenerator(results, processed_data, raw_data)
    summary = reporter.generate_summary_statistics()
    
    # 5. 导出结果
    print("\n[5/5] 导出结果...")
    reporter.export_to_excel('/mnt/user-data/outputs/analysis_results.xlsx')
    reporter.generate_markdown_report('/mnt/user-data/outputs/analysis_report.md')
    
    # 打印最终摘要
    print("\n" + "="*80)
    print("分析完成！关键发现:")
    print("="*80)
    print(f"\n1. 最具价值球员: {summary['key_findings']['top_player']}")
    print(f"   总价值: ${summary['key_findings']['top_player_value']:,.0f}")
    print(f"\n2. 期望利润: ${summary['key_findings']['expected_profit']:,.0f}")
    print(f"\n3. 最优WACC: {summary['key_findings']['optimal_wacc']:.2%}")
    print(f"\n4. 最高风险扩张城市: {summary['key_findings']['highest_risk_expansion']}")
    
    return results, processed_data, raw_data


if __name__ == "__main__":
    results, processed_data, raw_data = main()
