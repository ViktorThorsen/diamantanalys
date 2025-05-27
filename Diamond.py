import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import base64
import streamlit.components.v1 as components
import io
import numpy as np

def set_background(image_file):
    with open(image_file, "rb") as image:
        encoded = base64.b64encode(image.read()).decode()
        st.markdown(
            """
            <style>
            .stTabs [role="tablist"] {
                justify-content: center;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: url("data:image/png;base64,{encoded}");
                background-size: cover;
                background-position: center;
                background-attachment: fixed;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )


set_background("diamondBackground.jpg")


st.sidebar.markdown("## Ladda upp diamantdata (CSV)")
uploaded_file = st.sidebar.file_uploader("Välj en fil", type=["csv"])

@st.cache_data
def clean_diamond_data(uploaded_file):
    if uploaded_file is None:
        return None

    df = pd.read_csv(uploaded_file, sep=None, engine='python')
    df.reset_index(inplace=True)

    required_columns = ['index', 'cut', 'color', 'clarity', 'price', 'carat', 'x', 'y', 'z', 'depth']
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        st.error(f"Filen saknar följande kolumner: {', '.join(missing)}")
        return None

    df = df.dropna(subset=required_columns)
    df = df[(df['x'] > 0) & (df['y'] > 0) & (df['z'] > 0)]
    df = df[(df['x'] <= 15) & (df['y'] <= 15) & (df['z'] <= 15)]
    df = df[~((df['carat'] < 1) & (df['z'] > 10))]
    df['depth_calc'] = (df['z'] / ((df['x'] + df['y']) / 2)) * 100
    df['depth_diff'] = abs(df['depth_calc'] - df['depth'])
    df = df[df['depth_diff'] <= 1]
    return df


df = clean_diamond_data(uploaded_file)

if df is None:
    st.warning("⬅️ Vänligen ladda upp en korrekt CSV-fil för att visa grafer.")
    st.stop()


st.markdown(
    """
    <style>
    header.stAppHeader:before {
        content: "💎 Diamonds";
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        color: white;
        font-size: 20px;
        font-weight: bold;
        font-family: 'Segoe UI', sans-serif;
        z-index: 99999;
        pointer-events: none;
    }
    </style>
    """,
    unsafe_allow_html=True
)

tab1, tab2, tab3 = st.tabs(["Pris vs Karat", "Antal Diamanter","Beräkning"])

with tab1:
    fig = px.scatter(
        df,
        x='carat',
        y='price',
        hover_data=['cut', 'color', 'clarity', 'price'],
        title='Pris i förhållande till Karat',
        opacity=0.4
    )
    fig.update_traces(marker=dict(color='lightskyblue'))
    fig.update_layout(
        title={'x': 0.5, 'xanchor': 'center', 'font': {'color': 'white'}},
        paper_bgcolor='#1e1e1e',
        plot_bgcolor='#1e1e1e',
        font=dict(color='white'),
        xaxis=dict(color='white', gridcolor='rgba(255,255,255,0.2)'),
        yaxis=dict(color='white', gridcolor='rgba(255,255,255,0.2)'),
    )

    html_str = fig.to_html(include_plotlyjs='cdn')
    rounded_html = f"""
    <div style="
        background-color: #1e1e1e;
        border-radius: 20px;
        padding: 15px;
        overflow: hidden;
        box-shadow: 0 10px 10px rgba(0,0,0,0.5);
    ">
        {html_str}
    </div>
    """
    components.html(rounded_html, height=600, scrolling=False)

with tab2:
    st.subheader("Antal Diamanter")

    fig, ax = plt.subplots(figsize=(10, 5), facecolor="#1e1e1e")
    ax.set_facecolor("#1e1e1e")
    ax.hist(df['carat'], bins=30, color='lightskyblue', edgecolor='black')
    
    ax.set_xlabel("Carat", color='white')
    ax.set_ylabel("Antal diamanter", color='white')
    ax.tick_params(colors='white')
    ax.grid(True, color='gray', linestyle='--', alpha=0.3)
    ax.title.set_color('white')

    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", facecolor=fig.get_facecolor())
    data = base64.b64encode(buf.getbuffer()).decode("utf-8")

    st.markdown(
        f"""
        <div style="
            background-color: #1e1e1e;
            border-radius: 20px;
            padding: 15px;
            overflow: hidden;
            text-align: center;
            margin-top: 1rem;
            margin-bottom: 2rem;">
            <img src="data:image/png;base64,{data}" style="max-width: 100%; border-radius: 10px;">
        </div>
        """,
        unsafe_allow_html=True
    )

with tab3:
    nordic_df = df[(df['carat'] >= 0.1) & (df['carat'] <= 1.0)].copy()

    if not nordic_df.empty and 'carat' in nordic_df.columns:
        nordic_df = nordic_df.dropna(subset=['carat'])
        nordic_df['carat_bin'] = pd.cut(nordic_df['carat'], bins=np.arange(0.1, 1.05, 0.1))
    else:
        st.warning("Data saknas eller kolumn 'carat' är inte tillgänglig.")
        st.stop()

    volatility = nordic_df.groupby(['carat_bin', 'color'], observed=False)['price'].agg(['mean', 'std'])
    volatility['variation'] = volatility['std'] / volatility['mean']
    volatility = volatility.dropna()
    top_colors = volatility.sort_values(['carat_bin', 'variation'], ascending=[True, False]) \
                            .groupby(level='carat_bin').head(2).reset_index()['color'] \
                            .value_counts().head(2).index.tolist()

    volatility_clarity = nordic_df.groupby(['carat_bin', 'clarity'], observed=False)['price'].agg(['mean', 'std'])
    volatility_clarity['variation'] = volatility_clarity['std'] / volatility_clarity['mean']
    volatility_clarity = volatility_clarity.dropna()
    top_clarities = volatility_clarity.sort_values(['carat_bin', 'variation'], ascending=[True, False]) \
                                      .groupby(level='carat_bin').head(2).reset_index()['clarity'] \
                                      .value_counts().head(2).index.tolist()

    st.markdown("### Grupper med mest Volatilitet i detta datasetet")
    st.markdown(f"**Topp 2 - volatilitet färger:** {', '.join(top_colors)}")
    st.markdown(f"**Topp 2 - volatilitet clarity:** {', '.join(top_clarities)}")
    st.markdown(
    "<p style='color: #FFD700; font-weight: bold;'>När du väljer kategori, ha i åtanke att Guldfynds målgrupp efterfrågar</p>",
    unsafe_allow_html=True
    )
    st.markdown(
    "<p style='color: #FFD700;'>Färger: D och E</p>",
    unsafe_allow_html=True
    )
    st.markdown(
    "<p style='color: #FFD700;'>Clarity: IF och VVS1</p>",
    unsafe_allow_html=True
    )

    available_colors = sorted(nordic_df['color'].dropna().unique())
    available_clarities = sorted(nordic_df['clarity'].dropna().unique())

    selected_colors = st.multiselect("Välj färger att inkludera", available_colors, default=['D', 'E'])
    selected_clarities = st.multiselect("Välj clarity-nivåer att inkludera", available_clarities, default=['IF', 'VVS1'])

    filtered = nordic_df[(nordic_df['color'].isin(selected_colors)) &
                         (nordic_df['clarity'].isin(selected_clarities))].copy()

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
                cheap["med_price"] = median_price
                cheap["un_med_usd"] = (median_price - cheap[price_column]).round(2)
                cheap["un_med_percent"] = ((median_price - cheap[price_column]) / median_price * 100).round(1)
                result.append(cheap)

        return pd.concat(result, ignore_index=True) if result else pd.DataFrame()

    cheap = cheap_diamonds_by_carat(filtered, ['color', 'clarity', 'cut'])
    cheap = cheap.sort_values(by="un_med_usd", ascending=False)
    top50 = cheap[['index','price','med_price', 'un_med_usd', 'un_med_percent', 'kategori']].head(50)

    st.markdown("### Topp 50 mest prisvärda diamanter")
    st.dataframe(top50.reset_index(drop=True))

    st.markdown("### Visualisering av topp 50")
    cmap = plt.colormaps.get_cmap('tab20')
    colors = [cmap(i / 50) for i in range(50)]

    top50_full = nordic_df[['index', 'carat', 'price']].merge(
        top50[['index', 'med_price', 'un_med_percent', 'kategori']], on='index', how='inner'
    )

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(nordic_df['carat'], nordic_df['price'], alpha=0.3, color='lightgray', label='Alla diamanter')

    for i, (_, row) in enumerate(top50_full.iterrows()):
        color = colors[i]
        ax.plot([row['carat'], row['carat']], [row['price'], row['med_price']], color=color, linestyle='--', linewidth=1)
        ax.scatter(row['carat'], row['price'], color=color, s=60)
        ax.scatter(row['carat'], row['med_price'], color=color, marker='x', s=50)

    ax.set_title('Prisvärda diamanter markerade med avvikelse till median')
    ax.set_xlabel('Carat')
    ax.set_ylabel('Pris (USD)')
    ax.grid(True)

    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    data = base64.b64encode(buf.getbuffer()).decode("utf-8")

    st.markdown(f"""
        <div style="text-align:center;margin:20px">
            <img src="data:image/png;base64,{data}" style="max-width:100%;border-radius:10px;">
        </div>
    """, unsafe_allow_html=True)

    st.markdown("### Investeringssummering")
    top50_diamonds = top50.copy()
    top50_diamonds['med_price_10pct'] = top50_diamonds['med_price'] * 1.10
    top50_diamonds['vinst_median'] = top50_diamonds['med_price'] - top50_diamonds['price']
    top50_diamonds['vinst_10pct'] = top50_diamonds['med_price_10pct'] - top50_diamonds['price']

    st.success(f"Total investering (inköpspris): ${top50_diamonds['price'].sum():,.2f}")
    st.success(f"Möjlig vinst vid medianförsäljning: ${top50_diamonds['vinst_median'].sum():,.2f}")
    st.success(f"Möjlig vinst vid +10% över median: ${top50_diamonds['vinst_10pct'].sum():,.2f}")
