#!/bin/bash

# 이 스크립트는 `expect` 유틸리티가 필요합니다.
# macOS: brew install expect
# Ubuntu: sudo apt-get install expect

# --- 설정 ---
CREDENTIALS_FILE="a.txt"
PUBLIC_KEY_FILE="id_rsa.pub"
EXPECT_SCRIPT="./sftp_upload.exp" # expect 스크립트 경로
# --- 설정 끝 ---

# 필수 파일 존재 여부 확인
if [ ! -f "$CREDENTIALS_FILE" ]; then
    echo "오류: $CREDENTIALS_FILE 파일을 찾을 수 없습니다."
    exit 1
fi
if [ ! -f "$PUBLIC_KEY_FILE" ]; then
    echo "오류: $PUBLIC_KEY_FILE 파일을 찾을 수 없습니다."
    exit 1
fi
if [ ! -f "$EXPECT_SCRIPT" ]; then
    echo "오류: $EXPECT_SCRIPT 파일을 찾을 수 없습니다."
    echo "      sftp_upload.exp 스크립트가 동일한 디렉토리에 있는지 확인하세요."
    exit 1
fi

# a.txt 파일을 한 줄씩 읽어들여 처리
while IFS=':' read -r user password ip; do
    # 주석이거나 빈 줄은 건너뜁니다.
    if [[ -z "$user" || $user == \#* ]]; then
        continue
    fi

    echo "==> $ip 서버로 $PUBLIC_KEY_FILE 파일 업로드를 시도합니다. (사용자: $user)"

    # expect 스크립트를 호출하여 파일 업로드 실행
    "$EXPECT_SCRIPT" "$user" "$password" "$ip" "$PUBLIC_KEY_FILE"

    if [ $? -eq 0 ]; then
        echo "성공: $ip 서버에 성공적으로 업로드한 것으로 보입니다."
    else
        echo "실패: $ip 서버에 업로드하는 중 오류가 발생했습니다."
    fi
    echo "--------------------------------------------------"
done < "$CREDENTIALS_FILE"

echo "모든 작업이 완료되었습니다."
