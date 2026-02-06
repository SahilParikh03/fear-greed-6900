/**
 * Sound utilities for volatility alerts.
 * Apple-style tech-sleek notification sounds generated using Web Audio API.
 */

// Check if user has interacted with the page (required for autoplay)
let audioContextUnlocked = false;

export function unlockAudioContext() {
  audioContextUnlocked = true;
}

/**
 * Play a tech-sleek notification sound using Web Audio API.
 * Different sounds for different asset types.
 *
 * @param asset - Asset symbol ("BTC", "ETH", "SOL")
 */
export function playAlertSound(asset: "BTC" | "ETH" | "SOL" = "BTC") {
  if (!audioContextUnlocked) {
    console.log("Audio context not unlocked yet. Waiting for user interaction.");
    return;
  }

  try {
    const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();

    // Create oscillator for the base tone
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();

    // Connect nodes
    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);

    // Asset-specific frequencies (musical notes)
    const frequencies = {
      BTC: [800, 1000],   // High-pitched, urgent
      ETH: [600, 750],    // Medium-pitched, blue tone
      SOL: [500, 650],    // Lower-pitched, purple tone
    };

    const [freq1, freq2] = frequencies[asset] || frequencies.BTC;

    // Set oscillator type (sine wave for smooth, Apple-style sound)
    oscillator.type = "sine";
    oscillator.frequency.setValueAtTime(freq1, audioContext.currentTime);

    // Fade in/out envelope for smooth sound
    gainNode.gain.setValueAtTime(0, audioContext.currentTime);
    gainNode.gain.linearRampToValueAtTime(0.3, audioContext.currentTime + 0.01); // Quick attack
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.3); // Decay

    // Add a second note for a "ping" effect
    oscillator.frequency.exponentialRampToValueAtTime(freq2, audioContext.currentTime + 0.1);

    // Start and stop
    oscillator.start(audioContext.currentTime);
    oscillator.stop(audioContext.currentTime + 0.3);

    // Clean up
    oscillator.onended = () => {
      audioContext.close();
    };
  } catch (error) {
    console.error("Error playing sound:", error);
  }
}

/**
 * Play a double-tap notification (for critical alerts).
 */
export function playDoubleAlertSound(asset: "BTC" | "ETH" | "SOL" = "BTC") {
  playAlertSound(asset);
  setTimeout(() => playAlertSound(asset), 150);
}
