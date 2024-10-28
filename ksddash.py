import streamlit as st
import pandas as pd
import plotly.express as px
import logging
from datetime import datetime, timedelta
from pathlib import Path
import os

# 작업 디렉토리 설정
BASE_DIR = r"D:\Daily\20241028"
TEST_DATA_DIR = os.path.join(BASE_DIR, "test_data")
LOG_DIR = os.path.join(BASE_DIR, "logs")

# 로그 디렉토리 생성
os.makedirs(LOG_DIR, exist_ok=True)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "ksd_monitor.log"), encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# KSD 코드별 업무명 정의
KSD_BUSINESS_NAMES = {
    '631': '주식 매수',
    '632': '주식 매도',
    '633': '잔고 조회',
    '634': '계좌 조회',
    '635': '시세 조회',
    '636': '체결 확인',
    '637': '예탁금 조회',
    '638': '거래내역 조회',
    '639': '계좌이체',
    '640': '신용거래'
}

class KSDMonitor:
    def __init__(self):
        self.base_path = TEST_DATA_DIR
        logging.info(f"Initialized with base path: {self.base_path}")

    def get_current_log_file(self, prefix):
        """현재 시간 기준 로그 파일명 생성"""
        current_time = datetime.now()
        file_path = os.path.join(self.base_path, f"{prefix}.ksd653.log.{current_time.strftime('%m%d%H%M')}")
        logging.info(f"Looking for file: {file_path}")
        return file_path

    def read_summary_log(self, is_send=True):
        """총집계 로그 파일 읽기"""
        try:
            prefix = 's' if is_send else 'r'
            file_path = self.get_current_log_file(prefix)
            
            if not os.path.exists(file_path):
                logging.warning(f"Log file not found: {file_path}")
                return pd.DataFrame(), None
            
            data = []
            with open(file_path, 'r') as f:
                for line in f:
                    code, count = line.strip().split(':')
                    data.append({
                        'ksd_code': code,
                        'business_name': KSD_BUSINESS_NAMES.get(code, '미정의 업무'),
                        'count': int(count)
                    })
            
            if data:
                df = pd.DataFrame(data)
                total = df['count'].sum()
                df['percentage'] = (df['count'] / total * 100)
                logging.info(f"Successfully read {len(data)} records from {file_path}")
                return df, datetime.fromtimestamp(os.path.getmtime(file_path))
                
            return pd.DataFrame(), None

        except Exception as e:
            logging.error(f"로그 파일 읽기 실패: {e}")
            return pd.DataFrame(), None

    def read_transaction_log(self, start_time, end_time, direction=None):
        """거래 로그 파일 읽기"""
        try:
            data = []
            current = start_time
            
            while current <= end_time:
                for prefix in (['s'] if direction == 'SEND' else ['r'] if direction == 'RECV' else ['s', 'r']):
                    file_name = os.path.join(self.base_path, 
                        f"{prefix}.tran.ksd653.log.{current.strftime('%m%d%H%M')}")
                    logging.info(f"Checking transaction file: {file_name}")
                    if os.path.exists(file_name):
                        with open(file_name, 'r') as f:
                            for line in f:
                                timestamp, result_file, code, tran_type = line.strip().split(':')
                                data.append({
                                    'timestamp': datetime.strptime(timestamp, '%Y%m%d%H%M%S'),
                                    'result_file': result_file,
                                    'ksd_code': code,
                                    'business_name': KSD_BUSINESS_NAMES.get(code, '미정의 업무'),
                                    'direction': tran_type
                                })
                
                current += timedelta(minutes=1)
            
            return pd.DataFrame(data)

        except Exception as e:
            logging.error(f"거래 로그 읽기 실패: {e}")
            return pd.DataFrame()

def create_metrics_html(df, log_time, direction):
    """KPI 메트릭스를 위한 HTML 생성"""
    html = """
    <style>
        .metrics-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1rem;
            padding: 1rem;
            margin-bottom: 1rem;
        }
        .metric-card {
            background: #1E1E1E;
            border-radius: 10px;
            padding: 1.5rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
            transition: transform 0.2s;
            border: 1px solid #333;
        }
        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 8px rgba(0, 0, 0, 0.4);
            border-color: #4B4B4B;
        }
        .metric-title {
            color: #58A6FF;
            font-size: 1rem;
            font-weight: bold;
            margin-bottom: 0.8rem;
        }
        .metric-value {
            font-size: 1.8rem;
            font-weight: bold;
            color: #E1E1E1;
            margin-bottom: 0.8rem;
        }
        .metric-percent {
            font-size: 1rem;
            color: #9E9E9E;
        }
        .section-container {
            background: #1E1E1E;
            border-radius: 10px;
            padding: 1rem;
            margin-bottom: 1rem;
        }
        .update-time {
            color: #9E9E9E;
            font-size: 0.9rem;
            text-align: right;
            padding: 0.5rem;
            background: #2D2D2D;
            border-radius: 5px;
            margin-top: 0.5rem;
        }
    </style>
    <div class="section-container">
    """
    
    html += f"""
        <div class="metrics-container">
    """
    
    # 총 발생건수를 첫 번째 항목으로 추가
    total_count = df['count'].sum()
    data_with_total = pd.concat([
        pd.DataFrame([{
            'ksd_code': 'TOTAL',
            'business_name': '총 발생건수',
            'count': total_count,
            'percentage': 100.0
        }]),
        df.sort_values('count', ascending=False)
    ]).reset_index(drop=True)
    
    for _, row in data_with_total.iterrows():
        html += f"""
            <div class="metric-card">
                <div class="metric-title">{row['business_name']}</div>
                <div class="metric-value">{row['count']:,}건</div>
                <div class="metric-percent">
                    <span>{row['ksd_code']} | {row['percentage']:.1f}%</span>
                </div>
            </div>
        """
    
    html += "</div>"
    
    if log_time:
        html += f"""
        <div class="update-time">
            마지막 업데이트: {log_time.strftime('%Y-%m-%d %H:%M:%S')}
        </div>
        """
    
    html += "</div>"
    return html

def main():
    st.set_page_config(
        page_title="KSD 모니터링 시스템",
        page_icon="📊",
        layout="wide"
    )

    st.title("📊 KSD 모니터링 시스템")

    try:
        monitor = KSDMonitor()

        # 송신/수신 현황을 Tab으로 구분
        tab1, tab2 = st.tabs(["📤 송신 현황", "📥 수신 현황"])

        with tab1:
            st.header("📤 송신 현황")
            send_stats, send_time = monitor.read_summary_log(is_send=True)
            display_data(send_stats, send_time, "송신")

        with tab2:
            st.header("📥 수신 현황")
            recv_stats, recv_time = monitor.read_summary_log(is_send=False)
            display_data(recv_stats, recv_time, "수신")
        st.write("")
        st.write("")
        st.markdown("---")
        st.write("")
        # 거래 이력 조회는 아래에 배치
        st.header("🔍 거래 이력 조회")
        display_transaction_history(monitor)

    except Exception as e:
        st.error(f"시스템 오류가 발생했습니다: {e}")

# 데이터 표시 함수 정의
def display_data(stats, log_time, title):
    """HTML 대시보드와 도넛 차트를 한 행에 표시하는 함수."""
    if not stats.empty:
        col1, col2 = st.columns(2)

        with col1:
            st.components.v1.html(
                create_metrics_html(stats, log_time, title),
                height=450,
                scrolling=True
            )

        with col2:
            fig = px.pie(
                stats,
                values='count',
                names='business_name',
                title=f"{title} 업무별 분포",
                hole=0.6
            )

            fig.update_traces(
                textposition='inside',
                textinfo='percent+label',
                texttemplate='%{label}<br>%{percent:.1%}',
                hovertemplate='<b>%{label}</b><br>건수: %{value:,.0f}<br>비율: %{percent:.1%}<extra></extra>',
                marker=dict(
                    colors=px.colors.qualitative.Set3,
                    line=dict(color='#1E1E1E', width=2)
                )
            )

            fig.update_layout(
                showlegend=False,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(t=40, l=0, r=0, b=0),
                title={
                    'font': dict(size=20, color='#E1E1E1'),
                    'y': 0.99,
                    'x': 0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'
                },
                annotations=[dict(
                    text=f'총 {stats["count"].sum():,}건',
                    x=0.5, y=0.5,
                    font=dict(size=20, color='#E1E1E1'),
                    showarrow=False
                )],
                font=dict(color='#E1E1E1')
            )

            st.plotly_chart(fig, use_container_width=True)

    else:
        st.info(f"{title} 데이터가 없습니다.")

# 거래 이력 조회 표시 함수
def display_transaction_history(monitor):
    """거래 이력 조회 기능을 구현."""
    with st.expander("검색 조건"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            start_date = st.date_input("시작일", value=datetime.now().date())
            start_time = st.time_input("시작 시간", value=datetime.strptime("00:00", "%H:%M").time())
        
        with col2:
            end_date = st.date_input("종료일", value=datetime.now().date())
            end_time = st.time_input("종료 시간", value=datetime.now().time())
        
        with col3:
            direction = st.selectbox("송수신 구분", options=['전체', 'SEND', 'RECV'])

        start_datetime = datetime.combine(start_date, start_time)
        end_datetime = datetime.combine(end_date, end_time)

    if st.button("조회", type="primary"):
        with st.spinner("데이터를 조회중입니다..."):
            tran_data = monitor.read_transaction_log(
                start_datetime,
                end_datetime,
                None if direction == '전체' else direction
            )

            if not tran_data.empty:
                st.dataframe(
                    tran_data.style.format({
                        'timestamp': lambda x: x.strftime('%Y-%m-%d %H:%M:%S')
                    }),
                    use_container_width=True
                )
            else:
                st.info("조회된 데이터가 없습니다.")

if __name__ == "__main__":
    main()
