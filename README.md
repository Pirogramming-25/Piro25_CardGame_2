# 🃏 Piro25_CardGame_2

> 숫자 카드 한 장으로 승부를 거는 1:1 대결 게임

카드게임 2조 레포지토리입니다. 상대에게 카드로 공격을 걸고, 상대가 반격 카드를
선택하면 미리 정해진 승리 조건에 따라 승패가 갈리고 점수가 오갑니다.

제25기 피로그래밍(Pirogramming) 팀 프로젝트입니다.

---

## 🎮 게임 규칙

1. **공격** — 공격자는 1~10 중 무작위로 뽑힌 카드 5장 중 1장을 선택하고, 대결할 상대를 고릅니다.
   이때 **승리 조건(높은 숫자 승 / 낮은 숫자 승)이 서버에서 랜덤으로 확정**되어 저장되며,
   수비자는 반격하기 전까지 이 조건을 알 수 없습니다.
2. **대기** — 게임은 `반격 대기중(WAITING)` 상태가 되고, 공격자는 상대가 반격할 때까지 기다립니다.
   (아직 반격받지 않은 게임은 공격자가 직접 취소할 수 있습니다.)
3. **반격** — 수비자도 무작위 카드 5장 중 1장을 선택해 반격합니다.
4. **판정 & 점수 반영** — 두 카드를 비교해 승자를 정하고, 게임은 `종료(FINISHED)` 상태가 됩니다.
   - 승자: 자신이 낸 카드 숫자만큼 누적 점수 **+**
   - 패자: 자신이 낸 카드 숫자만큼 누적 점수 **-**
   - 두 카드가 같으면 **무승부**, 점수 변동 없음
5. **랭킹** — 모든 유저가 누적 점수 기준으로 순위표에 오릅니다.

---

## ✨ 핵심 기능

| 기능              | 설명                                                                                    |
| ----------------- | --------------------------------------------------------------------------------------- |
| 로그인 · 회원가입 | 아이디/비밀번호 로그인 + Google · Kakao · Naver 소셜 로그인(OAuth)                      |
| 공격하기          | 랜덤 카드 5장 중 1장 선택 → 상대 유저 선택 → 게임 생성 (승리 조건 랜덤 확정)            |
| 게임 리스트       | 내가 걸었거나 받은 게임을 상태별(대기중/종료)로 표시, 4개 단위 페이지네이션, 게임 취소  |
| 게임 상세 · 반격  | 공격자 대기 / 수비자 대기 / 종료 3가지 상태별 화면, 폴링으로 상대 반격 여부 실시간 확인 |
| 승패 판정         | 카드 비교 후 승자/패자 점수 자동 반영 (트랜잭션으로 중복 반격 요청 방지)                |
| 랭킹              | 누적 점수 내림차순 정렬, 상위 3명 별도 표시                                             |
| 아바타            | 상대 선택 · 게임 리스트 · 랭킹에서 이름 + 아바타로 유저를 시각적으로 구분               |

유저마다 `user.id % 5`로 `static/games/images/avatar/user1~5.png` 중 하나가 고정 배정되어,
같은 유저는 어느 화면에서나 항상 같은 아바타로 표시됩니다(별도 DB 필드 없이 계산으로 결정).

---

## 🚀 로컬 실행 방법
```
★ .env 파일이 반드시 필요하니 아래의 링크에서 .env 값을 복사한 후 본인 폴더에 생성해주세요!! ★
```
https://app.notion.com/p/env-3a3b1e86a9e4807085b0ccae162d0e14?source=copy_link

```bash
# 1. 저장소 클론
git clone https://github.com/Pirogramming-25/Piro25_CardGame_2.git
cd Piro25_CardGame_2

# 2. 가상환경 생성 및 활성화
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# 3. 의존성 설치
pip install -r requirements.txt

# 4. .env 파일 생성
#    .env.example을 참고해 최상위 폴더에 .env 파일을 만들고 소셜 로그인 키를 채웁니다.
#    (.env는 git에 올라가지 않으므로 각자 생성해야 합니다. 값이 없으면 해당 소셜 로그인만 비활성화됩니다.)
cp .env.example .env

# 5. 마이그레이션 & 서버 실행
python manage.py migrate
python manage.py runserver
```

실행 후 브라우저에서 http://localhost:8000 접속

### Docker로 실행

**로컬에서 직접 빌드**

```bash
docker compose up --build
```

**미리 빌드된 이미지로 실행**

```bash
docker pull kangbomin/piro25-cardgame-2
docker run --rm -p 8000:8000 --env-file .env kangbomin/piro25-cardgame-2
```

실행 후 브라우저에서 http://127.0.0.1:8000 접속

- `.env` 파일을 그대로 읽어 소셜 로그인 키를 주입합니다 (실행 전 `.env` 파일이 있어야 합니다).
- `SECRET_KEY` · `DEBUG` · `ALLOWED_HOSTS`도 환경변수로 제어됩니다 (`config/settings.py`).
  값을 넣지 않으면 `DEBUG=True`, `ALLOWED_HOSTS=[]`인 개발용 기본값으로 동작합니다.
- 배포용 이미지(`Dockerfile`)는 `collectstatic` 후 `migrate` → `gunicorn`으로 기동됩니다.

---

## 🛠️ 기술 스택

| 구분     | 기술                                                |
| -------- | --------------------------------------------------- |
| Backend  | Django 5.2                                          |
| Frontend | HTML · CSS · JS                                     |
| Database | SQLite3                                             |
| 인증     | Django 세션 로그인 + Google/Kakao/Naver (직접 구현) |
| 배포     | Docker · Gunicorn · WhiteNoise                      |

---

## 📁 프로젝트 구조

```
Piro25_CardGame_2/
├── config/                    # 프로젝트 설정
│   ├── settings.py            # ⚠️ 공통 - 앱 등록시에만 수정
│   └── urls.py                # ⚠️ 공통 - include() 한 줄씩만
│
├── accounts/                  # 👤 1. 인증 담당 (홍연우)
│   ├── models.py              # User (누적 점수 필드 포함)
│   ├── views.py                # 로그인/회원가입/소셜 로그인(Google·Kakao·Naver)
│   ├── env.py                  # .env 파일을 os.environ으로 로드하는 유틸
│   ├── urls.py
│   └── templates/accounts/
│
├── games/
│   ├── models.py               # ⚠️ 공통 - Game 모델 (확정)
│   ├── urls.py                 # ⚠️ 공통 - 한 줄씩만 추가
│   ├── views/                  # 파일 분리로 conflict 방지 ✨
│   │   ├── attack.py           # ⚔️ 2. 공격하기 담당 (유채영)
│   │   ├── list.py             # 📋 3. 게임 전적 담당 (서영은)
│   │   └── detail.py           # 🔍 4. 게임 상세 + 반격 담당 (강성훈)
│   └── templates/games/
│
├── rankings/                   # 🏆 5. 랭킹 + 공통 담당 (강보민)
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── templates/rankings/
│
├── templates/base.html
├── static/                     # css/js/images/fonts를 앱별 폴더로 나눠서 관리
│   ├── accounts/{css,images,js}
│   ├── games/{css,fonts,images,js}
│   └── rankings/{css,images,js}
│
├── Dockerfile                   # collectstatic → migrate → gunicorn으로 기동
├── docker-compose.yml           # web 서비스 + .env 로드
└── .dockerignore
```

---

## 🌿 브랜치 & 작업 규칙

- `develop` 브랜치에 초기 구조가 올라가 있고, 담당 브랜치가 미리 만들어져 있습니다. 각자 자신의 `feature/*` 브랜치에서 작업하세요.
- ⚠️ **공통 파일** — `config/settings.py`, `config/urls.py`, `games/models.py`, `games/urls.py`는 정해진 한 줄 추가 외 수정 금지 (다른 담당자와 충돌 방지)
- 작업 시작할 때마다 `git pull origin develop`으로 최신화하고 시작하기
- 파트 완료되면 `feature/*` → `develop`으로 PR 올리기 (`develop` → `main` PR은 별도)

---

## 👥 팀원 및 역할 분담

| 파트                     | 담당자 | 담당 브랜치           | 설명                                                                                     |
| ------------------------ | ------ | --------------------- | ---------------------------------------------------------------------------------------- |
| 1. 인증 담당             | 홍연우 | `feature/accounts`    | 로그인 전/후 메인 화면, 회원가입, 소셜 로그인(OAuth)                                     |
| 2. 공격하기 담당         | 유채영 | `feature/attack`      | 게임 시작 페이지, 카드 5장 랜덤 생성, 상대 유저 선택, 게임 생성 API                      |
| 3. 게임 전적 담당        | 서영은 | `feature/game-list`   | 게임 리스트 페이지, 상태별 분기(진행중/CounterAttack/종료), 게임 취소 기능               |
| 4. 게임 상세 + 반격 담당 | 강성훈 | `feature/game-detail` | detail 페이지 3가지 상태 표시, 반격하기 페이지, 카드 선택 후 승패 판정 + 점수 반영 로직  |
| 5. 랭킹 + 공통 담당      | 강보민 | `feature/rankings`    | 랭킹 페이지(누적 점수 정렬), User/Game 모델 설계 주도, 공통 레이아웃(네비게이션바), 배포 |

---

## 📎 협업 문서

| 도구   | 용도             | 링크                                                                                                                                       |
| ------ | ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| Figma  | 화면 디자인/시안 | [Figma 디자인](https://www.figma.com/design/Fxb0RcgjKCW4lkIMB9Ghou/%EC%A0%9C%EB%AA%A9-%EC%97%86%EC%9D%8C?node-id=0-1&t=rCZ62DoMC68eFRnL-1) |
| Notion | 기획/회의 문서   | [Notion 문서](https://app.notion.com/p/4-2-cb3b1e86a9e4824f9b9681f5e62e1c2c?source=copy_link)                                              |
