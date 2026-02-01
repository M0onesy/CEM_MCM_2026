import numpy as np
from scipy.optimize import linprog, milp, LinearConstraint, Bounds
import pandas as pd


class RosterOptimizer:
    """阵容优化模型"""

    def __init__(self, salary_cap=1400000):
        self.salary_cap = salary_cap
        self.min_roster = 11
        self.max_roster = 12
        self.position_requirements = {
            'G': 3,  # 至少3名后卫
            'F': 3,  # 至少3名前锋
            'C': 2  # 至少2名中锋
        }

    def optimize_roster(self, available_players: pd.DataFrame,
                        core_players: List[str] = None):
        """
        优化阵容选择

        参数:
        - available_players: DataFrame with columns [name, position, salary, value]
        - core_players: 必须保留的球员名单
        """
        n = len(available_players)

        # 目标函数：最大化总价值（转换为最小化负价值）
        c = -available_players['value'].values

        # 构建约束矩阵
        constraints = []

        # 1. 薪资帽约束: sum(salary * x) <= cap
        A_salary = available_players['salary'].values.reshape(1, -1)
        constraints.append(LinearConstraint(A_salary, -np.inf, self.salary_cap))

        # 2. 阵容规模约束: min <= sum(x) <= max
        A_roster = np.ones((1, n))
        constraints.append(LinearConstraint(A_roster, self.min_roster, self.max_roster))

        # 3. 位置约束
        for pos, req in self.position_requirements.items():
            A_pos = (available_players['position'].str.contains(pos)).astype(int).values.reshape(1, -1)
            constraints.append(LinearConstraint(A_pos, req, np.inf))

        # 4. 核心球员约束
        if core_players:
            for player in core_players:
                idx = available_players[available_players['name'] == player].index[0]
                A_core = np.zeros((1, n))
                A_core[0, idx] = 1
                constraints.append(LinearConstraint(A_core, 1, 1))

        # 变量边界：二进制变量
        bounds = Bounds(0, 1)
        integrality = np.ones(n)  # 所有变量为整数

        # 求解
        result = milp(c, constraints=constraints, bounds=bounds, integrality=integrality)

        if result.success:
            selected = available_players[result.x > 0.5].copy()
            return {
                'success': True,
                'roster': selected,
                'total_value': -result.fun,
                'total_salary': selected['salary'].sum(),
                'cap_space': self.salary_cap - selected['salary'].sum()
            }
        else:
            return {'success': False, 'message': result.message}

    def evaluate_trade(self, current_roster, outgoing, incoming):
        """评估交易"""
        # 移除交易出去的球员
        new_roster = current_roster[~current_roster['name'].isin(outgoing)].copy()

        # 添加交易进来的球员
        new_roster = pd.concat([new_roster, incoming], ignore_index=True)

        # 计算变化
        old_value = current_roster['value'].sum()
        new_value = new_roster['value'].sum()

        old_salary = current_roster['salary'].sum()
        new_salary = new_roster['salary'].sum()

        return {
            'value_change': new_value - old_value,
            'salary_change': new_salary - old_salary,
            'new_cap_space': self.salary_cap - new_salary,
            'recommendation': 'APPROVE' if new_value > old_value and new_salary <= self.salary_cap else 'REJECT'
        }

    def draft_value_analysis(self, draft_position, player_projections):
        """选秀价值分析"""
        # 历史数据：选秀位置与预期WAR的关系
        expected_war_by_pick = {
            1: 2.5, 2: 2.0, 3: 1.7, 4: 1.5, 5: 1.3,
            6: 1.1, 7: 1.0, 8: 0.9, 9: 0.8, 10: 0.7,
            11: 0.6, 12: 0.5
        }

        expected_war = expected_war_by_pick.get(draft_position, 0.3)
        rookie_salary = 76535  # 2024年首轮秀基础工资

        expected_value = expected_war * 300000
        cost_efficiency = expected_value / rookie_salary

        return {
            'pick': draft_position,
            'expected_war': expected_war,
            'expected_value': expected_value,
            'salary': rookie_salary,
            'value_per_dollar': cost_efficiency,
            'recommendation': player_projections.get(draft_position, 'BPA')
        }


# 示例：Indiana Fever阵容优化
available_players = pd.DataFrame({
    'name': ['Caitlin Clark', 'Aliyah Boston', 'Kelsey Mitchell', 'NaLyssa Smith',
             'Lexie Hull', 'Kristy Wallace', 'Katie Lou Samuelson', 'Temi Fagbenle',
             'Free Agent A', 'Free Agent B', 'Free Agent C'],
    'position': ['G', 'F/C', 'G', 'F', 'G', 'G', 'G/F', 'C', 'C', 'G', 'F'],
    'salary': [76535, 205000, 190000, 150000, 75000, 70000, 100000, 180000,
               200000, 120000, 150000],
    'value': [9840000, 1440000, 390000, 272000, 150000, 100000, 180000, 250000,
              400000, 200000, 220000]
})

optimizer = RosterOptimizer()
core = ['Caitlin Clark', 'Aliyah Boston', 'Kelsey Mitchell']
result = optimizer.optimize_roster(available_players, core)

if result['success']:
    print("Optimal Roster:")
    print(result['roster'][['name', 'position', 'salary', 'value']])
    print(f"\nTotal Value: ${result['total_value']:,.0f}")
    print(f"Total Salary: ${result['total_salary']:,.0f}")
    print(f"Cap Space Remaining: ${result['cap_space']:,.0f}")