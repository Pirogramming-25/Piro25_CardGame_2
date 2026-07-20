# Piro25_CardGame_2

카드게임 2조 레포지토리입니다.

---

## 팀원 및 역할 분담

| 파트                     |  담당자  | 담당 브랜치           | 설명                                                                                     |
| ------------------------ | ------ | --------------------- | ---------------------------------------------------------------------------------------- |
| 1. 인증 담당             |  홍연우  | `feature/accounts`    | 로그인 전/후 메인 화면, 회원가입, 소셜 로그인(OAuth)                                     |
| 2. 공격하기 담당         |  유채영  | `feature/attack`      | 게임 시작 페이지, 카드 5장 랜덤 생성, 상대 유저 선택, 게임 생성 API                      |
| 3. 게임 전적 담당        |  서영은  | `feature/game-list`   | 게임 리스트 페이지, 상태별 분기(진행중/CounterAttack/종료), 게임 취소 기능               |
| 4. 게임 상세 + 반격 담당 |  강성훈  | `feature/game-detail` | detail 페이지 3가지 상태 표시, 반격하기 페이지, 카드 선택 후 승패 판정 + 점수 반영 로직  |
| 5. 랭킹 + 공통 담당      |  강보민  | `feature/rankings`    | 랭킹 페이지(누적 점수 정렬), User/Game 모델 설계 주도, 공통 레이아웃(네비게이션바), 배포 |

---

## 브랜치 & 작업 규칙

- `develop` 브랜치에 초기 구조가 올라가 있고, 담당 브랜치가 미리 만들어져 있습니다. 각자 자신의 `feature/*` 브랜치에서 작업하세요.
- ⚠️ **공통 파일** — `config/settings.py`, `config/urls.py`, `games/models.py`, `games/urls.py`는 정해진 한 줄 추가 외 수정 금지 (다른 담당자와 충돌 방지)
- 작업 시작할 때마다 `git pull origin develop`으로 최신화하고 시작하기
- 파트 완료되면 `feature/*` → `develop`으로 PR 올리기 (`develop` → `main` PR은 별도)

---

## 파일 구조

```
Piro25_CardGame_2/
├── config/                       # 프로젝트 설정
│   ├── settings.py               # ⚠️ 공통 - 앱 등록시에만 수정
│   └── urls.py                   # ⚠️ 공통 - include() 한 줄씩만
│
├── accounts/                     # 👤 1. 인증 담당 (홍연우)
│   ├── models.py                 # User (누적 점수 필드 포함)
│   ├── views.py                  # 로그인/회원가입/소셜 로그인
│   ├── urls.py
│   └── templates/accounts/
│       ├── login.html            # 로그인 전 메인
│       └── main.html             # 로그인 후 메인
│
├── games/
│   ├── models.py                 # ⚠️ 공통 - Game 모델 (확정)
│   ├── urls.py                   # ⚠️ 공통 - 한 줄씩만 추가
│   ├── tests.py
│   ├── views/                    # 파일 분리로 conflict 방지 ✨
│   │   ├── attack.py             # ⚔️ 2. 공격하기 담당 (유채영)
│   │   ├── list.py               # 📋 3. 게임 전적 담당 (서영은)
│   │   └── detail.py             # 🔍 4. 게임 상세 + 반격 담당 (강성훈)
│   └── templates/games/
│       ├── attack.html
│       ├── game_list.html
│       ├── game_detail.html
│       └── counter.html
│
├── rankings/                     # 🏆 5. 랭킹 + 공통 담당 (강보민)
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── templates/rankings/ranking.html
│
├── templates/base.html
└── static/                       # css/js/images/fonts를 앱별 폴더로 나눠서 관리
    ├── accounts/{css,images,js}
    ├── games/{css,fonts,images,js}
    └── rankings/{css,images,js}
```
