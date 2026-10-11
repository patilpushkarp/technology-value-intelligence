/**
 * VEDANAM Ambient Harmonic Synthesizer
 * Built using native Web Audio API (zero external audio libraries)
 * Provides an unconventional sensory realization layer for enterprise value intelligence.
 * The harmonic frequencies modulate based on system tension, blast radius, and debt.
 */

let audioCtx: AudioContext | null = null
let masterGain: GainNode | null = null
let lowPassFilter: BiquadFilterNode | null = null
let oscRoot: OscillatorNode | null = null
let oscFifth: OscillatorNode | null = null
let oscOctave: OscillatorNode | null = null
let isPlayingState = false

export const useAudioSynth = () => {
  const isAudioActive = useState<boolean>('vedanam_audio_active', () => false)
  const tension = useState<number>('vedanam_audio_tension', () => 0)

  const initAudio = () => {
    if (!process.client || audioCtx) return

    try {
      const AudioContextClass = window.AudioContext || (window as any).webkitAudioContext
      audioCtx = new AudioContextClass()

      // Master Gain
      masterGain = audioCtx.createGain()
      masterGain.gain.setValueAtTime(0, audioCtx.currentTime)

      // Warm analog Low-Pass Filter
      lowPassFilter = audioCtx.createBiquadFilter()
      lowPassFilter.type = 'lowpass'
      lowPassFilter.frequency.setValueAtTime(380, audioCtx.currentTime)
      lowPassFilter.Q.setValueAtTime(1.5, audioCtx.currentTime)

      // Harmonic Foundation: 108 Hz (A2 harmonic fundamental - 432 Hz / 4)
      oscRoot = audioCtx.createOscillator()
      oscRoot.type = 'sine'
      oscRoot.frequency.setValueAtTime(108, audioCtx.currentTime)

      // Fifth: 162 Hz (Perfect 5th)
      oscFifth = audioCtx.createOscillator()
      oscFifth.type = 'triangle'
      oscFifth.frequency.setValueAtTime(162, audioCtx.currentTime)

      // Octave shimmer: 216 Hz
      oscOctave = audioCtx.createOscillator()
      oscOctave.type = 'sine'
      oscOctave.frequency.setValueAtTime(216, audioCtx.currentTime)

      // Sub gain mixes
      const gainFifth = audioCtx.createGain()
      gainFifth.gain.value = 0.35
      const gainOctave = audioCtx.createGain()
      gainOctave.gain.value = 0.2

      oscRoot.connect(lowPassFilter)
      oscFifth.connect(gainFifth).connect(lowPassFilter)
      oscOctave.connect(gainOctave).connect(lowPassFilter)

      lowPassFilter.connect(masterGain)
      masterGain.connect(audioCtx.destination)

      oscRoot.start()
      oscFifth.start()
      oscOctave.start()
      isPlayingState = true
    } catch (e) {
      console.warn('Web Audio initialization error:', e)
    }
  }

  const toggleSound = () => {
    if (!process.client) return
    initAudio()

    if (!audioCtx || !masterGain) return

    if (audioCtx.state === 'suspended') {
      audioCtx.resume()
    }

    if (!isAudioActive.value) {
      // Fade in smoothly
      masterGain.gain.cancelScheduledValues(audioCtx.currentTime)
      masterGain.gain.setValueAtTime(masterGain.gain.value, audioCtx.currentTime)
      masterGain.gain.linearRampToValueAtTime(0.12, audioCtx.currentTime + 1.2)
      isAudioActive.value = true
    } else {
      // Fade out smoothly
      masterGain.gain.cancelScheduledValues(audioCtx.currentTime)
      masterGain.gain.setValueAtTime(masterGain.gain.value, audioCtx.currentTime)
      masterGain.gain.linearRampToValueAtTime(0.0001, audioCtx.currentTime + 0.8)
      isAudioActive.value = false
    }
  }

  const setTensionLevel = (level: number) => {
    if (!process.client || !audioCtx || !lowPassFilter || !oscFifth) return
    tension.value = level

    const targetFreq = 380 + level * 520
    lowPassFilter.frequency.cancelScheduledValues(audioCtx.currentTime)
    lowPassFilter.frequency.setTargetAtTime(targetFreq, audioCtx.currentTime, 0.4)

    // Detune the fifth slightly under high tension to simulate architectural stress
    const detuneAmount = level * 35
    oscFifth.detune.cancelScheduledValues(audioCtx.currentTime)
    oscFifth.detune.setTargetAtTime(detuneAmount, audioCtx.currentTime, 0.4)
  }

  const playInteractChime = (pitchMultiplier = 1) => {
    if (!process.client || !isAudioActive.value || !audioCtx) return

    try {
      const chimeOsc = audioCtx.createOscillator()
      const chimeGain = audioCtx.createGain()
      const filter = audioCtx.createBiquadFilter()

      chimeOsc.type = 'sine'
      chimeOsc.frequency.setValueAtTime(432 * pitchMultiplier, audioCtx.currentTime)

      filter.type = 'bandpass'
      filter.frequency.setValueAtTime(864, audioCtx.currentTime)
      filter.Q.setValueAtTime(3, audioCtx.currentTime)

      chimeGain.gain.setValueAtTime(0.04, audioCtx.currentTime)
      chimeGain.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + 0.6)

      chimeOsc.connect(filter)
      filter.connect(chimeGain)
      chimeGain.connect(audioCtx.destination)

      chimeOsc.start()
      chimeOsc.stop(audioCtx.currentTime + 0.65)
    } catch {
      // Ignore audio glitches
    }
  }

  return {
    isAudioActive,
    tension,
    toggleSound,
    setTensionLevel,
    playInteractChime
  }
}
