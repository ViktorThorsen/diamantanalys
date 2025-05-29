def run_app(clean_diamond_data):
    import streamlit as st
    import pandas as pd
    import plotly.express as px
    import matplotlib.pyplot as plt
    import base64
    import streamlit.components.v1 as components
    import io
    import numpy as np
    from Diamond import cheap_diamonds_by_carat
    from Diamond import calculate_volatility_groups

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
            st.markdown("""
            <style>
            .stApp {
            background-color: #1e1e1e !important;
            color: white !important;
            }
            p, div, span, h1, h2, h3, h4, h5, h6 {
            color: white !important;
            }

            .css-1d391kg, .css-1lcbmhc {
            background-color: #111 !important;
            color: white !important;
            }
            </style>
            """, unsafe_allow_html=True)


    set_background("diamondBackground.jpg")


    st.sidebar.markdown("## Ladda upp diamantdata (CSV)")
    uploaded_file = st.sidebar.file_uploader("Välj en fil", type=["csv"])

    @st.cache_data

    def load_data(file):
        return clean_diamond_data(file)
    
    df, error = load_data(uploaded_file)

    if uploaded_file is None:
        st.warning("⬅️ Vänligen ladda upp en korrekt CSV-fil för att visa grafer.")
        st.stop()

    if error:
        st.error(f"❌ {error}")
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

    with tab3:
        nordic_df = df[(df['carat'] >= 0.1) & (df['carat'] <= 1.0)].copy()
        if 'index' not in df.columns:
            df.reset_index(inplace=True)

        if not nordic_df.empty and 'carat' in nordic_df.columns:
            nordic_df = nordic_df.dropna(subset=['carat'])
            nordic_df['carat_bin'] = pd.cut(nordic_df['carat'], bins=np.arange(0.1, 1, 0.01))
        else:
            st.warning("Data saknas eller kolumn 'carat' är inte tillgänglig.")
            st.stop()

        top_colors = calculate_volatility_groups(nordic_df, "color")
        top_clarities = calculate_volatility_groups(nordic_df, "clarity")
        top_cuts = calculate_volatility_groups(nordic_df, "cut")

        st.markdown("### Grupper med mest Volatilitet i detta datasetet")
        st.markdown(f"""
        <p style='font-size: 14px; font-weight: bold;'>Topp 3 - volatilitet färger: {', '.join(top_colors.index)}</p>
        <p style='font-size: 14px; font-weight: bold;'>Topp 3 - volatilitet clarity: {', '.join(top_clarities.index)}</p>
        <p style='font-size: 14px; font-weight: bold;'>Topp 3 - volatilitet cuts: {', '.join(top_cuts.index)}</p>
        """, unsafe_allow_html=True)

        st.markdown("<p style='color: #FFD700; font-weight: bold;'>När du väljer kategori, ha i åtanke att Guldfynds målgrupp efterfrågar</p>", unsafe_allow_html=True)
        st.markdown("""
        <p style='color: #FFD700; font-size: 14px;'>Färger: D, E och F</p>
        <p style='color: #FFD700; font-size: 14px;'>Clarity: IF, VVS1 och VVS2</p>
        <p style='color: #FFD700; font-size: 14px;'>Cuts: Ideal, Premium och Very Good</p>
        """, unsafe_allow_html=True)

        available_colors = sorted(nordic_df['color'].dropna().unique())
        available_clarities = sorted(nordic_df['clarity'].dropna().unique())
        available_cuts = sorted(nordic_df['cut'].dropna().unique())

        selected_colors = st.multiselect("Välj färger att inkludera", available_colors, default=list(top_colors.index))
        selected_clarities = st.multiselect("Välj clarity att inkludera", available_clarities, default=list(top_clarities.index))
        selected_cuts = st.multiselect("Välj cuts att inkludera", available_cuts, default=list(top_cuts.index))

        preferred_set = {'D', 'E', 'F', 'IF', 'VVS1', 'VVS2', 'Ideal', 'Premium', 'Very Good'}
        all_selected = selected_colors + selected_clarities + selected_cuts

        st.markdown("""
        <div style=\"display: flex; align-items: center; gap: 15px; margin-bottom: 10px;\">
            <div style=\"display: flex; align-items: center;\">
                <span style=\"width: 14px; height: 14px; background-color: #007f00; display: inline-block; border-radius: 50%; margin-right: 6px;\"></span>
                <span style=\"font-size: 13px; color: white; font-style: italic;\">Existerar i Guldfynds målgrupp</span>
            </div>
            <div style=\"display: flex; align-items: center;\">
                <span style=\"width: 14px; height: 14px; background-color: #cc0000; display: inline-block; border-radius: 50%; margin-right: 6px;\"></span>
                <span style=\"font-size: 13px; color: white; font-style: italic;\">Ej i målgruppen</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        color_boxes = ""
        for item in all_selected:
            bg = "#007f00" if item in preferred_set else "#cc0000"
            color_boxes += f"<span style='background-color: {bg}; color: white; padding: 5px 12px; border-radius: 6px; margin-right: 5px; font-size: 13px;'>{item}</span>"

        st.markdown(f"<div style='margin-bottom: 10px;'>{color_boxes}</div>", unsafe_allow_html=True)

        filtered = nordic_df[
            (nordic_df['color'].isin(selected_colors)) &
            (nordic_df['clarity'].isin(selected_clarities)) &
            (nordic_df['cut'].isin(selected_cuts))
        ].copy()
        filtered['carat_bin'] = pd.cut(filtered['carat'], bins=np.arange(0.1, 1, 0.01))

        cheap = cheap_diamonds_by_carat(filtered, ['carat_bin', 'color', 'clarity', 'cut'])
        if cheap.empty:
            st.warning("❌ Inga prisvärda diamanter kunde identifieras med vald filtrering.")
            st.stop()

        cheap = cheap.sort_values(by="un_med_usd", ascending=False)
        top50 = cheap[['index','price','med_price', 'un_med_usd', 'un_med_percent',
            'kategori', 'cut', 'color', 'clarity', 'carat_bin']].head(50)

        st.markdown("### Topp 50 mest prisvärda diamanter")
        st.dataframe(top50.reset_index(drop=True))

        # Visualisering
        st.markdown("### Visualisering av topp 50")
        cmap = plt.colormaps.get_cmap('tab20')
        colors = [cmap(i / 50) for i in range(50)]

        top50_full = pd.merge(filtered, top50, on='index', how='inner', suffixes=('', '_top'))

        median_per_bin = nordic_df.groupby('carat_bin')['price'].median().reset_index()
        median_per_bin['carat'] = median_per_bin['carat_bin'].apply(lambda x: (x.left + x.right) / 2)

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.scatter(nordic_df['carat'], nordic_df['price'], alpha=0.3, color='lightgray', label='Alla diamanter')

        for i, (_, row) in enumerate(top50_full.iterrows()):
            if i >= len(colors):
                break
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

        # Summering
        st.markdown("### Investeringssummering")
        top50_diamonds = top50.copy()
        top50_diamonds['med_price_10pct'] = top50_diamonds['med_price'] * 1.10
        top50_diamonds['vinst_median'] = top50_diamonds['med_price'] - top50_diamonds['price']
        top50_diamonds['vinst_10pct'] = top50_diamonds['med_price_10pct'] - top50_diamonds['price']

        st.success(f"Total investering (inköpspris): ${top50_diamonds['price'].sum():,.2f}")
        st.success(f"Möjlig vinst vid medianförsäljning: ${top50_diamonds['vinst_median'].sum():,.2f}")
        st.success(f"Möjlig vinst vid +10% över median: ${top50_diamonds['vinst_10pct'].sum():,.2f}")

