"""
WNBA多年数据收集系统 (2019-2024)
===============================
本模块提供完整的WNBA数据爬虫和处理功能，采用函数式编程风格。

数据来源:
- Basketball-Reference (https://www.basketball-reference.com/wnba/)
- Her Hoop Stats (https://herhoopstats.com/)
- Spotrac (https://www.spotrac.com/wnba/)

作者: MCM/ICM 2026 Team
日期: 2026-01-30
"""

import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Tuple, Optional, Callable
from functools import reduce, partial
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import time
import logging
import json
import os

# ============================================================================
# 配置常量
# ============================================================================

WNBA_TEAMS = {
    'ATL': {'name': 'Atlanta Dream', 'city': 'Atlanta', 'founded': 2008},
    'CHI': {'name': 'Chicago Sky', 'city': 'Chicago', 'founded': 2006},
    'CON': {'name': 'Connecticut Sun', 'city': 'Uncasville', 'founded': 2003},
    'DAL': {'name': 'Dallas Wings', 'city': 'Dallas', 'founded': 2016},
    'IND': {'name': 'Indiana Fever', 'city': 'Indianapolis', 'founded': 2000},
    'LVA': {'name': 'Las Vegas Aces', 'city': 'Las Vegas', 'founded': 2018},
    'LAX': {'name': 'Los Angeles Sparks', 'city': 'Los Angeles', 'founded': 1997},
    'MIN': {'name': 'Minnesota Lynx', 'city': 'Minneapolis', 'founded': 1999},
    'NYL': {'name': 'New York Liberty', 'city': 'New York', 'founded': 1997},
    'PHO': {'name': 'Phoenix Mercury', 'city': 'Phoenix', 'founded': 1997},
    'SEA': {'name': 'Seattle Storm', 'city': 'Seattle', 'founded': 2000},
    'WAS': {'name': 'Washington Mystics', 'city': 'Washington DC', 'founded': 1998},
}

SEASONS = [2019, 2020, 2021, 2022, 2023, 2024]

# 2020赛季因COVID缩短为22场
GAMES_PER_SEASON = {
    2019: 34,
    2020: 22,  # COVID shortened
    2021: 32,
    2022: 36,
    2023: 40,
    2024: 40,
}

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# 数据类定义
# ============================================================================

@dataclass
class PlayerStats:
    """球员统计数据结构"""
    player_id: str
    name: str
    team: str
    season: int
    position: str
    age: int
    games: int
    games_started: int
    minutes_per_game: float
    points: float
    rebounds: float
    assists: float
    steals: float
    blocks: float
    turnovers: float
    fg_pct: float
    fg3_pct: float
    ft_pct: float
    per: float
    bpm: float
    vorp: float
    ws: float


@dataclass
class TeamFinancials:
    """球队财务数据结构"""
    team: str
    season: int
    valuation: float
    revenue: float
    payroll: float
    attendance_avg: float
    ticket_price_avg: float


# ============================================================================
# 纯函数: 网络请求
# ============================================================================

def fetch_page(url: str, delay: float = 1.0) -> Optional[str]:
    """
    获取网页内容（带延迟防止被封）
    
    Args:
        url: 目标URL
        delay: 请求延迟（秒）
        
    Returns:
        网页HTML内容，失败返回None
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    try:
        time.sleep(delay)
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.text
    except Exception as e:
        logger.error(f"获取页面失败 {url}: {e}")
        return None


def parse_html(html: str) -> BeautifulSoup:
    """解析HTML为BeautifulSoup对象"""
    return BeautifulSoup(html, 'html.parser')


# ============================================================================
# 纯函数: Basketball-Reference 爬虫
# ============================================================================

def build_bbref_url(season: int, stat_type: str = 'per_game') -> str:
    """
    构建Basketball-Reference URL
    
    Args:
        season: 赛季年份
        stat_type: 统计类型 ('per_game', 'totals', 'advanced')
        
    Returns:
        完整URL
    """
    base_url = "https://www.basketball-reference.com/wnba"
    return f"{base_url}/years/{season}_{stat_type}.html"


def extract_player_row(row, season: int) -> Optional[Dict]:
    """
    从表格行提取球员数据
    
    Args:
        row: BeautifulSoup的tr元素
        season: 赛季年份
        
    Returns:
        球员数据字典
    """
    try:
        cells = row.find_all(['th', 'td'])
        if len(cells) < 10:
            return None
            
        # 提取数据
        player_name = cells[0].get_text(strip=True)
        if player_name == 'Player' or not player_name:
            return None
            
        def safe_float(val, default=0.0):
            try:
                return float(val) if val else default
            except:
                return default
                
        def safe_int(val, default=0):
            try:
                return int(val) if val else default
            except:
                return default
        
        return {
            'player': player_name,
            'season': season,
            'pos': cells[1].get_text(strip=True) if len(cells) > 1 else '',
            'age': safe_int(cells[2].get_text(strip=True)),
            'team': cells[3].get_text(strip=True) if len(cells) > 3 else '',
            'games': safe_int(cells[4].get_text(strip=True)),
            'games_started': safe_int(cells[5].get_text(strip=True)),
            'min_per_game': safe_float(cells[6].get_text(strip=True)),
            'fg': safe_float(cells[7].get_text(strip=True)),
            'fga': safe_float(cells[8].get_text(strip=True)),
            'fg_pct': safe_float(cells[9].get_text(strip=True)),
            'fg3': safe_float(cells[10].get_text(strip=True)) if len(cells) > 10 else 0.0,
            'fg3a': safe_float(cells[11].get_text(strip=True)) if len(cells) > 11 else 0.0,
            'fg3_pct': safe_float(cells[12].get_text(strip=True)) if len(cells) > 12 else 0.0,
            'ft': safe_float(cells[13].get_text(strip=True)) if len(cells) > 13 else 0.0,
            'fta': safe_float(cells[14].get_text(strip=True)) if len(cells) > 14 else 0.0,
            'ft_pct': safe_float(cells[15].get_text(strip=True)) if len(cells) > 15 else 0.0,
            'orb': safe_float(cells[16].get_text(strip=True)) if len(cells) > 16 else 0.0,
            'drb': safe_float(cells[17].get_text(strip=True)) if len(cells) > 17 else 0.0,
            'trb': safe_float(cells[18].get_text(strip=True)) if len(cells) > 18 else 0.0,
            'ast': safe_float(cells[19].get_text(strip=True)) if len(cells) > 19 else 0.0,
            'stl': safe_float(cells[20].get_text(strip=True)) if len(cells) > 20 else 0.0,
            'blk': safe_float(cells[21].get_text(strip=True)) if len(cells) > 21 else 0.0,
            'tov': safe_float(cells[22].get_text(strip=True)) if len(cells) > 22 else 0.0,
            'pf': safe_float(cells[23].get_text(strip=True)) if len(cells) > 23 else 0.0,
            'pts': safe_float(cells[24].get_text(strip=True)) if len(cells) > 24 else 0.0,
        }
    except Exception as e:
        logger.error(f"解析球员数据行失败: {e}")
        return None


def scrape_season_stats(season: int) -> List[Dict]:
    """
    爬取单个赛季的球员统计数据
    
    Args:
        season: 赛季年份
        
    Returns:
        球员数据列表
    """
    url = build_bbref_url(season)
    logger.info(f"正在爬取 {season} 赛季数据: {url}")
    
    html = fetch_page(url)
    if not html:
        return []
    
    soup = parse_html(html)
    table = soup.find('table', {'id': 'per_game_stats'})
    
    if not table:
        logger.warning(f"未找到 {season} 赛季数据表")
        return []
    
    rows = table.find('tbody').find_all('tr')
    
    # 函数式处理: map + filter
    extract_fn = partial(extract_player_row, season=season)
    players = list(filter(None, map(extract_fn, rows)))
    
    logger.info(f"成功提取 {len(players)} 名球员数据")
    return players


def scrape_advanced_stats(season: int) -> List[Dict]:
    """
    爬取单个赛季的高级统计数据 (PER, BPM, VORP, WS)
    
    Args:
        season: 赛季年份
        
    Returns:
        高级统计数据列表
    """
    url = build_bbref_url(season, 'advanced')
    logger.info(f"正在爬取 {season} 赛季高级数据: {url}")
    
    html = fetch_page(url)
    if not html:
        return []
    
    soup = parse_html(html)
    table = soup.find('table', {'id': 'advanced_stats'})
    
    if not table:
        return []
    
    rows = table.find('tbody').find_all('tr')
    advanced_stats = []
    
    for row in rows:
        cells = row.find_all(['th', 'td'])
        if len(cells) < 20:
            continue
            
        player_name = cells[0].get_text(strip=True)
        if player_name == 'Player' or not player_name:
            continue
            
        try:
            advanced_stats.append({
                'player': player_name,
                'season': season,
                'per': float(cells[7].get_text(strip=True) or 0),
                'ts_pct': float(cells[8].get_text(strip=True) or 0),
                'usg_pct': float(cells[11].get_text(strip=True) or 0),
                'ows': float(cells[15].get_text(strip=True) or 0),
                'dws': float(cells[16].get_text(strip=True) or 0),
                'ws': float(cells[17].get_text(strip=True) or 0),
                'ws_48': float(cells[18].get_text(strip=True) or 0),
                'obpm': float(cells[20].get_text(strip=True) or 0),
                'dbpm': float(cells[21].get_text(strip=True) or 0),
                'bpm': float(cells[22].get_text(strip=True) or 0),
                'vorp': float(cells[23].get_text(strip=True) or 0),
            })
        except:
            continue
    
    return advanced_stats


# ============================================================================
# 纯函数: Spotrac 薪资爬虫
# ============================================================================

def build_spotrac_url(season: int) -> str:
    """构建Spotrac薪资数据URL"""
    return f"https://www.spotrac.com/wnba/cap/{season}/"


def scrape_salary_data(season: int) -> List[Dict]:
    """
    爬取单个赛季的薪资数据
    
    Args:
        season: 赛季年份
        
    Returns:
        薪资数据列表
    """
    url = build_spotrac_url(season)
    logger.info(f"正在爬取 {season} 赛季薪资数据")
    
    html = fetch_page(url)
    if not html:
        return []
    
    soup = parse_html(html)
    
    # Spotrac的表格结构
    salary_data = []
    tables = soup.find_all('table', class_='datatable')
    
    for table in tables:
        rows = table.find_all('tr')[1:]  # 跳过表头
        for row in rows:
            cells = row.find_all('td')
            if len(cells) < 3:
                continue
            try:
                player_name = cells[0].get_text(strip=True)
                team = cells[1].get_text(strip=True) if len(cells) > 1 else ''
                salary_str = cells[2].get_text(strip=True).replace('$', '').replace(',', '')
                salary = float(salary_str) if salary_str else 0
                
                salary_data.append({
                    'player': player_name,
                    'team': team,
                    'season': season,
                    'salary': salary,
                })
            except:
                continue
    
    return salary_data


# ============================================================================
# 纯函数: 数据聚合与转换
# ============================================================================

def merge_player_data(basic: List[Dict], advanced: List[Dict]) -> List[Dict]:
    """
    合并基础统计和高级统计数据
    
    Args:
        basic: 基础统计数据列表
        advanced: 高级统计数据列表
        
    Returns:
        合并后的数据列表
    """
    # 创建高级数据查找字典
    advanced_lookup = {
        (d['player'], d['season']): d 
        for d in advanced
    }
    
    def merge_single(player: Dict) -> Dict:
        key = (player['player'], player['season'])
        adv = advanced_lookup.get(key, {})
        return {**player, **{k: v for k, v in adv.items() if k not in ['player', 'season']}}
    
    return list(map(merge_single, basic))


def aggregate_team_stats(players: List[Dict]) -> Dict[Tuple[str, int], Dict]:
    """
    聚合球队统计数据
    
    Args:
        players: 球员数据列表
        
    Returns:
        按(球队, 赛季)分组的统计字典
    """
    from collections import defaultdict
    
    team_stats = defaultdict(lambda: {
        'total_points': 0,
        'total_rebounds': 0, 
        'total_assists': 0,
        'player_count': 0,
        'total_minutes': 0,
    })
    
    for p in players:
        key = (p.get('team', ''), p.get('season', 0))
        team_stats[key]['total_points'] += p.get('pts', 0) * p.get('games', 0)
        team_stats[key]['total_rebounds'] += p.get('trb', 0) * p.get('games', 0)
        team_stats[key]['total_assists'] += p.get('ast', 0) * p.get('games', 0)
        team_stats[key]['player_count'] += 1
        team_stats[key]['total_minutes'] += p.get('min_per_game', 0) * p.get('games', 0)
    
    return dict(team_stats)


def calculate_war(player: Dict) -> float:
    """
    计算球员WAR值 (Wins Above Replacement)
    
    公式: WAR = (BPM - BPM_replacement) × MP / (48 × Games_per_season)
    
    Args:
        player: 球员数据字典
        
    Returns:
        WAR值
    """
    bpm = player.get('bpm', 0)
    bpm_replacement = -2.0
    mp = player.get('min_per_game', 0) * player.get('games', 0)
    games_in_season = GAMES_PER_SEASON.get(player.get('season', 2024), 40)
    
    if games_in_season == 0:
        return 0.0
    
    war = (bpm - bpm_replacement) * mp / (48 * games_in_season)
    return round(war, 2)


def calculate_value_per_win() -> float:
    """
    计算每场胜利的货币价值 (WNBA)
    
    基于:
    - 门票收入增加: +$50,000
    - 季后赛概率提升: +$100,000
    - 周边商品: +$30,000
    - 赞助价值: +$50,000
    
    Returns:
        VPW值 (美元)
    """
    ticket_impact = 50000
    playoff_impact = 100000
    merchandise_impact = 30000
    sponsorship_impact = 50000
    
    return ticket_impact + playoff_impact + merchandise_impact + sponsorship_impact


def calculate_performance_value(player: Dict) -> float:
    """
    计算球员表现价值
    
    公式: V_performance = WAR × VPW
    
    Args:
        player: 球员数据字典
        
    Returns:
        表现价值 (美元)
    """
    war = calculate_war(player)
    vpw = calculate_value_per_win()
    return round(war * vpw, 0)


# ============================================================================
# 高阶函数: 并行爬取
# ============================================================================

def scrape_all_seasons(
    seasons: List[int] = SEASONS,
    scraper_fn: Callable[[int], List[Dict]] = scrape_season_stats,
    max_workers: int = 3
) -> List[Dict]:
    """
    并行爬取多个赛季数据
    
    Args:
        seasons: 赛季列表
        scraper_fn: 爬虫函数
        max_workers: 最大并行数
        
    Returns:
        所有赛季数据的合并列表
    """
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(scraper_fn, seasons))
    
    # 使用reduce合并所有结果
    return reduce(lambda acc, x: acc + x, results, [])


def compose(*functions):
    """
    函数组合 (从右到左执行)
    
    Args:
        *functions: 要组合的函数
        
    Returns:
        组合后的函数
    """
    return reduce(lambda f, g: lambda x: f(g(x)), functions, lambda x: x)


def pipe(*functions):
    """
    管道函数 (从左到右执行)
    
    Args:
        *functions: 要组合的函数
        
    Returns:
        管道函数
    """
    return reduce(lambda f, g: lambda x: g(f(x)), functions, lambda x: x)


# ============================================================================
# 数据转换管道
# ============================================================================

def add_calculated_fields(player: Dict) -> Dict:
    """为球员数据添加计算字段"""
    return {
        **player,
        'war': calculate_war(player),
        'performance_value': calculate_performance_value(player),
        'efficiency': (
            player.get('pts', 0) + 
            player.get('trb', 0) + 
            player.get('ast', 0) + 
            player.get('stl', 0) + 
            player.get('blk', 0) - 
            player.get('tov', 0)
        ) / max(player.get('games', 1), 1),
    }


def filter_valid_players(players: List[Dict], min_games: int = 5) -> List[Dict]:
    """过滤有效球员 (至少出场min_games场)"""
    return list(filter(lambda p: p.get('games', 0) >= min_games, players))


def transform_players_pipeline(players: List[Dict]) -> List[Dict]:
    """
    球员数据转换管道
    
    流程: 过滤 -> 添加计算字段 -> 排序
    """
    transform = pipe(
        partial(filter_valid_players, min_games=5),
        lambda ps: list(map(add_calculated_fields, ps)),
        lambda ps: sorted(ps, key=lambda x: x.get('war', 0), reverse=True)
    )
    return transform(players)


# ============================================================================
# 数据导出函数
# ============================================================================

def players_to_dataframe(players: List[Dict]) -> pd.DataFrame:
    """将球员数据列表转换为DataFrame"""
    return pd.DataFrame(players)


def export_to_excel(
    data: Dict[str, pd.DataFrame],
    filepath: str
) -> str:
    """
    导出多个DataFrame到Excel
    
    Args:
        data: {sheet_name: DataFrame} 字典
        filepath: 输出文件路径
        
    Returns:
        输出文件路径
    """
    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        for sheet_name, df in data.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    logger.info(f"数据已导出到: {filepath}")
    return filepath


def export_to_csv(df: pd.DataFrame, filepath: str) -> str:
    """导出DataFrame到CSV"""
    df.to_csv(filepath, index=False, encoding='utf-8-sig')
    logger.info(f"数据已导出到: {filepath}")
    return filepath


# ============================================================================
# 主程序入口
# ============================================================================

def run_full_scraper(
    seasons: List[int] = SEASONS,
    output_dir: str = './data'
) -> Dict[str, str]:
    """
    运行完整的数据爬取流程
    
    Args:
        seasons: 要爬取的赛季列表
        output_dir: 输出目录
        
    Returns:
        输出文件路径字典
    """
    os.makedirs(output_dir, exist_ok=True)
    
    logger.info("=" * 60)
    logger.info("WNBA 数据爬取系统启动")
    logger.info(f"目标赛季: {seasons}")
    logger.info("=" * 60)
    
    # Step 1: 爬取基础统计
    logger.info("Step 1: 爬取基础统计数据...")
    basic_stats = scrape_all_seasons(seasons, scrape_season_stats)
    
    # Step 2: 爬取高级统计
    logger.info("Step 2: 爬取高级统计数据...")
    advanced_stats = scrape_all_seasons(seasons, scrape_advanced_stats)
    
    # Step 3: 合并数据
    logger.info("Step 3: 合并数据...")
    merged_data = merge_player_data(basic_stats, advanced_stats)
    
    # Step 4: 数据转换
    logger.info("Step 4: 数据转换与计算...")
    processed_data = transform_players_pipeline(merged_data)
    
    # Step 5: 爬取薪资数据
    logger.info("Step 5: 爬取薪资数据...")
    salary_data = scrape_all_seasons(seasons, scrape_salary_data)
    
    # Step 6: 转换为DataFrame
    players_df = players_to_dataframe(processed_data)
    salary_df = pd.DataFrame(salary_data) if salary_data else pd.DataFrame()
    
    # Step 7: 导出
    logger.info("Step 6: 导出数据...")
    output_files = {}
    
    # 主数据文件
    excel_data = {
        'All_Players': players_df,
        'Salary_Data': salary_df,
    }
    
    # 按赛季分表
    for season in seasons:
        season_df = players_df[players_df['season'] == season]
        if not season_df.empty:
            excel_data[f'Season_{season}'] = season_df
    
    # Indiana Fever专项
    fever_df = players_df[players_df['team'] == 'IND']
    if not fever_df.empty:
        excel_data['Indiana_Fever'] = fever_df
    
    output_files['excel'] = export_to_excel(
        excel_data,
        f"{output_dir}/wnba_2019_2024_complete.xlsx"
    )
    
    output_files['csv'] = export_to_csv(
        players_df,
        f"{output_dir}/wnba_players_all_seasons.csv"
    )
    
    logger.info("=" * 60)
    logger.info("数据爬取完成!")
    logger.info(f"总球员记录: {len(players_df)}")
    logger.info(f"输出文件: {list(output_files.values())}")
    logger.info("=" * 60)
    
    return output_files


if __name__ == "__main__":
    run_full_scraper()
