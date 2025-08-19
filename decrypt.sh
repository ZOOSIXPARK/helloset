#!/bin/bash

# decrypt.sh: stdin으로부터 Base64로 인코딩된 암호문을 읽어 복호화합니다.

# 마스터 키 파일 경로 (수정 가능)
KEY_FILE="${HOME}/.keys/db_master.key"

# 마스터 키 파일 존재 여부 확인
if [ ! -f "$KEY_FILE" ]; then
  echo "오류: 마스터 키 파일($KEY_FILE)을 찾을 수 없습니다." >&2
  exit 1
fi

# stdin으로부터 암호문을 읽어 복호화 실행
# -d: 복호화 모드
# -base64: 입력이 Base64로 인코딩되었음을 명시
openssl enc -d -aes-256-gcm -pbkdf2 -iter 100000 -pass "file:${KEY_FILE}" -base64
