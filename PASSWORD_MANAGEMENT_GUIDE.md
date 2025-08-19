# DB 암호의 안전한 관리 가이드 (OpenSSL 기반)

## 1. 개요

이 문서는 AIX 및 Linux 시스템에서 평문으로 관리되고 있는 데이터베이스(DB) 암호를 OpenSSL을 사용하여 안전하게 암호화하고, 필요할 때 복호화하여 사용하는 방법을 안내합니다.

이 가이드에서 제안하는 방식은 보안 감사 요구사항을 충족하고 최신 보안 표준을 따르는 것을 목표로 합니다.

## 2. 핵심 보안 개념

### AES-256-GCM: 강력한 인증 암호화

- **AES-256**: 미국 국립표준기술연구소(NIST)에서 지정한 표준 암호화 기술로, 현재 가장 신뢰받는 대칭키 암호화 방식 중 하나입니다.
- **GCM (Galois/Counter Mode)**: 암호화와 동시에 데이터의 `무결성`과 `인증`을 보장하는 AEAD(Authenticated Encryption with Associated Data) 방식입니다. 즉, 암호화된 데이터가 중간에 공격자에 의해 1비트라도 변경될 경우, 복호화 단계에서 이를 즉시 탐지할 수 있습니다. 이는 감사에서 매우 중요한 요소입니다.

### PBKDF2: 안전한 키 생성

사용자가 제공하는 마스터 비밀번호(Passphrase)를 그대로 암호화 키로 사용하면 보안에 취약할 수 있습니다. `PBKDF2`는 마스터 비밀번호에 `솔트(Salt)`라는 임의의 값을 추가하고, 수만 번 이상의 해시 함수를 반복 적용하여(이를 `Iteration`이라 함) 최종 암호화 키를 파생시킵니다. 이 과정은 무차별 대입 공격을 훨씬 더 어렵게 만듭니다.

### 마스터 키 파일: 모든 보안의 시작

모든 암호화/복호화의 기반이 되는 마스터 비밀번호를 담고 있는 파일입니다. 이 파일이 탈취되면 모든 암호가 해독될 수 있으므로, 시스템에서 가장 중요한 파일 중 하나로 다루어야 합니다. **파일 권한을 `400`으로 설정하여 소유자 외에는 아무도 읽을 수 없도록 하는 것이 필수입니다.**

## 3. 설정 절차

### 1단계: 마스터 키 파일 생성 및 보안 설정

암호화/복호화에 사용할 마스터 비밀번호를 담은 파일을 생성하고, 접근 권한을 강화합니다.

```bash
# 1. 키를 저장할 디렉토리 생성 (홈 디렉토리 아래에 .keys 와 같이 숨김 속성으로)
mkdir -p ~/.keys

# 2. 강력하고 예측 불가능한 마스터 비밀번호를 파일에 저장
# 예시: openssl rand -base64 32 > ~/.keys/db_master.key
echo "YourVeryStrong-And-Complex-Passphrase-Here-123!@#" > ~/.keys/db_master.key

# 3. 디렉토리와 파일에 대한 접근 권한 설정 (매우 중요!)
chmod 700 ~/.keys
chmod 400 ~/.keys/db_master.key

echo "마스터 키 파일 생성 및 보안 설정 완료."
```
**경고**: 마스터 비밀번호는 절대로 외부에 노출되어서는 안 됩니다.

### 2단계: 암호화/복호화 스크립트 준비

이 가이드와 함께 제공된 `encrypt.sh`와 `decrypt.sh` 스크립트를 서버의 적절한 위치(예: `/usr/local/bin`)에 두고, 실행 권한을 부여합니다.

```bash
chmod +x encrypt.sh decrypt.sh
```

## 4. 스크립트 사용법

### 암호화 (`encrypt.sh`)

DB 비밀번호와 같은 평문을 암호화합니다.

```bash
# 사용법: echo "평문" | ./encrypt.sh

# 예시: 'my_secret_db_password' 라는 문자열을 암호화
echo "my_secret_db_password" | ./encrypt.sh
```
- **결과**: `U2FsdGVkX1...` 와 같은 Base64로 인코딩된 암호문이 출력됩니다. 이 암호문을 설정 파일이나 필요한 곳에 저장하여 사용합니다.

### 복호화 (`decrypt.sh`)

암호문을 다시 평문으로 되돌립니다.

```bash
# 사용법: echo "암호문" | ./decrypt.sh

# 예시
echo "U2FsdGVkX1+vGhd9zGk5aUa2UP8jZ4v5/pGgM3bL3bYg8g==" | ./decrypt.sh
```
- **결과**: 원본 평문인 `my_secret_db_password`가 출력됩니다.

## 5. 실제 적용 예시 (어플리케이션 스크립트)

어플리케이션 구동 스크립트나 Crontab 등에서 암호화된 비밀번호를 사용하는 방법입니다.

1.  암호화된 DB 비밀번호를 파일에 저장합니다.
    ```bash
    echo "U2FsdGVkX1..." > /path/to/your/app/config/db_password.enc
    ```

2.  어플리케이션 실행 스크립트에서 복호화하여 환경변수로 주입합니다.
    ```bash
    #!/bin/bash

    # 암호화된 비밀번호 파일 경로
    ENCRYPTED_PW_FILE="/path/to/your/app/config/db_password.enc"

    # 복호화 스크립트를 실행하여 비밀번호를 변수에 담음
    export DB_PASSWORD=$(cat $ENCRYPTED_PW_FILE | /usr/local/bin/decrypt.sh)

    # 환경변수로 주입된 비밀번호를 사용하여 어플리케이션 실행
    /path/to/your/application --username myuser --password "$DB_PASSWORD"

    # (중요) 스크립트 종료 후 변수 unset
    unset DB_PASSWORD
    ```

## 6. 보안 및 감사 모범 사례

- **마스터 키 분리**: 가능하다면, 마스터 키 파일을 어플리케이션 서버가 아닌 별도의 안전한 공간에 보관하거나, **HashiCorp Vault**, **AWS KMS**와 같은 전문 시크릿 관리 솔루션을 도입하는 것이 가장 이상적인 방법입니다. 이 가이드의 방법은 차선책입니다.
- **정기적인 키 교체**: 보안 정책에 따라 마스터 키를 주기적으로 교체하는 것을 권장합니다.
- **감사 추적**: 누가, 언제 암호화/복호화 스크립트를 실행했는지 로깅(logging)하는 시스템(예: `logger` 명령어 연동)을 추가하면 감사 대응에 더욱 효과적입니다.
- **최소 권한 원칙**: 스크립트와 마스터 키 파일은 해당 DB 비밀번호가 꼭 필요한 시스템 계정만 접근할 수 있도록 소유자와 권한을 철저히 관리해야 합니다.
