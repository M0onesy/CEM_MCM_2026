"""
WNBA 数据收集与分析主程序
=========================
整合爬虫和模拟数据生成功能。

使用方法:
    python main.py --mode scrape     # 使用爬虫获取真实数据
    python main.py --mode generate   # 生成模拟数据（无网络时使用）
    python main.py --mode both       # 先尝试爬虫，失败则使用模拟

作者: MCM/ICM 2026 Team
日期: 2026-01-30
"""

import argparse
import sys
import os
from typing import Dict

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from wnba_data_scraper import run_full_scraper
from wnba_data_generator import export_complete_dataset


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='WNBA 数据收集系统 (2019-2024)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python main.py --mode generate              # 生成模拟数据
    python main.py --mode scrape --output ./my_data   # 爬取真实数据到指定目录
    python main.py --seasons 2022 2023 2024     # 只处理特定赛季
        """
    )
    
    parser.add_argument(
        '--mode', '-m',
        choices=['scrape', 'generate', 'both'],
        default='generate',
        help='数据获取模式: scrape=爬虫, generate=模拟, both=优先爬虫'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='./data',
        help='输出目录 (默认: ./data)'
    )
    
    parser.add_argument(
        '--seasons', '-s',
        type=int,
        nargs='+',
        default=[2019, 2020, 2021, 2022, 2023, 2024],
        help='要处理的赛季 (默认: 2019-2024)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='详细输出模式'
    )
    
    return parser.parse_args()


def run_scraper_mode(output_dir: str, seasons: list) -> Dict:
    """运行爬虫模式"""
    print("\n" + "=" * 60)
    print("🌐 模式: 网络爬虫 (实时数据)")
    print("=" * 60)
    
    try:
        return run_full_scraper(seasons=seasons, output_dir=output_dir)
    except Exception as e:
        print(f"\n❌ 爬虫失败: {e}")
        return None


def run_generator_mode(output_dir: str, seasons: list) -> Dict:
    """运行数据生成模式"""
    print("\n" + "=" * 60)
    print("🔧 模式: 模拟数据生成")
    print("=" * 60)
    
    try:
        return export_complete_dataset(output_dir=output_dir, seasons=seasons)
    except Exception as e:
        print(f"\n❌ 数据生成失败: {e}")
        raise


def main():
    """主函数"""
    args = parse_arguments()
    
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║     WNBA 多年数据收集系统 (2019-2024)                     ║
    ║     MCM/ICM 2026 - Problem D: Professional Sports Team    ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    print(f"📁 输出目录: {args.output}")
    print(f"📅 目标赛季: {args.seasons}")
    print(f"⚙️  运行模式: {args.mode}")
    
    result = None
    
    if args.mode == 'scrape':
        result = run_scraper_mode(args.output, args.seasons)
        
    elif args.mode == 'generate':
        result = run_generator_mode(args.output, args.seasons)
        
    elif args.mode == 'both':
        print("\n尝试网络爬虫...")
        result = run_scraper_mode(args.output, args.seasons)
        
        if result is None:
            print("\n爬虫失败，切换到模拟数据生成...")
            result = run_generator_mode(args.output, args.seasons)
    
    if result:
        print("\n" + "=" * 60)
        print("✅ 数据收集完成!")
        print("=" * 60)
        print("\n📄 生成的文件:")
        for key, path in result.items():
            print(f"   - {key}: {path}")
        print("\n下一步: 运行 Model A (球员价值评估)")
        print("   python models/model_a_player_value.py")
    else:
        print("\n❌ 数据收集失败，请检查网络连接或手动下载数据")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
