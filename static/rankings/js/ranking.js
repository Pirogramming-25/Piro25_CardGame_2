document.addEventListener('DOMContentLoaded', () => {

  const podiumBlocks = document.querySelectorAll('.podium-block');
  podiumBlocks.forEach((block, i) => {
    const targetHeight = block.style.height || getComputedStyle(block).height;
    block.style.height = '0px';
    block.style.transition = 'height 0.5s ease';
    setTimeout(() => {
      block.style.height = targetHeight;
    }, 150 + i * 150);
  });

  const rankRows = document.querySelectorAll('.rank-row');
  rankRows.forEach((row, i) => {
    row.style.opacity = '0';
    row.style.transform = 'translateX(-12px)';
    row.style.transition = 'opacity 0.35s ease, transform 0.35s ease';
    setTimeout(() => {
      row.style.opacity = '1';
      row.style.transform = 'translateX(0)';
    }, 500 + i * 80);
  });

  const myRow = document.querySelector('.rank-row.me');
  if (myRow) {
    myRow.addEventListener('animationend', () => {
      myRow.classList.remove('pulse');
    });
    setTimeout(() => {
      myRow.classList.add('pulse');
    }, 500 + rankRows.length * 80 + 200);
  }

  const myPodiumAvatar = document.querySelector('.podium-slot.me .podium-avatar');
  if (myPodiumAvatar) {
    myPodiumAvatar.addEventListener('animationend', () => {
      myPodiumAvatar.classList.remove('pulse');
    });
    setTimeout(() => {
      myPodiumAvatar.classList.add('pulse');
    }, 150 + podiumBlocks.length * 150 + 500);
  }

});