import numpy as np
from math import radians, sin, cos, sqrt, atan2
from typing import Dict, List, Tuple


class GeographicCompetitionModel:
    """地理竞争模型"""

    def __init__(self):
        # WNBA现有球队
        self.current_teams = {
            'IND': {'city': 'Indianapolis', 'coords': (39.7684, -86.1581), 'market_pop': 2.1},
            'CHI': {'city': 'Chicago', 'coords': (41.8781, -87.6298), 'market_pop': 9.5},
            'NYL': {'city': 'New York', 'coords': (40.7128, -74.0060), 'market_pop': 20.3},
            'LVA': {'city': 'Las Vegas', 'coords': (36.1699, -115.1398), 'market_pop': 2.3},
            'PHO': {'city': 'Phoenix', 'coords': (33.4484, -112.0740), 'market_pop': 4.9},
            'SEA': {'city': 'Seattle', 'coords': (47.6062, -122.3321), 'market_pop': 4.0},
            'MIN': {'city': 'Minneapolis', 'coords': (44.9778, -93.2650), 'market_pop': 3.7},
            'LAX': {'city': 'Los Angeles', 'coords': (34.0522, -118.2437), 'market_pop': 13.1},
            'ATL': {'city': 'Atlanta', 'coords': (33.7490, -84.3880), 'market_pop': 6.2},
            'CON': {'city': 'Uncasville', 'coords': (41.4340, -72.1187), 'market_pop': 3.6},
            'WAS': {'city': 'Washington', 'coords': (38.9072, -77.0369), 'market_pop': 6.3},
            'DAL': {'city': 'Dallas', 'coords': (32.7767, -96.7970), 'market_pop': 7.6},
        }

        # 已确认和潜在扩张城市
        self.expansion_cities = {
            'GSW': {'city': 'San Francisco', 'coords': (37.7749, -122.4194), 'market_pop': 4.7,
                    'status': 'Confirmed 2025'},
            'TOR': {'city': 'Toronto', 'coords': (43.6532, -79.3832), 'market_pop': 6.5, 'status': 'Confirmed 2026'},
            'DET': {'city': 'Detroit', 'coords': (42.3314, -83.0458), 'market_pop': 4.3, 'status': 'Potential'},
            'CLE': {'city': 'Cleveland', 'coords': (41.4993, -81.6944), 'market_pop': 2.0, 'status': 'Potential'},
            'CIN': {'city': 'Cincinnati', 'coords': (39.1031, -84.5120), 'market_pop': 2.2, 'status': 'Potential'},
            'MIA': {'city': 'Miami', 'coords': (25.7617, -80.1918), 'market_pop': 6.2, 'status': 'Potential'},
            'DEN': {'city': 'Denver', 'coords': (39.7392, -104.9903), 'market_pop': 2.9, 'status': 'Potential'},
            'POR': {'city': 'Portland', 'coords': (45.5152, -122.6784), 'market_pop': 2.5, 'status': 'Potential'},
            'KCY': {'city': 'Kansas City', 'coords': (39.0997, -94.5786), 'market_pop': 2.2, 'status': 'Potential'},
        }

        self.distance_decay = 0.003  # 衰减系数
        self.revenue_impact_factor = 0.15  # 重叠人口的收入影响系数

    def haversine_distance(self, coord1: Tuple, coord2: Tuple) -> float:
        """计算两点间距离（公里）"""
        R = 6371  # 地球半径

        lat1, lon1 = radians(coord1[0]), radians(coord1[1])
        lat2, lon2 = radians(coord2[0]), radians(coord2[1])

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        return R * c

    def calculate_market_overlap(self, team1_code: str, team2_code: str) -> Dict:
        """计算两队市场重叠"""
        # 获取球队信息
        team1 = self.current_teams.get(team1_code)
        team2 = self.current_teams.get(team2_code) or self.expansion_cities.get(team2_code)

        if not team1 or not team2:
            return None

        # 计算距离
        distance_km = self.haversine_distance(team1['coords'], team2['coords'])
        distance_miles = distance_km * 0.621371

        # 计算重叠因子
        overlap_factor = np.exp(-self.distance_decay * distance_km)

        # 重叠人口
        overlap_pop = min(team1['market_pop'], team2['market_pop']) * overlap_factor

        # 收入影响估算
        revenue_impact_pct = -overlap_pop / team1['market_pop'] * self.revenue_impact_factor

        return {
            'team1': team1_code,
            'team2': team2_code,
            'distance_km': round(distance_km, 0),
            'distance_miles': round(distance_miles, 0),
            'overlap_factor': round(overlap_factor, 4),
            'overlap_population_M': round(overlap_pop, 2),
            'revenue_impact_pct': round(revenue_impact_pct * 100, 2)
        }

    def classify_threat_level(self, distance_miles: float) -> str:
        """分类威胁等级"""
        if distance_miles < 200:
            return 'CRITICAL'
        elif distance_miles < 400:
            return 'HIGH'
        elif distance_miles < 700:
            return 'MODERATE'
        else:
            return 'LOW'

    def analyze_expansion_impact(self, incumbent_team: str = 'IND') -> Dict:
        """分析所有扩张对指定球队的影响"""
        impacts = {}

        for exp_code, exp_info in self.expansion_cities.items():
            overlap = self.calculate_market_overlap(incumbent_team, exp_code)

            if overlap:
                threat_level = self.classify_threat_level(overlap['distance_miles'])

                # 生成建议
                if threat_level == 'CRITICAL':
                    recommendation = f"URGENT: Aggressively defend market. Lock sponsors, increase community presence, consider lobbying against {exp_info['city']} expansion."
                elif threat_level == 'HIGH':
                    recommendation = f"ACTION NEEDED: Strengthen local ties before {exp_info['city']} enters. Secure long-term sponsor deals."
                elif threat_level == 'MODERATE':
                    recommendation = f"MONITOR: {exp_info['city']} may create beneficial rivalry. Prepare for increased regional competition."
                else:
                    recommendation = f"MINIMAL CONCERN: {exp_info['city']} too distant for significant impact. May increase league revenue share."

                impacts[exp_code] = {
                    'city': exp_info['city'],
                    'status': exp_info['status'],
                    'distance_miles': overlap['distance_miles'],
                    'threat_level': threat_level,
                    'revenue_impact_pct': overlap['revenue_impact_pct'],
                    'overlap_population_M': overlap['overlap_population_M'],
                    'recommendation': recommendation
                }

        # 排序：最威胁的在前
        threat_order = {'CRITICAL': 0, 'HIGH': 1, 'MODERATE': 2, 'LOW': 3}
        sorted_impacts = dict(sorted(impacts.items(),
                                     key=lambda x: (threat_order[x[1]['threat_level']],
                                                    -x[1]['revenue_impact_pct'])))

        return sorted_impacts

    def optimal_expansion_analysis(self, my_team: str = 'IND') -> Dict:
        """从我方球队角度，哪些扩张位置最有利/不利"""
        impacts = self.analyze_expansion_impact(my_team)

        # 分类
        harmful = {k: v for k, v in impacts.items() if v['threat_level'] in ['CRITICAL', 'HIGH']}
        neutral = {k: v for k, v in impacts.items() if v['threat_level'] == 'MODERATE'}
        beneficial = {k: v for k, v in impacts.items() if v['threat_level'] == 'LOW'}

        return {
            'most_harmful': harmful,
            'neutral': neutral,
            'least_harmful': beneficial,
            'summary': {
                'worst_case': list(harmful.keys())[:3] if harmful else [],
                'best_case': list(beneficial.keys())[:3] if beneficial else [],
                'total_risk_if_all_harmful': sum(v['revenue_impact_pct'] for v in harmful.values())
            }
        }

    def print_expansion_report(self, my_team: str = 'IND'):
        """打印扩张影响报告"""
        impacts = self.analyze_expansion_impact(my_team)
        analysis = self.optimal_expansion_analysis(my_team)

        print("═" * 70)
        print(f"       EXPANSION IMPACT ANALYSIS: {self.current_teams[my_team]['city'].upper()}")
        print("═" * 70)

        print(f"\n{'─' * 70}")
        print("ALL POTENTIAL EXPANSION CITIES:")
        print(f"{'─' * 70}")
        print(f"{'City':<15}{'Status':<18}{'Distance':<12}{'Threat':<12}{'Revenue':<10}")
        print(f"{'─' * 70}")

        for code, data in impacts.items():
            status = data['status'][:15]
            print(f"{data['city']:<15}{status:<18}{data['distance_miles']:<12.0f}"
                  f"{data['threat_level']:<12}{data['revenue_impact_pct']:>+.1f}%")

        print(f"\n{'─' * 70}")
        print("🚨 CRITICAL/HIGH THREAT EXPANSIONS:")
        print(f"{'─' * 70}")

        for code, data in analysis['most_harmful'].items():
            print(f"\n  {data['city']} ({code})")
            print(f"  Distance: {data['distance_miles']:.0f} miles | Impact: {data['revenue_impact_pct']:+.1f}%")
            print(f"  → {data['recommendation']}")

        if analysis['least_harmful']:
            print(f"\n{'─' * 70}")
            print("✅ BENEFICIAL/LOW-IMPACT EXPANSIONS:")
            print(f"{'─' * 70}")

            for code, data in list(analysis['least_harmful'].items())[:3]:
                print(f"\n  {data['city']} ({code})")
                print(f"  Distance: {data['distance_miles']:.0f} miles | Impact: {data['revenue_impact_pct']:+.1f}%")
                print(f"  → {data['recommendation']}")

        print(f"\n{'─' * 70}")
        print("📋 STRATEGIC SUMMARY:")
        print(f"{'─' * 70}")
        print(f"""
  WORST-CASE expansions for {self.current_teams[my_team]['city']}:
  {', '.join([impacts[c]['city'] for c in analysis['summary']['worst_case']]) or 'None identified'}

  BEST-CASE expansions for {self.current_teams[my_team]['city']}:
  {', '.join([impacts[c]['city'] for c in analysis['summary']['best_case']]) or 'None identified'}

  Total Revenue Risk (if all harmful cities expand): {analysis['summary']['total_risk_if_all_harmful']:.1f}%

  KEY RECOMMENDATION:
  The Fever should actively lobby for West Coast/South expansions
  and oppose any Midwest expansion (Detroit, Cleveland, Cincinnati).
        """)
        print("═" * 70)


# 运行地理竞争分析
model = GeographicCompetitionModel()
model.print_expansion_report('IND')