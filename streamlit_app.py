import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import matplotlib.font_manager as fm
import os

# 페이지 설정
st.set_page_config(
    layout="wide",
    page_title="코리안벨류업 종목 분석 대시보드",
    page_icon="📈"
)

# 색상 테마 설정
COLOR_SCALES = {
    'main': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b'],
    'diverging': 'RdYlBu',
    'sequential': 'Viridis',
    'categorical': 'Set3'
}

# 스타일 설정
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        padding: 1rem;
        border-bottom: 2px solid #1f77b4;
    }
    .kpi-container {
        display: flex;
        justify-content: space-between;
        flex-wrap: wrap;
    }
    .kpi-card {
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        padding: 20px;
        margin: 10px;
        flex: 1;
        min-width: 200px;
        text-align: center;
        transition: transform 0.3s ease;
        border-left: 5px solid #1f77b4;
    }
    .kpi-card:hover {
        transform: translateY(-5px);
    }
    .kpi-title {
        font-size: 1rem;
        color: #666;
        margin-bottom: 10px;
    }
    .kpi-value {
        font-size: 1.8rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .stock-info-container {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #666;
        margin-bottom: 5px;
    }
    .metric-value {
        font-size: 1.2rem;
        font-weight: bold;
        color: #1f77b4;
    }
    </style>
    """, unsafe_allow_html=True)

# 데이터 로드
@st.cache_data
def load_data():
    df = pd.read_csv("value_jipyo.csv")
    numeric_columns = ['PBR', 'PER', 'ROE', '배당수익률', '시가총액(단위:백만원)', 
                       '종가', '등락률', '거래량', '거래대금', '배당성향']
    
    year_columns = {
        'PBR': ['`23 사업연도말 PBR', '`22 사업연도말 PBR', '`21 사업연도말 PBR'],
        'PER': ['`23 사업연도말 PER', '`22 사업연도말 PER', '`21 사업연도말 PER'],  # '사업도말'을 '사업연도말'로 수정
        'ROE': ['`23 사업연도말 ROE', '`22 사업연도말 ROE', '`21 사업연도말 ROE'],
        '배당수익률': ['`23 사업연도말 배당수익률', '`22 사업연도말 배당수익률', '`21 사업연도말 배당수익률'],
        '배당성향': ['`23 사업연도말 배당성향', '`22 사업연도말 배당성향', '`21 사업연도말 배당성향']
    }
    
    # 기본 숫자형 변환 및 이상치 처리
    for col in numeric_columns:
        if col in df.columns:  # 열이 존재하는 경우에만 처리
            df[col] = pd.to_numeric(df[col], errors='coerce')
            if col in ['PER', 'PBR', 'ROE']:
                df[col] = df[col].clip(lower=df[col].quantile(0.01), 
                                     upper=df[col].quantile(0.99))
    
    # 연도별 데이터 숫자형 변환
    for metric, year_cols in year_columns.items():
        for col in year_cols:
            if col in df.columns:  # 열이 존재하는 경우에만 처리
                df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df, year_columns, numeric_columns

# 차트 기본 레이아웃 설정
def get_chart_layout(title=""):
    return {
        'title': title,
        'plot_bgcolor': 'white',
        'paper_bgcolor': 'white',
        'font': dict(color='black'),
        'showlegend': True,
        'legend': dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    }

# 메인 타이틀
st.title('코리안벨류업 종목 분석 대시보드')



# 데이터 로드 및 기본 계산
with st.spinner('데이터를 분석중입니다...'):
    df, year_columns, numeric_columns = load_data()
    
    # 기본 지표 계산
    total_market_cap = df['시가총액(단위:백만원)'].sum() / 1000000
    avg_pbr = df['PBR'].mean()
    avg_per = df['PER'].mean()
    avg_roe = df['ROE'].mean()
    avg_dividend_yield = df['배당수익률'].mean()
    market_momentum = df['등락률'].mean()
    high_roe_companies = df[df['ROE'] >= 15].shape[0]
    low_pbr_companies = df[df['PBR'] < 1].shape[0]
    
    # 섹터 통계
    sector_stats = df[df['섹터'].notna()].groupby('섹터').agg({
        '시가총액(단위:백만원)': 'sum',
        'PBR': 'mean',
        'PER': 'mean',
        'ROE': 'mean',
        '배당수익률': 'mean'
    }).reset_index()

# 탭 생성
tabs = st.tabs([
    "📊 시장 개요",
    "🏢 섹터 분석",
    "🔍 개별 종목 분석",
    "💰 배당 분석",
    "📅 연도별 추이",
    "💡 투자 기회"
])

with tabs[0]:  # 시장 개요
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("총 시가총액 (조원)", f"{total_market_cap:,.2f}")
    with col2:
        st.metric("평균 PBR", f"{avg_pbr:.2f}")
    with col3:
        st.metric("평균 ROE (%)", f"{avg_roe:.2f}")
    with col4:
        st.metric("시장 모멘텀 (%)", f"{market_momentum:.2f}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.pie(
            sector_stats.nlargest(5, '시가총액(단위:백만원)'),
            values='시가총액(단위:백만원)',
            names='섹터',
            title='상위 5개 섹터별 시가총액 비중',
            color_discrete_sequence=px.colors.qualitative.Set3
        )

    # 레이아웃 업데이트
        fig.update_layout(
            title={
                'text': "상위 5개 섹터별 시가총액 비중",
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top',
                'font': {'size': 24}
            },
            # 레이블을 오른쪽으로
            legend={
                'yanchor': "middle",
                'y': 0.5,
                'xanchor': "left",
                'x': 1.1
            }
        )
    
        # 파이 차트 레이블 설정
        fig.update_traces(
            textposition='inside', 
            textinfo='percent+label'
        )
    
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("이 차트는 시가총액 기준 상위 5개 섹터의 비중을 보여줍니다. 각 섹터가 전체 시장에서 차지하는 비율을 한눈에 파악할 수 있습니다.")
    with col2:
        fig = px.histogram(
            df,
            x='시가총액(단위:백만원)',
            nbins=50,
            title='기업 시가총액 분포',
            color_discrete_sequence=['#1f77b4']
        )
        
        fig.update_layout(
            title={
                'text': "기업 시가총액 분포",
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top',
                'font': {'size': 24}
            },
            yaxis=dict(
                title="기업 수",
                side='right',  # y축 레이블을 오른쪽으로
                titlefont=dict(size=14),
                tickfont=dict(size=12)
            ),
            xaxis=dict(
                title="시(:백만원)",
                titlefont=dict(size=14),
                tickfont=dict(size=12)
            ),
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("이 히스토그램은 기업들의 시가총액 분포를 보여줍니다. 대부분의 기업이 어느 범위의 시가총액을 가지고 있는지, 극단적으로 큰 시가총액을 가진 기업은 얼마나 있는지 파악할 수 있습니다.")
    # 배당률 높은 기업 트리맵 추가
    st.subheader("ROE 상위 50 기업 트리맵")
    
    # ROE 상위 50개 기업 선택
    top_roe_companies = df.nlargest(50, 'ROE').copy()
    
    # 배당수익률에 따른 색상 범위 설정
    min_dividend = top_roe_companies['배당수익률'].min()
    max_dividend = top_roe_companies['배당수익률'].max()

    # 트리맵 생성
    fig = px.treemap(
        top_roe_companies,
        path=['종목명'],
        values='ROE',
        color='배당수익률',
        hover_data=['ROE', '배당수익률', 'PBR', '시가총액(단위:백만원)'],
        color_continuous_scale='YlOrRd',  # 노랑-주황-빨강 색상 스키마
        range_color=[min_dividend, max_dividend]
    )

    fig.update_traces(
        textinfo="label+value",
        textfont=dict(size=12, color='black'),
        hovertemplate='<b>%{label}</b><br>' +
                      'ROE: %{value:.2f}%<br>' +
                      '배당수익률: %{customdata[1]:.2f}%<br>' +
                      'PBR: %{customdata[2]:.2f}<br>' +
                      '시가총액: %{customdata[3]:,.0f}백만원'
    )

    fig.update_layout(
        height=700,
        coloraxis_colorbar=dict(
            title="배당수익률 (%)",
            tickformat=".2f",
            len=0.5,  # 컬러바 길이 조정
            yanchor="top",  # 컬러바 위치 조정
            y=1,
            xanchor="left",
            x=1.02
        ),
        font=dict(family="Malgun Gothic", size=14),
        margin=dict(t=30, l=10, r=10, b=10),
        title={
            'text':' ',
            'y':0.98,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 24}
        }
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    **ROE 상위 50개 기업을 시각화한 트리맵입니다.**
    - 사각형의 크기: ROE 값
    - 색상: 배당수익률 (짙은 빨강일수록 높은 배당수익률)
    - 텍스트: 기업명과 ROE 값
    - 호버 보: ROE, 배당수익률, PBR, 시가총액

    이 시각화를 통해 ROE가 높은 기업들 중에서 배당수익률이 어떻게 분포되어 있는지,
    그리고 각 기업의 주요 지표들을 한눈에 파악할 수 있습니다.
    """)

    st.subheader("섹터별 배당률과 배당성향 히트맵")

    # 섹터별 평균 배당률과 배당성향 계산
    sector_dividend = df.groupby('섹터')[['배당수익률', '배당성향']].mean().reset_index()

    # 히트맵 생성
    fig = px.imshow(sector_dividend[['배당수익률', '배당성향']],
                    labels=dict(x="지표", y="섹터", color="값"),
                    x=['배당수익률', '배당성향'],
                    y=sector_dividend['섹터'],
                    color_continuous_scale="YlOrRd",
                    aspect="auto")

    # 셀에 값 표시
    fig.update_traces(text=sector_dividend[['배당수익률', '배당성향']].values.round(2), texttemplate="%{text}")
    fig.update_layout(
        title="섹터별 평균 배당률과 배당성향",
        xaxis_title="",
        yaxis_title="",
        height=600,
        width=800,
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    이 히트맵은 각 섹터의 평균 배당률과 배당성향을 보여줍니다:
    - 배당률: 주가 대비 1주당 배당금의 비율을 나타냅니다. 높을수록 현재 주가 대비 배당금이 많다는 의미입니다.
    - 배당성향: 순이익 대비 배당금 지급 비율을 나타냅니다. 높을수록 기업이 이익의 더 많은 부분을 배당으로 지급한다는 의미입니다.
    
    색상이 진할수록 해당 값이 높음을 나타냅니다. 이를 통해 어떤 섹터가 배당 투자에 적합한지 파악할 수 있습니다.
    """)

with tabs[1]:  # 섹터 분석
    st.subheader("섹터별 분석")
    
    # 섹터별 주요 지표
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=sector_stats['섹터'],
        y=sector_stats['PBR'],
        name='PBR',
        marker_color=COLOR_SCALES['main'][0]
    ))
    fig.add_trace(go.Bar(
        x=sector_stats['섹터'],
        y=sector_stats['ROE'],
        name='ROE',
        marker_color=COLOR_SCALES['main'][1]
    ))
    fig.update_layout(
        **get_chart_layout("섹터별 평균 PBR과 ROE"),
        barmode='group'
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("이 그래프는 각 섹터의 평균 PBR과 ROE를 비교하여 보여줍니다. 이를 통해 어떤 섹터가 상대적으로 저평가되어 있는지, 또는 수익성이 높은지 파악할 수 있습니다.")
    
    # 섹터별 평균 지표 비교
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.scatter(
            sector_stats,
            x='PBR',
            y='ROE',
            size='시가총액(단위:백만원)',
            color='섹터',
            title='섹터별 PBR vs ROE 비교',
            labels={'PBR': 'PBR', 'ROE': 'ROE (%)'}
        )
        fig.update_layout(get_chart_layout())
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("이 산점도는 각 섹터의 평균 PBR과 ROE를 비교하며, 버블의 크기는 해당 섹터의 총 시가총액을 나타냅니다. 이를 통해 각 섹터의 가치와 수익성, 그고 시장 규모를 한 번에 비교할 수 있습니다.")
    
    with col2:
        fig = px.bar(
            sector_stats.sort_values('배당수익률', ascending=False),
            x='섹터',
            y='배당수익률',
            title='섹터별 평균 배당수익률',
            color='배당수익률',
            color_continuous_scale=COLOR_SCALES['sequential']
        )
        fig.update_layout(get_chart_layout())
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("이 막대 그래프는 각 섹터의 평균 배당수익률을 보여줍니다. 색상의 진한 정도로 배당수익률의 높낮이를 직관적으로 파악할 수 있으며, 어떤 섹터가 상대적으로 높은 배당을 제공하는지 알 수 있습니다.")

    # 업종별 투자 매력도
    sector_metrics = df[df['섹터'].notna()].groupby('섹터').agg({
        'PBR': 'mean',
        '등락률': 'mean',
        '시가총액(단위:백만원)': 'sum'
    }).sort_values('PBR', ascending=True)
    
    sector_metrics['투자매력도'] = (1 / sector_metrics['PBR']) * (1 + sector_metrics['등락률'] / 100)
    sector_metrics = sector_metrics.sort_values('투자매력도', ascending=False)

    fig = px.bar(
        sector_metrics,
        y=sector_metrics.index,
        x='투자매력도',
        title="업종별 투자 매력도 (PBR의 역수 * (1 + 등락률))",
        color='시가총액(단위:백만원)',
        color_continuous_scale=COLOR_SCALES['sequential']
    )
    fig.update_layout(get_chart_layout())
    st.plotly_chart(fig, use_container_width=True)

with tabs[2]:  # 개별 종목 분석
    st.subheader("개별 종목 분석")
    
    # 종목 선택
    selected_stock = st.selectbox(
        "분석할 종목을 선택하세요",
        options=df['종목명'].unique()
    )
    
    # 선택된 종목 정보
    stock_data = df[df['종목명'] == selected_stock].iloc[0]
    
    # 종목 기본 정보 표시
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("현재가", f"{stock_data['종가']:,.0f}")
    with col2:
        st.metric("PER", f"{stock_data['PER']:.2f}")
    with col3:
        st.metric("PBR", f"{stock_data['PBR']:.2f}")
    with col4:
        st.metric("시가총액", f"{stock_data['시가총액(단위:백만원)']:,.0f}백만원")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("배당수익률", f"{stock_data['배당수익률']:.2f}%")
    with col2:
        st.metric("배당성향", f"{stock_data['배당성향']:.2f}%")
    with col3:
        st.metric("ROE", f"{stock_data['ROE']:.2f}%")
    with col4:
        st.metric("섹터", stock_data['섹터'])
    
    # 연도별 지표 추이
    st.subheader("연도별 추이")
    years = ['2023', '2022', '2021']
    
    col1, col2 = st.columns(2)
    
    with col1:
        # PBR 추이
        pbr_data = [stock_data[col] for col in year_columns['PBR']]
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=years,
            y=pbr_data,
            mode='lines+markers',
            name='PBR'
        ))
        fig.update_layout(**get_chart_layout("PBR 추이"))
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # ROE 추이
        roe_data = [stock_data[col] for col in year_columns['ROE']]
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=years,
            y=roe_data,
            mode='lines+markers',
            name='ROE'
        ))
        fig.update_layout(**get_chart_layout("ROE 추이"))
        st.plotly_chart(fig, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # PER 추이
        per_data = []
        for col in year_columns['PER']:
            try:
                per_data.append(stock_data[col])
            except KeyError:
                per_data.append(None)  # 데이터가 없는 경우 None 추가
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=years,
            y=per_data,
            mode='lines+markers',
            name='PER'
        ))
        fig.update_layout(**get_chart_layout("PER 추이"))
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # 배당수익률 추이
        dividend_data = [stock_data[col] for col in year_columns['배당수익률']]
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=years,
            y=dividend_data,
            mode='lines+markers',
            name='배당수익률'
        ))
        fig.update_layout(**get_chart_layout("배당수익률 추이"))
        st.plotly_chart(fig, use_container_width=True)
    
    # 동종 업계 비교
    st.subheader("동종 업계 비교")
    same_sector = df[df['섹터'] == stock_data['섹터']]
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.scatter(
            same_sector,
            x='PBR',
            y='ROE',
            size='시가총액(단위:백만원)',
            hover_name='종목명',
            title='동종 업계 PBR vs ROE',
            color='PER'
        )
        # 선택된 종목 강조
        fig.add_trace(go.Scatter(
            x=[stock_data['PBR']],
            y=[stock_data['ROE']],
            mode='markers',
            marker=dict(size=20, color='red', symbol='star'),
            name=selected_stock
        ))
        fig.update_layout(get_chart_layout())
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # 배당수익률 비교
        fig = px.bar(
            same_sector.nlargest(10, '배당수익률'),
            x='종목명',
            y='배당수익률',
            title='동종 업계 top 10 배당수익률',
            color='배당성향'
        )
        fig.update_layout(get_chart_layout())
        st.plotly_chart(fig, use_container_width=True)

    st.markdown(f"""
    ### {selected_stock} 종목 분석 요약
    
    - **현재 주가**: {stock_data['종가']:,.0f}원
    - **PER**: {stock_data['PER']:.2f} (업종 평균: {same_sector['PER'].mean():.2f})
    - **PBR**: {stock_data['PBR']:.2f} (업종 평균: {same_sector['PBR'].mean():.2f})
    - **ROE**: {stock_data['ROE']:.2f}% (업종 평균: {same_sector['ROE'].mean():.2f}%)
    - **배당수익률**: {stock_data['배당수익률']:.2f}% (업종 평균: {same_sector['배당수익률'].mean():.2f}%)
    - **배당성향**: {stock_data['배당성향']:.2f}% (업종 평균: {same_sector['배당성향'].mean():.2f}%)
    
    {selected_stock}은(는) 동종 업계 대비 {'높은' if stock_data['PER'] > same_sector['PER'].mean() else '낮은'} PER, 
    {'높은' if stock_data['PBR'] > same_sector['PBR'].mean() else '낮은'} PBR, 
    {'높은' if stock_data['ROE'] > same_sector['ROE'].mean() else '낮은'} ROE를 보이고 있습니다. 
    배당 측면에서는 {'높은' if stock_data['배당수익률'] > same_sector['배당수익률'].mean() else '낮은'} 배당수익률과 
    {'높은' if stock_data['배당성향'] > same_sector['배당성향'].mean() else '낮은'} 배당성향을 나타내고 있습니다.
    
    최근 3년간의 추이를 볼 때, PBR과 ROE는 {'상승' if pbr_data[0] > pbr_data[-1] and roe_data[0] > roe_data[-1] else '하락'} 추세를 보이고 있으며, 
    배당수익률은 {'증가' if dividend_data[0] > dividend_data[-1] else '감소'}하고 있습니다.
    """)

with tabs[3]:  # 배당 분석
    st.subheader("배당 분석")
    
    # 전체 배당 현황
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("평균 배당수익률", f"{df['배당수익률'].mean():.2f}%")
    with col2:
        st.metric("중앙값 배당수익률", f"{df['배당수익률'].median():.2f}%")
    with col3:
        st.metric("배당 지급 기업 수", f"{df[df['배당수익률'] > 0].shape[0]}")
    with col4:
        st.metric("평균 배당성향", f"{df['배당성향'].mean():.2f}%")
    
    # 섹터별 배당률과 배당성향 히트맵 추가
    st.subheader("섹터별 배당률과 배당성향 히트맵")

    # 섹터별 평균 배당률과 배당성향 계산
    sector_dividend = df.groupby('섹터')[['배당수익률', '배당성향']].mean().reset_index()

    # 히트맵 생성
    fig = px.imshow(sector_dividend[['배당수익률', '배당성향']],
                    labels=dict(x="지표", y="섹터", color="값"),
                    x=['배당수익률', '배당성향'],
                    y=sector_dividend['섹터'],
                    color_continuous_scale="YlOrRd",
                    aspect="auto")

    # 셀에 값 표시
    fig.update_traces(text=sector_dividend[['배당수익률', '배당성향']].values.round(2), texttemplate="%{text}")
    fig.update_layout(
        title="섹터별 평균 배당률과 배당성향",
        xaxis_title="",
        yaxis_title="",
        height=600,
        width=800,
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    이 히트맵은 각 섹터의 평균 배당률과 배당성향을 보여줍니다:
    - 배당률: 주가 대비 1주당 배당금의 비율을 나타냅니다. 높을수록 현재 주가 대비 배당금이 많다는 의미입니다.
    - 배당성향: 순이익 대비 배당금 지급 비율을 나타냅니다. 높을수록 기업이 이익의 더 많은 부분을 배당으로 지급한다는 의미입니다.
    
    색상이 진할수록 해당 값이 높음을 나타냅니다. 이를 통해 어떤 섹터가 배당 투자에 적합한지 파악할 수 있습니다.
    """)

    # 기존의 배당 분석 코드 계속...
    col1, col2 = st.columns(2)
    
    with col1:
        # 배당수익률 vs 배당성향 산점도
        fig = px.scatter(
            df,
            x='배당수익률',
            y='배당성향',
            size='시가총액(단위:백만원)',
            color='PBR',
            hover_name='종목명',
            title="배당수익률 vs 배당성향",
            labels={
                '배당수익률': '배당수익률 (%)',
                '배당성향': '배당성향 (%)',
                '시가총액(단위:백만원)': '시가총액'
            }
        )
        fig.update_layout(get_chart_layout())
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # 연도별 배당수익률 변화
        avg_dividend_by_year = {
            '2023': df[year_columns['배당수익률'][0]].mean(),
            '2022': df[year_columns['배당수익률'][1]].mean(),
            '2021': df[year_columns['배당수익률'][2]].mean()
        }
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=list(avg_dividend_by_year.keys()),
            y=list(avg_dividend_by_year.values()),
            mode='lines+markers',
            name='평균 배당수익률'
        ))
        fig.update_layout(**get_chart_layout("연도별 평균 배당수익률 추이"))
        st.plotly_chart(fig, use_container_width=True)
    
    # 상위 10개 고배당 기업
    st.subheader("Top 10 고배당 기업")
    top_dividend = df.nlargest(10, '배당수익률')
    
    fig = px.bar(
        top_dividend,
        x='종목명',
        y='배당수익률',
        color='섹터',
        title="상위 10 고배당 기업",
        text='배당수익률'
    )
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig.update_layout(get_chart_layout())
    st.plotly_chart(fig, use_container_width=True)

    # 배당 워드클라우드 추가
    st.subheader("전체 기업 배당 워드클라우드")

    # 배당수익률이 있는 기업만 선택
    dividend_companies = df[df['배당수익률'] > 0]

    # 워드클라우드용 데이터 생성
    word_freq = {row['종목명']: row['배당수익률'] for _, row in dividend_companies.iterrows()}

    # 서버에 설치된 한글 폰트 찾기
    #font_path = os.path.join(os.path.dirname(__file__), 'fonts', 'NanumGothic.ttf')
    #ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # fonts 폴더와 data 폴더 경로 설정
    #font_path = os.path.join(ROOT_DIR, 'fonts', 'NanumGothic.ttf')
    font_path='NanumGothic.ttf'
    #for font in fm.findSystemFonts():
    #    if 'gothic' in font.lower() or 'gulim' in font.lower():
    #        font_path = font
    #        break

    if font_path is None:
        st.error("적절한 한글 폰트를 찾을 수 없습니다. 서버에 한글 폰트를 설치해 주세요.")
    else:
        # 워드클라우드 생성
        wordcloud = WordCloud(
            font_path=font_path,
            width=800, 
            height=400, 
            background_color='white',
            colormap='viridis'
        ).generate_from_frequencies(word_freq)

        # 워드클라우드 표시
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        st.pyplot(fig)

        st.markdown("""
        이 워드클라우드는 배당을 지급하는 모든 기업을 보여줍니다. 
        글자의 크기는 배당수익률에 비례하며, 배당수익률이 높을수록 더 크게 표시됩니다.
        이를 통해 전체 시장에서 어떤 기업들이 높은 배당을 제공하는지 한눈에 파악할 수 있습니다.
        """)

with tabs[4]:  # 연도별 추이
    st.subheader("연도별 지표 추이 분석")
    
    # 지표 선택
    metric_choice = st.selectbox(
        "분석할 지표 선택",
        options=['PBR', 'PER', 'ROE', '배당수익률', '배당성향']
    )
    
    # 전체 시장 추이
    yearly_avg = {
        '2023': df[year_columns[metric_choice][0]].mean(),
        '2022': df[year_columns[metric_choice][1]].mean(),
        '2021': df[year_columns[metric_choice][2]].mean()
    }
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 전체 시장 추이
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=list(yearly_avg.keys()),
            y=list(yearly_avg.values()),
            mode='lines+markers',
            name=f'평균 {metric_choice}'
        ))
        fig.update_layout(**get_chart_layout(f"시장 평균 {metric_choice} 추이"))
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # 섹터별 연도별 추이
        sector_yearly = df[df['섹터'].notna()].groupby('섹터')[year_columns[metric_choice]].mean()
        
        fig = go.Figure()
        for year, col in zip(['2023', '2022', '2021'], year_columns[metric_choice]):
            fig.add_trace(go.Bar(
                name=year,
                x=sector_yearly.index,
                y=sector_yearly[col]
            ))
        fig.update_layout(
            **get_chart_layout(f"섹터별 연도별 {metric_choice} 추이"),
            barmode='group'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # 개선도 분석
    st.subheader("지표 개선도 분석")
    df[f'{metric_choice}_개선도'] = df[year_columns[metric_choice][0]] - df[year_columns[metric_choice][1]]
    
    top_improved = df.nlargest(10, f'{metric_choice}_개선도')
    fig = px.bar(
        top_improved,
        x='종목명',
        y=f'{metric_choice}_개선도',
        color='섹터',
        title=f"Top 10 {metric_choice} 개선 기업"
    )
    fig.update_layout(get_chart_layout())
    st.plotly_chart(fig, use_container_width=True)

with tabs[5]:  # 투자 기회
    st.subheader("투자 기회 분석")
    
    # 가치투자 점수 계산
    df['PBR_rank'] = df['PBR'].rank(ascending=True)
    df['ROE_rank'] = df['ROE'].rank(ascending=False)
    df['시가총액_rank'] = df['시가총액(단위:백만원)'].rank(ascending=False)
    df['가치투자_점수'] = (df['PBR_rank'] + df['ROE_rank'] + df['시가총액_rank']) / 3
    
    # 상위 가치투자 기회
    top_value = df.nlargest(100, '가치투자_점수')
    
    fig = px.scatter(
        top_value,
        x='PBR',
        y='ROE',
        size='시가총액(단위:백만원)',
        size_max=20,  # 데이터 포인트의 최대 크기를 50으로 설정
        color='섹터',
        hover_name='종목명',
        title=" 가치투자 기회"
    )
    fig.update_layout(get_chart_layout())
    st.plotly_chart(fig, use_container_width=True)
    
    # 투자 기회 목록
    st.dataframe(
        top_value[['종목명', 'PBR', 'ROE', '시가총액(단위:백만원)', '가치투자_점수', '섹터','배당수익률','배당성향']]
        .sort_values('가치투자_점수', ascending=False)
        .style.format({
            'PBR': '{:.2f}',
            'ROE': '{:.2f}%',
            '시가총액(단위:백만원)': '{:,.0f}',
            '가치투자_점수': '{:.0f}',
            '배당수익률': '{:.2f}%',
            '배당성향': '{:.2f}%',
        })
    )

# 자 전략 결론
st.markdown("---")
st.markdown(f"""
## 💡 투자 전략 제안

### 시장 현황
- 전체 시가총액: {total_market_cap:,.1f}조원
- 평균 PBR: {avg_pbr:.2f}배 (PBR 1배 미만 기업: {low_pbr_companies}개)
- 평균 ROE: {avg_roe:.2f}%
- 평균 배당수익률: {avg_dividend_yield:.2f}%

### 투자 전략 방향
1. **가치투자 접근**
   - PBR 1배 미만 + ROE {avg_roe:.1f}% 이상 기업 우선 검토
   - 시가총액 상위 기업 중 저평가 종목 발굴

2. **배당투자 전략**
   - 평균 배당수익률 {avg_dividend_yield:.2f}% 이상 기업 중 선별
   - 배당성향의 안정성 확인

3. **업종별 접근**
   - 최근 실적 개선 섹터 중심 투자
   - 저평가 업종 내 우량기업 발굴
""")



















