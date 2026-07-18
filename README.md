# Piro25_CardGame_2
카드게임 2조 레포지토리입니다.

---

## 파일 구조
```
pirogaming-game/
├── config/                  # 프로젝트 설정
│   ├── settings.py          # ⚠️ 공통 - 앱 등록시에만 수정
│   └── urls.py              # ⚠️ 공통 - include() 한 줄씩만
│
├── accounts/                # 👤 1번 담당
│   ├── models.py            # User (누적 점수 필드 포함)
│   ├── views.py             # 로그인/회원가입/소셜 로그인
│   ├── urls.py
│   └── templates/accounts/
│       ├── login.html       # 로그인 전 메인
│       └── main.html        # 로그인 후 메인
│
├── games/
│   ├── models.py            # ⚠️ 공통 - Game 모델 (첫날 확정)
│   ├── urls.py              # ⚠️ 공통 - 한 줄씩만 추가
│   ├── views/               # 파일 분리로 conflict 방지 ✨
│   │   ├── attack.py        # ⚔️ 2번 담당
│   │   ├── list.py          # 📋 3번 담당
│   │   └── detail.py        # 🔍 4번 담당 (detail + 반격 + 판정)
│   └── templates/games/
│       ├── attack.html      # 2번
│       ├── game_list.html   # 3번
│       ├── game_detail.html # 4번
│       └── counter.html     # 4번
│
├── rankings/                # 🏆 5번 담당
│   ├── views.py
│   ├── urls.py
│   └── templates/rankings/ranking.html
│
├── templates/base.html      # 5번이 제작, 나머지는 extends만
└── static/                  # css/js를 앱별 폴더로 나눠서 관리
```
