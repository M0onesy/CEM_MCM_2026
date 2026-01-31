from dataclasses import dataclass
from typing import Dict, List, Callable, Any
from datetime import datetime
import numpy as np


@dataclass
class TeamState:
    """球队状态"""
    # 球队表现
    wins: int = 0
    losses: int = 0
    games_remaining: int = 40
    playoff_probability: float = 0.5

    # 财务状态
    revenue_ytd: float = 0
    revenue_growth: float = 0
    cap_space: float = 650000

    # 球员状态
    star_injured: bool = False
    injury_weeks: int = 0
    star_minutes_avg: float = 35.0

    # 外部因素
    new_cba_announced: bool = False
    expansion_announced: bool = False
    new_team_distance: float = 2000  # miles

    @property
    def win_pct(self):
        total = self.wins + self.losses
        return self.wins / total if total > 0 else 0.5


class DynamicDecisionEngine:
    """动态决策引擎"""

    def __init__(self, team_state: TeamState):
        self.state = team_state
        self.triggers = self._define_triggers()
        self.decision_log = []

    def _define_triggers(self) -> Dict:
        """定义所有决策触发器"""
        return {
            # ═══════════════════════════════════════════════════
            # 业务运营触发器
            # ═══════════════════════════════════════════════════
            'revenue_surge': {
                'condition': lambda s: s.revenue_growth > 0.30,
                'priority': 'HIGH',
                'category': 'BUSINESS',
                'actions': [
                    'Accelerate arena investment timeline',
                    'Increase marketing budget 20%',
                    'Explore premium pricing tiers',
                    'Lock in long-term sponsor deals'
                ],
                'leverage_adjustment': 'Increase debt capacity by 10%',
                'expected_impact': '+$5M revenue opportunity'
            },

            'revenue_decline': {
                'condition': lambda s: s.revenue_growth < -0.10,
                'priority': 'CRITICAL',
                'category': 'BUSINESS',
                'actions': [
                    'Cut non-essential expenses immediately',
                    'Delay all capital projects',
                    'Review sponsorship commitments',
                    'Implement cost control measures'
                ],
                'leverage_adjustment': 'Reduce debt by 15%, preserve cash',
                'expected_impact': 'Protect $3-5M in liquidity'
            },

            # ═══════════════════════════════════════════════════
            # 球队运营触发器
            # ═══════════════════════════════════════════════════
            'playoff_contention': {
                'condition': lambda s: s.win_pct > 0.60 and s.games_remaining < 15,
                'priority': 'HIGH',
                'category': 'BASKETBALL',
                'actions': [
                    'Activate trade deadline budget',
                    'Target rental players for playoff push',
                    'Increase rest for key players',
                    'Scout playoff opponents'
                ],
                'leverage_adjustment': 'Short-term debt acceptable for player acquisition',
                'expected_impact': '+15% championship probability'
            },

            'lottery_bound': {
                'condition': lambda s: s.win_pct < 0.35 and s.games_remaining < 20,
                'priority': 'MEDIUM',
                'category': 'BASKETBALL',
                'actions': [
                    'Shift to development mode',
                    'Increase young player minutes',
                    'Trade veterans for picks/prospects',
                    'Tank responsibly for draft position'
                ],
                'leverage_adjustment': 'Preserve cap space for future',
                'expected_impact': 'Better draft position, future flexibility'
            },

            'mediocre_middle': {
                'condition': lambda s: 0.40 <= s.win_pct <= 0.55 and s.games_remaining < 15,
                'priority': 'MEDIUM',
                'category': 'BASKETBALL',
                'actions': [
                    'Evaluate: push for playoffs or sell?',
                    'Assess trade market for veterans',
                    'Consider strategic losses for draft position'
                ],
                'leverage_adjustment': 'No change - evaluate options',
                'expected_impact': 'Avoid "stuck in the middle" trap'
            },

            # ═══════════════════════════════════════════════════
            # 伤病触发器
            # ═══════════════════════════════════════════════════
            'star_injury_minor': {
                'condition': lambda s: s.star_injured and s.injury_weeks <= 3,
                'priority': 'MEDIUM',
                'category': 'INJURY',
                'actions': [
                    'Activate depth players',
                    'Adjust rotation',
                    'Monitor recovery closely',
                    'Prepare contingency messaging'
                ],
                'leverage_adjustment': 'No change',
                'expected_impact': '2-3 games affected'
            },

            'star_injury_major': {
                'condition': lambda s: s.star_injured and s.injury_weeks > 6,
                'priority': 'CRITICAL',
                'category': 'INJURY',
                'actions': [
                    'File insurance claim immediately',
                    'Sign replacement player (hardship exception)',
                    'Adjust marketing messaging',
                    'Reassess season goals',
                    'Communicate with sponsors'
                ],
                'leverage_adjustment': 'Use insurance proceeds, maintain structure',
                'expected_impact': '$10-15M revenue at risk'
            },

            'star_overwork': {
                'condition': lambda s: not s.star_injured and s.star_minutes_avg > 34,
                'priority': 'HIGH',
                'category': 'INJURY',
                'actions': [
                    'Implement load management protocol',
                    'Rest star in back-to-backs',
                    'Monitor fatigue indicators',
                    'Develop backup options'
                ],
                'leverage_adjustment': 'Invest in depth players',
                'expected_impact': 'Reduce injury probability by 30%'
            },

            # ═══════════════════════════════════════════════════
            # 外部环境触发器
            # ═══════════════════════════════════════════════════
            'cba_change': {
                'condition': lambda s: s.new_cba_announced,
                'priority': 'CRITICAL',
                'category': 'EXTERNAL',
                'actions': [
                    'Recalculate all player values',
                    'Adjust long-term contract strategy',
                    'Reassess salary cap projections',
                    'Update financial models'
                ],
                'leverage_adjustment': 'Full capital structure review',
                'expected_impact': 'Potentially +/-50% on player costs'
            },

            'nearby_expansion': {
                'condition': lambda s: s.expansion_announced and s.new_team_distance < 500,
                'priority': 'HIGH',
                'category': 'EXTERNAL',
                'actions': [
                    'Lock in local sponsors immediately',
                    'Accelerate community programs',
                    'Review regional media rights',
                    'Strengthen youth basketball ties'
                ],
                'leverage_adjustment': 'Increase marketing investment 25%',
                'expected_impact': 'Defend 5-10% of market share'
            },

            'distant_expansion': {
                'condition': lambda s: s.expansion_announced and s.new_team_distance >= 500,
                'priority': 'LOW',
                'category': 'EXTERNAL',
                'actions': [
                    'Monitor but no immediate action',
                    'Potential new rivalry opportunity',
                    'League revenue share may increase'
                ],
                'leverage_adjustment': 'No change',
                'expected_impact': 'Minimal direct impact'
            }
        }

    def evaluate_all_triggers(self) -> List[Dict]:
        """评估所有触发条件"""
        activated = []

        for name, trigger in self.triggers.items():
            try:
                if trigger['condition'](self.state):
                    activated.append({
                        'trigger': name,
                        'priority': trigger['priority'],
                        'category': trigger['category'],
                        'actions': trigger['actions'],
                        'leverage': trigger['leverage_adjustment'],
                        'impact': trigger['expected_impact']
                    })
            except Exception as e:
                print(f"Error evaluating trigger {name}: {e}")
                continue

        # 按优先级排序
        priority_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
        activated.sort(key=lambda x: priority_order.get(x['priority'], 99))

        return activated

    def generate_decision_report(self) -> Dict:
        """生成决策报告"""
        activated = self.evaluate_all_triggers()

        report = {
            'timestamp': datetime.now().isoformat(),
            'current_state': {
                'record': f"{self.state.wins}-{self.state.losses}",
                'win_pct': f"{self.state.win_pct:.1%}",
                'games_remaining': self.state.games_remaining,
                'revenue_growth': f"{self.state.revenue_growth:.1%}",
                'star_status': 'Injured' if self.state.star_injured else 'Healthy'
            },
            'triggers_activated': len(activated),
            'critical_alerts': [t for t in activated if t['priority'] == 'CRITICAL'],
            'high_priority': [t for t in activated if t['priority'] == 'HIGH'],
            'all_recommendations': activated
        }

        # 汇总所有建议行动
        all_actions = []
        all_leverage = []
        for trigger in activated:
            all_actions.extend(trigger['actions'])
            all_leverage.append(trigger['leverage'])

        report['consolidated_actions'] = list(set(all_actions))
        report['leverage_adjustments'] = list(set(all_leverage))

        return report

    def print_dashboard(self):
        """打印决策仪表板"""
        report = self.generate_decision_report()

        print("═" * 70)
        print("           INDIANA FEVER DYNAMIC DECISION DASHBOARD")
        print("═" * 70)
        print(f"\nTimestamp: {report['timestamp']}")
        print(f"\nCurrent State:")
        for key, value in report['current_state'].items():
            print(f"  • {key}: {value}")

        print(f"\n{'─' * 70}")
        print(f"TRIGGERS ACTIVATED: {report['triggers_activated']}")
        print(f"{'─' * 70}")

        if report['critical_alerts']:
            print("\n🚨 CRITICAL ALERTS:")
            for alert in report['critical_alerts']:
                print(f"  [{alert['category']}] {alert['trigger'].upper()}")
                print(f"     Impact: {alert['impact']}")
                for action in alert['actions']:
                    print(f"     → {action}")

        if report['high_priority']:
            print("\n⚠️  HIGH PRIORITY:")
            for alert in report['high_priority']:
                print(f"  [{alert['category']}] {alert['trigger'].upper()}")
                for action in alert['actions']:
                    print(f"     → {action}")

        print(f"\n{'─' * 70}")
        print("CONSOLIDATED ACTION PLAN:")
        print(f"{'─' * 70}")
        for i, action in enumerate(report['consolidated_actions'][:10], 1):
            print(f"  {i}. {action}")

        print(f"\n{'─' * 70}")
        print("LEVERAGE ADJUSTMENTS:")
        print(f"{'─' * 70}")
        for adj in report['leverage_adjustments']:
            print(f"  • {adj}")

        print("═" * 70)


# 示例：测试不同情景
print("\n" + "=" * 70)
print("SCENARIO 1: Strong Season, Healthy Team")
print("=" * 70)
state1 = TeamState(
    wins=15, losses=10, games_remaining=15,
    revenue_growth=0.35, star_injured=False, star_minutes_avg=35.8
)
engine1 = DynamicDecisionEngine(state1)
engine1.print_dashboard()

print("\n" + "=" * 70)
print("SCENARIO 2: Star Injured Mid-Season")
print("=" * 70)
state2 = TeamState(
    wins=12, losses=15, games_remaining=13,
    revenue_growth=-0.05, star_injured=True, injury_weeks=8
)
engine2 = DynamicDecisionEngine(state2)
engine2.print_dashboard()

print("\n" + "=" * 70)
print("SCENARIO 3: Nearby Expansion Announced")
print("=" * 70)
state3 = TeamState(
    wins=18, losses=12, games_remaining=10,
    expansion_announced=True, new_team_distance=300
)
engine3 = DynamicDecisionEngine(state3)
engine3.print_dashboard()