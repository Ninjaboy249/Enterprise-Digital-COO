(function () {
  const READY_DELAY_MS = 5000;
  const STORY_MESSAGE = "Hi, I'm COO Bot. Share your question and I'll turn the numbers into a clear business story with the next best move.";
  const SILENCE_TO_SEND_MS = 2500;
  let activeVoice = null;
  let pendingVoiceReply = false;
  let replyAudio = null;

  function voiceSubmit(input) {
    if (input.id === 'hero-ask-input' && typeof window.heroAsk === 'function') return window.heroAsk();
    if (input.id === 'ai-import-prompt' && typeof window.submitAIImport === 'function') return window.submitAIImport();
    if (input.id === 'chat-input' && typeof window.sendChat === 'function') return window.sendChat();
    input.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true }));
  }

  function setVoiceState(control, state, message) {
    control.wrap.classList.toggle('is-listening', state === 'listening');
    control.wrap.classList.toggle('is-processing', state === 'processing');
    control.button.setAttribute('aria-pressed', String(state === 'listening'));
    control.button.setAttribute('aria-label', state === 'listening' ? 'Stop listening' : 'Speak your question');
    control.status.textContent = message || '';
  }

  function stopVoice(control, shouldSubmit) {
    if (!control) return;
    clearTimeout(control.silenceTimer);
    control.shouldSubmit = shouldSubmit;
    control.manualStop = true;
    if (control.recorder?.state === 'recording') control.recorder.stop();
  }

  function submitVoiceTurn(control) {
    if (!control.heardSpeech || !control.input.value.trim()) return;
    clearTimeout(control.silenceTimer);
    control.shouldSubmit = false;
    control.heardSpeech = false;
    control.finalText = '';
    setVoiceState(control, 'listening', '');
    pendingVoiceReply = true;
    voiceSubmit(control.input);
    control.input.value = '';
    control.input.dispatchEvent(new Event('input', { bubbles: true }));
    control.originalText = '';
  }

  function resumeAfterSpeech(control) {
    if (!control || !control.recognition) return;
    control.pausedForSpeech = false;
    control.keepListening = true;
    window.setTimeout(() => {
      try { control.recognition.start(); } catch (_) {}
    }, 300);
  }

  async function speakOpenAIReply(text) {
    const clean = String(text || '').trim();
    if (!clean || !pendingVoiceReply) return;
    pendingVoiceReply = false;
    const control = activeVoice;
    if (control?.recognition) {
      clearTimeout(control.silenceTimer);
      control.pausedForSpeech = true;
      try { control.recognition.stop(); } catch (_) {}
    }
    try {
      const response = await fetch('/api/v1/realtime/speech', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({text: clean})
      });
      if (!response.ok) throw new Error('OpenAI speech unavailable');
      const url = URL.createObjectURL(await response.blob());
      if (replyAudio) { replyAudio.pause(); replyAudio.src = ''; }
      replyAudio = new Audio(url);
      const finish = () => { URL.revokeObjectURL(url); resumeAfterSpeech(control); };
      replyAudio.onended = finish;
      replyAudio.onerror = finish;
      await replyAudio.play();
    } catch (_) {
      resumeAfterSpeech(control);
    }
  }

  function initSpokenReplies() {
    const isFinalReply = text => text && !/^(thinking|analysing|analyzing|transcribing|sending)[…. .]*$/i.test(text.trim());
    const hero = document.getElementById('hero-answer');
    if (hero) new MutationObserver(() => {
      if (!hero.classList.contains('hidden') && isFinalReply(hero.textContent)) speakOpenAIReply(hero.textContent);
    }).observe(hero, {childList:true, characterData:true, subtree:true});
    [document.getElementById('chat-messages'), document.getElementById('chat-log')].filter(Boolean).forEach(messages => {
      new MutationObserver(records => records.forEach(record => record.addedNodes.forEach(node => {
        if (node.nodeType !== 1) return;
        const text = node.textContent || '';
        const isBot = node.classList?.contains('chat-msg-bot') || node.classList?.contains('msg-bot');
        if (isBot && !node.classList?.contains('error') && isFinalReply(text)) speakOpenAIReply(text);
      }))).observe(messages, {childList:true});
    });
  }

  function startVoice(control) {
    if (activeVoice && activeVoice !== control) stopVoice(activeVoice, false);
    if (activeVoice === control) return stopVoice(control, true);
    activeVoice = control;
    window.dispatchEvent(new Event('coo-compose-voice-start'));
    const launchRecording = async () => {
      if (!navigator.mediaDevices?.getUserMedia) {
        window.dispatchEvent(new Event('coo-compose-voice-end'));
        setVoiceState(control, 'idle', 'Microphone access requires HTTPS or localhost.');
        return;
      }
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          audio: { echoCancellation: true, noiseSuppression: true, autoGainControl: true }
        });
        const mimeType = ['audio/webm;codecs=opus', 'audio/webm', 'audio/mp4'].find(type => MediaRecorder.isTypeSupported(type)) || '';
        const recorder = new MediaRecorder(stream, mimeType ? { mimeType } : undefined);
        const chunks = [];
        const audioContext = new AudioContext();
        const analyser = audioContext.createAnalyser(); analyser.fftSize = 512;
        audioContext.createMediaStreamSource(stream).connect(analyser);
        const samples = new Uint8Array(analyser.fftSize);
        control.recorder = recorder; control.stream = stream; control.audioContext = audioContext;
        control.heardAudio = false; control.lastSoundAt = Date.now(); control.originalText = control.input.value.trim();
        control.manualStop = false; activeVoice = control;
        recorder.ondataavailable = event => { if (event.data.size) chunks.push(event.data); };
        recorder.onstop = async () => {
          cancelAnimationFrame(control.levelFrame); clearTimeout(control.silenceTimer);
          stream.getTracks().forEach(track => track.stop()); audioContext.close().catch(() => {});
          setVoiceState(control, 'processing', 'Transcribing…');
          try {
            if (!chunks.length || !control.heardAudio) throw new Error('No speech detected.');
            const extension = mimeType.includes('mp4') ? 'm4a' : 'webm';
            const form = new FormData(); form.append('file', new Blob(chunks, { type: mimeType || 'audio/webm' }), `recording.${extension}`);
            const response = await fetch('/api/v1/realtime/transcribe', { method: 'POST', body: form });
            const result = await response.json().catch(() => ({}));
            if (!response.ok) throw new Error(result.detail || 'OpenAI transcription failed.');
            const spoken = String(result.text || '').trim(); if (!spoken) throw new Error('No speech detected.');
            control.input.value = [control.originalText, spoken].filter(Boolean).join(' ');
            control.input.dispatchEvent(new Event('input', { bubbles: true }));
            control.heardSpeech = true; pendingVoiceReply = true; voiceSubmit(control.input);
            control.input.value = ''; control.input.dispatchEvent(new Event('input', { bubbles: true }));
            setVoiceState(control, 'idle', '');
          } catch (reason) { setVoiceState(control, 'idle', reason.message || 'Transcription failed.'); }
          finally {
            activeVoice = null; control.recorder = null; window.dispatchEvent(new Event('coo-compose-voice-end'));
            if (!control.status.textContent) setVoiceState(control, 'idle', '');
          }
        };
        const monitorLevel = () => {
          analyser.getByteTimeDomainData(samples);
          let energy = 0; for (const sample of samples) { const value = (sample - 128) / 128; energy += value * value; }
          const rms = Math.sqrt(energy / samples.length);
          if (rms > 0.025) { control.heardAudio = true; control.lastSoundAt = Date.now(); }
          if (control.heardAudio && Date.now() - control.lastSoundAt >= SILENCE_TO_SEND_MS) return stopVoice(control, true);
          control.levelFrame = requestAnimationFrame(monitorLevel);
        };
        recorder.start(250); setVoiceState(control, 'listening', ''); monitorLevel();
        control.silenceTimer = setTimeout(() => stopVoice(control, true), 30000);
      } catch (reason) {
        activeVoice = null;
        window.dispatchEvent(new Event('coo-compose-voice-end'));
        setVoiceState(control, 'idle', reason?.name === 'NotAllowedError' ? 'Microphone permission was denied. Allow it and try again.' : 'Could not start microphone recording.');
      }
    };
    void launchRecording();
  }

  function enhanceVoiceInput(input) {
    if (!input || input.dataset.voiceReady === 'true') return;
    input.dataset.voiceReady = 'true';
    const wrap = document.createElement('div');
    wrap.className = 'voice-input-shell';
    input.parentNode.insertBefore(wrap, input);
    wrap.appendChild(input);
    input.classList.add('voice-enabled-input');

    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'voice-mic-button';
    button.setAttribute('aria-label', 'Speak your question');
    button.setAttribute('aria-pressed', 'false');
    button.title = 'Speak your question';
    button.innerHTML = '<svg class="voice-mic-icon" aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="2" width="6" height="12" rx="3"></rect><path d="M5 10a7 7 0 0 0 14 0M12 17v5M8 22h8"></path></svg><span class="voice-wave" aria-hidden="true"><i></i><i></i><i></i></span><span class="voice-sr-only">Microphone</span>';
    const status = document.createElement('span');
    status.className = 'voice-status';
    status.setAttribute('role', 'status');
    status.setAttribute('aria-live', 'polite');
    wrap.append(button, status);
    const control = { input, wrap, button, status, recorder: null, stream: null, audioContext: null, silenceTimer: null, levelFrame: null };
    button.addEventListener('click', () => startVoice(control));
  }

  function initVoiceInputs() {
    ['hero-ask-input', 'chat-input', 'ai-import-prompt'].forEach(id => enhanceVoiceInput(document.getElementById(id)));
    const messages = document.getElementById('chat-messages');
    if (messages) {
      messages.setAttribute('role', 'log');
      messages.setAttribute('aria-live', 'polite');
      messages.setAttribute('aria-relevant', 'additions text');
    }
    const heroAnswer = document.getElementById('hero-answer');
    if (heroAnswer) {
      heroAnswer.setAttribute('role', 'status');
      heroAnswer.setAttribute('aria-live', 'polite');
    }
  }

  function createBot() {
    const bot = document.createElement('button');
    bot.type = 'button';
    bot.id = 'story-coo-bot';
    bot.className = 'story-bot-widget';
    bot.setAttribute('aria-label', 'Open COO Bot AI Insights');
    bot.innerHTML = `
      <span class="story-bot-figure" aria-hidden="true">
        <span class="story-bot-head">
          <span class="story-bot-ear left"></span>
          <span class="story-bot-ear right"></span>
          <span class="story-bot-face">
            <span class="story-bot-eye left"></span>
            <span class="story-bot-eye right"></span>
            <span class="story-bot-smile"></span>
          </span>
        </span>
        <span class="story-bot-body"><span class="story-bot-badge">COO</span></span>
        <span class="story-bot-arm"></span>
        <span class="story-bot-leg left"></span>
        <span class="story-bot-leg right"></span>
      </span>
      <span class="story-bot-copy"><strong>Hi, I'm COO Bot!</strong> I help businesses run smarter, faster and better.</span>
      <span class="story-bot-chip">COO Bot<span>AI Insights</span></span>
    `;
    return bot;
  }

  function seedStoryMessage() {
    const messages = document.getElementById('chat-messages');
    if (!messages || messages.children.length > 0 || typeof window.appendBotMsg !== 'function') return;
    window.appendBotMsg(STORY_MESSAGE);
  }

  function openEmbeddedChat(bot) {
    const chatTab = document.getElementById('tab-chat');
    const detailPanel = document.getElementById('detail-panel');
    if (!chatTab) return false;

    if (detailPanel && detailPanel.classList.contains('hidden')) {
      const target = document.getElementById('drop-zone') || detailPanel;
      target?.scrollIntoView({ behavior: 'smooth', block: 'center' });
      if (typeof window.showToast === 'function') {
        window.showToast('Upload or open a report first, then COO Bot can answer questions about it.');
      }
      return true;
    }

    const chatButton = Array.from(document.querySelectorAll('.tab-btn'))
      .find(btn => (btn.getAttribute('onclick') || '').includes("switchTab('chat'"));

    if (typeof window.switchTab === 'function') {
      window.switchTab('chat', chatButton || null);
    } else {
      document.querySelectorAll('.tab-content').forEach(tab => tab.classList.add('hidden'));
      chatTab.classList.remove('hidden');
      document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
      chatButton?.classList.add('active');
    }

    chatTab.scrollIntoView({ behavior: 'smooth', block: 'start' });

    const input = document.getElementById('chat-input');
    if (input) {
      setTimeout(() => input.focus(), 120);
    }

    syncChatState(bot);
    return true;
  }

  function openChat() {
    const panel = document.getElementById('chat-panel');
    const bot = document.getElementById('story-coo-bot');
    if (!panel) {
      openEmbeddedChat(bot);
      return;
    }

    if (panel.classList.contains('hidden') && typeof window.toggleChat === 'function') {
      window.toggleChat();
    } else if (panel.classList.contains('hidden')) {
      panel.classList.remove('hidden');
    }

    seedStoryMessage();

    const input = document.getElementById('chat-input');
    if (input) {
      setTimeout(() => input.focus(), 120);
    }

    syncChatState(bot);
  }

  function hideLegacyButton() {
    const legacy = document.getElementById('chat-toggle');
    if (!legacy) return;
    legacy.hidden = true;
    legacy.setAttribute('aria-hidden', 'true');
    legacy.setAttribute('tabindex', '-1');
  }

  function syncChatState(bot) {
    const panel = document.getElementById('chat-panel');
    if (!bot) return;

    if (panel) {
      bot.classList.toggle('is-chat-open', !panel.classList.contains('hidden'));
      return;
    }

    bot.classList.remove('is-chat-open');
  }

  function watchChatPanel(bot) {
    const panel = document.getElementById('chat-panel') || document.getElementById('tab-chat');
    if (!panel || !window.MutationObserver) return;
    syncChatState(bot);
    new MutationObserver(() => syncChatState(bot)).observe(panel, {
      attributes: true,
      attributeFilter: ['class']
    });
  }

  function init() {
    if (document.getElementById('story-coo-bot')) return;
    hideLegacyButton();
    const bot = createBot();
    const path = window.location.pathname.replace(/\/+$/, '');
    const isMainDashboard = path === '' || path === '/static' || path.endsWith('/index.html');
    if (!isMainDashboard) bot.classList.add('is-ready');
    document.body.appendChild(bot);
    if (isMainDashboard) {
      window.setTimeout(() => bot.classList.add('is-ready'), READY_DELAY_MS);
    }
    bot.addEventListener('click', openChat);
    watchChatPanel(bot);
    initVoiceInputs();
    initSpokenReplies();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
}());
