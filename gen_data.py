import os
from datetime import datetime, timedelta
import random
from pathlib import Path

# 작업 디렉토리 설정
BASE_DIR = r"D:\Daily\20241028"
TEST_DATA_DIR = os.path.join(BASE_DIR, "test_data")

def create_test_directories():
    """테스트 데이터 디렉토리 생성"""
    os.makedirs(TEST_DATA_DIR, exist_ok=True)
    print(f"Created test directory: {TEST_DATA_DIR}")

def generate_test_data():
    """테스트 데이터 생성"""
    current_time = datetime.now().replace(second=0, microsecond=0)
    time_str = current_time.strftime('%m%d%H%M')
    
    # 1. 총집계 로그 생성 (s.ksd653.log.MMDDHHmm)
    send_summary = [
        "631:150",
        "632:200",
        "633:180",
        "634:120",
        "635:90",
        "636:110",
        "637:85",
        "638:95",
        "639:75",
        "640:60"
    ]
    
    recv_summary = [
        "631:145",
        "632:195",
        "633:175",
        "634:115",
        "635:85",
        "636:105",
        "637:80",
        "638:90",
        "639:70",
        "640:55"
    ]
    
    # 송신 총집계 파일 생성
    with open(os.path.join(TEST_DATA_DIR, f"s.ksd653.log.{time_str}"), 'w') as f:
        f.write('\n'.join(send_summary))
    
    # 수신 총집계 파일 생성
    with open(os.path.join(TEST_DATA_DIR, f"r.ksd653.log.{time_str}"), 'w') as f:
        f.write('\n'.join(recv_summary))
    
    # 2. 거래 이력 로그 생성
    send_transactions = []
    recv_transactions = []
    
    # 각각 20개의 거래 이력 생성
    for i in range(20):
        timestamp = current_time - timedelta(seconds=random.randint(0, 59))
        timestamp_str = timestamp.strftime('%Y%m%d%H%M%S')
        
        # 송신 거래
        code = f"63{random.randint(1,9)}"
        send_transactions.append(f"{timestamp_str}:aaaa코드bbbb_{i:04d}:{code}:SEND")
        
        # 수신 거래
        code = f"63{random.randint(1,9)}"
        recv_transactions.append(f"{timestamp_str}:aaaa코드bbbb_{i:04d}:{code}:RECV")
    
    # 송신 거래 이력 파일 생성
    with open(os.path.join(TEST_DATA_DIR, f"s.tran.ksd653.log.{time_str}"), 'w') as f:
        f.write('\n'.join(sorted(send_transactions)))
    
    # 수신 거래 이력 파일 생성
    with open(os.path.join(TEST_DATA_DIR, f"r.tran.ksd653.log.{time_str}"), 'w') as f:
        f.write('\n'.join(sorted(recv_transactions)))
    
    print(f"\nGenerated test files for time: {time_str}")
    print("\nCreated files:")
    for file in os.listdir(TEST_DATA_DIR):
        print(f"  - {file}")

if __name__ == "__main__":
    create_test_directories()
    generate_test_data()
