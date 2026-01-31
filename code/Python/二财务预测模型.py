import numpy as np
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class FinancialInputs:
    """财务模型输入参数"""
    # 收入参数
    home_games: int = 20
    arena_capacity: int = 17274
    base_ticket_price: float = 85.0
    avg_attendance_rate: float = 0.95
    tv_revenue_national: float = 2500000
    tv_revenue_local: float = 4000000
    sponsorship_revenue: float = 10000000
    merchandise_revenue: float = 6000000
    other_revenue: float = 2000000

    # 成本参数
    payroll: float = 1300000
    operations: float = 8000000
    arena_costs: float = 5000000
    travel: float = 1500000
    marketing: float = 3000000
    other_costs: float = 2000000


class FinancialForecastModel:
    """财务预测模型"""

    def __init__(self, inputs: FinancialInputs):
        self.inputs = inputs

    def calculate_ticket_revenue(self, pricing_multipliers: List[float] = None):
        """计算门票收入"""
        if pricing_multipliers is None:
            pricing_multipliers = [1.0] * self.inputs.home_games

        total_revenue = 0
        for game_idx, multiplier in enumerate(pricing_multipliers):
            price = self.inputs.base_ticket_price * multiplier
            attendance = self.inputs.arena_capacity * self.inputs.avg_attendance_rate
            total_revenue += price * attendance

        return total_revenue

    def calculate_total_revenue(self, pricing_multipliers=None):
        """计算总收入"""
        ticket_rev = self.calculate_ticket_revenue(pricing_multipliers)

        total = (ticket_rev +
                 self.inputs.tv_revenue_national +
                 self.inputs.tv_revenue_local +
                 self.inputs.sponsorship_revenue +
                 self.inputs.merchandise_revenue +
                 self.inputs.other_revenue)

        return {
            'tickets': ticket_rev,
            'tv_national': self.inputs.tv_revenue_national,
            'tv_local': self.inputs.tv_revenue_local,
            'sponsorship': self.inputs.sponsorship_revenue,
            'merchandise': self.inputs.merchandise_revenue,
            'other': self.inputs.other_revenue,
            'total': total
        }

    def calculate_total_costs(self):
        """计算总成本"""
        total = (self.inputs.payroll +
                 self.inputs.operations +
                 self.inputs.arena_costs +
                 self.inputs.travel +
                 self.inputs.marketing +
                 self.inputs.other_costs)

        return {
            'payroll': self.inputs.payroll,
            'operations': self.inputs.operations,
            'arena': self.inputs.arena_costs,
            'travel': self.inputs.travel,
            'marketing': self.inputs.marketing,
            'other': self.inputs.other_costs,
            'total': total
        }

    def forecast_profit(self, pricing_multipliers=None):
        """预测利润"""
        revenue = self.calculate_total_revenue(pricing_multipliers)
        costs = self.calculate_total_costs()

        profit = revenue['total'] - costs['total']
        margin = profit / revenue['total'] * 100

        return {
            'revenue': revenue,
            'costs': costs,
            'profit': profit,
            'margin_pct': margin
        }

    def scenario_analysis(self):
        """情景分析"""
        scenarios = {}

        # 基准情景
        base = self.forecast_profit()
        scenarios['base'] = base

        # 乐观情景 (Clark MVP, 进总决赛)
        optimistic_inputs = FinancialInputs(
            avg_attendance_rate=0.99,
            base_ticket_price=95,
            sponsorship_revenue=15000000,
            merchandise_revenue=10000000,
            tv_revenue_local=6000000
        )
        opt_model = FinancialForecastModel(optimistic_inputs)
        scenarios['optimistic'] = opt_model.forecast_profit()

        # 悲观情景 (Clark受伤)
        pessimistic_inputs = FinancialInputs(
            avg_attendance_rate=0.70,
            base_ticket_price=70,
            sponsorship_revenue=6000000,
            merchandise_revenue=2000000,
            tv_revenue_local=2500000
        )
        pess_model = FinancialForecastModel(pessimistic_inputs)
        scenarios['pessimistic'] = pess_model.forecast_profit()

        return scenarios

    def sensitivity_analysis(self, variable: str, changes: List[float]):
        """敏感性分析"""
        results = []

        for change in changes:
            modified_inputs = FinancialInputs()
            current_value = getattr(modified_inputs, variable)
            setattr(modified_inputs, variable, current_value * (1 + change))

            model = FinancialForecastModel(modified_inputs)
            forecast = model.forecast_profit()

            results.append({
                'change_pct': change * 100,
                'new_value': current_value * (1 + change),
                'profit': forecast['profit'],
                'margin': forecast['margin_pct']
            })

        return results


# 运行财务预测
inputs = FinancialInputs()
model = FinancialForecastModel(inputs)

# 基准预测
forecast = model.forecast_profit()
print(f"Projected Revenue: ${forecast['revenue']['total']:,.0f}")
print(f"Projected Costs: ${forecast['costs']['total']:,.0f}")
print(f"Projected Profit: ${forecast['profit']:,.0f}")
print(f"Profit Margin: {forecast['margin_pct']:.1f}%")

# 情景分析
scenarios = model.scenario_analysis()
for name, result in scenarios.items():
    print(f"{name}: Profit = ${result['profit']:,.0f}")