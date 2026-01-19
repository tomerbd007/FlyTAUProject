"""Chart generation for reports - creates PNG images with our brand colors."""
import io
import base64
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for server-side rendering
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from typing import List, Dict, Optional, Tuple

# FLYTAU Brand Colors
BRAND_COLORS = {
    'primary': '#1a3a52',
    'secondary': '#2d5a7b',
    'accent': '#004b71',
    'light': '#4b6a82',
    'success': '#1f7a4d',
    'warning': '#856404',
    'danger': '#c0392b',
    'gray': '#5b6d81',
    'light_gray': '#e0e0e0',
    'background': '#f8f9fa',
}

# Color palette for charts (multiple data series)
CHART_PALETTE = [
    '#1a3a52',  # Primary dark blue
    '#2d5a7b',  # Secondary blue
    '#4b6a82',  # Light blue
    '#1f7a4d',  # Green
    '#856404',  # Gold/warning
    '#c0392b',  # Red
    '#6c5ce7',  # Purple
    '#00b894',  # Teal
]


def _fig_to_base64(fig: plt.Figure) -> str:
    """Turns a matplotlib figure into a base64 string we can embed in HTML."""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=120, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    plt.close(fig)
    return f"data:image/png;base64,{img_base64}"


def _apply_brand_style(ax: plt.Axes, title: str = None):
    """Makes the chart look consistent with our brand styling."""
    ax.set_facecolor('white')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(BRAND_COLORS['light_gray'])
    ax.spines['bottom'].set_color(BRAND_COLORS['light_gray'])
    ax.tick_params(colors=BRAND_COLORS['gray'], labelsize=9)
    if title:
        ax.set_title(title, fontsize=12, fontweight='bold', 
                     color=BRAND_COLORS['primary'], pad=15)


def create_donut_chart(value: float, max_value: float = 100, 
                       title: str = None, label: str = None) -> str:
    """
    Create a donut/gauge chart showing a single percentage value.
    
    Args:
        value: The value to display (0-100 for percentage)
        max_value: Maximum value (default 100)
        title: Chart title
        label: Label for the center value
    
    Returns:
        Base64-encoded PNG image string
    """
    fig, ax = plt.subplots(figsize=(4, 4))
    
    # Calculate percentages
    pct = min(value / max_value * 100, 100) if max_value > 0 else 0
    remaining = 100 - pct
    
    # Create donut
    colors = [BRAND_COLORS['primary'], BRAND_COLORS['light_gray']]
    wedges, _ = ax.pie([pct, remaining], colors=colors, startangle=90,
                       wedgeprops=dict(width=0.4, edgecolor='white'))
    
    # Center text
    center_text = f"{value:.1f}%"
    ax.text(0, 0.05, center_text, ha='center', va='center', 
            fontsize=24, fontweight='bold', color=BRAND_COLORS['primary'])
    if label:
        ax.text(0, -0.2, label, ha='center', va='center', 
                fontsize=10, color=BRAND_COLORS['gray'])
    
    if title:
        ax.set_title(title, fontsize=12, fontweight='bold', 
                     color=BRAND_COLORS['primary'], pad=10)
    
    ax.set_aspect('equal')
    fig.tight_layout()
    
    return _fig_to_base64(fig)


def create_bar_chart(labels: List[str], values: List[float], 
                     title: str = None, xlabel: str = None, 
                     ylabel: str = None, horizontal: bool = False,
                     color: str = None, value_format: str = '{:.1f}') -> str:
    """
    Create a simple bar chart.
    
    Args:
        labels: Bar labels
        values: Bar values
        title: Chart title
        xlabel: X-axis label
        ylabel: Y-axis label
        horizontal: If True, create horizontal bar chart
        color: Bar color (uses brand primary if not specified)
        value_format: Format string for value labels
    
    Returns:
        Base64-encoded PNG image string
    """
    fig, ax = plt.subplots(figsize=(8, max(4, len(labels) * 0.4) if horizontal else 5))
    
    bar_color = color or BRAND_COLORS['primary']
    
    if horizontal:
        y_pos = range(len(labels))
        bars = ax.barh(y_pos, values, color=bar_color, edgecolor='white', height=0.6)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(labels)
        ax.invert_yaxis()
        
        # Value labels
        for bar, val in zip(bars, values):
            ax.text(bar.get_width() + max(values) * 0.02, bar.get_y() + bar.get_height()/2,
                    value_format.format(val), va='center', fontsize=9, 
                    color=BRAND_COLORS['gray'])
    else:
        x_pos = range(len(labels))
        bars = ax.bar(x_pos, values, color=bar_color, edgecolor='white', width=0.6)
        ax.set_xticks(x_pos)
        ax.set_xticklabels(labels, rotation=45, ha='right')
        
        # Value labels
        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
                    value_format.format(val), ha='center', va='bottom', 
                    fontsize=9, color=BRAND_COLORS['gray'])
    
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=10, color=BRAND_COLORS['gray'])
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=10, color=BRAND_COLORS['gray'])
    
    _apply_brand_style(ax, title)
    fig.tight_layout()
    
    return _fig_to_base64(fig)


def create_grouped_bar_chart(categories: List[str], groups: List[str],
                             data: Dict[str, List[float]], title: str = None,
                             xlabel: str = None, ylabel: str = None,
                             value_format: str = '${:,.0f}') -> str:
    """
    Create a grouped bar chart for comparing multiple series.
    
    Args:
        categories: Category labels (x-axis groups)
        groups: Group names (legend items)
        data: Dict mapping group names to their values for each category
        title: Chart title
        xlabel: X-axis label
        ylabel: Y-axis label
        value_format: Format string for value labels
    
    Returns:
        Base64-encoded PNG image string
    """
    fig, ax = plt.subplots(figsize=(max(8, len(categories) * 1.5), 5))
    
    x = range(len(categories))
    n_groups = len(groups)
    width = 0.8 / n_groups
    
    for i, (group_name, group_values) in enumerate(data.items()):
        offset = (i - n_groups/2 + 0.5) * width
        bars = ax.bar([xi + offset for xi in x], group_values, width,
                      label=group_name, color=CHART_PALETTE[i % len(CHART_PALETTE)],
                      edgecolor='white')
    
    ax.set_xticks(x)
    ax.set_xticklabels(categories, rotation=45, ha='right')
    ax.legend(loc='upper right', frameon=False)
    
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=10, color=BRAND_COLORS['gray'])
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=10, color=BRAND_COLORS['gray'])
    
    _apply_brand_style(ax, title)
    fig.tight_layout()
    
    return _fig_to_base64(fig)


def create_stacked_bar_chart(labels: List[str], data: Dict[str, List[float]],
                             title: str = None, xlabel: str = None, 
                             ylabel: str = None, horizontal: bool = True) -> str:
    """
    Create a stacked bar chart.
    
    Args:
        labels: Bar labels
        data: Dict mapping stack names to their values
        title: Chart title
        xlabel: X-axis label
        ylabel: Y-axis label
        horizontal: If True, create horizontal stacked bar chart
    
    Returns:
        Base64-encoded PNG image string
    """
    fig, ax = plt.subplots(figsize=(10, max(4, len(labels) * 0.5)) if horizontal else (8, 5))
    
    stack_names = list(data.keys())
    n_bars = len(labels)
    
    if horizontal:
        y_pos = range(n_bars)
        left = [0] * n_bars
        
        for i, (stack_name, values) in enumerate(data.items()):
            color = CHART_PALETTE[i % len(CHART_PALETTE)]
            ax.barh(y_pos, values, left=left, label=stack_name, 
                    color=color, edgecolor='white', height=0.6)
            left = [l + v for l, v in zip(left, values)]
        
        ax.set_yticks(y_pos)
        ax.set_yticklabels(labels)
        ax.invert_yaxis()
    else:
        x_pos = range(n_bars)
        bottom = [0] * n_bars
        
        for i, (stack_name, values) in enumerate(data.items()):
            color = CHART_PALETTE[i % len(CHART_PALETTE)]
            ax.bar(x_pos, values, bottom=bottom, label=stack_name,
                   color=color, edgecolor='white', width=0.6)
            bottom = [b + v for b, v in zip(bottom, values)]
        
        ax.set_xticks(x_pos)
        ax.set_xticklabels(labels, rotation=45, ha='right')
    
    ax.legend(loc='upper right', frameon=False)
    
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=10, color=BRAND_COLORS['gray'])
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=10, color=BRAND_COLORS['gray'])
    
    _apply_brand_style(ax, title)
    fig.tight_layout()
    
    return _fig_to_base64(fig)


def create_line_chart(labels: List[str], values: List[float],
                      title: str = None, xlabel: str = None, 
                      ylabel: str = None, fill: bool = True,
                      marker: bool = True) -> str:
    """
    Create a line chart for trend data.
    
    Args:
        labels: X-axis labels (e.g., months)
        values: Y-axis values
        title: Chart title
        xlabel: X-axis label
        ylabel: Y-axis label
        fill: If True, fill area under the line
        marker: If True, show data point markers
    
    Returns:
        Base64-encoded PNG image string
    """
    fig, ax = plt.subplots(figsize=(10, 5))
    
    x = range(len(labels))
    
    # Plot line
    line_kwargs = {
        'color': BRAND_COLORS['primary'],
        'linewidth': 2.5,
        'marker': 'o' if marker else None,
        'markersize': 8,
        'markerfacecolor': 'white',
        'markeredgecolor': BRAND_COLORS['primary'],
        'markeredgewidth': 2,
    }
    ax.plot(x, values, **line_kwargs)
    
    # Fill area under line
    if fill:
        ax.fill_between(x, values, alpha=0.15, color=BRAND_COLORS['primary'])
    
    # Value labels on markers
    if marker:
        for xi, val in zip(x, values):
            ax.annotate(f'{val:.1f}%', (xi, val), textcoords="offset points",
                        xytext=(0, 10), ha='center', fontsize=9, 
                        color=BRAND_COLORS['gray'])
    
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha='right')
    ax.set_ylim(bottom=0)
    
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=10, color=BRAND_COLORS['gray'])
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=10, color=BRAND_COLORS['gray'])
    
    # Grid
    ax.yaxis.grid(True, linestyle='--', alpha=0.3, color=BRAND_COLORS['light_gray'])
    
    _apply_brand_style(ax, title)
    fig.tight_layout()
    
    return _fig_to_base64(fig)


def create_multi_bar_chart(categories: List[str], 
                           series1_label: str, series1_values: List[float],
                           series2_label: str, series2_values: List[float],
                           title: str = None, xlabel: str = None, 
                           ylabel: str = None) -> str:
    """
    Create a chart with two bar series side by side.
    
    Args:
        categories: Category labels
        series1_label: Label for first series
        series1_values: Values for first series
        series2_label: Label for second series
        series2_values: Values for second series
        title: Chart title
        xlabel: X-axis label
        ylabel: Y-axis label
    
    Returns:
        Base64-encoded PNG image string
    """
    fig, ax = plt.subplots(figsize=(max(8, len(categories) * 1.2), 5))
    
    x = range(len(categories))
    width = 0.35
    
    bars1 = ax.bar([xi - width/2 for xi in x], series1_values, width,
                   label=series1_label, color=BRAND_COLORS['primary'], edgecolor='white')
    bars2 = ax.bar([xi + width/2 for xi in x], series2_values, width,
                   label=series2_label, color=BRAND_COLORS['danger'], edgecolor='white')
    
    ax.set_xticks(x)
    ax.set_xticklabels(categories, rotation=45, ha='right')
    ax.tick_params(axis='x', pad=10)  # Add gap between labels and bars
    ax.legend(loc='upper right', frameon=False)
    
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=10, color=BRAND_COLORS['gray'])
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=10, color=BRAND_COLORS['gray'])
    
    _apply_brand_style(ax, title)
    fig.tight_layout()
    
    return _fig_to_base64(fig)
