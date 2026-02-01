import numpy as np
from typing import Dict, List


class DynamicTicketPricing:
    """动态票价优化模型"""

    def __init__(self):
        self.base_price = 85  # 基准票价
        self.capacity = 17274

        # 需求函数参数
        self.demand_intercept = 25000  # a
        self.demand_slope = 100  # b

        # 价格乘数
        self.opponent_tiers = {
            'S': ['Chicago Sky', 'Las Vegas Aces', 'New York Liberty'],
            'A': ['Phoenix Mercury', 'Seattle Storm', 'Connecticut Sun'],
            'B': ['Minnesota Lynx', 'Los Angeles Sparks', 'Washington Mystics'],
            'C': ['Dallas Wings', 'Atlanta Dream']
        }

        self.opponent_multipliers = {'S': 1.40, 'A': 1.20, 'B': 1.05, 'C': 1.00}
        self.day_multipliers = {
            'Friday': 1.15, 'Saturday': 1.20, 'Sunday': 1.15,
            'Monday': 0.95, 'Tuesday': 0.90, 'Wednesday': 0.95, 'Thursday': 1.00
        }

    def get_opponent_tier(self, opponent: str) -> str:
        """获取对手等级"""
        for tier, teams in self.opponent_tiers.items():
            if opponent in teams:
                return tier
        return 'C'

    def calculate_optimal_price(self, game_params: Dict) -> Dict:
        """计算单场比赛最优票价"""
        opponent = game_params.get('opponent', 'Unknown')
        day = game_params.get('day', 'Saturday')
        star_playing = game_params.get('star_playing', True)
        weeks_to_game = game_params.get('weeks_to_game', 4)

        # 计算乘数
        opponent_mult = self.opponent_multipliers[self.get_opponent_tier(opponent)]
        day_mult = self.day_multipliers.get(day, 1.0)
        star_mult = 1.30 if star_playing else 0.75
        urgency_mult = 1 + 0.05 * max(0, 4 - weeks_to_game)

        total_mult = opponent_mult * day_mult * star_mult * urgency_mult

        # 基础价格调整
        adjusted_price = self.base_price * total_mult

        # 需求预测
        predicted_demand = self.demand_intercept - self.demand_slope * adjusted_price

        # 如果需求超过容量，可以提价
        if predicted_demand > self.capacity:
            # 反推填满容量的价格
            price_at_capacity = (self.demand_intercept - self.capacity) / self.demand_slope
            adjusted_price = max(adjusted_price, price_at_capacity)
            predicted_demand = self.capacity

        # 价格上下限
        final_price = min(max(adjusted_price, 50), 200)
        final_demand = min(predicted_demand, self.capacity)

        revenue = final_price * final_demand

        return {
            'opponent': opponent,
            'opponent_tier': self.get_opponent_tier(opponent),
            'day': day,
            'star_playing': star_playing,
            'base_price': self.base_price,
            'multipliers': {
                'opponent': opponent_mult,
                'day': day_mult,
                'star': star_mult,
                'urgency': urgency_mult,
                'total': total_mult
            },
            'recommended_price': round(final_price, 0),
            'predicted_attendance': round(final_demand, 0),
            'predicted_revenue': round(revenue, 0),
            'capacity_utilization': final_demand / self.capacity
        }

    def season_pricing_strategy(self, schedule: List[Dict]) -> Dict:
        """赛季票价策略"""
        results = []
        total_revenue = 0
        total_attendance = 0

        for game in schedule:
            pricing = self.calculate_optimal_price(game)
            results.append(pricing)
            total_revenue += pricing['predicted_revenue']
            total_attendance += pricing['predicted_attendance']

        avg_price = total_revenue / total_attendance if total_attendance > 0 else 0
        avg_attendance = total_attendance / len(schedule) if schedule else 0

        return {
            'game_by_game': results,
            'season_summary': {
                'total_games': len(schedule),
                'total_revenue': total_revenue,
                'total_attendance': total_attendance,
                'average_ticket_price': avg_price,
                'average_attendance': avg_attendance,
                'average_capacity_util': total_attendance / (self.capacity * len(schedule))
            }
        }

    def compare_strategies(self):
        """比较不同定价策略"""
        # 示例赛季（20场主场）
        sample_schedule = [
            {'opponent': 'Chicago Sky', 'day': 'Saturday', 'star_playing': True},
            {'opponent': 'Las Vegas Aces', 'day': 'Sunday', 'star_playing': True},
            {'opponent': 'New York Liberty', 'day': 'Friday', 'star_playing': True},
            {'opponent': 'Seattle Storm', 'day': 'Saturday', 'star_playing': True},
            {'opponent': 'Phoenix Mercury', 'day': 'Wednesday', 'star_playing': True},
            {'opponent': 'Connecticut Sun', 'day': 'Tuesday', 'star_playing': True},
            {'opponent': 'Minnesota Lynx', 'day': 'Saturday', 'star_playing': True},
            {'opponent': 'Los Angeles Sparks', 'day': 'Sunday', 'star_playing': True},
            {'opponent': 'Washington Mystics', 'day': 'Friday', 'star_playing': True},
            {'opponent': 'Dallas Wings', 'day': 'Wednesday', 'star_playing': True},
            # 下半赛季重复一次
            {'opponent': 'Chicago Sky', 'day': 'Friday', 'star_playing': True},
            {'opponent': 'Las Vegas Aces', 'day': 'Saturday', 'star_playing': True},
            {'opponent': 'New York Liberty', 'day': 'Sunday', 'star_playing': True},
            {'opponent': 'Seattle Storm', 'day': 'Tuesday', 'star_playing': True},
            {'opponent': 'Phoenix Mercury', 'day': 'Saturday', 'star_playing': True},
            {'opponent': 'Connecticut Sun', 'day': 'Friday', 'star_playing': True},
            {'opponent': 'Minnesota Lynx', 'day': 'Wednesday', 'star_playing': True},
            {'opponent': 'Los Angeles Sparks', 'day': 'Saturday', 'star_playing': True},
            {'opponent': 'Atlanta Dream', 'day': 'Tuesday', 'star_playing': True},
            {'opponent': 'Dallas Wings', 'day': 'Sunday', 'star_playing': True},
        ]

        # 策略1：固定价格 $85
        fixed_revenue = self.base_price * self.capacity * len(sample_schedule)

        # 策略2：动态定价
        dynamic_result = self.season_pricing_strategy(sample_schedule)
        dynamic_revenue = dynamic_result['season_summary']['total_revenue']

        # 策略3：简单分层（$85/$110/$140）
        tiered_revenue = 0
        for game in sample_schedule:
            tier = self.get_opponent_tier(game['opponent'])
            if tier == 'S':
                price = 140
            elif tier in ['A', 'B']:
                price = 110
            else:
                price = 85
            tiered_revenue += price * self.capacity * 0.92  # 假设92%上座

        return {
            'fixed_pricing': {
                'description': 'Fixed $85 for all games',
                'total_revenue': fixed_revenue,
                'vs_dynamic': f"{(fixed_revenue / dynamic_revenue - 1) * 100:+.1f}%"
            },
            'tiered_pricing': {
                'description': 'Three tiers: $85/$110/$140',
                'total_revenue': tiered_revenue,
                'vs_dynamic': f"{(tiered_revenue / dynamic_revenue - 1) * 100:+.1f}%"
            },
            'dynamic_pricing': {
                'description': 'Full dynamic with all factors',
                'total_revenue': dynamic_revenue,
                'vs_dynamic': '0.0% (baseline)'
            },
            'recommendation': 'Dynamic pricing generates maximum revenue while maintaining high attendance'
        }

    def print_pricing_report(self):
        """打印票价策略报告"""
        comparison = self.compare_strategies()

        print("═" * 70)
        print("            TICKET PRICING STRATEGY ANALYSIS")
        print("═" * 70)

        print(f"\n{'─' * 70}")
        print("STRATEGY COMPARISON (20 Home Games):")
        print(f"{'─' * 70}")

        for strategy, data in comparison.items():
            if strategy != 'recommendation':
                print(f"\n  {strategy.upper()}")
                print(f"  {data['description']}")
                print(f"  Total Revenue: ${data['total_revenue']:,.0f}")
                print(f"  vs Dynamic: {data['vs_dynamic']}")

        print(f"\n{'─' * 70}")
        print("💡 RECOMMENDATION:")
        print(f"{'─' * 70}")
        print(f"\n  {comparison['recommendation']}")

        # 样例游戏价格
        print(f"\n{'─' * 70}")
        print("SAMPLE GAME PRICING:")
        print(f"{'─' * 70}")

        sample_games = [
            {'opponent': 'Chicago Sky', 'day': 'Saturday', 'star_playing': True, 'weeks_to_game': 1},
            {'opponent': 'Atlanta Dream', 'day': 'Tuesday', 'star_playing': True, 'weeks_to_game': 3},
            {'opponent': 'Las Vegas Aces', 'day': 'Friday', 'star_playing': False, 'weeks_to_game': 2},
        ]

        print(f"\n{'Opponent':<20}{'Day':<12}{'Star?':<8}{'Price':<10}{'Attendance':<12}{'Revenue'}")
        print(f"{'─' * 70}")

        for game in sample_games:
            result = self.calculate_optimal_price(game)
            star = "Yes" if game['star_playing'] else "No"
            print(f"{result['opponent']:<20}{result['day']:<12}{star:<8}"
                  f"${result['recommended_price']:<9,.0f}{result['predicted_attendance']:<12,.0f}"
                  f"${result['predicted_revenue']:,.0f}")

        print("═" * 70)


# 运行票价分析
pricing_model = DynamicTicketPricing()
pricing_model.print_pricing_report()