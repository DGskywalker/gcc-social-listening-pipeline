"""
Generate a high-fidelity visual dashboard preview PNG for the README.md documentation.
Simulates the dark executive GCC Social Listening Dashboard with KPI cards, charts, and table.
"""

from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_IMAGE = BASE_DIR / "dashboard" / "dashboard_preview.png"
OUTPUT_IMAGE.parent.mkdir(parents=True, exist_ok=True)


def create_preview_image():
    # Set high DPI and 16:9 widescreen canvas
    fig = plt.figure(figsize=(16, 9.5), dpi=150, facecolor='#0B0F19')
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor('#0B0F19')
    ax.set_xlim(0, 1600)
    ax.set_ylim(0, 950)
    ax.axis('off')

    # Header Bar
    header_box = patches.FancyBboxPatch(
        (30, 850), 1540, 75,
        boxstyle="round,pad=5,rounding_size=12",
        facecolor='#111827', edgecolor='#283548', linewidth=1.2
    )
    ax.add_patch(header_box)

    # Logo badge
    logo_box = patches.FancyBboxPatch(
        (48, 865), 55, 45,
        boxstyle="round,pad=3,rounding_size=8",
        facecolor='#F59E0B', edgecolor='none'
    )
    ax.add_patch(logo_box)
    ax.text(75, 887, 'GCC', color='#000000', fontsize=14, fontweight='bold', ha='center', va='center')

    # Title & Subtitle
    ax.text(120, 895, 'GCC Social Listening & Brand Intelligence Pipeline', color='#FFFFFF', fontsize=16, fontweight='bold', va='center')
    ax.text(120, 872, 'Ingestion → AWS S3 Lakehouse → Multilingual AI Tagging → Real-time Insight Dashboard', color='#9CA3AF', fontsize=9.5, va='center')

    # Status Badges
    live_badge = patches.FancyBboxPatch(
        (1330, 870), 105, 32, boxstyle="round,pad=3,rounding_size=16",
        facecolor='#10B981', alpha=0.15, edgecolor='#10B981', linewidth=1
    )
    ax.add_patch(live_badge)
    ax.text(1382, 886, '● S3 Live Sync', color='#10B981', fontsize=9, fontweight='bold', ha='center', va='center')

    synth_badge = patches.FancyBboxPatch(
        (1445, 870), 110, 32, boxstyle="round,pad=3,rounding_size=16",
        facecolor='#F59E0B', alpha=0.15, edgecolor='#F59E0B', linewidth=1
    )
    ax.add_patch(synth_badge)
    ax.text(1500, 886, '🛡️ Compliant Lake', color='#F59E0B', fontsize=9, fontweight='bold', ha='center', va='center')

    # Weekly Executive "So What?" Banner
    exec_box = patches.FancyBboxPatch(
        (30, 735), 1540, 100,
        boxstyle="round,pad=5,rounding_size=12",
        facecolor='#111827', edgecolor='#F59E0B', alpha=0.9, linewidth=1.5
    )
    ax.add_patch(exec_box)
    ax.text(50, 815, '⚡ WEEKLY EXECUTIVE "SO WHAT?" SYNTHESIS', color='#F59E0B', fontsize=11, fontweight='bold')
    
    # 3 Strategic Takeaways
    # 1. Alert
    b1 = patches.FancyBboxPatch((48, 747), 485, 55, boxstyle="round,pad=3,rounding_size=8", facecolor='#1F2937', edgecolor='#EF4444', linewidth=1)
    ax.add_patch(b1)
    ax.text(60, 785, '🚨 Al-Noor Telecom 5G Outage in Riyadh', color='#FFFFFF', fontsize=9.5, fontweight='bold')
    ax.text(60, 762, '44% negative mention spike in Al-Yasmin district; customer frustration with bot.', color='#9CA3AF', fontsize=7.5)

    # 2. Win
    b2 = patches.FancyBboxPatch((555, 747), 485, 55, boxstyle="round,pad=3,rounding_size=8", facecolor='#1F2937', edgecolor='#10B981', linewidth=1)
    ax.add_patch(b2)
    ax.text(567, 785, '💡 DesertPay 10% Ramadan Cashback Surge', color='#FFFFFF', fontsize=9.5, fontweight='bold')
    ax.text(567, 762, '78% positive sentiment; Share of voice expanded to 28% across Saudi fintech.', color='#9CA3AF', fontsize=7.5)

    # 3. Risk
    b3 = patches.FancyBboxPatch((1062, 747), 490, 55, boxstyle="round,pad=3,rounding_size=8", facecolor='#1F2937', edgecolor='#F59E0B', linewidth=1)
    ax.add_patch(b3)
    ax.text(1074, 785, '⚠️ Falcon Ride Surge Pricing Friction', color='#FFFFFF', fontsize=9.5, fontweight='bold')
    ax.text(1074, 762, 'Peak 2.8x multiplier backlash on weekends in Riyadh Boulevard and Downtown Dubai.', color='#9CA3AF', fontsize=7.5)

    # 4 KPI Cards
    kpis = [
        ("TOTAL MENTIONS TRACKED", "175", "100% compliant data lake", '#3B82F6'),
        ("NET SENTIMENT SCORE", "+34%", "% Positive − % Negative", '#10B981'),
        ("LEADING BRAND (SOV)", "Al-Noor Telecom", "31% of total tracked volume", '#F59E0B'),
        ("ACTIVE INCIDENTS", "9", "Network & Outage flare-ups", '#EF4444'),
    ]

    card_w = 365
    for i, (label, val, sub, col) in enumerate(kpis):
        cx = 30 + i * (card_w + 26)
        c_box = patches.FancyBboxPatch(
            (cx, 630), card_w, 90,
            boxstyle="round,pad=5,rounding_size=10",
            facecolor='#111827', edgecolor='#283548', linewidth=1
        )
        ax.add_patch(c_box)
        ax.text(cx + 18, 698, label, color='#9CA3AF', fontsize=8.5, fontweight='bold')
        ax.text(cx + 18, 665, val, color=col, fontsize=20, fontweight='bold')
        ax.text(cx + 18, 644, sub, color='#6B7280', fontsize=8)

    # Chart 1: Share of Voice (Doughnut)
    ch1_box = patches.FancyBboxPatch((30, 325), 485, 290, boxstyle="round,pad=5,rounding_size=10", facecolor='#111827', edgecolor='#283548')
    ax.add_patch(ch1_box)
    ax.text(50, 588, 'Share of Voice across GCC Brands', color='#FFFFFF', fontsize=11, fontweight='bold')
    ax.text(495, 588, 'Volume Share', color='#6B7280', fontsize=8, ha='right')

    # Draw mini doughnut inside ax
    sub_ax1 = fig.add_axes([0.05, 0.38, 0.24, 0.22])
    sub_ax1.set_facecolor('#111827')
    brands_labels = ['Al-Noor', 'DesertPay', 'Oasis Retail', 'Falcon Ride', 'GulfCloud']
    brands_shares = [31, 26, 18, 15, 10]
    brands_cols = ['#3B82F6', '#F59E0B', '#10B981', '#EF4444', '#8B5CF6']
    wedges, _ = sub_ax1.pie(brands_shares, colors=brands_cols, startangle=140, wedgeprops=dict(width=0.45, edgecolor='#111827', linewidth=2))
    sub_ax1.text(0, 0, '175\nPosts', color='#FFFFFF', fontsize=11, fontweight='bold', ha='center', va='center')

    # Chart 2: Sentiment Trend Line
    ch2_box = patches.FancyBboxPatch((535, 325), 515, 290, boxstyle="round,pad=5,rounding_size=10", facecolor='#111827', edgecolor='#283548')
    ax.add_patch(ch2_box)
    ax.text(555, 588, 'Sentiment Trajectory (30-Day Trend)', color='#FFFFFF', fontsize=11, fontweight='bold')
    ax.text(1030, 588, 'Pos vs Neg vs Neu', color='#6B7280', fontsize=8, ha='right')

    sub_ax2 = fig.add_axes([0.36, 0.38, 0.28, 0.21])
    sub_ax2.set_facecolor('#111827')
    days = np.arange(14)
    pos_line = np.array([5, 6, 8, 7, 9, 12, 14, 11, 10, 13, 15, 14, 16, 15])
    neg_line = np.array([8, 9, 7, 10, 14, 16, 12, 9, 8, 7, 6, 8, 7, 6])
    neu_line = np.array([4, 5, 4, 6, 5, 4, 6, 5, 6, 5, 4, 5, 6, 5])
    sub_ax2.plot(days, pos_line, color='#10B981', lw=2.2, label='Positive')
    sub_ax2.plot(days, neg_line, color='#EF4444', lw=2.2, label='Negative')
    sub_ax2.plot(days, neu_line, color='#94A3B8', lw=1.5, linestyle='--', label='Neutral')
    sub_ax2.fill_between(days, pos_line, color='#10B981', alpha=0.1)
    sub_ax2.fill_between(days, neg_line, color='#EF4444', alpha=0.1)
    sub_ax2.set_xticks([])
    sub_ax2.tick_params(colors='#9CA3AF', labelsize=8)
    sub_ax2.spines['top'].set_visible(False)
    sub_ax2.spines['right'].set_visible(False)
    sub_ax2.spines['left'].set_color('#283548')
    sub_ax2.spines['bottom'].set_color('#283548')
    sub_ax2.legend(loc='upper left', facecolor='#1F2937', edgecolor='none', labelcolor='#FFFFFF', fontsize=7.5)

    # Chart 3: Google Trends Overlay
    ch3_box = patches.FancyBboxPatch((1070, 325), 500, 290, boxstyle="round,pad=5,rounding_size=10", facecolor='#111827', edgecolor='#283548')
    ax.add_patch(ch3_box)
    ax.text(1090, 588, 'Google Trends vs Social Volume', color='#FFFFFF', fontsize=11, fontweight='bold')
    ax.text(1550, 588, 'Dual-Axis Overlay', color='#6B7280', fontsize=8, ha='right')

    sub_ax3 = fig.add_axes([0.70, 0.38, 0.27, 0.21])
    sub_ax3.set_facecolor('#111827')
    t_days = np.arange(12)
    search_idx = np.array([55, 58, 62, 60, 68, 75, 82, 85, 78, 72, 70, 68])
    social_vol = np.array([4, 5, 7, 6, 9, 14, 18, 16, 11, 8, 7, 6])
    sub_ax3.bar(t_days, social_vol, color='#F59E0B', alpha=0.45, edgecolor='#F59E0B', label='Social Vol')
    sub_ax3.tick_params(colors='#9CA3AF', labelsize=8)
    sub_ax3_twin = sub_ax3.twinx()
    sub_ax3_twin.plot(t_days, search_idx, color='#3B82F6', lw=2.5, label='Trends Index')
    sub_ax3_twin.tick_params(colors='#3B82F6', labelsize=8)
    sub_ax3.spines['top'].set_visible(False)
    sub_ax3_twin.spines['top'].set_visible(False)
    sub_ax3.spines['left'].set_color('#283548')
    sub_ax3.spines['bottom'].set_color('#283548')
    sub_ax3.set_xticks([])

    # Feed Table Snapshot Box (Bottom)
    table_box = patches.FancyBboxPatch((30, 30), 1540, 275, boxstyle="round,pad=5,rounding_size=10", facecolor='#111827', edgecolor='#283548')
    ax.add_patch(table_box)
    ax.text(50, 278, 'Live Monitored Feed & Multilingual Classification Explorer', color='#FFFFFF', fontsize=11.5, fontweight='bold')
    ax.text(1550, 278, 'Showing 175 audited posts', color='#9CA3AF', fontsize=8.5, ha='right')

    # Table Header
    headers = [("DATE", 50), ("PLATFORM", 170), ("BRAND", 310), ("TEXT CONTENT & ARABIC SARCASM DETECTION", 470), ("LANG/DIALECT", 1120), ("THEME", 1240), ("SENTIMENT", 1370), ("ENGAGEMENT", 1470)]
    th_box = patches.Rectangle((40, 245), 1520, 24, facecolor='#1F2937', edgecolor='none')
    ax.add_patch(th_box)
    for title, xpos in headers:
        ax.text(xpos, 257, title, color='#9CA3AF', fontsize=7.5, fontweight='bold', va='center')

    # Sample rows
    sample_rows = [
        ("2026-10-18", "TikTok (Synthetic)", "Al-Noor Telecom", "خدمة عملاء النور سريعة جداً ما شاء الله، رادين علي بعد ٤ أيام 👏🙃 [⚠️ Sarcasm]", "AR (Saudi)", "Customer Support", "NEGATIVE", "👁️ 45.2K  ❤️ 2.3K"),
        ("2026-10-18", "Instagram (Synthetic)", "DesertPay", "محفظة ديزرت باي فكت أزمة! كاش باك 10% فوري على كل مشتريات رمضان 🌙💳", "AR (Saudi)", "Promotions", "POSITIVE", "❤️ 3.4K  💬 412"),
        ("2026-10-17", "YouTube (Official)", "Al-Noor Telecom", "Al-Noor Telecom 5G in Business Bay is blistering fast! Over 920 Mbps testing.", "EN (English)", "Network", "POSITIVE", "👁️ 24.1K  ❤️ 1.8K"),
        ("2026-10-17", "TikTok (Synthetic)", "Falcon Ride", "مو معقول أسعار صقر رايد وقت خروج الموظفين في الرياض المشوار صار 110 ريال!", "AR (Saudi)", "Pricing", "NEGATIVE", "👁️ 18.9K  ❤️ 950"),
        ("2026-10-16", "Instagram (Synthetic)", "GulfCloud", "فخورون بإتمام نقل البنية التحتية لشركتنا إلى مراكز بيانات سحابة الخليج زمن 6ms.", "AR (Saudi)", "Cloud / UX", "POSITIVE", "❤️ 1.2K  💬 86"),
    ]

    for r_idx, (dt, plat, br, txt, lang, thm, sent, eng) in enumerate(sample_rows):
        ry = 215 - r_idx * 34
        line_box = patches.Rectangle((40, ry - 8), 1520, 28, facecolor='#111827' if r_idx % 2 == 0 else '#161F30', edgecolor='none')
        ax.add_patch(line_box)
        ax.text(50, ry + 5, dt, color='#9CA3AF', fontsize=7.5, va='center')
        ax.text(170, ry + 5, plat, color='#F59E0B' if 'TikTok' in plat else ('#E1306C' if 'Instagram' in plat else '#FF0000'), fontsize=7.5, fontweight='bold', va='center')
        ax.text(310, ry + 5, br, color='#FFFFFF', fontsize=7.5, fontweight='bold', va='center')
        ax.text(470, ry + 5, txt[:78] + "...", color='#E5E7EB', fontsize=7.5, va='center')
        ax.text(1120, ry + 5, lang, color='#9CA3AF', fontsize=7.5, va='center')
        ax.text(1240, ry + 5, thm, color='#60A5FA', fontsize=7.5, va='center')
        
        # Sentiment pill
        s_col = '#10B981' if sent == 'POSITIVE' else '#EF4444'
        pill = patches.FancyBboxPatch((1365, ry - 3), 75, 17, boxstyle="round,pad=2,rounding_size=6", facecolor=s_col, alpha=0.15, edgecolor=s_col, linewidth=0.8)
        ax.add_patch(pill)
        ax.text(1402, ry + 5, sent, color=s_col, fontsize=7, fontweight='bold', ha='center', va='center')
        
        ax.text(1470, ry + 5, eng, color='#9CA3AF', fontsize=7.2, va='center')

    plt.savefig(OUTPUT_IMAGE, bbox_inches='tight', dpi=150, facecolor='#0B0F19')
    plt.close()
    print(f"Successfully generated visual preview at: {OUTPUT_IMAGE}")


if __name__ == '__main__':
    create_preview_image()
