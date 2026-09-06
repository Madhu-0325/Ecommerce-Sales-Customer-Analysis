import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

REPORTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'reports')
os.makedirs(REPORTS_DIR, exist_ok=True)

sns.set_style('whitegrid')
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 11


def save_fig(name):
    plt.savefig(os.path.join(REPORTS_DIR, name), dpi=150, bbox_inches='tight')
    plt.close()


def plot_sales_overview(df):
    purchased = df[df['purchased'] == 1]
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    monthly = purchased.groupby('visit_month')['revenue'].sum()
    axes[0, 0].bar(monthly.index, monthly.values, color=sns.color_palette('viridis', 12))
    axes[0, 0].set_title('Revenue by Month')
    axes[0, 0].set_xlabel('Month')
    axes[0, 0].set_ylabel('Revenue ($)')

    cat_rev = purchased.groupby('category_label')['revenue'].sum().sort_values(ascending=True)
    cat_rev.plot(kind='barh', ax=axes[0, 1], color=sns.color_palette('magma', len(cat_rev)))
    axes[0, 1].set_title('Revenue by Product Category')

    dev_rev = purchased.groupby('device_label')['revenue'].sum()
    axes[1, 0].pie(dev_rev, labels=dev_rev.index, autopct='%1.1f%%', colors=sns.color_palette('Set2'))
    axes[1, 0].set_title('Revenue Share by Device')

    ch_rev = purchased.groupby('channel_label')['revenue'].sum().sort_values(ascending=True)
    ch_rev.plot(kind='barh', ax=axes[1, 1], color=sns.color_palette('coolwarm', len(ch_rev)))
    axes[1, 1].set_title('Revenue by Marketing Channel')

    plt.tight_layout()
    save_fig('sales_overview.png')


def plot_conversion_analysis(df):
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    conv_channel = df.groupby('channel_label')['purchased'].mean() * 100
    conv_channel.sort_values().plot(kind='barh', ax=axes[0, 0], color=sns.color_palette('RdYlGn', len(conv_channel)))
    axes[0, 0].set_title('Conversion Rate by Channel (%)')

    conv_device = df.groupby('device_label')['purchased'].mean() * 100
    conv_device.plot(kind='bar', ax=axes[0, 1], color=sns.color_palette('Set2', len(conv_device)))
    axes[0, 1].set_title('Conversion Rate by Device (%)')

    cart_data = df[df['added_to_cart'] == 1].groupby('category_label')['cart_abandoned'].mean() * 100
    cart_data.sort_values(ascending=True).plot(kind='barh', ax=axes[1, 0], color=sns.color_palette('Reds_r', len(cart_data)))
    axes[1, 0].set_title('Cart Abandonment Rate by Category (%)')

    df[df['purchased'] == 1]['pages_viewed'].hist(ax=axes[1, 1], alpha=0.6, label='Purchased', bins=20, color='green')
    df[df['purchased'] == 0]['pages_viewed'].hist(ax=axes[1, 1], alpha=0.4, label='Not Purchased', bins=20, color='red')
    axes[1, 1].set_title('Pages Viewed Distribution')
    axes[1, 1].legend()

    plt.tight_layout()
    save_fig('conversion_analysis.png')


def plot_correlation(df):
    num_cols = ['unit_price', 'quantity', 'discount_percent', 'discount_amount', 'revenue',
                'pages_viewed', 'time_on_site_sec', 'added_to_cart', 'purchased', 'cart_abandoned', 'rating']
    fig, ax = plt.subplots(figsize=(12, 10))
    corr = df[num_cols].corr()
    mask = __import__('numpy').triu(__import__('numpy').ones_like(corr, dtype=bool))
    sns.heatmap(corr, mask=mask, annot=True, fmt='.2f', cmap='coolwarm', center=0, ax=ax, square=True)
    ax.set_title('Feature Correlation Heatmap')
    plt.tight_layout()
    save_fig('correlation_heatmap.png')


if __name__ == '__main__':
    from data_loader import load_data, add_labels
    df = load_data()
    df = add_labels(df)
    plot_sales_overview(df)
    plot_conversion_analysis(df)
    plot_correlation(df)
    print("All charts saved to reports/")
