import numpy as np
from scipy.optimize import minimize_scalar
from dataclasses import dataclass
from typing import Dict


@dataclass
class CapitalStructureInputs:
    """资本结构输入参数"""
    team_value: float = 200000000  # 球队估值 $200M
    revenue: float = 55000000  # 年收入
    operating_income: float = 25000000  # 营业利润
    tax_rate: float = 0.21  # 公司税率
    risk_free_rate: float = 0.04  # 无风险利率
    market_premium: float = 0.06  # 市场风险溢价
    base_beta: float = 1.0  # 基础beta
    base_debt_rate: float = 0.06  # 基础债务利率


class CapitalStructureOptimizer:
    """资本结构优化模型"""

    def __init__(self, inputs: CapitalStructureInputs):
        self.inputs = inputs

    def calculate_cost_of_debt(self, debt_ratio: float) -> float:
        """计算债务成本（随杠杆增加而上升）"""
        # 风险利差随债务比率非线性增加
        spread = 0.02 * (debt_ratio / 0.3) ** 2
        return self.inputs.base_debt_rate + spread

    def calculate_cost_of_equity(self, debt_ratio: float) -> float:
        """计算股权成本（CAPM + 杠杆调整）"""
        # 杠杆beta
        leveraged_beta = self.inputs.base_beta * (1 + (1 - self.inputs.tax_rate) *
                                                  debt_ratio / (1 - debt_ratio + 0.001))

        # CAPM
        return self.inputs.risk_free_rate + leveraged_beta * self.inputs.market_premium

    def calculate_wacc(self, debt_ratio: float) -> float:
        """计算WACC"""
        if debt_ratio <= 0:
            return self.calculate_cost_of_equity(0)
        if debt_ratio >= 1:
            return float('inf')

        r_d = self.calculate_cost_of_debt(debt_ratio)
        r_e = self.calculate_cost_of_equity(debt_ratio)

        wacc = ((1 - debt_ratio) * r_e +
                debt_ratio * r_d * (1 - self.inputs.tax_rate))

        return wacc

    def find_optimal_structure(self) -> Dict:
        """寻找最优资本结构"""
        # 约束：债务比率在0-50%之间（体育行业保守）
        result = minimize_scalar(
            self.calculate_wacc,
            bounds=(0.05, 0.50),
            method='bounded'
        )

        optimal_ratio = result.x

        return {
            'optimal_debt_ratio': optimal_ratio,
            'optimal_debt_pct': f"{optimal_ratio:.1%}",
            'minimum_wacc': f"{result.fun:.2%}",
            'recommended_debt': self.inputs.team_value * optimal_ratio,
            'recommended_equity': self.inputs.team_value * (1 - optimal_ratio),
            'interest_coverage': self.inputs.operating_income / (
                    self.inputs.team_value * optimal_ratio *
                    self.calculate_cost_of_debt(optimal_ratio)
            ) if optimal_ratio > 0 else float('inf')
        }

    def scenario_analysis(self) -> Dict:
        """资本结构情景分析"""
        scenarios = {
            'conservative': {
                'debt_ratio': 0.15,
                'description': '保守策略：低杠杆，高灵活性'
            },
            'moderate': {
                'debt_ratio': 0.25,
                'description': '适度杠杆：平衡风险与收益'
            },
            'aggressive': {
                'debt_ratio': 0.40,
                'description': '激进策略：高杠杆，最大化税盾'
            }
        }

        results = {}
        for name, config in scenarios.items():
            ratio = config['debt_ratio']
            wacc = self.calculate_wacc(ratio)
            debt_amount = self.inputs.team_value * ratio
            interest = debt_amount * self.calculate_cost_of_debt(ratio)
            tax_shield = interest * self.inputs.tax_rate
            coverage = self.inputs.operating_income / interest if interest > 0 else float('inf')

            results[name] = {
                'description': config['description'],
                'debt_ratio': f"{ratio:.0%}",
                'debt_amount': f"${debt_amount / 1e6:.1f}M",
                'wacc': f"{wacc:.2%}",
                'annual_interest': f"${interest / 1e6:.2f}M",
                'tax_shield': f"${tax_shield / 1e6:.2f}M",
                'interest_coverage': f"{coverage:.1f}x",
                'financial_flexibility': 'High' if ratio < 0.2 else ('Medium' if ratio < 0.35 else 'Low'),
                'risk_level': 'Low' if coverage > 5 else ('Medium' if coverage > 3 else 'High')
            }

        return results

    def print_recommendation(self):
        """打印资本结构建议"""
        optimal = self.find_optimal_structure()
        scenarios = self.scenario_analysis()

        print("═" * 70)
        print("           CAPITAL STRUCTURE RECOMMENDATION")
        print("═" * 70)

        print(f"\n📊 OPTIMAL STRUCTURE (Theoretical):")
        print(f"   Debt Ratio: {optimal['optimal_debt_pct']}")
        print(f"   WACC: {optimal['minimum_wacc']}")
        print(f"   Recommended Debt: ${optimal['recommended_debt'] / 1e6:.1f}M")
        print(f"   Interest Coverage: {optimal['interest_coverage']:.1f}x")

        print(f"\n{'─' * 70}")
        print("SCENARIO COMPARISON:")
        print(f"{'─' * 70}")

        for name, data in scenarios.items():
            print(f"\n{name.upper()}: {data['description']}")
            print(f"   Debt: {data['debt_amount']} ({data['debt_ratio']})")
            print(f"   WACC: {data['wacc']}")
            print(f"   Tax Shield: {data['tax_shield']}/year")
            print(f"   Coverage: {data['interest_coverage']}")
            print(f"   Flexibility: {data['financial_flexibility']} | Risk: {data['risk_level']}")

        print(f"\n{'─' * 70}")
        print("💡 RECOMMENDATION FOR INDIANA FEVER:")
        print(f"{'─' * 70}")
        print("""
  Given the Fever's current situation:
  • Strong revenue growth (Clark effect)
  • High asset appreciation potential
  • CBA uncertainty

  RECOMMENDED: MODERATE LEVERAGE (20-25% D/V)

  Specific Actions:
  1. Secure $40-50M credit facility (not fully drawn)
  2. Use for: Arena improvements, marketing expansion
  3. Avoid: Long-term fixed obligations until new CBA clarity
  4. Maintain 4x+ interest coverage ratio
        """)
        print("═" * 70)


# 运行资本结构优化
inputs = CapitalStructureInputs(
    team_value=200000000,
    revenue=55000000,
    operating_income=25000000
)

optimizer = CapitalStructureOptimizer(inputs)
optimizer.print_recommendation()