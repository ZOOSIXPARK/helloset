import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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
    numeric_columns = ['PBR', 'PER', 'ROE', '배당수익률', '시가총액(단위:백만원)', '자산총액(단위:백만원)', 
                      '종가', '등락률', '거래량', '거래대금', '배당성향']
    
    year_columns = {
        'PBR': ['`23 사업연도말 PBR', '`22 사업연도말 PBR', '`21 사업연도말 PBR'],
        'PER': ['`23 사업연도말 PER', '`22 사업연도말 PER', '`21 사업연도말 PER'],
        'ROE': ['`23 사업연도말 ROE', '`22 사업연도말 ROE', '`21 사업연도말 ROE'],
        '배당수익률': ['`23 사업연도말 배당수익률', '`22 사업연도말 배당수익률', '`21 사업연도말 배당수익률'],
        '배당성향': ['`23 사업연도말 배당성향', '`22 사업연도말 배당성향', '`21 사업연도말 배당성향']
    }
    
    # 기본 숫자형 변환 및 이상치 처리
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        if col in ['PER', 'PBR', 'ROE']:
            df[col] = df[col].clip(lower=df[col].quantile(0.01), 
                                 upper=df[col].quantile(0.99))
    
    # 연도별 데이터 숫자형 변환
    for metric, year_cols in year_columns.items():
        for col in year_cols:
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
st.markdown('<h1 class="main-header">📊 코리안벨류업 종목 분석 대시보드</h1>', unsafe_allow_html=True)

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
            title='섹터별 시가총액 비중',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig.update_layout(get_chart_layout())
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.histogram(
            df,
            x='시가총액(단위:백만원)',
            nbins=50,
            title='시가총액 분포',
            color_discrete_sequence=['#1f77b4']
        )
        fig.update_layout(get_chart_layout())
        st.plotly_chart(fig, use_container_width=True)
# 이전 코드에 이어서...

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
        **get_chart_layout("섹터별 PBR과 ROE"),
        barmode='group'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # 섹터별 평균 지표 비교
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.scatter(
            sector_stats,
            x='PBR',
            y='ROE',
            size='시가총액(단위:백만원)',
            color='섹터',
            title='섹터별 PBR vs ROE',
            labels={'PBR': 'PBR', 'ROE': 'ROE (%)'}
        )
        fig.update_layout(get_chart_layout())
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # 섹터별 평균 배당수익률
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
        st.metric("등락률", f"{stock_data['등락률']:.2f}%")
    with col3:
        st.metric("시가총액", f"{stock_data['시가총액(단위:백만원)']:,.0f}백만원")
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
# 이전 코드에 이어서...

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
        title="상위 10개 고배당 기업",
        text='배당수익률'
    )
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig.update_layout(get_chart_layout())
    st.plotly_chart(fig, use_container_width=True)

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
    top_value = df.nlargest(20, '가치투자_점수')
    
    fig = px.scatter(
        top_value,
        x='PBR',
        y='ROE',
        size='시가총액(단위:백만원)',
        color='섹터',
        hover_name='종목명',
        title="Top 20 가치투자 기회"
    )
    fig.update_layout(get_chart_layout())
    st.plotly_chart(fig, use_container_width=True)
    
    # 투자 기회 목록
    st.dataframe(
        top_value[['종목명', 'PBR', 'ROE', '시가총액(단위:백만원)', '가치투자_점수', '섹터']]
        .sort_values('가치투자_점수', ascending=False)
        .style.format({
            'PBR': '{:.2f}',
            'ROE': '{:.2f}%',
            '시가총액(단위:백만원)': '{:,.0f}',
            '가치투자_점수': '{:.0f}'
        })
    )

# 투자 전략 결론
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
