from pathlib import Path

import matplotlib

# Use a non-interactive backend so the script can run in headless environments.
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def _apply_style() -> None:
    """Try preferred seaborn-like style with a safe fallback for older Matplotlib."""
    try:
        plt.style.use("seaborn-v0_8-darkgrid")
    except OSError:
        # Older Matplotlib versions may not have the versioned seaborn styles.
        plt.style.use("seaborn-darkgrid")


_apply_style()


def _save_and_close(fig, filename: str) -> Path:
    """Save figure to the reports folder and close it."""
    output_dir = Path(__file__).resolve().parent
    output_path = output_dir / filename
    fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)
    return output_path

# ==========================================
# גרף 1: הכנסות לפי יצרן ומחלקה
# ==========================================

def plot_revenue_chart():
    # נתונים מתוך עמוד 4 [cite: 106]
    # הקטגוריות: שילוב של יצרן וגודל
    categories = ['Boeing (L)', 'Boeing (S)', 'Airbus (L)', 'Airbus (S)', 'Dassault (L)', 'Dassault (S)']
    
    # הכנסות ממחלקת תיירים (Economy)
    economy_revenue = np.array([1100.0, 189.0, 1056.0, 172.5, 580.0, 246.0])
    
    # הכנסות ממחלקת עסקים (Business)
    # שים לב: לפי הדוח נראה שחלק מהמטוסים הקטנים או דגמים מסוימים לא הניבו הכנסות עסקים
    business_revenue = np.array([0.0, 0.0, 1770.0, 0.0, 1200.0, 0.0])

    x = np.arange(len(categories))  # מיקומי העמודות
    width = 0.6  # רוחב העמודות

    fig, ax = plt.subplots(figsize=(10, 6))

    # יצירת עמודות מצטברות (Stacked Bars)
    p1 = ax.bar(x, economy_revenue, width, label='Economy', color='#3498db', alpha=0.9)
    p2 = ax.bar(x, business_revenue, width, bottom=economy_revenue, label='Business', color='#2ecc71', alpha=0.9)

    # עיצוב הגרף
    ax.set_ylabel('Total Revenue ($)')
    ax.set_title('Revenue by Manufacturer & Airplane Size (Split by Class)')
    ax.set_xticks(x)
    ax.set_xticklabels(categories, rotation=15)
    ax.legend()

    # הוספת תוויות מספרים על העמודות
    ax.bar_label(p1, label_type='center', color='white', fmt='%.0f')
    ax.bar_label(p2, label_type='center', color='white', fmt='%.0f')

    plt.tight_layout()
    return _save_and_close(fig, "revenue_chart.png")

# ==========================================
# גרף 2: אחוז ניצולת מטוסים (Utilization Rate)
# ==========================================

def plot_utilization_chart():
    data = [
        {"Month": 1, "Rate": 60.00},
        {"Month": 2, "Rate": 25.00},
        {"Month": 9, "Rate": 25.00},
        {"Month": 10, "Rate": 25.00},
        {"Month": 11, "Rate": 0.00},
    ]

    df = pd.DataFrame(data).sort_values("Month")

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(
        df["Month"],
        df["Rate"],
        marker="o",
        linestyle="-",
        color="#8e44ad",
        linewidth=2,
        markersize=8,
    )

    ax.set_xticks(np.arange(1, 13, 1))
    ax.set_xlim(0.5, 12.5)
    ax.set_ylim(0, max(100, df["Rate"].max() * 1.2))

    ax.set_title("Monthly Purchase Cancellation Rate (%) - Trend Analysis", fontsize=16)
    ax.set_xlabel("Month (1=Jan, 12=Dec)", fontsize=12)
    ax.set_ylabel("Cancellation Rate (%)", fontsize=12)

    ax.grid(True, linestyle="--", alpha=0.7)

    for x, y in zip(df["Month"], df["Rate"]):
        ax.annotate(
            f"{y:.0f}%",
            (x, y),
            textcoords="offset points",
            xytext=(0, 10),
            ha="center",
            fontsize=10,
            fontweight="bold",
        )

    plt.tight_layout()
    return _save_and_close(fig, "utilization_chart.png")


if __name__ == "__main__":
    print("Generating Revenue Chart...")
    revenue_path = plot_revenue_chart()
    print(f"Saved revenue chart to {revenue_path}")

    print("\nGenerating Utilization Chart...")
    utilization_path = plot_utilization_chart()
    print(f"Saved utilization chart to {utilization_path}")