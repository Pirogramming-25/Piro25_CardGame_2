document.addEventListener('DOMContentLoaded', function () {
  const profiles = document.querySelectorAll('.profile-card');
  const counterBtn = document.querySelector('.counterattack-btn');
  const selectedText = document.querySelector('.selected-user');
  // 💡 hidden input 요소 가져오기
  const defenderInput = document.getElementById('selected-defender-id');
  let selectedUser = null;
  let selectedUserId = null;

  counterBtn.classList.add('disabled');

  profiles.forEach(profile => {
    profile.addEventListener('click', function () {
      profiles.forEach(p => p.classList.remove('selected'));
      profile.classList.add('selected');

      // HTML의 data-user-id와 data-user(이름 등) 읽기
      selectedUserId = profile.dataset.userId;
      selectedUser = profile.dataset.user;

      // 💡 핵심: hidden input의 value에 유저 ID 주입!
      if (defenderInput) {
        defenderInput.value = selectedUserId;
      }

      if (selectedText) {
        selectedText.textContent = '선택한 유저 : ' + (selectedUser || selectedUserId);
      }

      counterBtn.classList.remove('disabled');
    });
  });

  counterBtn.addEventListener('click', function (e) {
    // 💡 selectedUserId 및 input value 검증
    if (!selectedUserId || (defenderInput && !defenderInput.value)) {
      e.preventDefault();
      alert('상대 유저를 먼저 선택해주세요!');
      return;
    }
    console.log('선택된 유저 ID:', selectedUserId);
  });
});