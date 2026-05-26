#!/usr/bin/env python3
"""
李白人生颜色图 — 可视化生成器
生成横向时间轴色带图 + 文字注解
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.font_manager import FontProperties
import numpy as np
import os
import sys

# 添加数据模块路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from libai_data import get_poems, get_color_rgb, get_annotations, get_color_meanings

# ═══════════════════════════════════════════
# 字体设置（中文）
# ═══════════════════════════════════════════

def get_chinese_font():
    """Try to find a Chinese font on the system."""
    font_paths = [
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
    ]
    for fp in font_paths:
        if os.path.exists(fp):
            return FontProperties(fname=fp)
    # Fallback: try matplotlib's default
    return FontProperties(family='sans-serif')


def calculate_stage_color(poems, color_rgb, start_age, end_age):
    """计算阶段内所有颜色的加权平均值"""
    color_counts = {}
    
    for poem in poems:
        age = poem["age"]
        if start_age <= age <= end_age:
            for color_name in poem["colors"].keys():
                if color_name in color_rgb:
                    color_counts[color_name] = color_counts.get(color_name, 0) + 1
    
    if not color_counts:
        return (128, 128, 128)  # 灰色默认值
    
    # 加权平均计算
    total_r, total_g, total_b = 0, 0, 0
    total_weight = 0
    
    for color_name, count in color_counts.items():
        r, g, b = color_rgb[color_name]
        total_r += r * count
        total_g += g * count
        total_b += b * count
        total_weight += count
    
    if total_weight == 0:
        return (128, 128, 128)
    
    avg_r = int(total_r / total_weight)
    avg_g = int(total_g / total_weight)
    avg_b = int(total_b / total_weight)
    
    return (avg_r, avg_g, avg_b)


# ═══════════════════════════════════════════
# 主可视化
# ═══════════════════════════════════════════

def generate_color_bar(output_path="libai_color_of_life.png"):
    poems = get_poems()
    color_rgb = get_color_rgb()
    annotations = get_annotations()
    color_meanings = get_color_meanings()

    font_prop = get_chinese_font()

    ages = [p["age"] for p in poems]
    min_age = min(ages) - 2
    max_age = max(ages) + 2

    # ── 创建画布 ──
    fig = plt.figure(figsize=(22, 16), facecolor='#1a1a2e')

    # 主色带区域
    ax_bar = fig.add_axes([0.08, 0.55, 0.84, 0.12])
    # 阶段合并色带区域
    ax_stage = fig.add_axes([0.08, 0.45, 0.84, 0.08])
    # 注解区域
    ax_annot = fig.add_axes([0.08, 0.08, 0.84, 0.32])
    # 图例区域
    ax_legend = fig.add_axes([0.08, 0.93, 0.84, 0.06])

    ax_bar.set_facecolor('#1a1a2e')
    ax_stage.set_facecolor('#1a1a2e')
    ax_annot.set_facecolor('#1a1a2e')
    ax_legend.set_facecolor('#1a1a2e')

    # ── 绘制色带 ──
    bar_height = 1.0
    
    for i, poem in enumerate(poems):
        age = poem["age"]
        colors = poem["colors"]
        
        if not colors:
            # 无颜色——用灰色表示
            x_start = age - 1
            x_end = age + 1
            ax_bar.add_patch(mpatches.FancyBboxPatch(
                (x_start, 0), x_end - x_start, bar_height,
                boxstyle="round,pad=0.1",
                facecolor='#333333', edgecolor='none', alpha=0.6
            ))
            continue

        # 每种颜色画一个色块
        n_colors = len(colors)
        block_width = 2.0 / n_colors  # 每个颜色块的宽度
        
        for j, (color_name, color_note) in enumerate(colors.items()):
            rgb = color_rgb.get(color_name, (128, 128, 128))
            x_start = age - 1 + j * block_width
            
            ax_bar.add_patch(mpatches.FancyBboxPatch(
                (x_start, 0.05), block_width - 0.05, bar_height - 0.1,
                boxstyle="round,pad=0.08",
                facecolor=tuple(c/255 for c in rgb),
                edgecolor='white', linewidth=0.3, alpha=0.9
            ))

    # ── 阶段合并色带 ──
    stages = [
        (15, 24, "少年漫游", "#4FC3F7"),
        (25, 42, "求仕长安", "#FFB74D"),
        (43, 55, "流放漂泊", "#E57373"),
        (56, 61, "晚年飘零", "#9575CD"),
    ]
    
    for start, end, label, color in stages:
        stage_color = calculate_stage_color(poems, color_rgb, start, end)
        stage_color_normalized = tuple(c/255 for c in stage_color)
        
        # 绘制阶段合并色块
        ax_stage.add_patch(mpatches.FancyBboxPatch(
            (start, 0.1), end - start, 0.8,
            boxstyle="round,pad=0.1",
            facecolor=stage_color_normalized, edgecolor='white', 
            linewidth=1, alpha=0.9
        ))
        
        # 阶段标签
        ax_stage.text((start + end) / 2, 0.5, label,
                     ha='center', va='center', fontproperties=font_prop, 
                     color='white', fontsize=10, fontweight='bold')
        
        # 颜色信息
        color_name = f"({stage_color[0]},{stage_color[1]},{stage_color[2]})"
        ax_stage.text((start + end) / 2, 0.15, color_name,
                     ha='center', va='center', fontproperties=font_prop, 
                     color='#cccccc', fontsize=7)

    ax_stage.set_xlim(min_age, max_age)
    ax_stage.set_ylim(-0.1, 1.2)
    ax_stage.set_title('阶段合并色（加权平均）', fontproperties=font_prop, 
                      color='white', fontsize=11, pad=8)
    ax_stage.axis('off')

    # ── 年龄标记 ──
    for age in range(10, 65, 5):
        ax_bar.axvline(x=age, color='#555555', linewidth=0.5, linestyle='--', alpha=0.5)
        ax_bar.text(age, -0.35, f"{age}岁", ha='center', va='top',
                    fontproperties=font_prop, color='#aaaaaa', fontsize=9)

    ax_bar.set_xlim(min_age, max_age)
    ax_bar.set_ylim(-0.6, 1.5)
    ax_bar.set_title('李白的人生颜色  The Color of Li Bai\'s Life (701-762)',
                     fontproperties=font_prop, color='white', fontsize=16, pad=15)
    ax_bar.axis('off')

    # ── 人生阶段标注 ──
    for start, end, label, color in stages:
        ax_bar.annotate('', xy=(end, 1.35), xytext=(start, 1.35),
                       arrowprops=dict(arrowstyle='<->', color=color, lw=2))
        ax_bar.text((start + end) / 2, 1.45, label,
                   ha='center', fontproperties=font_prop, color=color, fontsize=10, fontweight='bold')

    # ── 注解区域 ──
    ax_annot.axis('off')
    ax_annot.set_title('诗作注解', fontproperties=font_prop, color='white', fontsize=13, pad=10)

    y_positions = np.linspace(0.95, 0.05, len(poems))
    
    for i, (poem, y) in enumerate(zip(poems, y_positions)):
        age = poem["age"]
        colors_str = "".join(poem["colors"].keys()) if poem["colors"] else "无"
        annot = annotations.get(age, "")
        
        # 年龄+诗名
        text = f"【{age}岁】{poem['poem']}"
        ax_annot.text(0.0, y, text, fontproperties=font_prop, color='white',
                     fontsize=9, fontweight='bold', transform=ax_annot.transAxes)
        
        # 诗句（截取）
        line = poem["line"][:40] + "..." if len(poem["line"]) > 40 else poem["line"]
        ax_annot.text(0.22, y, f'"{line}"', fontproperties=font_prop, color='#cccccc',
                     fontsize=8, style='italic', transform=ax_annot.transAxes)
        
        # 颜色标记
        color_dots = ""
        for c in poem["colors"].keys():
            rgb = color_rgb.get(c, (128, 128, 128))
            color_dots += f"■{c} "
        ax_annot.text(0.72, y, color_dots, fontproperties=font_prop, color='#aaaaaa',
                     fontsize=8, transform=ax_annot.transAxes)

        # 人生注解
        ax_annot.text(0.85, y, annot[:20], fontproperties=font_prop, color='#888888',
                     fontsize=7, transform=ax_annot.transAxes)

    # ── 图例 ──
    ax_legend.axis('off')
    legend_items = []
    for color_name, rgb in color_rgb.items():
        if color_name in ["赤", "丹", "彩"]:  # 跳过重复色
            continue
        patch = mpatches.Patch(color=tuple(c/255 for c in rgb), label=color_name)
        legend_items.append(patch)
    
    ax_legend.legend(handles=legend_items, loc='center', ncol=len(legend_items),
                    frameon=False, prop=font_prop,
                    labelcolor='white', fontsize=9)

    # ── 保存 ──
    plt.savefig(output_path, dpi=150, bbox_inches='tight',
                facecolor='#1a1a2e', edgecolor='none')
    plt.close()
    print(f"Saved to: {output_path}")
    return output_path


if __name__ == "__main__":
    output = generate_color_bar()
    print(f"Done! Image: {output}")
