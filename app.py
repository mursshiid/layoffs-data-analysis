import streamlit as st
import pandas as pd
import plotly.express as px

# ---------- Page config ----------
st.set_page_config(page_title='Layoffs Dashboard', layout='wide', initial_sidebar_state='expanded')

# ---------- Brand palette ----------
PRIMARY = '#3B5BA5'      # primary blue - used for standard bars/lines
ACCENT = '#8C54FF'       # secondary accent - used for highlights
SEVERITY_SCALE = 'RdBu_r'  # diverging scale reserved for severity/negative metrics
SEQUENTIAL_SCALE = 'Blues'  # reserved for map/magnitude
PLOTLY_TEMPLATE = 'plotly_white'
CHART_CONFIG = {
    'displayModeBar': 'hover',
    'modeBarButtonsToRemove': ['lasso2d', 'select2d', 'autoScale2d'],
    'displaylogo': False
}

# ---------- White theme + card styling ----------
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #262730; }
    [data-testid="stMetric"] {
        background-color: #f7f9fb;
        border: 1px solid #e3e7ec;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }
    [data-testid="stMetricLabel"] { color: #555; }
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #ffffff;
        border: 1px solid #e3e7ec;
        border-radius: 10px;
        padding: 10px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    }
    </style>
""", unsafe_allow_html=True)

# ---------- Load data ----------
@st.cache_data
def load_data():
    df = pd.read_csv('data/cleaned/layoffs_cleaned.csv', parse_dates=['date', 'date_added'])
    return df

df = load_data()

st.title('📉 Global Tech Layoffs Dashboard (2020–2026)')
st.caption('Interactive analysis of global tech industry layoffs, tracking trends across industries, companies, countries, and funding stages.')

# ---------- Sidebar filters ----------
st.sidebar.header('🔍 Filters')

with st.sidebar.expander('📅 Date Range', expanded=True):
    min_date, max_date = df['date'].min().date(), df['date'].max().date()
    date_range = st.slider('Select range', min_value=min_date, max_value=max_date,
                            value=(min_date, max_date), format='YYYY-MM')

with st.sidebar.expander('🏭 Industry', expanded=False):
    industries = sorted(df['industry'].dropna().unique())
    select_all_ind = st.checkbox('Select all industries', value=True)
    if select_all_ind:
        selected_industries = industries
    else:
        selected_industries = st.multiselect('Choose industries', industries, default=[])

with st.sidebar.expander('🌍 Country', expanded=False):
    countries = sorted(df['country'].dropna().unique())
    select_all_country = st.checkbox('Select all countries', value=True)
    if select_all_country:
        selected_countries = countries
    else:
        selected_countries = st.multiselect('Choose countries', countries, default=[])

filtered = df[
    (df['date'].dt.date >= date_range[0]) & (df['date'].dt.date <= date_range[1]) &
    (df['industry'].isin(selected_industries)) &
    (df['country'].isin(selected_countries))
]

st.sidebar.markdown('---')
st.sidebar.caption(f"Showing **{len(filtered):,}** of {len(df):,} records")
csv = filtered.to_csv(index=False).encode('utf-8')
st.sidebar.download_button('⬇️ Download Filtered Data (CSV)', csv, 'layoffs_filtered.csv', 'text/csv')

# ---------- KPI Cards ----------
k1, k2, k3, k4 = st.columns(4)
k1.metric('Total Layoffs', f"{int(filtered['total_laid_off'].sum(skipna=True)):,}")
k2.metric('Companies Affected', f"{filtered['company'].nunique():,}")
k3.metric('Countries Affected', f"{filtered['country'].nunique():,}")
k4.metric('Avg. % Workforce Cut', f"{filtered['percentage_laid_off'].mean()*100:.1f}%")

st.markdown('---')

# ---------- Tabs ----------
tab1, tab2, tab3, tab4 = st.tabs(['📊 Overview', '🌍 Geography', '🏢 Companies & Stages', '📋 Raw Data'])

with tab1:
    c1, c2 = st.columns(2)
    with c1, st.container(border=True):
        top_ind = filtered[filtered['industry'] != 'Other'].groupby('industry')['total_laid_off'].sum().sort_values(ascending=False).head(10)
        fig = px.bar(top_ind, orientation='h', title='Top Industries by Layoffs', template=PLOTLY_TEMPLATE,
                     color_discrete_sequence=[PRIMARY])
        fig.update_layout(showlegend=False, yaxis_title='Industry', xaxis_title='Total Laid Off',
                           yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)
    with c2, st.container(border=True):
        monthly = filtered.groupby(filtered['date'].dt.to_period('M'))['total_laid_off'].sum()
        monthly.index = monthly.index.astype(str)
        fig = px.line(monthly, title='Monthly Layoffs Trend', markers=True, template=PLOTLY_TEMPLATE,
                      color_discrete_sequence=[PRIMARY])
        fig.update_layout(showlegend=False, xaxis_title='Month', yaxis_title='Total Laid Off')
        st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)

    c3, c4 = st.columns(2)
    with c3, st.container(border=True):
        fig = px.scatter(filtered, x='funds_raised', y='total_laid_off', opacity=0.5,
                          title='Funds Raised vs Layoff Size', template=PLOTLY_TEMPLATE, log_x=True,
                          color_discrete_sequence=[ACCENT])
        fig.update_layout(yaxis_title='Total Employees Laid Off', xaxis_title='Funds Raised ($M)')
        st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)
    with c4, st.container(border=True):
        stage_order = filtered[filtered['stage'] != 'Unknown'].groupby('stage')['percentage_laid_off'].median().sort_values(ascending=False).index.tolist()
        if 'Unknown' in filtered['stage'].unique():
            stage_order.append('Unknown')
        fig = px.box(filtered, x='stage', y='percentage_laid_off', category_orders={'stage': stage_order},
                     title='Layoff Severity by Funding Stage', template=PLOTLY_TEMPLATE,
                     color_discrete_sequence=[PRIMARY])
        fig.update_layout(xaxis_title='Funding Stage', yaxis_title='Percentage of Workforce Laid Off')
        st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)

with tab2:
    c1, c2 = st.columns([2, 1])
    with c1, st.container(border=True):
        country_totals = filtered.groupby('country')['total_laid_off'].sum().reset_index()
        fig = px.choropleth(country_totals, locations='country', locationmode='country names',
                             color='total_laid_off', color_continuous_scale=SEQUENTIAL_SCALE,
                             title='Global Layoffs by Country', template=PLOTLY_TEMPLATE)
        fig.update_geos(bgcolor='#ffffff', landcolor='#f0f0f0', showocean=True, oceancolor='#e6f2ff',
                         showcountries=True, countrycolor='#cccccc')
        fig.update_layout(paper_bgcolor='#ffffff', plot_bgcolor='#ffffff')
        st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)
    with c2, st.container(border=True):
        top_countries = filtered.groupby('country')['total_laid_off'].sum().sort_values(ascending=False).head(10)
        fig = px.bar(top_countries, orientation='h', title='Top 10 Countries (log scale)', template=PLOTLY_TEMPLATE,
                     text=top_countries.values, color_discrete_sequence=[PRIMARY])
        fig.update_traces(texttemplate='%{text:,}', textposition='outside')
        fig.update_layout(showlegend=False, yaxis={'categoryorder': 'total ascending'},
                           xaxis_title='Total Employees Laid Off (log scale)', yaxis_title='Country',
                           xaxis_type='log')
        st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)

with tab3:
    c1, c2 = st.columns(2)
    with c1, st.container(border=True):
        top_comp = filtered.groupby('company')['total_laid_off'].sum().sort_values(ascending=False).head(10)
        fig = px.bar(top_comp, orientation='h', title='Top Companies by Layoffs', template=PLOTLY_TEMPLATE,
                     color_discrete_sequence=[PRIMARY])
        fig.update_layout(showlegend=False, yaxis={'categoryorder': 'total ascending'},
                           xaxis_title='Total Employees Laid Off', yaxis_title='Company')
        st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)
    with c2, st.container(border=True):
        stage_counts = filtered['stage'].value_counts()
        threshold = stage_counts.sum() * 0.03
        major = stage_counts[stage_counts >= threshold]
        minor_sum = stage_counts[stage_counts < threshold].sum()
        if minor_sum > 0:
            major['Other (small stages)'] = minor_sum

        fig = px.pie(values=major.values, names=major.index, title='Layoff Events by Funding Stage',
                     template=PLOTLY_TEMPLATE, hole=0.4,
                     color_discrete_sequence=px.colors.sequential.Blues_r)
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)

with tab4:
    st.subheader('Filtered Dataset')
    display_df = filtered.copy()
    display_df['date'] = display_df['date'].dt.date
    display_df['date_added'] = display_df['date_added'].dt.date
    st.dataframe(display_df, use_container_width=True)
    st.caption(f"Showing {len(filtered):,} of {len(df):,} total rows")