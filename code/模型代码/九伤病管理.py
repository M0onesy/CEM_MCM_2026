import numpy as np
from typing import Dict, List


class InjuryManagementModel:
    """伤病风险管理模型"""

    def __init__(self, star_player: str = 'Caitlin Clark'):
        self.star_player = star_player

        # 伤病概率参数
        self.base_injury_rate = 0.08  # 8%的重大伤病基准概率
        self.minutes_factor = 0.002  # 每分钟增加的风险
        self.fatigue_threshold = 33  # 疲劳阈值（分钟）

    def calculate_injury_probability(self, minutes_avg: float,
                                     games_played: int,
                                     rest_days_avg: float) -> Dict:
        """计算伤病概率"""
        # 基准风险
        prob = self.base_injury_rate

        # 高负荷风险
        if minutes_avg > self.fatigue_threshold:
            excess_minutes = minutes_avg - self.fatigue_threshold
            prob += excess_minutes * self.minutes_factor

        # 赛季疲劳累积
        season_fatigue = games_played / 40 * 0.02
        prob += season_fatigue

        # 休息不足
        if rest_days_avg < 2:
            prob += 0.02

        return {
            'base_probability': self.base_injury_rate,
            'final_probability': min(prob, 0.30),  # 上限30%
            'risk_factors': {
                'high_minutes': minutes_avg > self.fatigue_threshold,
                'season_fatigue': games_played > 30,
                'insufficient_rest': rest_days_avg < 2
            }
        }

    def financial_impact_analysis(self, injury_weeks: int,
                                  player_commercial_value: float) -> Dict:
        """分析伤病财务影响"""
        # 收入影响（按周计算）
        weekly_revenue_loss = player_commercial_value / 22  # 22周赛季
        total_revenue_loss = weekly_revenue_loss * injury_weeks

        # 间接损失
        attendance_drop = 0.25 if injury_weeks > 4 else 0.15  # 上座率下降
        sponsor_impact = 0.10 * injury_weeks / 22  # 赞助价值影响

        indirect_loss = player_commercial_value * (attendance_drop * 0.5 + sponsor_impact)

        return {
            'injury_duration_weeks': injury_weeks,
            'direct_revenue_loss': total_revenue_loss,
            'indirect_losses': indirect_loss,
            'total_financial_impact': total_revenue_loss + indirect_loss,
            'games_missed': injury_weeks * 2  # 约每周2场
        }

    def insurance_recommendation(self, player_value: float) -> Dict:
        """保险建议"""
        # 保险参数
        coverage_amount = player_value * 1.2  # 120%覆盖
        premium_rate = 0.03  # 3%保费率
        annual_premium = coverage_amount * premium_rate

        # 期望价值分析
        injury_prob = 0.10  # 假设10%重大伤病概率
        expected_loss = player_value * injury_prob

        return {
            'recommended_coverage': coverage_amount,
            'annual_premium': annual_premium,
            'expected_loss_without_insurance': expected_loss,
            'net_benefit': expected_loss - annual_premium,
            'recommendation': 'PURCHASE' if expected_loss > annual_premium * 1.2 else 'OPTIONAL'
        }

    def load_management_protocol(self, current_minutes: float) -> Dict:
        """负荷管理方案"""
        if current_minutes > 35:
            protocol = {
                'status': 'HIGH RISK',
                'target_minutes': 32,
                'rest_games': 'Every 3rd back-to-back',
                'actions': [
                    'Reduce minutes by 3-4 per game',
                    'No overtime unless critical',
                    'Extra rest in blowouts',
                    'Enhanced recovery protocols'
                ]
            }
        elif current_minutes > 32:
            protocol = {
                'status': 'MODERATE RISK',
                'target_minutes': 30,
                'rest_games': 'Occasional back-to-back rest',
                'actions': [
                    'Monitor fatigue indicators',
                    'Flexible minutes based on game situation',
                    'Increased focus on recovery'
                ]
            }
        else:
            protocol = {
                'status': 'LOW RISK',
                'target_minutes': current_minutes,
                'rest_games': 'As needed',
                'actions': [
                    'Maintain current approach',
                    'Standard recovery protocols'
                ]
            }

        return protocol

    def contingency_plan(self, injury_scenario: str) -> Dict:
        """伤病应急预案"""
        plans = {
            'minor': {
                'duration': '1-2 weeks',
                'actions': [
                    'Activate backup guard',
                    'Adjust rotation',
                    'No roster changes needed'
                ],
                'expected_wins_lost': 0.5,
                'revenue_impact': '-5%'
            },
            'moderate': {
                'duration': '3-6 weeks',
                'actions': [
                    'Sign hardship replacement',
                    'Reallocate offensive responsibility',
                    'Adjust marketing messaging',
                    'File insurance claim'
                ],
                'expected_wins_lost': 2.0,
                'revenue_impact': '-15%'
            },
            'major': {
                'duration': '6+ weeks / season-ending',
                'actions': [
                    'Activate full insurance coverage',
                    'Sign experienced FA replacement',
                    'Reassess season goals',
                    'Heavy marketing pivot',
                    'Communicate transparently with fans',
                    'Consider long-term roster moves'
                ],
                'expected_wins_lost': 5.0,
                'revenue_impact': '-35%'
            }
        }

        return plans.get(injury_scenario, plans['moderate'])

    def monte_carlo_simulation(self, n_simulations: int = 10000) -> Dict:
        """蒙特卡洛模拟"""
        results = []

        for _ in range(n_simulations):
            # 随机生成伤病事件
            injury_occurs = np.random.random() < 0.10

            if injury_occurs:
                # 随机伤病时长
                injury_weeks = np.random.choice([2, 4, 6, 10], p=[0.4, 0.3, 0.2, 0.1])
                wins_lost = injury_weeks * 0.5
                revenue_loss = injury_weeks * 0.02 * 55000000  # 假设$55M总收入
            else:
                injury_weeks = 0
                wins_lost = 0
                revenue_loss = 0

            results.append({
                'injury': injury_occurs,
                'weeks': injury_weeks,
                'wins_lost': wins_lost,
                'revenue_loss': revenue_loss
            })

        # 统计分析
        injury_rate = sum(r['injury'] for r in results) / n_simulations
        avg_wins_lost = np.mean([r['wins_lost'] for r in results])
        avg_revenue_loss = np.mean([r['revenue_loss'] for r in results])

        # 分位数
        revenue_losses = [r['revenue_loss'] for r in results]
        p50 = np.percentile(revenue_losses, 50)
        p90 = np.percentile(revenue_losses, 90)
        p99 = np.percentile(revenue_losses, 99)

        return {
            'n_simulations': n_simulations,
            'injury_rate': injury_rate,
            'expected_wins_lost': avg_wins_lost,
            'expected_revenue_loss': avg_revenue_loss,
            'revenue_loss_percentiles': {
                'p50': p50,
                'p90': p90,
                'p99': p99
            },
            'var_95': np.percentile(revenue_losses, 95)  # Value at Risk
        }

    def print_injury_report(self, player_data: Dict):
        """打印伤病管理报告"""
        print("═" * 70)
        print(f"       INJURY RISK MANAGEMENT: {self.star_player}")
        print("═" * 70)

        # 风险评估
        risk = self.calculate_injury_probability(
            player_data['minutes_avg'],
            player_data['games_played'],
            player_data['rest_days_avg']
        )

        print(f"\n📊 RISK ASSESSMENT:")
        print(f"   Injury Probability: {risk['final_probability']:.1%}")
        print(f"   Risk Factors:")
        for factor, status in risk['risk_factors'].items():
            icon = "⚠️" if status else "✓"
            print(f"     {icon} {factor}: {'Yes' if status else 'No'}")

        # 财务影响
        impact_4wk = self.financial_impact_analysis(4, player_data['commercial_value'])
        impact_8wk = self.financial_impact_analysis(8, player_data['commercial_value'])

        print(f"\n💰 FINANCIAL IMPACT SCENARIOS:")
        print(f"   4-Week Injury: ${impact_4wk['total_financial_impact'] / 1e6:.1f}M loss")
        print(f"   8-Week Injury: ${impact_8wk['total_financial_impact'] / 1e6:.1f}M loss")

        # 保险建议
        insurance = self.insurance_recommendation(player_data['commercial_value'])

        print(f"\n🛡️ INSURANCE RECOMMENDATION:")
        print(f"   Coverage: ${insurance['recommended_coverage'] / 1e6:.1f}M")
        print(f"   Annual Premium: ${insurance['annual_premium'] / 1e6:.2f}M")
        print(f"   Recommendation: {insurance['recommendation']}")

        # 负荷管理
        protocol = self.load_management_protocol(player_data['minutes_avg'])

        print(f"\n⚙️ LOAD MANAGEMENT PROTOCOL:")
        print(f"   Status: {protocol['status']}")
        print(f"   Target Minutes: {protocol['target_minutes']}")
        print(f"   Rest Policy: {protocol['rest_games']}")
        print(f"   Actions:")
        for action in protocol['actions']:
            print(f"     → {action}")

        # 蒙特卡洛
        mc_results = self.monte_carlo_simulation()

        print(f"\n📈 MONTE CARLO SIMULATION ({mc_results['n_simulations']:,} runs):")
        print(f"   Expected Wins Lost: {mc_results['expected_wins_lost']:.1f}")
        print(f"   Expected Revenue Loss: ${mc_results['expected_revenue_loss'] / 1e6:.2f}M")
        print(f"   Value at Risk (95%): ${mc_results['var_95'] / 1e6:.2f}M")

        print("═" * 70)


# 运行伤病分析
injury_model = InjuryManagementModel('Caitlin Clark')
player_data = {
    'minutes_avg': 35.8,
    'games_played': 36,
    'rest_days_avg': 1.8,
    'commercial_value': 15000000
}
injury_model.print_injury_report(player_data)