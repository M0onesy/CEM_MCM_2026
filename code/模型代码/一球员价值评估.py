import numpy as np
import pandas as pd


class PlayerValueModel:
    """双维度球员价值评估模型"""

    def __init__(self, value_per_win=300000, alpha=0.4):
        self.vpw = value_per_win
        self.alpha = alpha  # 表现价值权重
        self.replacement_bpm = -2.0
        self.games_per_season = 40
        self.minutes_per_game = 48

    def calculate_war(self, bpm, minutes_played):
        """计算WAR值"""
        war = ((bpm - self.replacement_bpm) * minutes_played) / \
              (self.minutes_per_game * self.games_per_season)
        return max(0, war)  # WAR不能为负

    def calculate_performance_value(self, player_stats):
        """计算表现价值"""
        bpm = player_stats.get('bpm', 0)
        mp = player_stats.get('minutes_played', 0)

        war = self.calculate_war(bpm, mp)
        return war * self.vpw

    def calculate_commercial_value(self, player_data, team_revenue):
        """计算商业价值"""
        # 市场影响力指数
        followers = (player_data.get('instagram', 0) +
                     player_data.get('twitter', 0) +
                     player_data.get('tiktok', 0))

        jersey_rank = player_data.get('jersey_rank', 100)
        rating_impact = player_data.get('rating_impact', 1.0)

        # 综合市场影响力
        market_index = (followers / 1000000 * 0.3 +
                        (100 - jersey_rank) / 100 * 0.3 +
                        (rating_impact - 1) * 0.4)

        # 收入归因（假设球队因明星效应增加的收入）
        revenue_uplift = team_revenue.get('uplift', 0)  # 明星带来的增量收入

        # 商业价值 = 市场影响力占比 × 增量收入
        return market_index * revenue_uplift

    def calculate_total_value(self, player_stats, player_commercial, team_revenue):
        """计算球员总价值"""
        v_perf = self.calculate_performance_value(player_stats)
        v_comm = self.calculate_commercial_value(player_commercial, team_revenue)

        v_total = self.alpha * v_perf + (1 - self.alpha) * v_comm

        return {
            'performance_value': v_perf,
            'commercial_value': v_comm,
            'total_value': v_total,
            'war': self.calculate_war(
                player_stats.get('bpm', 0),
                player_stats.get('minutes_played', 0)
            ),
            'perf_comm_ratio': v_perf / v_comm if v_comm > 0 else float('inf')
        }

    def evaluate_roster(self, roster_stats, roster_commercial, team_revenue):
        """评估整个阵容"""
        results = []

        for player_name in roster_stats.keys():
            stats = roster_stats[player_name]
            commercial = roster_commercial.get(player_name, {})

            value = self.calculate_total_value(stats, commercial, team_revenue)
            value['player'] = player_name
            results.append(value)

        df = pd.DataFrame(results)
        df = df.sort_values('total_value', ascending=False)

        return df


# Indiana Fever 示例应用
fever_players = {
    'Caitlin Clark': {
        'bpm': 4.5,
        'minutes_played': 1287,  # 35.8 min × 36 games
    },
    'Aliyah Boston': {
        'bpm': 2.8,
        'minutes_played': 1152,
    },
    'Kelsey Mitchell': {
        'bpm': 1.5,
        'minutes_played': 1080,
    },
    'NaLyssa Smith': {
        'bpm': 0.5,
        'minutes_played': 900,
    }
}

fever_commercial = {
    'Caitlin Clark': {
        'instagram': 5200000,
        'twitter': 1500000,
        'tiktok': 2000000,
        'jersey_rank': 1,
        'rating_impact': 3.0
    },
    'Aliyah Boston': {
        'instagram': 450000,
        'twitter': 150000,
        'tiktok': 200000,
        'jersey_rank': 8,
        'rating_impact': 1.2
    },
    'Kelsey Mitchell': {
        'instagram': 85000,
        'twitter': 25000,
        'tiktok': 30000,
        'jersey_rank': 35,
        'rating_impact': 1.0
    },
    'NaLyssa Smith': {
        'instagram': 100000,
        'twitter': 30000,
        'tiktok': 40000,
        'jersey_rank': 40,
        'rating_impact': 1.0
    }
}

team_revenue = {
    'total': 55000000,
    'baseline': 15000000,  # 无明星时的基准收入
    'uplift': 40000000  # Clark带来的增量
}

# 运行模型
model = PlayerValueModel(alpha=0.4)
roster_values = model.evaluate_roster(fever_players, fever_commercial, team_revenue)
print(roster_values)