import pandas as pd
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

DEVICE_MAP = {0: 'Desktop', 1: 'Mobile', 2: 'Tablet'}
USER_MAP = {0: 'Returning', 1: 'New'}
CHANNEL_MAP = {0: 'Organic', 1: 'Paid Search', 2: 'Social Media', 3: 'Email', 4: 'Direct', 5: 'Referral'}
CATEGORY_MAP = {0: 'Electronics', 1: 'Clothing', 2: 'Home & Garden', 3: 'Books', 4: 'Sports', 5: 'Beauty', 6: 'Toys', 7: 'Food'}
PAYMENT_MAP = {0: 'Credit Card', 1: 'Debit Card', 2: 'PayPal', 3: 'Bank Transfer', 4: 'Cash on Delivery', 5: 'Wallet'}
SEASON_MAP = {0: 'Winter', 1: 'Spring', 2: 'Summer', 3: 'Fall'}


def load_data(filename='Ecommerce_sales.csv'):
    filepath = os.path.join(DATA_DIR, filename)
    df = pd.read_csv(filepath)
    df['visit_date'] = pd.to_datetime(df['visit_date'], format='%d-%m-%Y')
    return df


def add_labels(df):
    df = df.copy()
    df['device_label'] = df['device_type'].map(DEVICE_MAP)
    df['user_label'] = df['user_type'].map(USER_MAP)
    df['channel_label'] = df['marketing_channel'].map(CHANNEL_MAP)
    df['category_label'] = df['product_category'].map(CATEGORY_MAP)
    df['payment_label'] = df['payment_method'].map(PAYMENT_MAP)
    df['season_label'] = df['visit_season'].map(SEASON_MAP)
    return df


def get_kpis(df):
    total_sessions = len(df)
    total_purchases = int(df['purchased'].sum())
    conversion_rate = total_purchases / total_sessions * 100
    total_revenue = df['revenue'].sum()
    avg_order_value = df[df['purchased'] == 1]['revenue'].mean()
    return {
        'total_sessions': total_sessions,
        'total_purchases': total_purchases,
        'conversion_rate': round(conversion_rate, 2),
        'total_revenue': round(total_revenue, 2),
        'avg_order_value': round(avg_order_value, 2),
    }


def get_segment(row):
    if row['total_purchases'] >= 3 and row['total_revenue'] > 5000:
        return 'Champions'
    elif row['total_purchases'] >= 2 and row['total_revenue'] > 2000:
        return 'Loyal'
    elif row['total_purchases'] >= 1 and row['total_revenue'] > 0:
        return 'Active'
    elif row['total_sessions'] >= 3:
        return 'At Risk'
    return 'New/Lost'


def segment_customers(df):
    customer_df = df.groupby('customer_id').agg(
        total_sessions=('session_id', 'count'),
        total_purchases=('purchased', 'sum'),
        total_revenue=('revenue', 'sum'),
        avg_pages=('pages_viewed', 'mean'),
        avg_time=('time_on_site_sec', 'mean'),
        favorite_category=('category_label', lambda x: x.mode()[0] if len(x.mode()) > 0 else 'Unknown'),
        primary_device=('device_label', lambda x: x.mode()[0] if len(x.mode()) > 0 else 'Unknown')
    ).reset_index()
    customer_df['conversion_rate'] = (customer_df['total_purchases'] / customer_df['total_sessions'] * 100).round(1)
    customer_df['segment'] = customer_df.apply(get_segment, axis=1)
    return customer_df


if __name__ == '__main__':
    df = load_data()
    df = add_labels(df)
    kpis = get_kpis(df)
    print("KPIs:", kpis)
    customer_df = segment_customers(df)
    print("\nSegments:", customer_df['segment'].value_counts().to_dict())
