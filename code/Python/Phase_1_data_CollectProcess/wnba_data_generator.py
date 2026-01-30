"""
WNBA 模拟数据生成器 (2019-2024)
==============================
当无法访问网络时，使用此模块生成合理的模拟数据。
数据基于真实WNBA统计分布和历史趋势。

作者: MCM/ICM 2026 Team
日期: 2026-01-30
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional
from functools import reduce
from dataclasses import dataclass
import random
import string

# ============================================================================
# 配置常量
# ============================================================================

WNBA_TEAMS = {
    'ATL': {'name': 'Atlanta Dream', 'city': 'Atlanta', 'market_size': 6.2, 'arena_capacity': 4500},
    'CHI': {'name': 'Chicago Sky', 'city': 'Chicago', 'market_size': 9.5, 'arena_capacity': 6000},
    'CON': {'name': 'Connecticut Sun', 'city': 'Uncasville', 'market_size': 3.6, 'arena_capacity': 9518},
    'DAL': {'name': 'Dallas Wings', 'city': 'Dallas', 'market_size': 7.6, 'arena_capacity': 6000},
    'IND': {'name': 'Indiana Fever', 'city': 'Indianapolis', 'market_size': 4.5, 'arena_capacity': 17274},
    'LVA': {'name': 'Las Vegas Aces', 'city': 'Las Vegas', 'market_size': 2.3, 'arena_capacity': 12000},
    'LAX': {'name': 'Los Angeles Sparks', 'city': 'Los Angeles', 'market_size': 13.1, 'arena_capacity': 10161},
    'MIN': {'name': 'Minnesota Lynx', 'city': 'Minneapolis', 'market_size': 3.7, 'arena_capacity': 8400},
    'NYL': {'name': 'New York Liberty', 'city': 'New York', 'market_size': 20.3, 'arena_capacity': 17732},
    'PHO': {'name': 'Phoenix Mercury', 'city': 'Phoenix', 'market_size': 4.9, 'arena_capacity': 12000},
    'SEA': {'name': 'Seattle Storm', 'city': 'Seattle', 'market_size': 4.0, 'arena_capacity': 9000},
    'WAS': {'name': 'Washington Mystics', 'city': 'Washington DC', 'market_size': 6.3, 'arena_capacity': 4200},
}

SEASONS = [2019, 2020, 2021, 2022, 2023, 2024]

GAMES_PER_SEASON = {
    2019: 34, 2020: 22, 2021: 32, 2022: 36, 2023: 40, 2024: 40,
}

# 工资帽历史 (万美元)
SALARY_CAP = {
    2019: 107.3, 2020: 136.8, 2021: 136.8, 2022: 140.2, 2023: 143.9, 2024: 146.3,
}

# 位置分布
POSITIONS = ['G', 'G-F', 'F', 'F-C', 'C']
POSITION_WEIGHTS = [0.30, 0.15, 0.25, 0.15, 0.15]

# ============================================================================
# 核心明星球员数据 (基于真实数据)
# ============================================================================

STAR_PLAYERS = {
    # Indiana Fever 核心
    'Caitlin Clark': {
        'team': 'IND', 'pos': 'G', 'birth_year': 2002, 'draft_year': 2024,
        'base_stats': {'pts': 19.2, 'reb': 5.7, 'ast': 8.4, 'stl': 1.3, 'blk': 0.7, 'tov': 5.6},
        'fg_pct': 0.418, 'fg3_pct': 0.345, 'ft_pct': 0.907,
        'per': 19.5, 'bpm': 4.5, 'vorp': 2.4,
        'social_media': {'instagram': 5200000, 'twitter': 1500000},
        'jersey_rank': 1, 'marketability': 10.0,
    },
    'Aliyah Boston': {
        'team': 'IND', 'pos': 'F-C', 'birth_year': 2001, 'draft_year': 2023,
        'base_stats': {'pts': 14.3, 'reb': 8.9, 'ast': 2.4, 'stl': 1.0, 'blk': 1.2, 'tov': 1.6},
        'fg_pct': 0.478, 'fg3_pct': 0.250, 'ft_pct': 0.772,
        'per': 18.2, 'bpm': 2.5, 'vorp': 2.0,
        'social_media': {'instagram': 450000, 'twitter': 150000},
        'jersey_rank': 8, 'marketability': 7.5,
    },
    'Kelsey Mitchell': {
        'team': 'IND', 'pos': 'G', 'birth_year': 1995, 'draft_year': 2018,
        'base_stats': {'pts': 19.2, 'reb': 2.5, 'ast': 3.7, 'stl': 1.1, 'blk': 0.2, 'tov': 2.4},
        'fg_pct': 0.456, 'fg3_pct': 0.417, 'ft_pct': 0.894,
        'per': 17.8, 'bpm': 2.2, 'vorp': 1.8,
        'social_media': {'instagram': 85000, 'twitter': 25000},
        'jersey_rank': 25, 'marketability': 5.0,
    },
    'NaLyssa Smith': {
        'team': 'IND', 'pos': 'F', 'birth_year': 2000, 'draft_year': 2022,
        'base_stats': {'pts': 11.8, 'reb': 7.2, 'ast': 1.5, 'stl': 0.8, 'blk': 0.5, 'tov': 1.3},
        'fg_pct': 0.455, 'fg3_pct': 0.317, 'ft_pct': 0.755,
        'per': 14.5, 'bpm': 0.8, 'vorp': 1.2,
        'social_media': {'instagram': 65000, 'twitter': 18000},
        'jersey_rank': 35, 'marketability': 4.5,
    },
    # Las Vegas Aces 核心
    "A'ja Wilson": {
        'team': 'LVA', 'pos': 'F-C', 'birth_year': 1996, 'draft_year': 2018,
        'base_stats': {'pts': 26.9, 'reb': 11.9, 'ast': 2.6, 'stl': 1.8, 'blk': 2.6, 'tov': 1.7},
        'fg_pct': 0.527, 'fg3_pct': 0.325, 'ft_pct': 0.857,
        'per': 34.5, 'bpm': 12.5, 'vorp': 5.2,
        'social_media': {'instagram': 950000, 'twitter': 380000},
        'jersey_rank': 2, 'marketability': 9.5,
    },
    'Kelsey Plum': {
        'team': 'LVA', 'pos': 'G', 'birth_year': 1994, 'draft_year': 2017,
        'base_stats': {'pts': 17.8, 'reb': 2.8, 'ast': 4.5, 'stl': 1.0, 'blk': 0.3, 'tov': 2.3},
        'fg_pct': 0.445, 'fg3_pct': 0.385, 'ft_pct': 0.892,
        'per': 19.2, 'bpm': 3.5, 'vorp': 2.8,
        'social_media': {'instagram': 580000, 'twitter': 220000},
        'jersey_rank': 5, 'marketability': 8.0,
    },
    'Chelsea Gray': {
        'team': 'LVA', 'pos': 'G', 'birth_year': 1992, 'draft_year': 2014,
        'base_stats': {'pts': 15.5, 'reb': 2.9, 'ast': 6.8, 'stl': 0.9, 'blk': 0.2, 'tov': 2.1},
        'fg_pct': 0.465, 'fg3_pct': 0.350, 'ft_pct': 0.885,
        'per': 20.5, 'bpm': 4.8, 'vorp': 3.0,
        'social_media': {'instagram': 180000, 'twitter': 75000},
        'jersey_rank': 12, 'marketability': 6.5,
    },
    'Jackie Young': {
        'team': 'LVA', 'pos': 'G-F', 'birth_year': 1997, 'draft_year': 2019,
        'base_stats': {'pts': 16.8, 'reb': 5.0, 'ast': 4.6, 'stl': 1.3, 'blk': 0.5, 'tov': 2.2},
        'fg_pct': 0.498, 'fg3_pct': 0.345, 'ft_pct': 0.820,
        'per': 18.5, 'bpm': 3.0, 'vorp': 2.5,
        'social_media': {'instagram': 220000, 'twitter': 95000},
        'jersey_rank': 10, 'marketability': 7.0,
    },
    # New York Liberty
    'Breanna Stewart': {
        'team': 'NYL', 'pos': 'F', 'birth_year': 1994, 'draft_year': 2016,
        'base_stats': {'pts': 20.4, 'reb': 9.3, 'ast': 4.1, 'stl': 1.5, 'blk': 1.7, 'tov': 2.5},
        'fg_pct': 0.465, 'fg3_pct': 0.345, 'ft_pct': 0.895,
        'per': 27.5, 'bpm': 8.5, 'vorp': 4.2,
        'social_media': {'instagram': 680000, 'twitter': 285000},
        'jersey_rank': 3, 'marketability': 9.0,
    },
    'Sabrina Ionescu': {
        'team': 'NYL', 'pos': 'G', 'birth_year': 1997, 'draft_year': 2020,
        'base_stats': {'pts': 18.2, 'reb': 6.1, 'ast': 6.9, 'stl': 1.2, 'blk': 0.5, 'tov': 2.8},
        'fg_pct': 0.435, 'fg3_pct': 0.395, 'ft_pct': 0.910,
        'per': 21.5, 'bpm': 5.0, 'vorp': 3.5,
        'social_media': {'instagram': 890000, 'twitter': 420000},
        'jersey_rank': 4, 'marketability': 8.5,
    },
    # Chicago Sky
    'Angel Reese': {
        'team': 'CHI', 'pos': 'F', 'birth_year': 2002, 'draft_year': 2024,
        'base_stats': {'pts': 13.6, 'reb': 13.1, 'ast': 1.9, 'stl': 1.3, 'blk': 0.5, 'tov': 2.1},
        'fg_pct': 0.392, 'fg3_pct': 0.000, 'ft_pct': 0.739,
        'per': 16.8, 'bpm': 1.5, 'vorp': 1.5,
        'social_media': {'instagram': 3200000, 'twitter': 850000},
        'jersey_rank': 6, 'marketability': 9.5,
    },
    'Kahleah Copper': {
        'team': 'PHO', 'pos': 'G-F', 'birth_year': 1994, 'draft_year': 2016,
        'base_stats': {'pts': 21.5, 'reb': 4.0, 'ast': 2.8, 'stl': 1.5, 'blk': 0.8, 'tov': 2.0},
        'fg_pct': 0.455, 'fg3_pct': 0.345, 'ft_pct': 0.850,
        'per': 20.8, 'bpm': 4.2, 'vorp': 2.8,
        'social_media': {'instagram': 180000, 'twitter': 65000},
        'jersey_rank': 15, 'marketability': 6.0,
    },
    # Seattle Storm
    'Jewell Loyd': {
        'team': 'SEA', 'pos': 'G', 'birth_year': 1994, 'draft_year': 2015,
        'base_stats': {'pts': 19.7, 'reb': 3.9, 'ast': 4.4, 'stl': 1.1, 'blk': 0.5, 'tov': 2.5},
        'fg_pct': 0.420, 'fg3_pct': 0.365, 'ft_pct': 0.885,
        'per': 18.5, 'bpm': 3.2, 'vorp': 2.5,
        'social_media': {'instagram': 280000, 'twitter': 110000},
        'jersey_rank': 9, 'marketability': 7.0,
    },
    # Minnesota Lynx
    'Napheesa Collier': {
        'team': 'MIN', 'pos': 'F', 'birth_year': 1996, 'draft_year': 2019,
        'base_stats': {'pts': 20.4, 'reb': 9.7, 'ast': 3.4, 'stl': 1.9, 'blk': 1.4, 'tov': 2.3},
        'fg_pct': 0.485, 'fg3_pct': 0.375, 'ft_pct': 0.865,
        'per': 26.5, 'bpm': 7.5, 'vorp': 4.0,
        'social_media': {'instagram': 195000, 'twitter': 85000},
        'jersey_rank': 7, 'marketability': 7.5,
    },
    # Connecticut Sun
    'Alyssa Thomas': {
        'team': 'CON', 'pos': 'F', 'birth_year': 1992, 'draft_year': 2014,
        'base_stats': {'pts': 11.3, 'reb': 8.4, 'ast': 7.8, 'stl': 1.3, 'blk': 0.6, 'tov': 2.8},
        'fg_pct': 0.515, 'fg3_pct': 0.250, 'ft_pct': 0.655,
        'per': 20.2, 'bpm': 5.5, 'vorp': 3.2,
        'social_media': {'instagram': 125000, 'twitter': 55000},
        'jersey_rank': 18, 'marketability': 5.5,
    },
    'DeWanna Bonner': {
        'team': 'CON', 'pos': 'F', 'birth_year': 1987, 'draft_year': 2009,
        'base_stats': {'pts': 15.8, 'reb': 5.5, 'ast': 2.5, 'stl': 1.0, 'blk': 0.8, 'tov': 1.8},
        'fg_pct': 0.435, 'fg3_pct': 0.355, 'ft_pct': 0.825,
        'per': 17.5, 'bpm': 2.5, 'vorp': 2.0,
        'social_media': {'instagram': 95000, 'twitter': 45000},
        'jersey_rank': 22, 'marketability': 5.0,
    },
}

# 常用女性名字用于生成虚拟球员
FIRST_NAMES = [
    'Aaliyah', 'Brianna', 'Cameron', 'Deja', 'Erica', 'Feyonda', 'Grace', 'Haley',
    'Imani', 'Jasmine', 'Kalani', 'Lexie', 'Megan', 'Nia', 'Odyssey', 'Paris',
    'Quinn', 'Renee', 'Shyla', 'Tiffany', 'Unique', 'Victoria', 'Whitney', 'Ximena',
    'Yolanda', 'Zoe', 'Monique', 'Diamond', 'Crystal', 'Janelle', 'Kayla', 'Tierra',
    'Destinee', 'Kianna', 'Tiana', 'Azura', 'Bria', 'Cierra', 'Danielle', 'Elena',
]

LAST_NAMES = [
    'Adams', 'Brown', 'Carter', 'Davis', 'Evans', 'Foster', 'Green', 'Harris',
    'Irving', 'Jackson', 'King', 'Lewis', 'Moore', 'Nelson', 'Owens', 'Parker',
    'Quinn', 'Robinson', 'Smith', 'Taylor', 'Underwood', 'Vaughn', 'Williams', 'Xavier',
    'Young', 'Zhang', 'Johnson', 'Jones', 'Anderson', 'Thompson', 'White', 'Martin',
    'Garcia', 'Martinez', 'Robinson', 'Clark', 'Rodriguez', 'Lewis', 'Lee', 'Walker',
]


# ============================================================================
# 纯函数: 数据生成
# ============================================================================

def generate_player_id() -> str:
    """生成唯一球员ID"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))


def generate_random_name() -> str:
    """生成随机球员姓名"""
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"


def generate_random_stats(
    position: str,
    experience_years: int,
    is_starter: bool = False
) -> Dict:
    """
    生成随机球员统计数据
    
    Args:
        position: 球员位置
        experience_years: 经验年数
        is_starter: 是否首发
        
    Returns:
        统计数据字典
    """
    np.random.seed(None)
    
    # 基于位置的基础统计范围
    position_stats = {
        'G': {'pts': (8, 18), 'reb': (2, 4), 'ast': (3, 7), 'stl': (0.8, 1.8), 'blk': (0.1, 0.5)},
        'G-F': {'pts': (7, 16), 'reb': (3, 6), 'ast': (2, 5), 'stl': (0.7, 1.5), 'blk': (0.2, 0.8)},
        'F': {'pts': (8, 18), 'reb': (5, 10), 'ast': (1.5, 4), 'stl': (0.6, 1.4), 'blk': (0.4, 1.2)},
        'F-C': {'pts': (7, 16), 'reb': (6, 11), 'ast': (1, 3), 'stl': (0.5, 1.2), 'blk': (0.6, 1.8)},
        'C': {'pts': (6, 14), 'reb': (6, 12), 'ast': (0.8, 2.5), 'stl': (0.4, 1.0), 'blk': (0.8, 2.2)},
    }
    
    stats_range = position_stats.get(position, position_stats['F'])
    
    # 经验加成
    exp_bonus = 1 + (experience_years * 0.05)
    
    # 首发/替补差异
    starter_multiplier = 1.3 if is_starter else 0.7
    
    def gen_stat(stat_name: str) -> float:
        low, high = stats_range[stat_name]
        base = np.random.uniform(low, high)
        return round(base * exp_bonus * starter_multiplier * np.random.uniform(0.85, 1.15), 1)
    
    # 命中率基于位置
    fg_base = {'G': 0.40, 'G-F': 0.42, 'F': 0.44, 'F-C': 0.46, 'C': 0.48}
    fg3_base = {'G': 0.34, 'G-F': 0.32, 'F': 0.30, 'F-C': 0.28, 'C': 0.22}
    ft_base = {'G': 0.85, 'G-F': 0.82, 'F': 0.78, 'F-C': 0.75, 'C': 0.70}
    
    return {
        'pts': gen_stat('pts'),
        'reb': gen_stat('reb'),
        'ast': gen_stat('ast'),
        'stl': gen_stat('stl'),
        'blk': gen_stat('blk'),
        'tov': round(np.random.uniform(1.0, 3.5), 1),
        'fg_pct': round(fg_base.get(position, 0.43) + np.random.uniform(-0.05, 0.05), 3),
        'fg3_pct': round(fg3_base.get(position, 0.32) + np.random.uniform(-0.08, 0.08), 3),
        'ft_pct': round(ft_base.get(position, 0.80) + np.random.uniform(-0.10, 0.10), 3),
    }


def calculate_advanced_stats(
    basic_stats: Dict,
    minutes: float,
    games: int,
    season_games: int
) -> Dict:
    """
    计算高级统计数据
    
    Args:
        basic_stats: 基础统计
        minutes: 场均时间
        games: 出场数
        season_games: 赛季总场数
        
    Returns:
        高级统计字典
    """
    pts = basic_stats.get('pts', 0)
    reb = basic_stats.get('reb', 0)
    ast = basic_stats.get('ast', 0)
    stl = basic_stats.get('stl', 0)
    blk = basic_stats.get('blk', 0)
    tov = basic_stats.get('tov', 0)
    fg_pct = basic_stats.get('fg_pct', 0.40)
    
    # PER (Player Efficiency Rating) 简化计算
    per = ((pts + reb + ast + stl + blk) * 0.7 - tov * 0.5) * (40 / max(minutes, 1))
    per = max(0, min(40, per + np.random.uniform(-2, 2)))
    
    # BPM (Box Plus/Minus) 简化计算
    bpm = (per - 15) / 3 + np.random.uniform(-1, 1)
    
    # VORP (Value Over Replacement Player)
    vorp = bpm * (minutes / 40) * (games / season_games) * 2.7
    
    # WS (Win Shares) 简化
    ws = (per / 15) * (minutes * games / 2000) * np.random.uniform(0.8, 1.2)
    
    return {
        'per': round(per, 1),
        'ts_pct': round(fg_pct + np.random.uniform(0.03, 0.08), 3),
        'usg_pct': round(np.random.uniform(15, 30), 1),
        'bpm': round(bpm, 1),
        'vorp': round(vorp, 1),
        'ws': round(ws, 1),
        'ws_48': round(ws * 48 / max(minutes * games, 1) * 100, 3),
    }


def generate_salary(
    is_star: bool,
    experience_years: int,
    season: int,
    per: float
) -> float:
    """
    生成球员薪资
    
    Args:
        is_star: 是否明星球员
        experience_years: 经验年数
        season: 赛季
        per: 球员效率值
        
    Returns:
        薪资 (美元)
    """
    cap = SALARY_CAP.get(season, 140) * 10000  # 转换为美元
    
    if is_star:
        # 明星球员获得顶薪附近
        base = cap * np.random.uniform(0.18, 0.22)
    else:
        # 普通球员
        base = cap * np.random.uniform(0.03, 0.12)
    
    # 经验加成
    exp_bonus = 1 + (experience_years * 0.02)
    
    # PER加成
    per_bonus = 1 + ((per - 15) * 0.02)
    
    salary = base * exp_bonus * per_bonus
    
    # WNBA最低/最高薪资限制
    min_salary = 60000 + (season - 2019) * 5000
    max_salary = cap * 0.25
    
    return round(max(min_salary, min(max_salary, salary)), 0)


def generate_social_media(
    is_star: bool,
    marketability: float = 5.0
) -> Dict:
    """
    生成社交媒体数据
    
    Args:
        is_star: 是否明星球员
        marketability: 市场化指数 (1-10)
        
    Returns:
        社交媒体粉丝数字典
    """
    if is_star:
        instagram_base = marketability * 100000
        twitter_base = marketability * 30000
    else:
        instagram_base = np.random.uniform(5000, 50000)
        twitter_base = np.random.uniform(1000, 15000)
    
    return {
        'instagram': int(instagram_base * np.random.uniform(0.7, 1.3)),
        'twitter': int(twitter_base * np.random.uniform(0.7, 1.3)),
    }


# ============================================================================
# 生成完整球员数据
# ============================================================================

def generate_star_player_season(
    name: str,
    player_data: Dict,
    season: int
) -> Optional[Dict]:
    """
    生成明星球员单赛季数据
    
    Args:
        name: 球员姓名
        player_data: 球员基础数据
        season: 赛季
        
    Returns:
        赛季数据字典
    """
    draft_year = player_data.get('draft_year', 2015)
    
    # 检查球员是否在该赛季已在联盟
    if season < draft_year:
        return None
    
    experience = season - draft_year
    games_in_season = GAMES_PER_SEASON.get(season, 40)
    
    # 获取基础统计
    base_stats = player_data.get('base_stats', {})
    
    # 赛季变化 (早期逐年进步，后期略微下降)
    if experience <= 3:
        season_factor = 1 + (experience * 0.05)  # 新秀进步
    elif experience <= 7:
        season_factor = 1.15  # 巅峰期
    else:
        season_factor = 1.15 - ((experience - 7) * 0.02)  # 缓慢下降
    
    # 随机波动
    noise = np.random.uniform(0.92, 1.08)
    
    # 调整统计
    def adjust_stat(stat_val: float) -> float:
        return round(stat_val * season_factor * noise, 1)
    
    # 计算比赛数据
    games = int(games_in_season * np.random.uniform(0.85, 1.0))  # 可能缺席几场
    games_started = games if experience >= 1 else int(games * np.random.uniform(0.6, 0.9))
    minutes = round(np.random.uniform(28, 36), 1) if experience >= 1 else round(np.random.uniform(22, 30), 1)
    
    pts = adjust_stat(base_stats.get('pts', 10))
    reb = adjust_stat(base_stats.get('reb', 5))
    ast = adjust_stat(base_stats.get('ast', 3))
    stl = adjust_stat(base_stats.get('stl', 1))
    blk = adjust_stat(base_stats.get('blk', 0.5))
    tov = adjust_stat(base_stats.get('tov', 2))
    
    basic_stats_adj = {
        'pts': pts, 'reb': reb, 'ast': ast,
        'stl': stl, 'blk': blk, 'tov': tov,
        'fg_pct': player_data.get('fg_pct', 0.43) + np.random.uniform(-0.02, 0.02),
        'fg3_pct': player_data.get('fg3_pct', 0.33) + np.random.uniform(-0.03, 0.03),
        'ft_pct': player_data.get('ft_pct', 0.80) + np.random.uniform(-0.02, 0.02),
    }
    
    # 高级统计
    advanced = calculate_advanced_stats(basic_stats_adj, minutes, games, games_in_season)
    
    # 调整高级统计以匹配预设值
    per_base = player_data.get('per', 18)
    bpm_base = player_data.get('bpm', 2)
    vorp_base = player_data.get('vorp', 2)
    
    advanced['per'] = round(per_base * season_factor * noise, 1)
    advanced['bpm'] = round(bpm_base * season_factor * noise, 1)
    advanced['vorp'] = round(vorp_base * (games / games_in_season) * season_factor * noise, 1)
    
    # 薪资
    salary = generate_salary(True, experience, season, advanced['per'])
    
    # 社交媒体 (仅最新赛季有完整数据)
    social = player_data.get('social_media', {})
    if season < 2024:
        # 历史赛季社交媒体较少
        growth_factor = 0.5 + (season - 2019) * 0.1
        social = {
            'instagram': int(social.get('instagram', 100000) * growth_factor),
            'twitter': int(social.get('twitter', 50000) * growth_factor),
        }
    
    # 计算年龄
    birth_year = player_data.get('birth_year', 1995)
    age = season - birth_year
    
    return {
        'player_id': generate_player_id(),
        'player': name,
        'season': season,
        'team': player_data.get('team', 'UNK'),
        'pos': player_data.get('pos', 'F'),
        'age': age,
        'experience': experience,
        'games': games,
        'games_started': games_started,
        'min_per_game': minutes,
        'pts': pts,
        'reb': reb,
        'ast': ast,
        'stl': stl,
        'blk': blk,
        'tov': tov,
        'fg_pct': round(basic_stats_adj['fg_pct'], 3),
        'fg3_pct': round(basic_stats_adj['fg3_pct'], 3),
        'ft_pct': round(basic_stats_adj['ft_pct'], 3),
        **advanced,
        'salary': salary,
        'instagram_followers': social.get('instagram', 10000),
        'twitter_followers': social.get('twitter', 5000),
        'jersey_rank': player_data.get('jersey_rank', 50) if season == 2024 else 50,
        'marketability': player_data.get('marketability', 5.0) if season >= 2023 else 5.0,
        'is_star': True,
    }


def generate_role_player(
    team: str,
    season: int,
    roster_position: int
) -> Dict:
    """
    生成角色球员数据
    
    Args:
        team: 球队代码
        season: 赛季
        roster_position: 阵容位置 (1-15, 越小越重要)
        
    Returns:
        球员数据字典
    """
    name = generate_random_name()
    position = np.random.choice(POSITIONS, p=POSITION_WEIGHTS)
    
    # 经验年数
    experience = np.random.choice(range(0, 12), p=[
        0.15, 0.12, 0.12, 0.11, 0.10, 0.10, 0.08, 0.07, 0.06, 0.04, 0.03, 0.02
    ])
    
    birth_year = season - 22 - experience
    age = season - birth_year
    
    games_in_season = GAMES_PER_SEASON.get(season, 40)
    
    # 根据阵容位置决定是否首发
    is_starter = roster_position <= 5
    
    # 出场数据
    if is_starter:
        games = int(games_in_season * np.random.uniform(0.80, 0.95))
        games_started = int(games * np.random.uniform(0.8, 1.0))
        minutes = round(np.random.uniform(25, 34), 1)
    else:
        games = int(games_in_season * np.random.uniform(0.40, 0.85))
        games_started = int(games * np.random.uniform(0, 0.3))
        minutes = round(np.random.uniform(10, 24), 1)
    
    # 基础统计
    basic_stats = generate_random_stats(position, experience, is_starter)
    
    # 高级统计
    advanced = calculate_advanced_stats(basic_stats, minutes, games, games_in_season)
    
    # 薪资
    salary = generate_salary(False, experience, season, advanced['per'])
    
    # 社交媒体
    social = generate_social_media(False, np.random.uniform(3, 6))
    
    return {
        'player_id': generate_player_id(),
        'player': name,
        'season': season,
        'team': team,
        'pos': position,
        'age': age,
        'experience': experience,
        'games': games,
        'games_started': games_started,
        'min_per_game': minutes,
        **basic_stats,
        **advanced,
        'salary': salary,
        'instagram_followers': social['instagram'],
        'twitter_followers': social['twitter'],
        'jersey_rank': np.random.randint(30, 150),
        'marketability': round(np.random.uniform(2, 6), 1),
        'is_star': False,
    }


# ============================================================================
# 主生成函数
# ============================================================================

def generate_season_data(season: int, players_per_team: int = 12) -> List[Dict]:
    """
    生成单赛季完整数据
    
    Args:
        season: 赛季年份
        players_per_team: 每队球员数
        
    Returns:
        球员数据列表
    """
    all_players = []
    
    # 为每支球队生成数据
    for team_code, team_info in WNBA_TEAMS.items():
        team_players = []
        
        # 先添加该队的明星球员
        star_count = 0
        for name, data in STAR_PLAYERS.items():
            if data.get('team') == team_code:
                player = generate_star_player_season(name, data, season)
                if player:
                    team_players.append(player)
                    star_count += 1
        
        # 填充角色球员
        for i in range(players_per_team - star_count):
            roster_pos = star_count + i + 1
            player = generate_role_player(team_code, season, roster_pos)
            team_players.append(player)
        
        all_players.extend(team_players)
    
    return all_players


def generate_all_seasons_data(
    seasons: List[int] = SEASONS,
    players_per_team: int = 12
) -> pd.DataFrame:
    """
    生成所有赛季数据
    
    Args:
        seasons: 赛季列表
        players_per_team: 每队球员数
        
    Returns:
        完整数据DataFrame
    """
    all_data = []
    
    for season in seasons:
        print(f"生成 {season} 赛季数据...")
        season_data = generate_season_data(season, players_per_team)
        all_data.extend(season_data)
    
    df = pd.DataFrame(all_data)
    
    # 添加计算字段
    df['war'] = df.apply(lambda x: calculate_war_value(x), axis=1)
    df['performance_value'] = df['war'] * 300000
    df['commercial_value'] = df.apply(lambda x: calculate_commercial_value(x), axis=1)
    df['total_value'] = df['performance_value'] * 0.4 + df['commercial_value'] * 0.6
    
    return df


def calculate_war_value(row: pd.Series) -> float:
    """计算WAR值"""
    bpm = row.get('bpm', 0)
    mp = row.get('min_per_game', 0) * row.get('games', 0)
    season_games = GAMES_PER_SEASON.get(row.get('season', 2024), 40)
    
    war = (bpm + 2) * mp / (48 * season_games)
    return round(war, 2)


def calculate_commercial_value(row: pd.Series) -> float:
    """计算商业价值"""
    instagram = row.get('instagram_followers', 0)
    twitter = row.get('twitter_followers', 0)
    jersey_rank = row.get('jersey_rank', 50)
    marketability = row.get('marketability', 5)
    
    # 社交媒体价值: $0.10 per follower
    social_value = (instagram + twitter) * 0.10
    
    # 球衣销量价值
    jersey_value = max(0, (151 - jersey_rank) * 10000)
    
    # 市场化指数加成
    market_multiplier = 1 + (marketability - 5) * 0.2
    
    total = (social_value + jersey_value) * market_multiplier
    return round(total, 0)


# ============================================================================
# 生成球队和联盟数据
# ============================================================================

def generate_team_financials(season: int) -> List[Dict]:
    """
    生成球队财务数据
    
    Args:
        season: 赛季
        
    Returns:
        球队财务数据列表
    """
    financials = []
    
    # 基础估值增长趋势
    base_valuations = {
        2019: 50, 2020: 55, 2021: 60, 2022: 70, 2023: 90, 2024: 120,
    }
    base_val = base_valuations.get(season, 100)
    
    for team_code, team_info in WNBA_TEAMS.items():
        market_factor = team_info['market_size'] / 10
        capacity = team_info['arena_capacity']
        
        # 球队估值 (百万美元)
        valuation = base_val * market_factor * np.random.uniform(0.85, 1.15)
        
        # Indiana Fever 特殊处理 (Caitlin Clark效应)
        if team_code == 'IND' and season >= 2024:
            valuation *= 2.5
        
        # 收入
        games_played = GAMES_PER_SEASON.get(season, 40) // 2  # 主场比赛
        attendance_pct = np.random.uniform(0.65, 0.95)
        if team_code == 'IND' and season >= 2024:
            attendance_pct = 0.98  # Caitlin效应
        
        avg_ticket = 50 + (season - 2019) * 8 + market_factor * 10
        if team_code == 'IND' and season >= 2024:
            avg_ticket *= 1.5
        
        ticket_revenue = games_played * capacity * attendance_pct * avg_ticket / 1000000
        
        # 其他收入
        tv_revenue = base_val * 0.05 * market_factor
        sponsorship = base_val * 0.08 * market_factor
        merchandise = base_val * 0.03 * (1.5 if team_code == 'IND' and season >= 2024 else 1)
        
        total_revenue = ticket_revenue + tv_revenue + sponsorship + merchandise
        
        # 薪资支出
        payroll = SALARY_CAP.get(season, 140) * np.random.uniform(0.85, 1.0)
        
        financials.append({
            'team': team_code,
            'team_name': team_info['name'],
            'season': season,
            'valuation_millions': round(valuation, 1),
            'revenue_millions': round(total_revenue, 2),
            'ticket_revenue': round(ticket_revenue, 2),
            'tv_revenue': round(tv_revenue, 2),
            'sponsorship_revenue': round(sponsorship, 2),
            'merchandise_revenue': round(merchandise, 2),
            'payroll_millions': round(payroll / 100, 2),
            'attendance_avg': int(capacity * attendance_pct),
            'attendance_pct': round(attendance_pct * 100, 1),
            'avg_ticket_price': round(avg_ticket, 0),
            'arena_capacity': capacity,
            'market_size_millions': team_info['market_size'],
        })
    
    return financials


def generate_all_team_financials(seasons: List[int] = SEASONS) -> pd.DataFrame:
    """生成所有赛季球队财务数据"""
    all_data = []
    for season in seasons:
        all_data.extend(generate_team_financials(season))
    return pd.DataFrame(all_data)


# ============================================================================
# 导出函数
# ============================================================================

def export_complete_dataset(
    output_dir: str = './data',
    seasons: List[int] = SEASONS
) -> Dict[str, str]:
    """
    导出完整数据集
    
    Args:
        output_dir: 输出目录
        seasons: 赛季列表
        
    Returns:
        输出文件路径字典
    """
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    print("=" * 60)
    print("WNBA 数据生成系统启动")
    print(f"目标赛季: {seasons}")
    print("=" * 60)
    
    # 生成球员数据
    print("\n生成球员统计数据...")
    players_df = generate_all_seasons_data(seasons)
    print(f"总球员记录数: {len(players_df)}")
    
    # 生成球队财务数据
    print("\n生成球队财务数据...")
    financials_df = generate_all_team_financials(seasons)
    print(f"球队财务记录数: {len(financials_df)}")
    
    # 创建各种视图
    print("\n创建数据视图...")
    
    # Indiana Fever 专项
    fever_df = players_df[players_df['team'] == 'IND'].copy()
    
    # 明星球员
    stars_df = players_df[players_df['is_star'] == True].copy()
    
    # 每赛季Top20
    top_scorers = players_df.nlargest(100, 'pts')[['player', 'season', 'team', 'pts', 'reb', 'ast', 'per', 'war']]
    top_war = players_df.nlargest(100, 'war')[['player', 'season', 'team', 'war', 'bpm', 'vorp', 'per']]
    top_value = players_df.nlargest(100, 'total_value')[['player', 'season', 'team', 'total_value', 'performance_value', 'commercial_value', 'salary']]
    
    # 赛季汇总
    season_summary = players_df.groupby('season').agg({
        'player': 'count',
        'pts': 'mean',
        'reb': 'mean',
        'ast': 'mean',
        'salary': 'mean',
        'war': 'sum',
    }).round(2).reset_index()
    season_summary.columns = ['season', 'total_players', 'avg_pts', 'avg_reb', 'avg_ast', 'avg_salary', 'total_war']
    
    # 导出Excel
    print("\n导出Excel文件...")
    excel_path = f"{output_dir}/wnba_2019_2024_complete.xlsx"
    
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        players_df.to_excel(writer, sheet_name='All_Players', index=False)
        fever_df.to_excel(writer, sheet_name='Indiana_Fever', index=False)
        stars_df.to_excel(writer, sheet_name='Star_Players', index=False)
        financials_df.to_excel(writer, sheet_name='Team_Financials', index=False)
        season_summary.to_excel(writer, sheet_name='Season_Summary', index=False)
        top_scorers.to_excel(writer, sheet_name='Top_Scorers', index=False)
        top_war.to_excel(writer, sheet_name='Top_WAR', index=False)
        top_value.to_excel(writer, sheet_name='Top_Value', index=False)
        
        # 按赛季分表
        for season in seasons:
            df = players_df[players_df['season'] == season]
            df.to_excel(writer, sheet_name=f'Season_{season}', index=False)
    
    print(f"Excel已保存: {excel_path}")
    
    # 导出CSV
    csv_path = f"{output_dir}/wnba_players_all_seasons.csv"
    players_df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    print(f"CSV已保存: {csv_path}")
    
    fin_csv_path = f"{output_dir}/wnba_team_financials.csv"
    financials_df.to_csv(fin_csv_path, index=False, encoding='utf-8-sig')
    print(f"财务CSV已保存: {fin_csv_path}")
    
    print("\n" + "=" * 60)
    print("数据生成完成!")
    print(f"球员总数: {players_df['player'].nunique()}")
    print(f"总记录数: {len(players_df)}")
    print(f"赛季范围: {min(seasons)}-{max(seasons)}")
    print("=" * 60)
    
    return {
        'excel': excel_path,
        'players_csv': csv_path,
        'financials_csv': fin_csv_path,
    }


if __name__ == "__main__":
    export_complete_dataset()
