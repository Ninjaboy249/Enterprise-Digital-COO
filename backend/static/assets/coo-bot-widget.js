(function () {
  const READY_DELAY_MS = 5000;
  const STORY_MESSAGE = "Hi, I'm COO Bot. Share your question and I'll turn the numbers into a clear business story with the next best move.";
  const SILENCE_TO_SEND_MS = 2500;
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  let activeVoice = null;

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
    if (control.recognition) {
      try { control.recognition.stop(); } catch (_) {}
    }
  }

  function startVoice(control) {
    if (window.COORealtimeVoice) {
      window.COORealtimeVoice.open();
      return;
    }
    if (!SpeechRecognition) {
      setVoiceState(control, 'idle', 'Voice input is not supported in this browser.');
      return;
    }
    if (activeVoice && activeVoice !== control) stopVoice(activeVoice, false);
    if (activeVoice === control) return stopVoice(control, true);

    const recognition = new SpeechRecognition();
    control.recognition = recognition;
    control.shouldSubmit = false;
    control.finalText = '';
    control.originalText = control.input.value.trim();
    recognition.lang = document.documentElement.lang || navigator.language || 'en-US';
    recognition.interimResults = true;
    recognition.continuous = true;

    recognition.onstart = () => {
      activeVoice = control;
      setVoiceState(control, 'listening', 'Listening… pause for 2.5 seconds to send.');
    };
    recognition.onresult = event => {
      let interim = '';
      for (let i = event.resultIndex; i < event.results.length; i += 1) {
        const words = event.results[i][0].transcript;
        if (event.results[i].isFinal) control.finalText += words + ' ';
        else interim += words;
      }
      const spoken = (control.finalText + interim).trim();
      control.input.value = [control.originalText, spoken].filter(Boolean).join(control.originalText && spoken ? ' ' : '');
      control.input.dispatchEvent(new Event('input', { bubbles: true }));
      clearTimeout(control.silenceTimer);
      control.silenceTimer = setTimeout(() => stopVoice(control, true), SILENCE_TO_SEND_MS);
    };
    recognition.onerror = event => {
      const denied = event.error === 'not-allowed' || event.error === 'service-not-allowed';
      setVoiceState(control, 'idle', denied ? 'Microphone permission is needed for voice input.' : 'I could not hear that. Please try again.');
      activeVoice = null;
    };
    recognition.onend = () => {
      clearTimeout(control.silenceTimer);
      const submit = control.shouldSubmit && control.input.value.trim();
      activeVoice = null;
      control.recognition = null;
      if (submit) {
        setVoiceState(control, 'processing', 'Sending your question…');
        window.setTimeout(() => {
          voiceSubmit(control.input);
          setVoiceState(control, 'idle', 'Sent.');
        }, 120);
      } else {
        setVoiceState(control, 'idle', '');
      }
    };
    try { recognition.start(); } catch (_) { setVoiceState(control, 'idle', 'Could not start the microphone.'); }
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
    const control = { input, wrap, button, status, recognition: null, silenceTimer: null };
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
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
}());
