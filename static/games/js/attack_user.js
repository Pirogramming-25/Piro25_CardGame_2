document.addEventListener('DOMContentLoaded', function () {
  const profiles = document.querySelectorAll('.profile-card');
  const counterBtn = document.querySelector('.counterattack-btn');
  const selectedText = document.querySelector('.selected-user');
  let selectedUser = null;

  counterBtn.classList.add('disabled');

  profiles.forEach(profile => {
    profile.addEventListener('click', function () {
      profiles.forEach(p => p.classList.remove('selected'));
      profile.classList.add('selected');
      selectedUser = profile.dataset.user;

      if (selectedText) {
        selectedText.textContent = '선택한 유저 : ' + selectedUser;
      }

      counterBtn.classList.remove('disabled');
    });
  });

  counterBtn.addEventListener('click', function (e) {
    if (!selectedUser) {
      e.preventDefault();
      alert('상대 유저를 먼저 선택해주세요!');
      return;
    }
    console.log('선택된 유저:', selectedUser);
  });
});
