#!/bin/bash

# ==============================================================================
# connect_db.sh: 암호화된 비밀번호를 복호화하여 DB에 접속하는 예제 스크립트
# ==============================================================================

# --- 설정 (사용자 환경에 맞게 수정) ---

# 1. DB 접속 정보
DB_USER="your_db_user"
DB_HOST="your_db_host"
DB_NAME="your_db_name" # Oracle의 경우 SID 또는 Service Name

# 2. 암호화된 비밀번호가 저장된 파일의 절대 경로
ENCRYPTED_PW_FILE="/home/user/config/db_password.enc"

# 3. decrypt.sh 스크립트의 절대 경로
DECRYPT_SCRIPT="/usr/local/bin/decrypt.sh"

# --- 스크립트 실행 ---

# 필수 파일 존재 여부 확인
if [ ! -f "$ENCRYPTED_PW_FILE" ]; then
    echo "오류: 암호화된 비밀번호 파일($ENCRYPTED_PW_FILE)을 찾을 수 없습니다." >&2
    exit 1
fi
if [ ! -x "$DECRYPT_SCRIPT" ]; then
    echo "오류: 복호화 스크립트($DECRYPT_SCRIPT)를 찾을 수 없거나 실행 권한이 없습니다." >&2
    exit 1
fi

# 복호화 스크립트를 실행하여 비밀번호를 변수에 저장
# || exit 1 구문은 복호화 실패 시 스크립트를 즉시 중단시킴
DB_PASSWORD=$(cat "$ENCRYPTED_PW_FILE" | "$DECRYPT_SCRIPT" || exit 1)

# 복호화에 실패했는지 확인 (결과가 비어있는 경우)
if [ -z "$DB_PASSWORD" ]; then
    echo "오류: 비밀번호 복호화에 실패했습니다. 마스터 키 또는 암호 파일이 올바른지 확인하세요." >&2
    exit 1
fi

echo "DB 접속을 시도합니다..."

# --- DB 클라이언트별 접속 명령어 (사용하는 DB에 맞게 주석 해제 및 수정) ---

# 예제 1: Oracle (sqlplus)
# sqlplus -S "${DB_USER}/${DB_PASSWORD}@${DB_HOST}/${DB_NAME}" <<EOF
# SELECT * FROM DUAL;
# exit;
# EOF

# 예제 2: MySQL (mysql)
# mysql -u"${DB_USER}" -p"${DB_PASSWORD}" -h"${DB_HOST}" "${DB_NAME}" -e "SELECT 1;"

# 예제 3: PostgreSQL (psql)
# export PGPASSWORD="${DB_PASSWORD}"
# psql -U "${DB_USER}" -h "${DB_HOST}" -d "${DB_NAME}" -c "SELECT 1;"
# unset PGPASSWORD


# --- 메모리에서 비밀번호 즉시 제거 (보안 필수 사항) ---
# 위 명령어 실행 후 DB_PASSWORD 변수를 즉시 메모리에서 삭제하여 노출 시간을 최소화합니다.
unset DB_PASSWORD

echo "DB 접속 스크립트 완료."
