import pandas as pd

df = pd.read_csv(r'D:\Ecommerce_sales_customer_analysis\data\Ecommerce_sales.csv')

print('=== SHAPE ===')
print(f'{df.shape[0]:,} rows x {df.shape[1]} columns')

print('\n=== COLUMNS ===')
for i, col in enumerate(df.columns, 1):
    print(f'{i:2}. {col:30} | dtype: {str(df[col].dtype):7} | unique: {df[col].nunique():6} | null: {df[col].isnull().sum()}')

print('\n=== SAMPLE DATA (5 rows) ===')
print(df.head().to_string())

print('\n=== DATA QUALITY ===')
print(f'Duplicates: {df.duplicated().sum()}')
print(f'Total nulls: {df.isnull().sum().sum()}')

print('\n=== NUMERIC STATS ===')
print(df.describe().round(2).to_string())

rev_zero = (df['revenue'] == 0).sum()
rev_pos = (df['revenue'] > 0).sum()
print('\n=== REVENUE DISTRIBUTION ===')
print(f'Revenue = 0: {rev_zero} ({rev_zero/len(df)*100:.1f}%)')
print(f'Revenue > 0: {rev_pos} ({rev_pos/len(df)*100:.1f}%)')
print(f'Max revenue: ${df["revenue"].max():,.2f}')
print(f'Avg revenue (purchases only): ${df[df["purchased"]==1]["revenue"].mean():,.2f}')

purch_1 = (df['purchased'] == 1).sum()
purch_0 = (df['purchased'] == 0).sum()
print('\n=== PURCHASE DISTRIBUTION ===')
print(f'Purchased=1: {purch_1} ({purch_1/len(df)*100:.1f}%)')
print(f'Purchased=0: {purch_0} ({purch_0/len(df)*100:.1f}%)')

df['visit_date'] = pd.to_datetime(df['visit_date'], format='%d-%m-%Y')
print('\n=== DATE RANGE ===')
print(f'From: {df["visit_date"].min().date()}')
print(f'To:   {df["visit_date"].max().date()}')
print(f'Unique dates: {df["visit_date"].dt.date.nunique()}')

print('\n=== CATEGORICAL COLUMNS ===')
for col in ['device_type','user_type','marketing_channel','product_category','payment_method','visit_season','session_duration_bucket']:
    print(f'{col}: {sorted(df[col].unique())}')

print('\n=== CORRELATIONS WITH PURCHASE ===')
num_cols = ['unit_price','quantity','discount_percent','pages_viewed','time_on_site_sec','added_to_cart','rating']
for col in num_cols:
    corr = df[col].corr(df['purchased'])
    print(f'  {col:25}: {corr:+.3f}')
