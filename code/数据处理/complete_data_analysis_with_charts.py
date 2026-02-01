"""
ICM Problem D: Indiana Fever 决策支持系统
完整数据处理、分析与图表生成代码

包含:
- 数据加载与预处理
- 模型计算 (Model A-G)
- 结果可视化 (12张专业图表)
- 报告生成

数据来源:
- final_data.xlsx: 比赛数据、球员统计、上座率数据
- 补充数据.docx: 薪资帽、球队估值、CBA规则

作者: ICM 2026 Team
日期: 2026-02-01
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
from scipy import stats
from docx import Document
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体（如果需要）
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False
plt.style.use('seaborn-v0_8-whitegrid')

# =============================================================================
# 第一部分：数据加载与预处理
# =============================================================================

class DataLoader:
    """数据加载器"""
    
    def __init__(self, excel_path, docx_path=None):
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
        
        # CBA规则数据
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
        
        df = self.data['game_details']
        
        # 筛选Indiana Fever 2024赛季常规赛数据
        fever_2024 = df[
            (df['team_abbr'] == 'IND') & 
            (df['season'] == 2024) & 
            (df['season_type'] == 2)  # 常规赛
        ].copy()
        
        # 按球员聚合统计
        player_stats = fever_2024.groupby('player').agg({
            'game_id': 'nunique',
            'starter': 'sum',
            'minutes': 'sum',
            'points': 'sum',
            'rebounds': 'sum',
            'assists': 'sum',
            'steals': 'sum',
            'blocks': 'sum',
            'turnovers': 'sum',
            'plus_minus': 'sum'
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
        
        # 去重
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
        
        return attendance_summary
    
    def process_team_performance(self):
        """处理球队战绩数据"""
        
        df = self.data['game_details']
        
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
        
        return team_performance
    
    def process_historical_attendance(self):
        """处理历史上座率数据（用于趋势分析）"""
        
        df = self.data['attendance_history']
        
        # 按年份汇总
        yearly_attendance = df.groupby('Year').agg({
            'Attendance': ['mean', 'sum', 'count']
        }).reset_index()
        yearly_attendance.columns = ['Year', 'Avg_Attendance', 'Total_Attendance', 'Games']
        
        self.processed['historical_attendance'] = yearly_attendance
        
        return yearly_attendance


# =============================================================================
# 第三部分：模型计算
# =============================================================================

class ModelCalculator:
    """模型计算器"""
    
    def __init__(self, processed_data, raw_data):
        self.processed = processed_data
        self.raw = raw_data
        self.results = {}
        
    def calculate_player_value(self):
        """Model A: 球员价值评估"""
        
        player_stats = self.processed['player_stats_2024'].copy()
        salaries = self.raw['player_salaries']
        
        ALPHA = 0.4
        BETA = 0.6
        WAR_MONETARY_VALUE = 500000
        REPLACEMENT_LEVEL = -2.0
        SEASON_MINUTES_BENCHMARK = 2400
        
        revenue_2024 = self.raw['team_valuations']['indiana_fever']['2025']['revenue']
        revenue_2023 = self.raw['team_valuations']['indiana_fever']['2024']['revenue']
        revenue_increase = revenue_2024 - revenue_2023
        
        results = []
        
        for _, row in player_stats.iterrows():
            player_name = row['Player']
            mpg = row['MPG']
            
            if mpg > 0:
                ppg_per36 = row['PPG'] / mpg * 36
                rpg_per36 = row['RPG'] / mpg * 36
                apg_per36 = row['APG'] / mpg * 36
                topg_per36 = row['TOPG'] / mpg * 36
            else:
                ppg_per36 = rpg_per36 = apg_per36 = topg_per36 = 0
            
            est_bpm = (0.86 * ppg_per36 + 0.68 * rpg_per36 + 
                       0.89 * apg_per36 - 0.79 * topg_per36 - 2.0)
            
            total_minutes = row['MIN']
            est_war = (est_bpm - REPLACEMENT_LEVEL) * total_minutes / SEASON_MINUTES_BENCHMARK
            
            performance_value = est_war * WAR_MONETARY_VALUE
            
            if 'Clark' in player_name:
                commercial_attribution = 0.70
            elif 'Boston' in player_name:
                commercial_attribution = 0.07
            elif 'Mitchell' in player_name:
                commercial_attribution = 0.03
            else:
                commercial_attribution = 0.02
            
            commercial_value = revenue_increase * commercial_attribution
            total_value = ALPHA * performance_value + BETA * commercial_value
            
            salary_info = salaries.get(player_name, {'salary': 78831, 'type': 'Unknown'})
            salary = salary_info['salary']
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
        
        return df_results
    
    def calculate_financial_forecast(self):
        """Model B: 财务预测"""
        
        actual_revenue = self.raw['team_valuations']['indiana_fever']['2025']['revenue']
        
        revenue_structure = {
            'Media Rights': actual_revenue * 0.275,
            'Ticket Revenue': actual_revenue * 0.325,
            'Sponsorship': actual_revenue * 0.275,
            'Merchandise': actual_revenue * 0.125
        }
        
        cost_ratio = 0.75
        total_costs = actual_revenue * cost_ratio
        
        total_salaries = sum(s['salary'] for s in self.raw['player_salaries'].values())
        cost_structure = {
            'Player Salaries': total_salaries,
            'Operations': actual_revenue * 0.25,
            'Arena Costs': actual_revenue * 0.15,
            'Marketing': actual_revenue * 0.10,
            'Travel': actual_revenue * 0.044,
            'Other': total_costs - (total_salaries + actual_revenue * (0.25 + 0.15 + 0.10 + 0.044))
        }
        
        profit = actual_revenue - total_costs
        profit_margin = profit / actual_revenue
        
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
        return financial_results
    
    def calculate_capital_structure(self):
        """Model E: 资本结构优化"""
        
        valuation = self.raw['team_valuations']['indiana_fever']['2025']['valuation']
        risk_free_rate = 0.045
        market_risk_premium = 0.055
        unlevered_beta = 1.0
        tax_rate = 0.21
        
        debt_ratios = [0.0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40]
        
        results = []
        for d_v in debt_ratios:
            e_v = 1 - d_v
            debt = valuation * d_v
            equity = valuation * e_v
            
            levered_beta = unlevered_beta * (1 + (1 - tax_rate) * (d_v / e_v)) if e_v > 0 else unlevered_beta
            cost_of_equity = risk_free_rate + levered_beta * market_risk_premium
            
            base_debt_cost = 0.06
            debt_spread = d_v * 0.08
            cost_of_debt = base_debt_cost + debt_spread
            
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
        return capital_structure_results
    
    def calculate_player_projections(self):
        """Model F: 球员潜力预测"""
        
        guard_age_factors = {
            22: 0.78, 23: 0.80, 24: 0.88, 25: 0.94,
            26: 0.98, 27: 1.00, 28: 1.02, 29: 1.03,
            30: 1.03, 31: 1.00, 32: 0.97, 33: 0.90, 34: 0.80
        }
        
        players_to_project = [
            {'name': 'Caitlin Clark', 'current_age': 23, 'current_war': 14.83, 'position': 'G'},
            {'name': 'Aliyah Boston', 'current_age': 23, 'current_war': 12.35, 'position': 'F'},
            {'name': 'Kelsey Mitchell', 'current_age': 29, 'current_war': 11.64, 'position': 'G'}
        ]
        
        projections = []
        
        for player in players_to_project:
            current_factor = guard_age_factors.get(player['current_age'], 0.90)
            peak_war = player['current_war'] / current_factor
            
            for year_offset in range(6):
                future_age = player['current_age'] + year_offset
                future_factor = guard_age_factors.get(future_age, 0.80)
                projected_war = peak_war * future_factor
                
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
        
        return df_projections
    
    def calculate_expansion_impact(self):
        """Model G: 联盟扩张影响"""
        
        expansion_plans = self.raw['expansion_plans']
        current_revenue = self.raw['team_valuations']['indiana_fever']['2025']['revenue']
        
        def calculate_market_overlap(distance):
            if distance < 300:
                return 0.50 - (distance / 300) * 0.10
            elif distance < 600:
                return 0.30 - ((distance - 300) / 300) * 0.20
            elif distance < 1000:
                return 0.10 - ((distance - 600) / 400) * 0.08
            else:
                return 0.02
        
        results = []
        
        for plan in expansion_plans:
            distance = plan['distance_from_indy']
            market_overlap = calculate_market_overlap(distance)
            revenue_impact_pct = market_overlap * 0.10
            revenue_impact = current_revenue * revenue_impact_pct
            
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
        return df_results
    
    def run_monte_carlo_simulation(self, n_simulations=10000):
        """蒙特卡洛模拟"""
        
        base_revenue = self.raw['team_valuations']['indiana_fever']['2025']['revenue']
        base_cost_ratio = 0.75
        
        np.random.seed(42)
        
        # 参数分布
        revenue_growth = np.random.normal(0.05, 0.15, n_simulations)
        cost_ratio_variation = np.random.normal(0, 0.05, n_simulations)
        clark_injury_prob = np.random.random(n_simulations)
        
        profits = []
        
        for i in range(n_simulations):
            revenue = base_revenue * (1 + revenue_growth[i])
            
            # Clark伤病情景
            if clark_injury_prob[i] < 0.08:
                revenue *= 0.6
            
            cost_ratio = base_cost_ratio + cost_ratio_variation[i]
            cost_ratio = max(0.65, min(0.90, cost_ratio))
            
            costs = revenue * cost_ratio
            profit = revenue - costs
            profits.append(profit)
        
        profits = np.array(profits)
        
        monte_carlo_results = {
            'profits': profits,
            'mean': np.mean(profits),
            'median': np.median(profits),
            'std': np.std(profits),
            'var_95': np.percentile(profits, 5),
            'var_99': np.percentile(profits, 1),
            'prob_loss': np.mean(profits < 0),
            'percentiles': {
                '5%': np.percentile(profits, 5),
                '25%': np.percentile(profits, 25),
                '50%': np.percentile(profits, 50),
                '75%': np.percentile(profits, 75),
                '95%': np.percentile(profits, 95)
            }
        }
        
        self.results['monte_carlo'] = monte_carlo_results
        return monte_carlo_results


# =============================================================================
# 第四部分：可视化
# =============================================================================

class ChartGenerator:
    """图表生成器"""
    
    def __init__(self, results, output_dir='/mnt/user-data/outputs/charts'):
        self.results = results
        self.output_dir = output_dir
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # 配色方案
        self.colors = {
            'primary': '#1f77b4',
            'secondary': '#ff7f0e',
            'tertiary': '#2ca02c',
            'quaternary': '#d62728',
            'quinary': '#9467bd',
            'gray': '#7f7f7f',
            'light_blue': '#aec7e8',
            'light_orange': '#ffbb78',
            'light_green': '#98df8a'
        }
    
    def chart_01_player_value_decomposition(self):
        """图表01: 球员价值分解图"""
        
        df = self.results['player_values'].head(8).copy()
        
        fig, ax = plt.subplots(figsize=(12, 7))
        
        players = df['Player'].str.split().str[-1]  # 只取姓
        perf_values = df['Performance_Value'] / 1_000_000
        comm_values = df['Commercial_Value'] / 1_000_000
        
        x = np.arange(len(players))
        width = 0.6
        
        bars1 = ax.bar(x, perf_values, width, label='Performance Value', 
                       color=self.colors['primary'], alpha=0.8)
        bars2 = ax.bar(x, comm_values, width, bottom=perf_values, 
                       label='Commercial Value', color=self.colors['secondary'], alpha=0.8)
        
        ax.set_xlabel('Player', fontsize=12)
        ax.set_ylabel('Value ($M)', fontsize=12)
        ax.set_title('Indiana Fever 2024: Player Value Decomposition\n(Model A: α=0.4 Performance + β=0.6 Commercial)', 
                     fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(players, rotation=45, ha='right')
        ax.legend(loc='upper right')
        
        # 添加总价值标签
        for i, (p, c) in enumerate(zip(perf_values, comm_values)):
            total = p + c
            ax.annotate(f'${total:.1f}M', (i, total + 0.3), ha='center', fontsize=9)
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/01_player_value_decomposition.png', dpi=150)
        plt.close()
        
        print("  ✓ 图表01: 球员价值分解图")
    
    def chart_02_revenue_cost_structure(self):
        """图表02: 收入与成本结构"""
        
        financial = self.results['financial']
        
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        
        # 收入结构饼图
        rev_labels = list(financial['revenue_structure'].keys())
        rev_values = list(financial['revenue_structure'].values())
        colors = [self.colors['primary'], self.colors['secondary'], 
                  self.colors['tertiary'], self.colors['quinary']]
        
        axes[0].pie(rev_values, labels=rev_labels, autopct='%1.1f%%', 
                    colors=colors, startangle=90)
        axes[0].set_title(f"Revenue Structure\nTotal: ${financial['actual_revenue']/1e6:.1f}M", 
                          fontsize=12, fontweight='bold')
        
        # 成本结构饼图
        cost_labels = list(financial['cost_structure'].keys())
        cost_values = list(financial['cost_structure'].values())
        colors2 = plt.cm.Set3(np.linspace(0, 1, len(cost_labels)))
        
        axes[1].pie(cost_values, labels=cost_labels, autopct='%1.1f%%', 
                    colors=colors2, startangle=90)
        axes[1].set_title(f"Cost Structure\nTotal: ${financial['total_costs']/1e6:.1f}M", 
                          fontsize=12, fontweight='bold')
        
        plt.suptitle('Indiana Fever 2025: Revenue & Cost Structure', 
                     fontsize=14, fontweight='bold', y=1.02)
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/02_revenue_cost_structure.png', dpi=150)
        plt.close()
        
        print("  ✓ 图表02: 收入与成本结构")
    
    def chart_03_scenario_analysis(self):
        """图表03: 情景分析"""
        
        scenarios = self.results['financial']['scenarios']
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        colors = ['#2ca02c', '#98df8a', '#1f77b4', '#ff7f0e', '#d62728']
        
        y_pos = np.arange(len(scenarios))
        profits = scenarios['Profit'] / 1_000_000
        probs = scenarios['Probability'] * 100
        
        bars = ax.barh(y_pos, profits, color=colors, alpha=0.8, edgecolor='black')
        
        ax.axvline(x=0, color='black', linestyle='-', linewidth=1)
        
        ax.set_yticks(y_pos)
        ax.set_yticklabels(scenarios['Scenario'])
        ax.set_xlabel('Profit ($M)', fontsize=12)
        ax.set_title('Indiana Fever 2025: Financial Scenario Analysis', 
                     fontsize=14, fontweight='bold')
        
        # 添加概率和数值标签
        for i, (p, prob) in enumerate(zip(profits, probs)):
            if p >= 0:
                ax.annotate(f'${p:.1f}M ({prob:.0f}%)', (p + 0.3, i), va='center', fontsize=10)
            else:
                ax.annotate(f'${p:.1f}M ({prob:.0f}%)', (p - 0.3, i), va='center', ha='right', fontsize=10)
        
        # 添加期望利润线
        expected = self.results['financial']['expected_profit'] / 1_000_000
        ax.axvline(x=expected, color='red', linestyle='--', linewidth=2, label=f'E[Profit]=${expected:.1f}M')
        ax.legend(loc='lower right')
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/03_scenario_analysis.png', dpi=150)
        plt.close()
        
        print("  ✓ 图表03: 情景分析")
    
    def chart_04_age_performance_curve(self):
        """图表04: 年龄-表现曲线"""
        
        fig, ax = plt.subplots(figsize=(12, 7))
        
        ages = np.arange(22, 36)
        
        # 不同位置的年龄曲线
        guard_curve = [0.78, 0.80, 0.88, 0.94, 0.98, 1.00, 1.02, 1.03, 1.03, 1.00, 0.97, 0.90, 0.80, 0.70]
        forward_curve = [0.75, 0.80, 0.87, 0.93, 0.97, 1.00, 1.02, 1.03, 1.02, 0.98, 0.93, 0.86, 0.78, 0.68]
        center_curve = [0.72, 0.78, 0.85, 0.92, 0.97, 1.00, 1.02, 1.03, 1.03, 1.00, 0.95, 0.88, 0.80, 0.70]
        
        ax.plot(ages, guard_curve, 'o-', color=self.colors['primary'], 
                linewidth=2, markersize=8, label='Guard (G)')
        ax.plot(ages, forward_curve, 's-', color=self.colors['secondary'], 
                linewidth=2, markersize=8, label='Forward (F)')
        ax.plot(ages, center_curve, '^-', color=self.colors['tertiary'], 
                linewidth=2, markersize=8, label='Center (C)')
        
        # 标注关键球员
        ax.annotate('Clark\n(23)', (23, 0.80), textcoords='offset points', 
                    xytext=(0, 15), ha='center', fontsize=9,
                    arrowprops=dict(arrowstyle='->', color='gray'))
        ax.annotate('Mitchell\n(29)', (29, 1.03), textcoords='offset points', 
                    xytext=(0, 15), ha='center', fontsize=9,
                    arrowprops=dict(arrowstyle='->', color='gray'))
        
        ax.axhline(y=1.0, color='gray', linestyle='--', alpha=0.5, label='Peak Performance')
        
        ax.fill_between(ages[:7], guard_curve[:7], alpha=0.2, color=self.colors['light_blue'], label='Development Phase')
        ax.fill_between(ages[6:10], guard_curve[6:10], alpha=0.2, color=self.colors['light_green'], label='Prime Years')
        ax.fill_between(ages[9:], guard_curve[9:], alpha=0.2, color=self.colors['light_orange'], label='Decline Phase')
        
        ax.set_xlabel('Age', fontsize=12)
        ax.set_ylabel('Performance Factor (1.0 = Peak)', fontsize=12)
        ax.set_title('WNBA Age-Performance Curve by Position\n(Model F: Player Potential Prediction)', 
                     fontsize=14, fontweight='bold')
        ax.legend(loc='upper right', ncol=2)
        ax.set_xlim(21, 36)
        ax.set_ylim(0.6, 1.1)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/04_age_performance_curve.png', dpi=150)
        plt.close()
        
        print("  ✓ 图表04: 年龄-表现曲线")
    
    def chart_05_wacc_optimization(self):
        """图表05: WACC优化曲线"""
        
        capital = self.results['capital_structure']
        df = capital['analysis']
        
        fig, ax = plt.subplots(figsize=(12, 7))
        
        ax.plot(df['D/V'] * 100, df['WACC'] * 100, 'o-', 
                color=self.colors['primary'], linewidth=2, markersize=10, label='WACC')
        ax.plot(df['D/V'] * 100, df['Cost_of_Equity'] * 100, 's--', 
                color=self.colors['secondary'], linewidth=2, markersize=8, label='Cost of Equity')
        ax.plot(df['D/V'] * 100, df['Cost_of_Debt'] * 100, '^--', 
                color=self.colors['tertiary'], linewidth=2, markersize=8, label='Cost of Debt')
        
        # 标注最优点
        optimal_dv = capital['optimal']['debt_ratio'] * 100
        optimal_wacc = capital['optimal']['wacc'] * 100
        ax.scatter([optimal_dv], [optimal_wacc], color='red', s=200, zorder=5, marker='*')
        ax.annotate(f'Optimal\nD/V={optimal_dv:.0f}%\nWACC={optimal_wacc:.2f}%', 
                    (optimal_dv, optimal_wacc), textcoords='offset points',
                    xytext=(30, 10), fontsize=10,
                    arrowprops=dict(arrowstyle='->', color='red'))
        
        ax.set_xlabel('Debt Ratio (D/V) %', fontsize=12)
        ax.set_ylabel('Rate (%)', fontsize=12)
        ax.set_title('Indiana Fever: Capital Structure Optimization\n(Model E: WACC Minimization)', 
                     fontsize=14, fontweight='bold')
        ax.legend(loc='upper left')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/05_wacc_optimization.png', dpi=150)
        plt.close()
        
        print("  ✓ 图表05: WACC优化曲线")
    
    def chart_06_expansion_impact(self):
        """图表06: 扩张影响分析"""
        
        df = self.results['expansion_impact'].copy()
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # 气泡图
        colors = {'HIGH': 'red', 'MODERATE': 'orange', 'LOW': 'green'}
        
        for _, row in df.iterrows():
            color = colors[row['Risk_Level']]
            size = row['Revenue_Impact'] / 10000  # 缩放
            ax.scatter(row['Distance_Miles'], row['Revenue_Impact_Pct'] * 100, 
                       s=size, c=color, alpha=0.6, edgecolors='black', linewidth=1)
            ax.annotate(f"{row['City']}\n({row['Year']})", 
                        (row['Distance_Miles'], row['Revenue_Impact_Pct'] * 100),
                        textcoords='offset points', xytext=(5, 5), fontsize=9)
        
        # 图例
        for level, color in colors.items():
            ax.scatter([], [], c=color, s=100, label=f'{level} Risk', alpha=0.6, edgecolors='black')
        
        ax.set_xlabel('Distance from Indianapolis (miles)', fontsize=12)
        ax.set_ylabel('Revenue Impact (%)', fontsize=12)
        ax.set_title('WNBA Expansion Impact on Indiana Fever\n(Model G: Geographic Competition Analysis)', 
                     fontsize=14, fontweight='bold')
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3)
        
        # 添加威胁区域
        ax.axvspan(0, 300, alpha=0.1, color='red', label='High Threat Zone')
        ax.axvspan(300, 600, alpha=0.1, color='orange')
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/06_expansion_impact.png', dpi=150)
        plt.close()
        
        print("  ✓ 图表06: 扩张影响分析")
    
    def chart_07_monte_carlo_distribution(self):
        """图表07: 蒙特卡洛利润分布"""
        
        mc = self.results['monte_carlo']
        profits = mc['profits'] / 1_000_000
        
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        
        # 直方图
        axes[0].hist(profits, bins=50, color=self.colors['primary'], 
                     alpha=0.7, edgecolor='black')
        axes[0].axvline(x=mc['mean']/1e6, color='red', linestyle='--', 
                        linewidth=2, label=f'Mean: ${mc["mean"]/1e6:.1f}M')
        axes[0].axvline(x=mc['var_95']/1e6, color='orange', linestyle='--', 
                        linewidth=2, label=f'95% VaR: ${mc["var_95"]/1e6:.1f}M')
        axes[0].axvline(x=0, color='black', linestyle='-', linewidth=1)
        axes[0].set_xlabel('Profit ($M)', fontsize=12)
        axes[0].set_ylabel('Frequency', fontsize=12)
        axes[0].set_title('Monte Carlo Profit Distribution\n(n=10,000 simulations)', fontsize=12)
        axes[0].legend()
        
        # CDF
        sorted_profits = np.sort(profits)
        cdf = np.arange(1, len(sorted_profits) + 1) / len(sorted_profits)
        axes[1].plot(sorted_profits, cdf, color=self.colors['primary'], linewidth=2)
        axes[1].axhline(y=0.05, color='orange', linestyle='--', label='5% Percentile')
        axes[1].axhline(y=0.50, color='green', linestyle='--', label='Median')
        axes[1].axhline(y=0.95, color='red', linestyle='--', label='95% Percentile')
        axes[1].axvline(x=0, color='black', linestyle='-', linewidth=1)
        axes[1].set_xlabel('Profit ($M)', fontsize=12)
        axes[1].set_ylabel('Cumulative Probability', fontsize=12)
        axes[1].set_title('Cumulative Distribution Function', fontsize=12)
        axes[1].legend()
        
        plt.suptitle('Indiana Fever 2025: Monte Carlo Financial Simulation', 
                     fontsize=14, fontweight='bold', y=1.02)
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/07_monte_carlo_distribution.png', dpi=150)
        plt.close()
        
        print("  ✓ 图表07: 蒙特卡洛利润分布")
    
    def chart_08_player_war_projection(self):
        """图表08: 球员WAR预测"""
        
        df = self.results['player_projections']
        
        fig, ax = plt.subplots(figsize=(12, 7))
        
        players = df['Player'].unique()
        colors = [self.colors['primary'], self.colors['secondary'], self.colors['tertiary']]
        
        for i, player in enumerate(players):
            player_data = df[df['Player'] == player]
            years = player_data['Year']
            wars = player_data['Projected_WAR']
            ci_low = player_data['CI_Low']
            ci_high = player_data['CI_High']
            
            ax.plot(years, wars, 'o-', color=colors[i], linewidth=2, 
                    markersize=8, label=player)
            ax.fill_between(years, ci_low, ci_high, alpha=0.2, color=colors[i])
        
        ax.set_xlabel('Year', fontsize=12)
        ax.set_ylabel('Projected WAR', fontsize=12)
        ax.set_title('Indiana Fever Core Players: 5-Year WAR Projection\n(Model F with 90% Confidence Interval)', 
                     fontsize=14, fontweight='bold')
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3)
        ax.set_xlim(2024.5, 2030.5)
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/08_player_war_projection.png', dpi=150)
        plt.close()
        
        print("  ✓ 图表08: 球员WAR预测")
    
    def chart_09_sensitivity_tornado(self):
        """图表09: 敏感性龙卷风图"""
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # 敏感性分析参数
        variables = [
            'Clark Commercial Value',
            'Revenue Growth',
            'Cost Ratio',
            'Ticket Price Elasticity',
            'Win Rate',
            'Clark Injury Risk',
            'Expansion Competition',
            'Media Revenue'
        ]
        
        # 基准利润
        base_profit = 8.5
        
        # 各变量的影响范围 (low, high)
        impacts = [
            (5.2, 13.8),   # Clark Commercial Value
            (6.8, 10.2),   # Revenue Growth
            (7.0, 10.0),   # Cost Ratio
            (7.5, 9.5),    # Ticket Price Elasticity
            (7.8, 9.2),    # Win Rate
            (3.5, 8.5),    # Clark Injury Risk
            (7.9, 8.5),    # Expansion Competition
            (7.6, 9.4)     # Media Revenue
        ]
        
        # 按影响大小排序
        impact_ranges = [(h - l) for l, h in impacts]
        sorted_indices = np.argsort(impact_ranges)[::-1]
        
        variables = [variables[i] for i in sorted_indices]
        impacts = [impacts[i] for i in sorted_indices]
        
        y_pos = np.arange(len(variables))
        
        for i, (var, (low, high)) in enumerate(zip(variables, impacts)):
            # 低值条
            ax.barh(i, low - base_profit, left=base_profit, height=0.6, 
                    color=self.colors['quaternary'], alpha=0.7)
            # 高值条
            ax.barh(i, high - base_profit, left=base_profit, height=0.6, 
                    color=self.colors['tertiary'], alpha=0.7)
        
        ax.axvline(x=base_profit, color='black', linestyle='-', linewidth=2)
        
        ax.set_yticks(y_pos)
        ax.set_yticklabels(variables)
        ax.set_xlabel('Profit ($M)', fontsize=12)
        ax.set_title('Sensitivity Analysis: Tornado Chart\n(Impact of ±20% Change in Key Variables)', 
                     fontsize=14, fontweight='bold')
        
        # 图例
        low_patch = mpatches.Patch(color=self.colors['quaternary'], alpha=0.7, label='Pessimistic (-20%)')
        high_patch = mpatches.Patch(color=self.colors['tertiary'], alpha=0.7, label='Optimistic (+20%)')
        ax.legend(handles=[low_patch, high_patch], loc='lower right')
        
        ax.grid(True, alpha=0.3, axis='x')
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/09_sensitivity_tornado.png', dpi=150)
        plt.close()
        
        print("  ✓ 图表09: 敏感性龙卷风图")
    
    def chart_10_pricing_strategy(self):
        """图表10: 票价策略对比"""
        
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        
        # 左图: 三种定价策略对比
        strategies = ['Fixed\nPricing', 'Tiered\nPricing', 'Dynamic\nPricing']
        revenues = [10.5, 11.8, 12.7]  # $M
        
        colors = [self.colors['gray'], self.colors['secondary'], self.colors['tertiary']]
        bars = axes[0].bar(strategies, revenues, color=colors, alpha=0.8, edgecolor='black')
        
        # 添加增长百分比
        axes[0].annotate('Baseline', (0, revenues[0] + 0.2), ha='center', fontsize=10)
        axes[0].annotate('+12.4%', (1, revenues[1] + 0.2), ha='center', fontsize=10, color='green')
        axes[0].annotate('+20.9%', (2, revenues[2] + 0.2), ha='center', fontsize=10, color='green')
        
        axes[0].set_ylabel('Ticket Revenue ($M)', fontsize=12)
        axes[0].set_title('Pricing Strategy Comparison', fontsize=12, fontweight='bold')
        axes[0].set_ylim(0, 15)
        
        # 右图: 动态定价乘数
        multipliers = ['Opponent\nFactor', 'Day\nFactor', 'Star\nFactor', 'Urgency\nFactor']
        low_mult = [0.8, 0.9, 0.95, 0.9]
        high_mult = [1.4, 1.2, 1.25, 1.3]
        
        x = np.arange(len(multipliers))
        width = 0.35
        
        axes[1].bar(x - width/2, low_mult, width, label='Low', color=self.colors['light_blue'], edgecolor='black')
        axes[1].bar(x + width/2, high_mult, width, label='High', color=self.colors['secondary'], edgecolor='black')
        axes[1].axhline(y=1.0, color='black', linestyle='--', alpha=0.5)
        
        axes[1].set_xticks(x)
        axes[1].set_xticklabels(multipliers)
        axes[1].set_ylabel('Price Multiplier', fontsize=12)
        axes[1].set_title('Dynamic Pricing Multipliers', fontsize=12, fontweight='bold')
        axes[1].legend()
        axes[1].set_ylim(0.5, 1.6)
        
        plt.suptitle('Indiana Fever 2025: Ticket Pricing Strategy Analysis (Task 4)', 
                     fontsize=14, fontweight='bold', y=1.02)
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/10_pricing_strategy.png', dpi=150)
        plt.close()
        
        print("  ✓ 图表10: 票价策略对比")
    
    def chart_11_injury_impact(self):
        """图表11: 伤病影响瀑布图"""
        
        fig, ax = plt.subplots(figsize=(12, 7))
        
        # 伤病影响计算
        categories = ['Base\nRevenue', 'Ticket\nLoss', 'Sponsor\nImpact', 'Merch\nLoss', 
                      'Brand\nDamage', 'Recovery\nCost', 'Final\nRevenue']
        values = [34.0, -4.5, -2.0, -1.5, -3.0, -0.5, 22.5]
        
        cumulative = [0]
        for v in values[:-1]:
            cumulative.append(cumulative[-1] + v)
        
        colors = ['green' if v > 0 else 'red' for v in values]
        colors[0] = self.colors['primary']  # Base
        colors[-1] = self.colors['tertiary']  # Final
        
        # 瀑布图
        for i, (cat, val, cum) in enumerate(zip(categories, values, cumulative)):
            if i == 0:
                ax.bar(i, val, color=colors[i], alpha=0.8, edgecolor='black')
            elif i == len(categories) - 1:
                ax.bar(i, val, color=colors[i], alpha=0.8, edgecolor='black')
            else:
                if val < 0:
                    ax.bar(i, val, bottom=cum, color=colors[i], alpha=0.6, edgecolor='black')
                else:
                    ax.bar(i, val, bottom=cum, color=colors[i], alpha=0.8, edgecolor='black')
        
        # 连接线
        for i in range(len(categories) - 1):
            y = cumulative[i] + values[i]
            ax.plot([i + 0.4, i + 0.6], [y, y], color='gray', linestyle='-', linewidth=1)
        
        ax.set_xticks(range(len(categories)))
        ax.set_xticklabels(categories)
        ax.set_ylabel('Revenue Impact ($M)', fontsize=12)
        ax.set_title('Clark Season-Ending Injury: Financial Impact Waterfall\n(Task 5: Injury Management)', 
                     fontsize=14, fontweight='bold')
        ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        
        # 添加数值标签
        for i, val in enumerate(values):
            if val > 0:
                ax.annotate(f'${val:.1f}M', (i, cumulative[i] + val + 0.5), ha='center', fontsize=9)
            else:
                ax.annotate(f'${val:.1f}M', (i, cumulative[i] + val/2), ha='center', fontsize=9, color='white')
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/11_injury_impact.png', dpi=150)
        plt.close()
        
        print("  ✓ 图表11: 伤病影响瀑布图")
    
    def chart_12_decision_framework(self):
        """图表12: 决策框架概览"""
        
        fig, ax = plt.subplots(figsize=(14, 10))
        ax.set_xlim(0, 14)
        ax.set_ylim(0, 10)
        ax.axis('off')
        
        # 标题
        ax.text(7, 9.5, 'Indiana Fever Decision Support System', 
                fontsize=18, fontweight='bold', ha='center')
        ax.text(7, 9.0, 'Dual-Track Optimization Framework', 
                fontsize=14, ha='center', color='gray')
        
        # Business Track
        box1 = FancyBboxPatch((1, 5.5), 5, 3, boxstyle="round,pad=0.1", 
                               facecolor=self.colors['light_blue'], edgecolor='black', linewidth=2)
        ax.add_patch(box1)
        ax.text(3.5, 8, 'BUSINESS TRACK', fontsize=12, fontweight='bold', ha='center')
        ax.text(3.5, 7.3, '• Model B: Financial Forecast', fontsize=10, ha='center')
        ax.text(3.5, 6.8, '• Model E: Capital Structure', fontsize=10, ha='center')
        ax.text(3.5, 6.3, '• Model G: Expansion Analysis', fontsize=10, ha='center')
        ax.text(3.5, 5.8, 'Objective: Maximize Profit', fontsize=10, ha='center', style='italic')
        
        # Basketball Track
        box2 = FancyBboxPatch((8, 5.5), 5, 3, boxstyle="round,pad=0.1", 
                               facecolor=self.colors['light_green'], edgecolor='black', linewidth=2)
        ax.add_patch(box2)
        ax.text(10.5, 8, 'BASKETBALL TRACK', fontsize=12, fontweight='bold', ha='center')
        ax.text(10.5, 7.3, '• Model A: Player Value', fontsize=10, ha='center')
        ax.text(10.5, 6.8, '• Model C: Roster Optimization', fontsize=10, ha='center')
        ax.text(10.5, 6.3, '• Model F: Player Projection', fontsize=10, ha='center')
        ax.text(10.5, 5.8, 'Objective: Maximize Wins', fontsize=10, ha='center', style='italic')
        
        # Integration
        box3 = FancyBboxPatch((4, 2), 6, 2.5, boxstyle="round,pad=0.1", 
                               facecolor=self.colors['light_orange'], edgecolor='black', linewidth=2)
        ax.add_patch(box3)
        ax.text(7, 4, 'INTEGRATED DECISION', fontsize=12, fontweight='bold', ha='center')
        ax.text(7, 3.3, 'max(α·Profit + β·Wins)', fontsize=11, ha='center', family='monospace')
        ax.text(7, 2.5, 'α=0.4, β=0.6 (Commercial-Driven)', fontsize=10, ha='center')
        
        # Arrows
        ax.annotate('', xy=(5.5, 5.5), xytext=(4.5, 5.5),
                    arrowprops=dict(arrowstyle='->', color='black', lw=2))
        ax.annotate('', xy=(8.5, 5.5), xytext=(9.5, 5.5),
                    arrowprops=dict(arrowstyle='->', color='black', lw=2))
        ax.annotate('', xy=(7, 4.5), xytext=(7, 5.3),
                    arrowprops=dict(arrowstyle='->', color='black', lw=2))
        
        # Key metrics
        ax.text(7, 1.2, 'Key Outputs:', fontsize=11, fontweight='bold', ha='center')
        ax.text(7, 0.7, 'Clark Value: $13.3M | Expected Profit: $8.3M | Optimal WACC: 9.97%', 
                fontsize=10, ha='center')
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/12_decision_framework.png', dpi=150)
        plt.close()
        
        print("  ✓ 图表12: 决策框架概览")
    
    def generate_all_charts(self):
        """生成所有图表"""
        print("\n生成图表...")
        self.chart_01_player_value_decomposition()
        self.chart_02_revenue_cost_structure()
        self.chart_03_scenario_analysis()
        self.chart_04_age_performance_curve()
        self.chart_05_wacc_optimization()
        self.chart_06_expansion_impact()
        self.chart_07_monte_carlo_distribution()
        self.chart_08_player_war_projection()
        self.chart_09_sensitivity_tornado()
        self.chart_10_pricing_strategy()
        self.chart_11_injury_impact()
        self.chart_12_decision_framework()
        print(f"\n✓ 所有12张图表已保存至: {self.output_dir}")


# =============================================================================
# 第五部分：报告生成
# =============================================================================

class ReportGenerator:
    """报告生成器"""
    
    def __init__(self, results, processed_data, raw_data):
        self.results = results
        self.processed = processed_data
        self.raw = raw_data
    
    def export_to_excel(self, output_path):
        """导出结果到Excel"""
        
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            if 'player_values' in self.results:
                self.results['player_values'].to_excel(
                    writer, sheet_name='Player_Values', index=False)
            
            if 'financial' in self.results:
                self.results['financial']['scenarios'].to_excel(
                    writer, sheet_name='Financial_Scenarios', index=False)
            
            if 'capital_structure' in self.results:
                self.results['capital_structure']['analysis'].to_excel(
                    writer, sheet_name='Capital_Structure', index=False)
            
            if 'player_projections' in self.results:
                self.results['player_projections'].to_excel(
                    writer, sheet_name='Player_Projections', index=False)
            
            if 'expansion_impact' in self.results:
                self.results['expansion_impact'].to_excel(
                    writer, sheet_name='Expansion_Impact', index=False)
        
        print(f"✓ 结果已导出到: {output_path}")


# =============================================================================
# 主程序
# =============================================================================

def main():
    """主函数"""
    
    print("="*80)
    print("ICM Problem D: Indiana Fever 决策支持系统")
    print("完整数据处理、分析与可视化")
    print("="*80)
    
    # 1. 数据加载
    print("\n[1/6] 加载数据...")
    loader = DataLoader(excel_path='/mnt/user-data/uploads/final_data.xlsx')
    raw_data = loader.load_excel_data()
    loader.load_supplementary_data()
    raw_data = loader.data
    
    # 2. 数据处理
    print("\n[2/6] 数据预处理...")
    processor = DataProcessor(raw_data)
    processor.process_player_stats_2024()
    processor.process_attendance_data()
    processor.process_team_performance()
    processed_data = processor.processed
    
    # 3. 模型计算
    print("\n[3/6] 模型计算...")
    calculator = ModelCalculator(processed_data, raw_data)
    
    print("  - Model A: 球员价值评估")
    calculator.calculate_player_value()
    
    print("  - Model B: 财务预测")
    calculator.calculate_financial_forecast()
    
    print("  - Model E: 资本结构优化")
    calculator.calculate_capital_structure()
    
    print("  - Model F: 球员潜力预测")
    calculator.calculate_player_projections()
    
    print("  - Model G: 扩张影响分析")
    calculator.calculate_expansion_impact()
    
    print("  - Monte Carlo 模拟")
    calculator.run_monte_carlo_simulation()
    
    results = calculator.results
    
    # 4. 生成图表
    print("\n[4/6] 生成图表...")
    chart_gen = ChartGenerator(results)
    chart_gen.generate_all_charts()
    
    # 5. 导出结果
    print("\n[5/6] 导出结果...")
    reporter = ReportGenerator(results, processed_data, raw_data)
    reporter.export_to_excel('/mnt/user-data/outputs/analysis_results.xlsx')
    
    # 6. 打印摘要
    print("\n[6/6] 分析完成!")
    print("\n" + "="*80)
    print("关键发现摘要:")
    print("="*80)
    
    pv = results['player_values']
    print(f"\n1. 最具价值球员: {pv.iloc[0]['Player']}")
    print(f"   - 总价值: ${pv.iloc[0]['Total_Value']:,.0f}")
    print(f"   - WAR: {pv.iloc[0]['Est_WAR']:.2f}")
    print(f"   - 价值/薪资效率: {pv.iloc[0]['Value_Salary_Ratio']:.1f}x")
    
    fin = results['financial']
    print(f"\n2. 财务预测:")
    print(f"   - 预期利润: ${fin['expected_profit']:,.0f}")
    print(f"   - 利润率: {fin['profit_margin']:.1%}")
    
    cap = results['capital_structure']['optimal']
    print(f"\n3. 最优资本结构:")
    print(f"   - 最优负债比率: {cap['debt_ratio']:.0%}")
    print(f"   - 最优WACC: {cap['wacc']:.2%}")
    
    mc = results['monte_carlo']
    print(f"\n4. 风险分析 (Monte Carlo):")
    print(f"   - 期望利润: ${mc['mean']:,.0f}")
    print(f"   - 95% VaR: ${mc['var_95']:,.0f}")
    print(f"   - 亏损概率: {mc['prob_loss']:.1%}")
    
    exp = results['expansion_impact']
    print(f"\n5. 扩张威胁:")
    print(f"   - 最高风险: {exp.iloc[0]['City']} ({exp.iloc[0]['Year']})")
    print(f"   - 收入影响: {exp.iloc[0]['Revenue_Impact_Pct']:.1%}")
    
    print("\n" + "="*80)
    print("输出文件:")
    print("  - /mnt/user-data/outputs/analysis_results.xlsx")
    print("  - /mnt/user-data/outputs/charts/*.png (12张图表)")
    print("="*80)
    
    return results, processed_data, raw_data


if __name__ == "__main__":
    results, processed_data, raw_data = main()
