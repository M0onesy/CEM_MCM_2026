import numpy as np
from typing import Dict, List


class PlayerPotentialModel:
    """球员潜力预测模型"""

    def __init__(self):
        # 位置特定的年龄曲线参数
        self.position_curves = {
            'G': {'peak_start': 25, 'peak_end': 30, 'decline_rate': 0.04, 'growth_rate': 0.10},
            'F': {'peak_start': 24, 'peak_end': 29, 'decline_rate': 0.05, 'growth_rate': 0.12},
            'C': {'peak_start': 25, 'peak_end': 31, 'decline_rate': 0.06, 'growth_rate': 0.08}
        }

        self.vpw = 300000  # Value per win
        self.discount_rate = 0.08

    def age_adjustment_factor(self, current_age: int, future_age: int, position: str) -> float:
        """计算年龄调整因子"""
        curve = self.position_curves.get(position[0], self.position_curves['F'])

        if future_age < curve['peak_start']:
            # 上升期：每年提升
            years_to_peak = curve['peak_start'] - future_age
            return 1.0 - (years_to_peak * curve['growth_rate'] * 0.5)
        elif future_age <= curve['peak_end']:
            # 巅峰期：稳定 + 经验增益
            return 1.0 + 0.02 * (future_age - curve['peak_start'])
        else:
            # 下降期
            years_past_peak = future_age - curve['peak_end']
            return max(0.5, 1.0 - years_past_peak * curve['decline_rate'])

    def injury_risk_factor(self, player: Dict, age: int) -> float:
        """计算伤病风险调整因子"""
        base_risk = 0.05
        age_risk = 0.01 * max(0, age - 28)
        history_risk = 0.03 * player.get('major_injuries', 0)
        minutes_risk = 0.01 * max(0, player.get('minutes_avg', 30) - 32)

        total_risk = min(0.30, base_risk + age_risk + history_risk + minutes_risk)
        return 1 - total_risk

    def project_performance(self, player: Dict, years_ahead: int = 5) -> List[Dict]:
        """预测球员未来表现"""
        current_war = player['war']
        current_age = player['age']
        position = player['position']

        projections = []

        for year in range(1, years_ahead + 1):
            future_age = current_age + year

            # 年龄调整
            age_factor = self.age_adjustment_factor(current_age, future_age, position)

            # 伤病风险
            injury_factor = self.injury_risk_factor(player, future_age)

            # 预测WAR
            projected_war = current_war * age_factor * injury_factor

            # 置信区间
            uncertainty = 0.15 * year  # 越远越不确定
            lower_bound = projected_war * (1 - uncertainty)
            upper_bound = projected_war * (1 + uncertainty)

            projections.append({
                'year': 2025 + year,
                'age': future_age,
                'projected_war': round(projected_war, 2),
                'age_factor': round(age_factor, 3),
                'injury_factor': round(injury_factor, 3),
                'confidence_interval': (round(lower_bound, 2), round(upper_bound, 2)),
                'projected_value': round(projected_war * self.vpw, 0)
            })

        return projections

    def calculate_contract_npv(self, player: Dict, contract_years: int) -> Dict:
        """计算合同的净现值"""
        projections = self.project_performance(player, contract_years)

        npv = 0
        annual_values = []

        for i, proj in enumerate(projections):
            annual_value = proj['projected_war'] * self.vpw
            discounted_value = annual_value / (1 + self.discount_rate) ** (i + 1)
            npv += discounted_value
            annual_values.append({
                'year': proj['year'],
                'nominal_value': annual_value,
                'discounted_value': discounted_value
            })

        return {
            'total_npv': npv,
            'annual_breakdown': annual_values,
            'projections': projections,
            'average_annual_value': npv / contract_years if contract_years > 0 else 0
        }

    def recommend_contract(self, player: Dict, contract_years: int) -> Dict:
        """推荐合同条款"""
        npv_analysis = self.calculate_contract_npv(player, contract_years)
        avg_value = npv_analysis['average_annual_value']

        # WNBA薪资约束 (2024)
        supermax = 252450
        max_salary = 234936
        min_salary = 64154

        if avg_value > max_salary * 3:
            # 价值远超顶薪
            return {
                'contract_type': 'Supermax + Supplemental',
                'recommended_salary': supermax,
                'total_contract': supermax * contract_years,
                'value_captured': supermax * contract_years / npv_analysis['total_npv'],
                'note': 'Player worth significantly more than max. Consider equity sharing, marketing guarantees, or post-career opportunities.',
                'surplus_value': npv_analysis['total_npv'] - supermax * contract_years
            }
        elif avg_value > max_salary:
            return {
                'contract_type': 'Max Contract',
                'recommended_salary': max_salary,
                'total_contract': max_salary * contract_years,
                'value_captured': max_salary * contract_years / npv_analysis['total_npv'],
                'note': 'Offer max immediately. Player provides surplus value.',
                'surplus_value': npv_analysis['total_npv'] - max_salary * contract_years
            }
        elif avg_value > min_salary * 2:
            recommended = avg_value * 0.85  # 85% of value
            return {
                'contract_type': 'Market Value',
                'recommended_salary': min(recommended, max_salary),
                'total_contract': min(recommended, max_salary) * contract_years,
                'value_captured': min(recommended, max_salary) * contract_years / npv_analysis['total_npv'],
                'note': 'Standard negotiation. Offer 80-90% of calculated value.',
                'surplus_value': npv_analysis['total_npv'] - min(recommended, max_salary) * contract_years
            }
        else:
            return {
                'contract_type': 'Minimum or Near-Minimum',
                'recommended_salary': max(min_salary, avg_value * 0.9),
                'total_contract': max(min_salary, avg_value * 0.9) * contract_years,
                'value_captured': 1.0 if avg_value < min_salary else 0.9,
                'note': 'Role player. Keep costs low.',
                'surplus_value': max(0, npv_analysis['total_npv'] - min_salary * contract_years)
            }

    def full_analysis(self, player: Dict, contract_years: int = 4):
        """完整球员分析"""
        print("═" * 70)
        print(f"        PLAYER POTENTIAL ANALYSIS: {player['name']}")
        print("═" * 70)

        print(f"\n📊 CURRENT PROFILE:")
        print(f"   Age: {player['age']}")
        print(f"   Position: {player['position']}")
        print(f"   Current WAR: {player['war']}")
        print(f"   Current Value: ${player['war'] * self.vpw:,.0f}")

        projections = self.project_performance(player, contract_years)

        print(f"\n📈 {contract_years}-YEAR PROJECTION:")
        print(f"{'─' * 70}")
        print(f"{'Year':<8}{'Age':<6}{'Proj WAR':<12}{'Value':<15}{'Confidence':<20}")
        print(f"{'─' * 70}")

        for proj in projections:
            conf = f"({proj['confidence_interval'][0]:.1f} - {proj['confidence_interval'][1]:.1f})"
            print(f"{proj['year']:<8}{proj['age']:<6}{proj['projected_war']:<12.2f}"
                  f"${proj['projected_value']:>12,.0f}  {conf}")

        contract = self.recommend_contract(player, contract_years)

        print(f"\n{'─' * 70}")
        print(f"💰 CONTRACT RECOMMENDATION:")
        print(f"{'─' * 70}")
        print(f"   Type: {contract['contract_type']}")
        print(f"   Recommended Annual Salary: ${contract['recommended_salary']:,.0f}")
        print(f"   Total Contract Value: ${contract['total_contract']:,.0f}")
        print(f"   Surplus Value to Team: ${contract['surplus_value']:,.0f}")
        print(f"   Note: {contract['note']}")

        print("═" * 70)

        return {
            'projections': projections,
            'contract_recommendation': contract
        }


# 分析 Indiana Fever 核心球员
players = [
    {'name': 'Caitlin Clark', 'age': 23, 'position': 'G', 'war': 4.5, 'major_injuries': 0, 'minutes_avg': 35.8},
    {'name': 'Aliyah Boston', 'age': 23, 'position': 'F/C', 'war': 3.0, 'major_injuries': 0, 'minutes_avg': 32.0},
    {'name': 'Kelsey Mitchell', 'age': 29, 'position': 'G', 'war': 1.5, 'major_injuries': 1, 'minutes_avg': 30.0},
]

model = PlayerPotentialModel()

for player in players:
    model.full_analysis(player, contract_years=4)
    print("\n")