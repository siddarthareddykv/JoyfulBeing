/**
 * JoyfulBeing — Calm Experience Controller
 * Ambient soundscapes dock, 60-second Mindful Minute pause, and circadian themes.
 */

(function () {
  'use strict';

  // Clear any previously saved theme to ensure pristine background colors
  try {
    localStorage.removeItem('joyfulbeing_calm_theme');
    document.documentElement.removeAttribute('data-calm-theme');
  } catch (e) {}

  // --- 2. Ambient Soundscape Dock ---
  function initSoundscapeUI() {
    const soundBtn = document.getElementById('calmSoundToggle');
    const soundDock = document.getElementById('calmSoundDock');
    const closeBtn = document.getElementById('calmSoundClose');
    const volumeSlider = document.getElementById('calmVolumeSlider');
    const trackBtns = document.querySelectorAll('.calm-track-btn');
    const nowPlayingText = document.getElementById('calmNowPlaying');

    if (!soundBtn || !soundDock) return;

    soundBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      soundDock.classList.toggle('is-open');
    });

    closeBtn?.addEventListener('click', () => {
      soundDock.classList.remove('is-open');
    });

    document.addEventListener('click', (e) => {
      if (!soundDock.contains(e.target) && !soundBtn.contains(e.target)) {
        soundDock.classList.remove('is-open');
      }
    });

    if (volumeSlider) {
      volumeSlider.addEventListener('input', (e) => {
        window.calmAudio?.setVolume(parseFloat(e.target.value));
      });
    }

    trackBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        const track = btn.dataset.track;
        const isPlaying = window.calmAudio?.playTrack(track);

        trackBtns.forEach(b => b.classList.remove('is-active'));
        if (isPlaying) {
          btn.classList.add('is-active');
          soundBtn.classList.add('is-playing');
          if (nowPlayingText) nowPlayingText.textContent = `Playing: ${btn.textContent.trim()}`;
        } else {
          soundBtn.classList.remove('is-playing');
          if (nowPlayingText) nowPlayingText.textContent = 'Paused';
        }
      });
    });
  }

  // --- 3. "Take a Mindful Minute" (Interactive 60s Calm Reset) ---
  let minuteTimer = null;
  let remainingSeconds = 60;
  let breathPhase = 'inhale'; // inhale, hold, exhale

  function initMindfulMinute() {
    const triggerBtn = document.getElementById('mindfulMinuteBtn');
    const modal = document.getElementById('mindfulModal');
    const closeBtn = document.getElementById('mindfulClose');
    const startPauseBtn = document.getElementById('mindfulActionBtn');
    const orb = document.getElementById('mindfulOrb');
    const instruction = document.getElementById('mindfulInstruction');
    const timerDisplay = document.getElementById('mindfulTimer');
    const chimeToggle = document.getElementById('mindfulChimeToggle');

    if (!triggerBtn || !modal) return;

    triggerBtn.addEventListener('click', () => {
      openMindfulModal();
    });

    closeBtn?.addEventListener('click', () => {
      closeMindfulModal();
    });

    modal.addEventListener('click', (e) => {
      if (e.target === modal) closeMindfulModal();
    });

    function openMindfulModal() {
      modal.classList.add('is-active');
      resetSession();
      startSession();
    }

    function closeMindfulModal() {
      modal.classList.remove('is-active');
      stopSession();
    }

    function resetSession() {
      remainingSeconds = 60;
      updateTimerUI(60);
      instruction.textContent = 'Prepare gently. Inhale deeply...';
      orb.className = 'mindful-orb';
    }

    function startSession() {
      if (minuteTimer) clearInterval(minuteTimer);

      let cycleTime = 0; // 0..11 seconds (4s in, 3s hold, 5s out)
      breathCycleStep(0);

      minuteTimer = setInterval(() => {
        remainingSeconds--;
        cycleTime = (cycleTime + 1) % 12;

        updateTimerUI(remainingSeconds);
        breathCycleStep(cycleTime);

        if (remainingSeconds <= 0) {
          endSession();
        }
      }, 1000);
    }

    function breathCycleStep(sec) {
      if (sec === 0) {
        instruction.textContent = 'Inhale slowly...';
        orb.className = 'mindful-orb is-inhale';
        if (chimeToggle?.checked) window.calmAudio?.ringChime(432);
      } else if (sec === 4) {
        instruction.textContent = 'Hold your breath gently...';
        orb.className = 'mindful-orb is-hold';
      } else if (sec === 7) {
        instruction.textContent = 'Exhale completely and soften...';
        orb.className = 'mindful-orb is-exhale';
        if (chimeToggle?.checked) window.calmAudio?.ringChime(320);
      }
    }

    function updateTimerUI(sec) {
      if (timerDisplay) {
        const m = Math.floor(sec / 60);
        const s = sec % 60;
        timerDisplay.textContent = `${m}:${s < 10 ? '0' : ''}${s}`;
      }
    }

    function stopSession() {
      if (minuteTimer) {
        clearInterval(minuteTimer);
        minuteTimer = null;
      }
    }

    function endSession() {
      stopSession();
      instruction.textContent = '🌸 Peace in your heart. You are centered.';
      orb.className = 'mindful-orb is-complete';
      if (chimeToggle?.checked) window.calmAudio?.ringChime(528);
    }
  }

  // --- Document Ready ---
  document.addEventListener('DOMContentLoaded', () => {
    initSoundscapeUI();
    initMindfulMinute();
  });
})();

