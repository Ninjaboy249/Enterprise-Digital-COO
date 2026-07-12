import React, { lazy, Suspense, useCallback, useEffect, useRef, useState } from 'react';
import { createRoot } from 'react-dom/client';
import './voice.css';
import EmailAgentModal, { type EmailDraft } from './EmailAgentModal';

type Role = 'user' | 'assistant';
type Message = { id: string; role: Role; text: string; createdAt: number };
type VoiceStatus = 'idle' | 'connecting' | 'listening' | 'thinking' | 'speaking' | 'error';
type RealtimeEvent = Record<string, any> & { type: string };

declare global {
  interface Window {
    COORealtimeVoice?: { open: () => void; close: () => void };
    COOEmailAgent?: { open: (draft: EmailDraft) => void; close: () => void };
  }
}

const HISTORY_KEY = 'coo-realtime-voice-history';
const WakeWordController = lazy(() => import('./WakeWordController'));

function isMainDashboard() {
  const path = location.pathname.replace(/\/+$/, '');
  return path === '' || path === '/' || path === '/static' || path.endsWith('/index.html');
}

function loadHistory(): Message[] {
  try { return JSON.parse(localStorage.getItem(HISTORY_KEY) || '[]').slice(-40); }
  catch { return []; }
}

function Waveform({ analyser, active }: { analyser: AnalyserNode | null; active: boolean }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  useEffect(() => {
    let frame = 0;
    const draw = () => {
      const canvas = canvasRef.current;
      if (!canvas) return;
      const ctx = canvas.getContext('2d');
      if (!ctx) return;
      const width = canvas.width = canvas.clientWidth * devicePixelRatio;
      const height = canvas.height = canvas.clientHeight * devicePixelRatio;
      ctx.clearRect(0, 0, width, height);
      const values = new Uint8Array(analyser?.frequencyBinCount || 64);
      if (analyser && active) analyser.getByteFrequencyData(values);
      const bars = 32;
      const gap = 4 * devicePixelRatio;
      const barWidth = (width - gap * (bars - 1)) / bars;
      for (let i = 0; i < bars; i += 1) {
        const value = analyser && active ? values[Math.floor(i * values.length / bars)] / 255 : .08 + Math.sin(Date.now() / 500 + i) * .025;
        const barHeight = Math.max(4 * devicePixelRatio, value * height * .9);
        const gradient = ctx.createLinearGradient(0, height, 0, 0);
        gradient.addColorStop(0, '#7c3aed'); gradient.addColorStop(1, '#22d3ee');
        ctx.fillStyle = gradient;
        ctx.beginPath();
        ctx.roundRect(i * (barWidth + gap), (height - barHeight) / 2, barWidth, barHeight, barWidth / 2);
        ctx.fill();
      }
      frame = requestAnimationFrame(draw);
    };
    draw();
    return () => cancelAnimationFrame(frame);
  }, [analyser, active]);
  return <canvas ref={canvasRef} className="rt-waveform" aria-hidden="true" />;
}

function VoiceConversation() {
  const [open, setOpen] = useState(false);
  const [status, setStatus] = useState<VoiceStatus>('idle');
  const [history, setHistory] = useState<Message[]>(loadHistory);
  const [liveUser, setLiveUser] = useState('');
  const [liveAssistant, setLiveAssistant] = useState('');
  const [error, setError] = useState('');
  const [analyser, setAnalyser] = useState<AnalyserNode | null>(null);
  const pcRef = useRef<RTCPeerConnection | null>(null);
  const dcRef = useRef<RTCDataChannel | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const assistantDraft = useRef('');
  const scrollRef = useRef<HTMLDivElement>(null);
  const conversationEndTimer = useRef<number | null>(null);

  useEffect(() => { localStorage.setItem(HISTORY_KEY, JSON.stringify(history.slice(-40))); }, [history]);
  useEffect(() => { scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' }); }, [history, liveUser, liveAssistant]);

  const addMessage = useCallback((role: Role, text: string, id?: string) => {
    const clean = text.trim(); if (!clean) return;
    setHistory(prev => {
      const key = id || crypto.randomUUID();
      if (prev.some(item => item.id === key)) return prev;
      return [...prev, { id: key, role, text: clean, createdAt: Date.now() }].slice(-40);
    });
  }, []);

  const handleEvent = useCallback((event: RealtimeEvent) => {
    if (conversationEndTimer.current) { clearTimeout(conversationEndTimer.current); conversationEndTimer.current = null; }
    switch (event.type) {
      case 'input_audio_buffer.speech_started':
        if (audioRef.current) audioRef.current.muted = true;
        setStatus('listening'); setLiveUser('Listening…');
        break;
      case 'input_audio_buffer.speech_stopped':
        setStatus('thinking'); setLiveUser('Transcribing…');
        break;
      case 'conversation.item.input_audio_transcription.delta':
        setLiveUser(prev => prev === 'Listening…' || prev === 'Transcribing…' ? (event.delta || '') : prev + (event.delta || ''));
        break;
      case 'conversation.item.input_audio_transcription.completed':
        addMessage('user', event.transcript || '', event.item_id); setLiveUser('');
        break;
      case 'response.output_audio_transcript.delta':
      case 'response.audio_transcript.delta':
        if (audioRef.current) audioRef.current.muted = false;
        assistantDraft.current += event.delta || '';
        setLiveAssistant(assistantDraft.current); setStatus('speaking');
        break;
      case 'response.output_audio_transcript.done':
      case 'response.audio_transcript.done':
        if (event.transcript) assistantDraft.current = event.transcript;
        break;
      case 'response.done':
        addMessage('assistant', assistantDraft.current, event.response?.id);
        assistantDraft.current = ''; setLiveAssistant(''); setStatus('listening');
        conversationEndTimer.current = window.setTimeout(() => {
          disconnectRef.current();
          setOpen(false);
          document.body.classList.remove('coo-wake-active');
          window.dispatchEvent(new Event('coo-realtime-ended'));
        }, 10000);
        break;
      case 'error':
        setError(event.error?.message || 'Realtime connection error'); setStatus('error');
        break;
    }
  }, [addMessage]);

  const disconnectRef = useRef<() => void>(() => undefined);

  const disconnect = useCallback(() => {
    if (conversationEndTimer.current) { clearTimeout(conversationEndTimer.current); conversationEndTimer.current = null; }
    dcRef.current?.close(); pcRef.current?.close();
    streamRef.current?.getTracks().forEach(track => track.stop());
    audioContextRef.current?.close().catch(() => undefined);
    if (audioRef.current) audioRef.current.srcObject = null;
    dcRef.current = null; pcRef.current = null; streamRef.current = null;
    audioContextRef.current = null; setAnalyser(null); setStatus('idle');
    setLiveUser(''); setLiveAssistant(''); assistantDraft.current = '';
  }, []);
  disconnectRef.current = disconnect;

  const connect = useCallback(async () => {
    if (pcRef.current) return;
    setError(''); setStatus('connecting');
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: { echoCancellation: true, noiseSuppression: true, autoGainControl: true } });
      streamRef.current = stream;
      const audioContext = new AudioContext();
      const source = audioContext.createMediaStreamSource(stream);
      const nextAnalyser = audioContext.createAnalyser(); nextAnalyser.fftSize = 128; nextAnalyser.smoothingTimeConstant = .82;
      source.connect(nextAnalyser); audioContextRef.current = audioContext; setAnalyser(nextAnalyser);

      const pc = new RTCPeerConnection(); pcRef.current = pc;
      stream.getTracks().forEach(track => pc.addTrack(track, stream));
      pc.ontrack = event => {
        if (!audioRef.current) return;
        audioRef.current.srcObject = event.streams[0];
        audioRef.current.play().catch(() => undefined);
      };
      pc.onconnectionstatechange = () => {
        if (pc.connectionState === 'connected') setStatus('listening');
        if (['failed', 'disconnected'].includes(pc.connectionState)) { setError('Voice connection was lost.'); setStatus('error'); }
      };
      const dc = pc.createDataChannel('oai-events'); dcRef.current = dc;
      dc.onmessage = message => { try { handleEvent(JSON.parse(message.data)); } catch { /* ignore non-JSON */ } };
      const offer = await pc.createOffer(); await pc.setLocalDescription(offer);
      const response = await fetch('/api/v1/realtime/call', { method: 'POST', headers: { 'Content-Type': 'application/sdp' }, body: offer.sdp });
      if (!response.ok) { const body = await response.text(); throw new Error(body.includes('OPENAI_API_KEY') ? 'OpenAI API key is not configured on the server.' : 'Could not start the voice session.'); }
      await pc.setRemoteDescription({ type: 'answer', sdp: await response.text() });
    } catch (reason) {
      disconnect(); setError(reason instanceof Error ? reason.message : 'Microphone access failed.'); setStatus('error');
    }
  }, [disconnect, handleEvent]);

  const interrupt = () => {
    if (dcRef.current?.readyState === 'open') dcRef.current.send(JSON.stringify({ type: 'response.cancel' }));
    if (audioRef.current) audioRef.current.muted = true;
    assistantDraft.current = ''; setLiveAssistant(''); setStatus('listening');
  };

  useEffect(() => {
    window.COORealtimeVoice = { open: () => setOpen(true), close: () => setOpen(false) };
    return () => { delete window.COORealtimeVoice; disconnect(); };
  }, [disconnect]);
  useEffect(() => { if (open && status === 'idle') connect(); }, [open, status, connect]);

  if (!open) return null;
  const active = ['listening', 'thinking', 'speaking'].includes(status);
  const label = ({ idle:'Ready', connecting:"I'm listening...", listening:'Listening', thinking:'Thinking…', speaking:'COO Bot is speaking', error:'Connection issue' } as const)[status];

  return <div className="rt-overlay" role="dialog" aria-modal="true" aria-label="COO Bot voice conversation">
    <section className="rt-panel">
      <header className="rt-header">
        <div><span className="rt-live-dot" /> <strong>COO Bot Voice</strong><small>OpenAI Realtime · WebRTC</small></div>
        <button className="rt-close" onClick={() => { disconnect(); setOpen(false); document.body.classList.remove('coo-wake-active'); window.dispatchEvent(new Event('coo-realtime-ended')); }} aria-label="Close voice conversation">×</button>
      </header>
      <div className="rt-stage">
        <div className={`rt-orb rt-${status}`}><span>COO</span></div>
        <p className="rt-status" role="status">{label}</p>
        <Waveform analyser={analyser} active={active} />
        <p className="rt-hint">Speak naturally. Pause when finished — you can interrupt at any time.</p>
      </div>
      <div className="rt-transcript" ref={scrollRef} aria-live="polite">
        {history.length === 0 && <p className="rt-empty">Your live conversation transcript will appear here.</p>}
        {history.map(item => <div key={item.id} className={`rt-message rt-${item.role}`}><b>{item.role === 'user' ? 'You' : 'COO Bot'}</b><span>{item.text}</span></div>)}
        {liveUser && <div className="rt-message rt-user rt-live"><b>You</b><span>{liveUser}</span></div>}
        {liveAssistant && <div className="rt-message rt-assistant rt-live"><b>COO Bot</b><span>{liveAssistant}<i className="rt-caret" /></span></div>}
      </div>
      {error && <p className="rt-error" role="alert">{error}</p>}
      <footer className="rt-controls">
        {status === 'speaking' ?
          <button className="rt-main-button rt-interrupt" onClick={interrupt}><span>■</span> Interrupt</button> :
          status === 'error' || status === 'idle' ? <button className="rt-main-button" onClick={connect}>🎙 Start voice</button> :
          <button className="rt-main-button rt-listening" onClick={disconnect}><span className="rt-mini-wave">|||</span> End conversation</button>}
        <button className="rt-clear" onClick={() => setHistory([])} disabled={!history.length}>Clear transcript</button>
      </footer>
      <audio ref={audioRef} autoPlay />
    </section>
  </div>;
}

const root = document.createElement('div'); root.id = 'coo-realtime-voice-root'; document.body.appendChild(root);
createRoot(root).render(<><Suspense fallback={null}>{isMainDashboard() && <WakeWordController />}</Suspense><VoiceConversation />{isMainDashboard() && <EmailAgentModal />}</>);
