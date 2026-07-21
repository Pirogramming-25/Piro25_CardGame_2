document.addEventListener('DOMContentLoaded', function () {
  const cards = document.querySelectorAll('.card');
  const nextBtn = document.getElementById('next-btn');
  const cardInput = document.getElementById('selected-card-input');
  const selectedCardNum = document.getElementById('selected-card-num');
  const form = document.getElementById('attack-card-form');

  let selectedCardValue = null;

  // 처음에 버튼 비활성화 스타일이 필요하다면 사용
  if (nextBtn) {
    nextBtn.classList.add('disabled');
  }

  cards.forEach(card => {
    card.addEventListener('click', function () {
      // 1. 모든 카드 선택 클래스 제거 후 클릭한 카드만 선택 처리
      cards.forEach(c => c.classList.remove('selected'));
      card.classList.add('selected');

      // 2. data-card 속성에서 숫자를 가져오고, 없으면 textContent 사용
      selectedCardValue = card.dataset.card || card.textContent.trim();

      // 3. 💡 핵심: hidden input의 value에 선택한 카드 숫자를 집어넣음!
      if (cardInput) {
        cardInput.value = selectedCardValue;
      }

      // 4. 화면 UI 텍스트 업데이트 및 버튼 비활성화 해제
      if (selectedCardNum) {
        selectedCardNum.textContent = selectedCardValue;
      }

      if (nextBtn) {
        nextBtn.classList.remove('disabled');
      }
    });
  });

  // 폼 제출 시 카드가 선택되지 않았으면 제출 방지
  if (form) {
    form.addEventListener('submit', function (e) {
      if (!cardInput || !cardInput.value) {
        e.preventDefault();
        alert('카드를 먼저 선택해주세요!');
      }
    });
  }
});