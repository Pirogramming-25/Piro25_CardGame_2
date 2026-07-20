document.addEventListener('DOMContentLoaded', function () {
  const cards = document.querySelectorAll('.card');
  const nextBtn = document.querySelector('.next-btn');
  const selectedText = document.querySelector('.selected-card');
  let selectedCard = null;

  nextBtn.classList.add('disabled');

  cards.forEach(card => {
    card.addEventListener('click', function () {
      cards.forEach(c => c.classList.remove('selected'));
      card.classList.add('selected');
      selectedCard = card.textContent.trim();

      if (selectedText) {
        selectedText.textContent = '선택한 카드 : ' + selectedCard;
      }

      nextBtn.classList.remove('disabled');
    });
  });

  nextBtn.addEventListener('click', function (e) {
    if (!selectedCard) {
      e.preventDefault();
      alert('카드를 먼저 선택해주세요!');
      return;
    }
    document.cookie = 'selected_card=' + selectedCard + '; path=/';
  });
});
