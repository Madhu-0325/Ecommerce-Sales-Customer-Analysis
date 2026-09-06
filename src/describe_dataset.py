import pandas as pd

df = pd.read_csv(r'D:\Ecommerce_sales_customer_analysis\data\Ecommerce_sales.csv')

cat_map = {0:'Electronics',1:'Clothing',2:'Home & Garden',3:'Books',4:'Sports',5:'Beauty',6:'Toys',7:'Food'}
channel_map = {0:'Organic',1:'Paid Search',2:'Social Media',3:'Email',4:'Direct',5:'Referral'}
device_map = {0:'Desktop',1:'Mobile',2:'Tablet'}
payment_map = {0:'Credit Card',1:'Debit Card',2:'PayPal',3:'Bank Transfer',4:'Cash on Delivery',5:'Wallet'}
season_map = {0:'Winter',1:'Spring',2:'Summer',3:'Fall'}
weekday_map = {0:'Sun',1:'Mon',2:'Tue',3:'Wed',4:'Thu',5:'Fri',6:'Sat'}

df['cat'] = df['product_category'].map(cat_map)
df['ch'] = df['marketing_channel'].map(channel_map)
df['dev'] = df['device_type'].map(device_map)

print('=== WHAT IS THIS DATASET? ===')
print('This is a MULTI-PRODUCT E-COMMERCE PLATFORM dataset')
print('covering one full year (Jan-Dec 2024) of customer sessions.\n')

print('=== PRODUCT CATEGORIES (8 types) ===')
cat = df['cat'].value_counts()
for c, n in cat.items():
    rev = df[df['cat']==c]['revenue'].sum()
    print(f'  {c:15}: {n:5} sessions | Revenue: ${rev:>12,.2f}')

print('\n=== PRICE RANGES BY CATEGORY ===')
for c in sorted(df['cat'].unique()):
    sub = df[df['cat']==c]
    print(f'  {c:15}: ${sub["unit_price"].min():.0f} - ${sub["unit_price"].max():.0f} (avg ${sub["unit_price"].mean():.0f})')

print('\n=== BUSINESS TYPE ===')
print('  - B2C (Business to Consumer) platform')
print('  - Sells physical products across 8 categories')
print('  - Price range: $50 - $2,000 per item')
print('  - Average order: ~$1,800')
print('  - Accepts 6 payment methods')
print('  - 225 geographic locations')
print('  - 6 marketing channels')

print('\n=== CUSTOMER BEHAVIOR ===')
print(f'  Sessions with cart adds: {(df["added_to_cart"]==1).sum()} ({(df["added_to_cart"]==1).mean()*100:.0f}%)')
print(f'  Sessions with purchase:  {df["purchased"].sum()} ({df["purchased"].mean()*100:.0f}%)')
print(f'  Sessions abandoned cart: {df["cart_abandoned"].sum()} ({df["cart_abandoned"].mean()*100:.0f}%)')
print(f'  Avg pages per session:   {df["pages_viewed"].mean():.1f}')
print(f'  Avg time on site:        {df["time_on_site_sec"].mean():.0f} seconds')
