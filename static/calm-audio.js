/**
 * JoyfulBeing — Calm Web Audio Engine
 * Procedural ambient soundscapes and meditative chimes using HTML5 Web Audio API.
 * 100% client-side, zero MP3 downloads, zero latency.
 */

class CalmAudioEngine {
  constructor() {
    this.ctx = null;
    this.masterGain = null;
    this.currentTrack = null;
    this.activeNodes = [];
    this.isPlaying = false;
    this.volume = 0.5;
  }

  init() {
    if (!this.ctx) {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      this.ctx = new AudioContext();
      this.masterGain = this.ctx.createGain();
      this.masterGain.gain.setValueAtTime(this.volume, this.ctx.currentTime);
      this.masterGain.connect(this.ctx.destination);
    }
    if (this.ctx.state === 'suspended') {
      this.ctx.resume();
    }
  }

  setVolume(val) {
    this.volume = Math.max(0, Math.min(1, val));
    if (this.masterGain && this.ctx) {
      this.masterGain.gain.setTargetAtTime(this.volume, this.ctx.currentTime, 0.05);
    }
  }

  stop() {
    if (!this.isPlaying) return;
    this.isPlaying = false;
    this.currentTrack = null;

    if (this.activeNodes.length > 0) {
      this.activeNodes.forEach(node => {
        try {
          if (node.stop) node.stop();
          if (node.disconnect) node.disconnect();
        } catch (e) {}
      });
      this.activeNodes = [];
    }
  }

  playTrack(trackName) {
    this.init();
    if (this.isPlaying && this.currentTrack === trackName) {
      this.stop();
      return false; // Stopped
    }

    this.stop();
    this.isPlaying = true;
    this.currentTrack = trackName;

    switch (trackName) {
      case 'ocean':
        this.startOceanWaves();
        break;
      case 'rain':
        this.startGentleRain();
        break;
      case 'bowl':
        this.startSingingBowlDrone();
        break;
      case 'breeze':
        this.startForestBreeze();
        break;
      case 'om':
        this.startOmResonance();
        break;
      default:
        this.startOceanWaves();
    }
    return true; // Playing
  }

  // --- Soundscape 1: Ocean Waves (Filtered Pink Noise with Cyclical LFO) ---
  startOceanWaves() {
    const bufferSize = 2 * this.ctx.sampleRate;
    const noiseBuffer = this.ctx.createBuffer(1, bufferSize, this.ctx.sampleRate);
    const output = noiseBuffer.getChannelData(0);
    let b0 = 0, b1 = 0, b2 = 0, b3 = 0, b4 = 0, b5 = 0, b6 = 0;

    for (let i = 0; i < bufferSize; i++) {
      const white = Math.random() * 2 - 1;
      b0 = 0.99886 * b0 + white * 0.0555179;
      b1 = 0.99332 * b1 + white * 0.0750759;
      b2 = 0.96900 * b2 + white * 0.1538520;
      b3 = 0.86650 * b3 + white * 0.3104856;
      b4 = 0.55000 * b4 + white * 0.5329522;
      b5 = -0.7616 * b5 - white * 0.0168980;
      output[i] = (b0 + b1 + b2 + b3 + b4 + b5 + b6 + white * 0.5362) * 0.05;
      b6 = white * 0.115926;
    }

    const whiteNoise = this.ctx.createBufferSource();
    whiteNoise.buffer = noiseBuffer;
    whiteNoise.loop = true;

    // Filter to simulate ocean swells
    const filter = this.ctx.createBiquadFilter();
    filter.type = 'lowpass';
    filter.frequency.setValueAtTime(320, this.ctx.currentTime);
    filter.Q.setValueAtTime(2.5, this.ctx.currentTime);

    // LFO for wave rhythm (period ~7.5 seconds)
    const lfo = this.ctx.createOscillator();
    lfo.frequency.setValueAtTime(0.13, this.ctx.currentTime); // ~7.7s per wave cycle

    const lfoGain = this.ctx.createGain();
    lfoGain.gain.setValueAtTime(280, this.ctx.currentTime);

    lfo.connect(lfoGain);
    lfoGain.connect(filter.frequency);

    const waveGain = this.ctx.createGain();
    waveGain.gain.setValueAtTime(0.7, this.ctx.currentTime);

    whiteNoise.connect(filter);
    filter.connect(waveGain);
    waveGain.connect(this.masterGain);

    whiteNoise.start();
    lfo.start();

    this.activeNodes.push(whiteNoise, lfo, filter, lfoGain, waveGain);
  }

  // --- Soundscape 2: Gentle Rain ---
  startGentleRain() {
    const bufferSize = 2 * this.ctx.sampleRate;
    const noiseBuffer = this.ctx.createBuffer(1, bufferSize, this.ctx.sampleRate);
    const output = noiseBuffer.getChannelData(0);
    let lastOut = 0.0;

    for (let i = 0; i < bufferSize; i++) {
      const white = Math.random() * 2 - 1;
      output[i] = (lastOut + (0.02 * white)) / 1.02;
      lastOut = output[i];
      output[i] *= 2.2;
    }

    const rain = this.ctx.createBufferSource();
    rain.buffer = noiseBuffer;
    rain.loop = true;

    const bandpass = this.ctx.createBiquadFilter();
    bandpass.type = 'bandpass';
    bandpass.frequency.setValueAtTime(950, this.ctx.currentTime);
    bandpass.Q.setValueAtTime(0.8, this.ctx.currentTime);

    const rainGain = this.ctx.createGain();
    rainGain.gain.setValueAtTime(0.65, this.ctx.currentTime);

    rain.connect(bandpass);
    bandpass.connect(rainGain);
    rainGain.connect(this.masterGain);

    rain.start();
    this.activeNodes.push(rain, bandpass, rainGain);
  }

  // --- Soundscape 3: Tibetan Singing Bowl (432 Hz Warm Resonance) ---
  startSingingBowlDrone() {
    const freqs = [432, 864, 1296, 2160];
    const gains = [0.35, 0.12, 0.06, 0.02];

    const bowlGroup = [];
    freqs.forEach((freq, idx) => {
      const osc = this.ctx.createOscillator();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(freq, this.ctx.currentTime);

      // Subtle frequency vibrato
      const vibrato = this.ctx.createOscillator();
      vibrato.frequency.setValueAtTime(0.2 + idx * 0.05, this.ctx.currentTime);
      const vGain = this.ctx.createGain();
      vGain.gain.setValueAtTime(1.2, this.ctx.currentTime);
      vibrato.connect(vGain);
      vGain.connect(osc.frequency);

      const gain = this.ctx.createGain();
      gain.gain.setValueAtTime(gains[idx], this.ctx.currentTime);

      osc.connect(gain);
      gain.connect(this.masterGain);

      osc.start();
      vibrato.start();
      bowlGroup.push(osc, vibrato, vGain, gain);
    });

    this.activeNodes.push(...bowlGroup);
  }

  // --- Soundscape 4: Forest Breeze ---
  startForestBreeze() {
    const bufferSize = 2 * this.ctx.sampleRate;
    const noiseBuffer = this.ctx.createBuffer(1, bufferSize, this.ctx.sampleRate);
    const output = noiseBuffer.getChannelData(0);
    for (let i = 0; i < bufferSize; i++) {
      output[i] = (Math.random() * 2 - 1) * 0.2;
    }

    const wind = this.ctx.createBufferSource();
    wind.buffer = noiseBuffer;
    wind.loop = true;

    const filter = this.ctx.createBiquadFilter();
    filter.type = 'lowpass';
    filter.frequency.setValueAtTime(260, this.ctx.currentTime);
    filter.Q.setValueAtTime(4.0, this.ctx.currentTime);

    const lfo = this.ctx.createOscillator();
    lfo.frequency.setValueAtTime(0.18, this.ctx.currentTime);
    const lfoGain = this.ctx.createGain();
    lfoGain.gain.setValueAtTime(220, this.ctx.currentTime);
    lfo.connect(lfoGain);
    lfoGain.connect(filter.frequency);

    const windGain = this.ctx.createGain();
    windGain.gain.setValueAtTime(0.5, this.ctx.currentTime);

    wind.connect(filter);
    filter.connect(windGain);
    windGain.connect(this.masterGain);

    wind.start();
    lfo.start();
    this.activeNodes.push(wind, filter, lfo, lfoGain, windGain);
  }

  // --- Soundscape 5: Earth Om Resonance (136.1 Hz Cosmic Octave) ---
  startOmResonance() {
    const freqs = [136.1, 272.2, 408.3];
    const gains = [0.4, 0.15, 0.08];

    const omGroup = [];
    freqs.forEach((f, i) => {
      const osc = this.ctx.createOscillator();
      osc.type = i === 0 ? 'triangle' : 'sine';
      osc.frequency.setValueAtTime(f, this.ctx.currentTime);

      const gain = this.ctx.createGain();
      gain.gain.setValueAtTime(gains[i], this.ctx.currentTime);

      osc.connect(gain);
      gain.connect(this.masterGain);
      osc.start();
      omGroup.push(osc, gain);
    });

    this.activeNodes.push(...omGroup);
  }

  // --- Bell Chime for Breath Transition / Mindful Minute ---
  ringChime(pitch = 528) {
    this.init();
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();

    osc.type = 'sine';
    osc.frequency.setValueAtTime(pitch, this.ctx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(pitch * 0.98, this.ctx.currentTime + 3.0);

    const t = this.ctx.currentTime;
    gain.gain.setValueAtTime(0.0001, t);
    gain.gain.exponentialRampToValueAtTime(0.4, t + 0.04);
    gain.gain.exponentialRampToValueAtTime(0.0001, t + 3.5);

    osc.connect(gain);
    gain.connect(this.masterGain);

    osc.start(t);
    osc.stop(t + 3.6);
  }

  // --- Soft Japa Bead Bell for Mantra Chant Counting ---
  ringChantBead(count = 1) {
    this.init();
    const t = this.ctx.currentTime;
    
    // Primary chime
    const pitch = count === 108 ? 864 : (count % 10 === 0 ? 648 : 528);
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();

    osc.type = 'sine';
    osc.frequency.setValueAtTime(pitch, t);
    
    // Organic bead tap harmonic
    const overtone = this.ctx.createOscillator();
    const overGain = this.ctx.createGain();
    overtone.type = 'sine';
    overtone.frequency.setValueAtTime(pitch * 2.02, t);

    gain.gain.setValueAtTime(0.0001, t);
    gain.gain.exponentialRampToValueAtTime(0.35, t + 0.02);
    gain.gain.exponentialRampToValueAtTime(0.0001, t + 1.8);

    overGain.gain.setValueAtTime(0.0001, t);
    overGain.gain.exponentialRampToValueAtTime(0.12, t + 0.01);
    overGain.gain.exponentialRampToValueAtTime(0.0001, t + 0.9);

    osc.connect(gain);
    overtone.connect(overGain);
    gain.connect(this.masterGain);
    overGain.connect(this.masterGain);

    osc.start(t);
    overtone.start(t);
    osc.stop(t + 1.9);
    overtone.stop(t + 1.0);
  }

  // =========================================================================
  // SACRED MANTRA VIBRATIONAL SOUND ENGINES
  // =========================================================================

  playMantra(mantraName) {
    this.init();
    const key = (mantraName || '').toLowerCase().trim();

    if (this.isPlaying && this.currentTrack === 'mantra_' + key) {
      this.stop();
      return false; // Stopped
    }

    this.stop();
    this.isPlaying = true;
    this.currentTrack = 'mantra_' + key;

    if (key.includes('asatoma') || key.includes('असतो मा')) {
      this.startAsatomaSacredPad();
    } else if (key.includes('mrityunjaya') || key.includes('महामृत्युंजय')) {
      this.startMrityunjayaHealingDrone();
    } else if (key.includes('gayatri') || key.includes('गायत्री')) {
      this.startGayatriSolarHarmonics();
    } else if (key.includes('mahamantra') || key.includes('महामंत्र') || key.includes('krishna') || key.includes('rama')) {
      this.startMahamantraDevotionalChimes();
    } else if (key.includes('brahmasmi') || key.includes('ब्रह्मास्मि')) {
      this.startBrahmasmiCosmicBowl();
    } else if (key.includes('tat tvam') || key.includes('तत् त्वम्') || key.includes('tat-tvam')) {
      this.startTatTvamAsiUnityChimes();
    } else if (key.includes('so hum') || key.includes('so-hum') || key.includes('सो ऽहम्') || key.includes('सो हम्')) {
      this.startSoHumBreathSound();
    } else if (key.includes('om') || key.includes('ॐ') || key.includes('aum')) {
      this.startOmResonance();
    } else {
      // Default to classical sacred Tanpura ambiance
      this.startTanpuraDrone();
    }

    return true; // Playing
  }

  // --- Classical Indian Sacred Tanpura Drone ---
  startTanpuraDrone() {
    // Fundamental C#3 (138.6 Hz), Pa (G#3 207.65 Hz), Sa' (C#4 277.2 Hz)
    const strings = [
      { f: 207.65, gain: 0.18, type: 'sawtooth', filterFreq: 600 },
      { f: 277.18, gain: 0.22, type: 'sawtooth', filterFreq: 750 },
      { f: 277.60, gain: 0.20, type: 'sawtooth', filterFreq: 760 }, // Shimmer detune
      { f: 138.59, gain: 0.35, type: 'triangle', filterFreq: 380 },
    ];

    const group = [];
    strings.forEach((s, i) => {
      const osc = this.ctx.createOscillator();
      osc.type = s.type;
      osc.frequency.setValueAtTime(s.f, this.ctx.currentTime);

      // Warm acoustic filter simulating wooden gourd body
      const filter = this.ctx.createBiquadFilter();
      filter.type = 'lowpass';
      filter.frequency.setValueAtTime(s.filterFreq, this.ctx.currentTime);
      filter.Q.setValueAtTime(2.0, this.ctx.currentTime);

      // Slow cyclical pluck swell (strum effect)
      const lfo = this.ctx.createOscillator();
      lfo.frequency.setValueAtTime(0.25, this.ctx.currentTime); // ~4 second strum cycle
      const lfoGain = this.ctx.createGain();
      lfoGain.gain.setValueAtTime(s.gain * 0.4, this.ctx.currentTime);

      const gain = this.ctx.createGain();
      gain.gain.setValueAtTime(s.gain * 0.7, this.ctx.currentTime);

      lfo.connect(lfoGain);
      lfoGain.connect(gain.gain);

      osc.connect(filter);
      filter.connect(gain);
      gain.connect(this.masterGain);

      osc.start();
      lfo.start();
      group.push(osc, filter, lfo, lfoGain, gain);
    });

    this.activeNodes.push(...group);
  }

  // --- So Hum: The Inhale-Exhale Breath Wave ---
  startSoHumBreathSound() {
    // 432 Hz "So" (inhale) and 384 Hz "Hum" (exhale) gentle oscillation
    const osc1 = this.ctx.createOscillator();
    const osc2 = this.ctx.createOscillator();
    osc1.type = 'sine';
    osc2.type = 'sine';
    osc1.frequency.setValueAtTime(432, this.ctx.currentTime);
    osc2.frequency.setValueAtTime(384, this.ctx.currentTime);

    // Filtered pink breath noise
    const bufferSize = 2 * this.ctx.sampleRate;
    const noiseBuffer = this.ctx.createBuffer(1, bufferSize, this.ctx.sampleRate);
    const output = noiseBuffer.getChannelData(0);
    for (let i = 0; i < bufferSize; i++) {
      output[i] = (Math.random() * 2 - 1) * 0.15;
    }
    const noise = this.ctx.createBufferSource();
    noise.buffer = noiseBuffer;
    noise.loop = true;

    const noiseFilter = this.ctx.createBiquadFilter();
    noiseFilter.type = 'bandpass';
    noiseFilter.frequency.setValueAtTime(450, this.ctx.currentTime);
    noiseFilter.Q.setValueAtTime(3.0, this.ctx.currentTime);

    const lfo = this.ctx.createOscillator();
    lfo.frequency.setValueAtTime(0.125, this.ctx.currentTime); // 8-second gentle breath cycle

    const gain1 = this.ctx.createGain();
    const gain2 = this.ctx.createGain();
    const noiseGain = this.ctx.createGain();

    gain1.gain.setValueAtTime(0.2, this.ctx.currentTime);
    gain2.gain.setValueAtTime(0.2, this.ctx.currentTime);
    noiseGain.gain.setValueAtTime(0.25, this.ctx.currentTime);

    osc1.connect(gain1);
    osc2.connect(gain2);
    noise.connect(noiseFilter);
    noiseFilter.connect(noiseGain);

    gain1.connect(this.masterGain);
    gain2.connect(this.masterGain);
    noiseGain.connect(this.masterGain);

    osc1.start();
    osc2.start();
    noise.start();
    lfo.start();

    this.activeNodes.push(osc1, osc2, noise, noiseFilter, lfo, gain1, gain2, noiseGain);
  }

  // --- Gayatri Mantra: Solar 528 Hz Dawn Harmonics ---
  startGayatriSolarHarmonics() {
    // 528 Hz (solar DNA transformation) + 264 Hz octave + 396 Hz root
    const freqs = [264, 396, 528, 792];
    const gains = [0.3, 0.2, 0.25, 0.08];
    const group = [];

    freqs.forEach((f, i) => {
      const osc = this.ctx.createOscillator();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(f, this.ctx.currentTime);

      const gain = this.ctx.createGain();
      gain.gain.setValueAtTime(gains[i], this.ctx.currentTime);

      // Gentle tremolo
      const trem = this.ctx.createOscillator();
      trem.frequency.setValueAtTime(0.3, this.ctx.currentTime);
      const tremGain = this.ctx.createGain();
      tremGain.gain.setValueAtTime(gains[i] * 0.2, this.ctx.currentTime);

      trem.connect(tremGain);
      tremGain.connect(gain.gain);

      osc.connect(gain);
      gain.connect(this.masterGain);

      osc.start();
      trem.start();
      group.push(osc, gain, trem, tremGain);
    });

    this.activeNodes.push(...group);
  }

  // --- Mahamantra: Uplifting Devotional Chimes & Rhythm ---
  startMahamantraDevotionalChimes() {
    // Joyful melodic bells & singing drone
    const freqs = [330, 440, 550, 660];
    const group = [];

    freqs.forEach((f, i) => {
      const osc = this.ctx.createOscillator();
      osc.type = 'triangle';
      osc.frequency.setValueAtTime(f, this.ctx.currentTime);

      const filter = this.ctx.createBiquadFilter();
      filter.type = 'lowpass';
      filter.frequency.setValueAtTime(800 + i * 200, this.ctx.currentTime);

      const gain = this.ctx.createGain();
      gain.gain.setValueAtTime(0.12, this.ctx.currentTime);

      osc.connect(filter);
      filter.connect(gain);
      gain.connect(this.masterGain);

      osc.start();
      group.push(osc, filter, gain);
    });

    this.activeNodes.push(...group);
  }

  // --- Maha Mrityunjaya: Restorative Deep Healing Drone ---
  startMrityunjayaHealingDrone() {
    const freqs = [174, 285, 528]; // Solfeggio healing frequencies
    const group = [];

    freqs.forEach((f, i) => {
      const osc = this.ctx.createOscillator();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(f, this.ctx.currentTime);

      const gain = this.ctx.createGain();
      gain.gain.setValueAtTime(0.28 / (i + 1), this.ctx.currentTime);

      osc.connect(gain);
      gain.connect(this.masterGain);
      osc.start();
      group.push(osc, gain);
    });

    this.activeNodes.push(...group);
  }

  // --- Aham Brahmasmi: Infinite Consciousness Crystal Bowl ---
  startBrahmasmiCosmicBowl() {
    const freqs = [432, 864, 1296];
    const group = [];

    freqs.forEach((f, i) => {
      const osc = this.ctx.createOscillator();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(f, this.ctx.currentTime);

      // Binaural wave at 8 Hz (Alpha wave for awakening)
      const binaural = this.ctx.createOscillator();
      binaural.type = 'sine';
      binaural.frequency.setValueAtTime(f + 8, this.ctx.currentTime);

      const gain = this.ctx.createGain();
      gain.gain.setValueAtTime(0.18 / (i + 1), this.ctx.currentTime);

      osc.connect(gain);
      binaural.connect(gain);
      gain.connect(this.masterGain);

      osc.start();
      binaural.start();
      group.push(osc, binaural, gain);
    });

    this.activeNodes.push(...group);
  }

  // --- Tat Tvam Asi: Unity Fifth Harmonics ---
  startTatTvamAsiUnityChimes() {
    const freqs = [261.63, 392.00, 523.25]; // C4, G4 (perfect 5th), C5
    const group = [];

    freqs.forEach((f, i) => {
      const osc = this.ctx.createOscillator();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(f, this.ctx.currentTime);

      const gain = this.ctx.createGain();
      gain.gain.setValueAtTime(0.22 / (i + 1), this.ctx.currentTime);

      osc.connect(gain);
      gain.connect(this.masterGain);
      osc.start();
      group.push(osc, gain);
    });

    this.activeNodes.push(...group);
  }

  // --- Asatoma Sadgamaya: Sacred Ascending Light Pad ---
  startAsatomaSacredPad() {
    const freqs = [220, 277.18, 329.63, 440]; // A Major serene chord
    const group = [];

    freqs.forEach((f, i) => {
      const osc = this.ctx.createOscillator();
      osc.type = 'triangle';
      osc.frequency.setValueAtTime(f, this.ctx.currentTime);

      const filter = this.ctx.createBiquadFilter();
      filter.type = 'lowpass';
      filter.frequency.setValueAtTime(650, this.ctx.currentTime);

      const gain = this.ctx.createGain();
      gain.gain.setValueAtTime(0.15, this.ctx.currentTime);

      osc.connect(filter);
      filter.connect(gain);
      gain.connect(this.masterGain);

      osc.start();
      group.push(osc, filter, gain);
    });

    this.activeNodes.push(...group);
  }
}

// Global instance
window.calmAudio = new CalmAudioEngine();

