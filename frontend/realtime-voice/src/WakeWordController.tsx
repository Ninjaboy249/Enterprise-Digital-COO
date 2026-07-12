import { useEffect, useRef } from 'react';

type RecognitionResultEvent = Event & { resultIndex: number; results: SpeechRecognitionResultList };
type RecognitionErrorEvent = Event & { error: string };
type BrowserSpeechRecognition = EventTarget & {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  onresult: ((event: RecognitionResultEvent) => void) | null;
  onerror: ((event: RecognitionErrorEvent) => void) | null;
  onend: (() => void) | null;
  start: () => void;
  stop: () => void;
  abort: () => void;
};

type RecognitionConstructor = new () => BrowserSpeechRecognition;

declare global {
  interface Window {
    SpeechRecognition?: RecognitionConstructor;
    webkitSpeechRecognition?: RecognitionConstructor;
  }
}

const WAKE_PHRASE = 'hey enterprise digital coo';

function normalize(value: string) {
  return value.toLowerCase().replace(/[^a-z0-9 ]/g, ' ').replace(/\s+/g, ' ').trim();
}

function playWakeSound() {
  const context = new AudioContext();
  const oscillator = context.createOscillator();
  const gain = context.createGain();
  oscillator.type = 'sine';
  oscillator.frequency.setValueAtTime(620, context.currentTime);
  oscillator.frequency.exponentialRampToValueAtTime(920, context.currentTime + .18);
  gain.gain.setValueAtTime(.0001, context.currentTime);
  gain.gain.exponentialRampToValueAtTime(.07, context.currentTime + .025);
  gain.gain.exponentialRampToValueAtTime(.0001, context.currentTime + .24);
  oscillator.connect(gain).connect(context.destination);
  oscillator.start(); oscillator.stop(context.currentTime + .25);
  oscillator.onended = () => context.close().catch(() => undefined);
}

async function askCOO(command: string): Promise<string> {
  const response = await fetch('/api/v1/metrics/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: command, context: 'general' }),
  });
  if (!response.ok) throw new Error('AI request failed');
  const result = await response.json() as { answer?: string };
  return result.answer || 'I could not find an answer for that.';
}

export default function WakeWordController() {
  const recognition = useRef<BrowserSpeechRecognition | null>(null);
  const mode = useRef<'wake' | 'command' | 'processing' | 'speaking'>('wake');
  const commandTimer = useRef<number | null>(null);
  const mounted = useRef(true);
  const shouldRestart = useRef(true);

  useEffect(() => {
    mounted.current = true;
    const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!Recognition) {
      console.warn('Wake word mode requires a browser with Web Speech API support.');
      return;
    }

    const engine = new Recognition();
    recognition.current = engine;
    engine.continuous = true;
    engine.interimResults = false;
    engine.lang = document.documentElement.lang || navigator.language || 'en-US';

    const clearCommandTimer = () => {
      if (commandTimer.current !== null) clearTimeout(commandTimer.current);
      commandTimer.current = null;
    };
    const returnToWakeMode = () => {
      clearCommandTimer();
      mode.current = 'wake';
      shouldRestart.current = true;
      document.body.classList.remove('coo-wake-active', 'coo-wake-thinking');
      try { engine.start(); } catch { /* already running */ }
    };
    const waitForCommand = () => {
      mode.current = 'command';
      document.body.classList.add('coo-wake-active');
      playWakeSound();
      clearCommandTimer();
      commandTimer.current = window.setTimeout(returnToWakeMode, 10000);
    };
    const speak = (text: string) => {
      mode.current = 'speaking';
      document.body.classList.remove('coo-wake-thinking');
      document.body.classList.add('coo-wake-speaking');
      speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 1; utterance.pitch = 1; utterance.volume = 1;
      const voices = speechSynthesis.getVoices();
      utterance.voice = voices.find(voice => /en/i.test(voice.lang) && /natural|aria|samantha|google/i.test(voice.name)) || voices.find(voice => /en/i.test(voice.lang)) || null;
      utterance.onend = utterance.onerror = () => {
        document.body.classList.remove('coo-wake-speaking');
        if (mounted.current) returnToWakeMode();
      };
      speechSynthesis.speak(utterance);
    };
    const handleCommand = async (command: string) => {
      clearCommandTimer();
      mode.current = 'processing'; shouldRestart.current = false;
      document.body.classList.remove('coo-wake-active');
      document.body.classList.add('coo-wake-thinking');
      try { engine.stop(); } catch { /* already stopped */ }
      try { speak(await askCOO(command)); }
      catch { speak('Sorry, I could not reach the AI service. Please try again.'); }
    };

    engine.onresult = event => {
      for (let index = event.resultIndex; index < event.results.length; index += 1) {
        if (!event.results[index].isFinal) continue;
        const transcript = event.results[index][0].transcript.trim();
        if (!transcript) continue;
        if (mode.current === 'wake') {
          if (normalize(transcript).includes(WAKE_PHRASE)) waitForCommand();
        } else if (mode.current === 'command') {
          void handleCommand(transcript);
          break;
        }
      }
    };
    engine.onerror = event => {
      if (event.error === 'not-allowed' || event.error === 'service-not-allowed') shouldRestart.current = false;
    };
    engine.onend = () => {
      if (!mounted.current || !shouldRestart.current || mode.current === 'processing' || mode.current === 'speaking') return;
      window.setTimeout(() => { try { engine.start(); } catch { /* restart race */ } }, 250);
    };

    navigator.mediaDevices.getUserMedia({ audio: true }).then(stream => {
      stream.getTracks().forEach(track => track.stop());
      if (mounted.current) engine.start();
    }).catch(() => { shouldRestart.current = false; });

    return () => {
      mounted.current = false; shouldRestart.current = false; clearCommandTimer();
      speechSynthesis.cancel(); document.body.classList.remove('coo-wake-active', 'coo-wake-thinking', 'coo-wake-speaking');
      engine.onend = null; engine.abort(); recognition.current = null;
    };
  }, []);

  return null;
}
