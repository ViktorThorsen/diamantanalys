import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.cm as cm

def clean_diamond_data(df):
    total_start = df.shape[0]
    removed = {}

    # Rensar ut nullvärden
    before = df.shape[0]
    df = df.dropna(subset=['index', 'cut', 'color', 'clarity', 'price', 'carat', 'x', 'y', 'z', 'depth'])
    removed["Saknade värden"] = before - df.shape[0]

    # Nollvärden i numeriska kolumner
    numeric_cols = ['carat', 'depth', 'table', 'price', 'x', 'y', 'z']
    before = df.shape[0]
    for col in numeric_cols:
        df = df[df[col] > 0]
    removed["Nollvärden i numeriska kolumner"] = before - df.shape[0]

    # Extrema mått
    before = df.shape[0]
    df = df[(df['x'] <= 15) & (df['y'] <= 15) & (df['z'] <= 15)]
    removed["Extrema mått (>15 mm)"] = before - df.shape[0]

    # Oproportionerligt djup
    before = df.shape[0]
    df = df[~((df['carat'] < 1) & (df['z'] > 10))]
    removed["Misstänkt djup (carat < 1 & z > 10)"] = before - df.shape[0]

    # Depth-avvikelse
    df['depth_calc'] = (df['z'] / ((df['x'] + df['y']) / 2)) * 100
    df['depth_diff'] = abs(df['depth_calc'] - df['depth'])
    before = df.shape[0]
    df = df[df['depth_diff'] <= 1]
    removed[">1% avvikelse i depth"] = before - df.shape[0]

    # Sammanställning
    print("Sammanställning av borttagna rader:")
    for reason, quant in removed.items():
        print(f"- {reason}: {quant} rader")

    total_borttagna = total_start - df.shape[0]
    print(f"\nTotalt borttagna rader: {total_borttagna}")
    print(f"Rader kvar: {df.shape[0]}")

    return df


df = clean_diamond_data(pd.read_csv("diamonds.csv", sep=";"))

#-------------------------------------------------------------

fig, ax = plt.subplots(1, 2, figsize=(14, 6))

ax[0].scatter(df['carat'], df['price'], alpha=0.2)
ax[0].set_title('Pris i förhållande till vikt (carat)')
ax[0].set_xlabel('Carat')
ax[0].set_ylabel('Pris (USD)')
ax[0].grid(True)

ax[1].hist(df['carat'], bins=30, color='skyblue', edgecolor='black')
ax[1].set_title('Histogram över carat')
ax[1].set_xlabel('Carat')
ax[1].set_ylabel('Antal diamanter')
ax[1].grid(True)

plt.tight_layout()
plt.show()

#-------------------------------------------------------------

nordic_df = df[(df['carat'] >= 0.1) & (df['carat'] <= 1.0)]

plt.figure(figsize=(10, 6))
plt.scatter(nordic_df['carat'], nordic_df['price'], alpha=0.3, color='teal')
plt.title('Pris i förhållande till vikt (0.1–1.0 carat) – Nordiska preferenser')
plt.xlabel('Carat')
plt.ylabel('Pris (USD)')
plt.grid(True)
plt.tight_layout()
plt.show()

#-------------------------------------------------------------

nordic_df = nordic_df.copy()

# Grupperar i 0.1 carat
nordic_df['carat_bin'] = pd.cut(nordic_df['carat'], bins=np.arange(0.1, 1.05, 0.1))

# Gruppera på caratintervall + färg, och beräkna variation
volatility = nordic_df.groupby(['carat_bin', 'color'], observed=False)['price'].agg(['mean', 'std', 'min', 'max'])
volatility['variation'] = volatility['std'] / volatility['mean']
volatility = volatility.dropna()
volatility_sorted = volatility.sort_values(by=['carat_bin', 'variation'], ascending=[True, False])

# Tar top 2 för varje carat_bin
top2_per_bin = volatility_sorted.groupby(level='carat_bin', observed=True).head(2)

topp2_färger = färg_frekvens.head(2)

print("Topp 2 vanligaste färger bland mest volatila per carat-intervall:")
print(topp2_färger)

#-------------------------------------------------------------

nordic_df = nordic_df.copy()

if 'carat_bin' not in nordic_df.columns:
    nordic_df['carat_bin'] = pd.cut(nordic_df['carat'], bins=np.arange(0.1, 1.05, 0.1))

clarity_volatility = nordic_df.groupby(['carat_bin', 'clarity'], observed=False)['price'].agg(['mean', 'std', 'min', 'max'])
clarity_volatility['variation'] = clarity_volatility['std'] / clarity_volatility['mean']
clarity_volatility = clarity_volatility.dropna()

clarity_sorted = clarity_volatility.sort_values(by=['carat_bin', 'variation'], ascending=[True, False])

top2_per_bin_clarity = clarity_sorted.groupby(level='carat_bin', observed=True).head(2)

clarity_frekvens = top2_per_bin_clarity.reset_index()['clarity'].value_counts()

topp2_clarity = clarity_frekvens.head(2)

print("Topp 2 vanligaste clarity-värden bland mest volatila per carat-intervall:")
print(topp2_clarity)

#-------------------------------------------------------------

nordic_df = nordic_df.copy()

if 'carat_bin' not in nordic_df.columns:
    nordic_df['carat_bin'] = pd.cut(nordic_df['carat'], bins=np.arange(0.1, 1.05, 0.1))

cut_volatility = nordic_df.groupby(['carat_bin', 'cut'], observed=False)['price'].agg(['mean', 'std', 'min', 'max'])
cut_volatility['variation'] = cut_volatility['std'] / cut_volatility['mean']
cut_volatility = cut_volatility.dropna()

cut_sorted = cut_volatility.sort_values(by=['carat_bin', 'variation'], ascending=[True, False])

top2_per_bin_cut = cut_sorted.groupby(level='carat_bin', observed=True).head(2)

cut_frekvens = top2_per_bin_cut.reset_index()['cut'].value_counts()

topp2_cut = cut_frekvens.head(2)

print("Topp 2 vanligaste cut-nivåer bland mest volatila per carat-intervall:")
print(topp2_cut)

#-------------------------------------------------------------

filtered = nordic_df[
    (nordic_df['color'].isin(['D', 'E'])) &
    (nordic_df['clarity'].isin(['IF', 'VVS2']))
]

kombinationer = filtered.groupby(['color', 'clarity', 'cut']).size().reset_index(name='antal')
print(kombinationer)

#-------------------------------------------------------------

def cheap_diamonds_by_carat(df, group_columns, price_column="price", carat_column="carat"):
    df = df[df[carat_column] <= 1.0].copy()

    result = []
    groups = df.groupby(group_columns)

    for name, group in groups:
        group = group.copy()
        group['carat_round'] = (group[carat_column] * 10).round() / 10

        for carat_val, sub_group in group.groupby('carat_round'):
            if len(sub_group) < 10:
                continue

            median_price = sub_group[price_column].median()
            cheap = sub_group[sub_group[price_column] < median_price].copy()
            cheap["kategori"] = f"{name[0]},{name[1]},{name[2]}"
            cheap["med_price"] = median_price  # 👈 Lägg till detta
            cheap["un_med_usd"] = (median_price - cheap[price_column]).round(2)
            cheap["un_med_percent"] = ((median_price - cheap[price_column]) / median_price * 100).round(1)
            result.append(cheap)

    if result:
        return pd.concat(result, ignore_index=True)
    else:
        return pd.DataFrame()
cheap = cheap_diamonds_by_carat(filtered, ['color', 'clarity', 'cut'])

cheap = cheap.sort_values(by="un_med_usd", ascending=False)

top50 = cheap[['index','price','med_price', 'un_med_usd', 'un_med_percent', 'kategori']].head(50)
print(top50)

#-------------------------------------------------------------

# Färger (tab20 interpolerad till 50 färger)
cmap = plt.colormaps.get_cmap('tab20')
colors = [cmap(i / 50) for i in range(50)]

# Välj tydligt vad vi vill ha med i merge
top50_full = nordic_df[['index', 'carat', 'price']].merge(
    top50[['index', 'med_price', 'un_med_percent', 'kategori']], on='index', how='inner'
)

plt.figure(figsize=(12, 7))
plt.scatter(nordic_df['carat'], nordic_df['price'], alpha=0.3, color='lightgray', label='Alla diamanter')

# Rita linjer + prickar
for i, (_, row) in enumerate(top50_full.iterrows()):
    color = colors[i]
    carat = row['carat']
    price = row['price']
    median_price = row['med_price']
    idx = int(row['index'])

    plt.plot([carat, carat], [price, median_price], color=color, linestyle='--', linewidth=1)
    plt.scatter(carat, price, color=color, s=60)
    plt.scatter(carat, median_price, color=color, marker='x', s=50)

    plt.annotate(
        text=str(),
        xy=(carat, price),
        xytext=(carat, price + 250 + np.random.uniform(-100, 100)),
        arrowprops=dict(arrowstyle='-', color='gray'),
        fontsize=8,
        color='black',
        ha='center'
    )

plt.title('Diamanter: pris i förhållande till carat (med top 50 och medianlinjer)')
plt.xlabel('Carat')
plt.ylabel('Pris (USD)')
plt.grid(True)
plt.tight_layout()
plt.show()
# Sortera top50 efter procentuell skillnad mot medianen (störst först)
sorted_top50 = top50.sort_values(by='un_med_percent', ascending=False)

# Skriva ut listan
for _, row in sorted_top50.iterrows():
    print(f"ID {int(row['index'])}: {row['kategori']} – {row['price']} USD (−{row['un_med_percent']}% mot median)")

#-------------------------------------------------------------

top50_diamonds = top50.copy()

# (Den här raden gör inget, du kan ta bort den)
# top50_diamonds = top50_diamonds.rename(columns={"un_med_usd": "un_med_usd"})

top50_diamonds['med_price'] = top50_diamonds['price'] + top50_diamonds['un_med_usd']
top50_diamonds['med_price_10pct'] = top50_diamonds['med_price'] * 1.10

top50_diamonds['vinst_median'] = top50_diamonds['med_price'] - top50_diamonds['price']
top50_diamonds['vinst_10pct'] = top50_diamonds['med_price_10pct'] - top50_diamonds['price']

total_investering = top50_diamonds['price'].sum()
total_vinst_median = top50_diamonds['vinst_median'].sum()
total_vinst_10pct = top50_diamonds['vinst_10pct'].sum()

print(f"Total investering (inköpspris för 50 diamanter): ${total_investering:,.2f}")
print(f"Total möjlig vinst vid försäljning till medianpris: ${total_vinst_median:,.2f}")
print(f"Total möjlig vinst vid försäljning till +10% över median: ${total_vinst_10pct:,.2f}")