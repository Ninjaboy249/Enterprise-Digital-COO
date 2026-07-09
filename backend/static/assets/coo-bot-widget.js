(function () {
  const READY_DELAY_MS = 5000;
  const STORY_MESSAGE = "Hi, I'm COO Bot. Share your question and I'll turn the numbers into a clear business story with the next best move.";

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
    document.body.appendChild(bot);
    window.setTimeout(() => bot.classList.add('is-ready'), READY_DELAY_MS);
    bot.addEventListener('click', openChat);
    watchChatPanel(bot);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
}());
