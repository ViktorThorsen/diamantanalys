import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import base64
import streamlit.components.v1 as components
import io
import numpy as np

def clean_diamond_data(uploaded_file):
    """
    Läser in och validerar en CSV-fil med diamantdata.

    Funktionens syfte är att säkerställa att filen innehåller alla nödvändiga kolumner,
    samt att rensa bort ogiltiga eller orimliga värden. Den beräknar även skillnaden
    mellan faktiskt och beräknat djup för att filtrera bort inkonsekvent data.

    Parametrar:
    - uploaded_file: En filuppladdningsinstans från Streamlit (eller mock-fil i tester).

    Returnerar:
    - df (DataFrame): Den rensade datan.
    - error (str eller None): Ett felmeddelande om något gick fel, annars None.
    """
    if uploaded_file is None:
        return None, None

    try:
        content = uploaded_file.read()

        decoded = content.decode("utf-8")
        if "\x00" in decoded:
            raise ValueError("Innehåller ogiltiga binära tecken.")
    except Exception:
        return None, "Kunde inte läsa CSV-filen – kontrollera att filen är korrekt kodad som text."

    try:
        df = pd.read_csv(io.StringIO(decoded), sep=None, engine='python')
        if 'index' not in df.columns:
            df.reset_index(inplace=True)
    except Exception:
        return None, "Kunde inte läsa CSV-filen – kontrollera formatet."

    required_columns = ['index', 'cut', 'color', 'clarity', 'price', 'carat', 'x', 'y', 'z', 'depth']
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        return None, f"CSV-filen saknar följande kolumner: {', '.join(missing)}"

    df = df.dropna(subset=required_columns)
    df = df[(df['x'] > 0) & (df['y'] > 0) & (df['z'] > 0)]
    df = df[(df['x'] <= 15) & (df['y'] <= 15) & (df['z'] <= 15)]
    df = df[~((df['carat'] < 1) & (df['z'] > 10))]
    df['depth_calc'] = (df['z'] / ((df['x'] + df['y']) / 2)) * 100
    df['depth_diff'] = abs(df['depth_calc'] - df['depth'])
    df = df[df['depth_diff'] <= 1]

    allowed_cuts = ["Ideal", "Premium", "Very Good", "Good", "Fair"]
    allowed_colors = ['D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L',
                      'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U',
                      'V', 'W', 'X', 'Y', 'Z']
    allowed_clarities = ['FL', 'IF', 'VVS1', 'VVS2', 'VS1', 'VS2',
                         'SI1', 'SI2', 'SI3', 'I1', 'I2', 'I3']

    df = df[df['cut'].isin(allowed_cuts)]
    df = df[df['color'].isin(allowed_colors)]
    df = df[df['clarity'].isin(allowed_clarities)]

    return df, None

def cheap_diamonds_by_carat(df, group_columns, price_column="price", carat_column="carat"):
    """
    Identifierar prisvärda diamanter genom att jämföra varje diamants pris med medianpriset
    för andra diamanter med samma egenskaper (inkl. carat).

    Returnerar en DataFrame med diamanter vars pris är under medianen för sin grupp.
    """
    df = df[df[carat_column] <= 1.0].copy()
    df['carat_bin'] = pd.cut(df[carat_column], bins=np.arange(0.1, 1, 0.01))

    result = []
    groups = df.groupby(group_columns + ['carat_bin'])

    for name, group in groups:
        if len(group) < 10:
            continue
        median_price = group[price_column].median()
        cheap = group[group[price_column] < median_price].copy()

        kategori = ",".join(str(x) for x in name if not isinstance(x, pd.Interval))
        cheap["kategori"] = kategori
        cheap["med_price"] = median_price
        cheap["un_med_usd"] = (median_price - cheap[price_column]).round(2)
        cheap["un_med_percent"] = ((median_price - cheap[price_column]) / median_price * 100).round(1)

        cheap["color"] = group.loc[cheap.index, "color"].values
        cheap["clarity"] = group.loc[cheap.index, "clarity"].values
        cheap["cut"] = group.loc[cheap.index, "cut"].values
        cheap["carat_bin"] = group.loc[cheap.index, "carat_bin"].values

        result.append(cheap)

    return pd.concat(result, ignore_index=True) if result else pd.DataFrame()



def calculate_volatility_groups(df, group_column):
    df = df[(df['carat'] >= 0.1) & (df['carat'] <= 1.0)].copy()
    df['carat_bin'] = pd.cut(df['carat'], bins=np.arange(0.1, 1, 0.01))

    grouped = df.groupby(['carat_bin', group_column], observed=False)['price'].agg(['mean', 'std'])
    grouped['variation'] = grouped['std'] / grouped['mean']
    grouped = grouped.dropna()

    sorted_grouped = grouped.sort_values(['carat_bin', 'variation'], ascending=[True, False])
    top2_per_bin = sorted_grouped.groupby(level='carat_bin').head(3)

    frekvens = top2_per_bin.reset_index()[group_column].value_counts()

    return frekvens.head(3)

def main():
    from DiamondUI import run_app
    run_app(clean_diamond_data)

if __name__ == "__main__":
    main()