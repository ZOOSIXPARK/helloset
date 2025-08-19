#!/bin/bash

# encrypt.sh: stdin으로부터 평문을 읽어 AES-256-GCM 방식으로 암호화합니다.

# 마스터 키 파일 경로 (수정 가능)
# 홈 디렉토리의 .keys/db_master.key 파일을 사용하도록 설정
KEY_FILE="${HOME}/.keys/db_master.key"

# 마스터 키 파일 존재 여부 확인
if [ ! -f "$KEY_FILE" ]; then
  echo "오류: 마스터 키 파일($KEY_FILE)을 찾을 수 없습니다." >&2
  exit 1
fi

# stdin으로부터 평문을 읽어 암호화 실행
# -aes-256-gcm: 암호화 알고리즘 및 모드
# -salt: 암호화 시 임의의 솔트를 추가하여 보안 강화 (기본값)
# -pbkdf2: 키 파생 함수 사용
# -iter 100000: PBKDF2 반복 횟수 (높을수록 안전)
# -pass file:...: 암호화에 사용할 마스터 키 파일 지정
# -base64: 결과를 Base64로 인코딩하여 출력
openssl enc -aes-256-gcm -salt -pbkdf2 -iter 100000 -pass "file:${KEY_FILE}" -base64
