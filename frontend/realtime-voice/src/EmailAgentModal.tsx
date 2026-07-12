import { FormEvent, useEffect, useState } from 'react';
import './email-agent.css';

export type EmailDraft = {
  recipient: string;
  subject: string;
  greeting: string;
  body: string;
  closing: string;
  signature: string;
  needs_details?: boolean;
};

const EMPTY_DRAFT: EmailDraft = {
  recipient: '', subject: '', greeting: 'Hello,', body: '', closing: 'Best regards,', signature: 'Enterprise Digital COO\nAI Command Center',
};

declare global {
  interface Window {
    COOEmailAgent?: { open: (draft: EmailDraft) => void; close: () => void };
  }
}

export default function EmailAgentModal() {
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState<EmailDraft>(EMPTY_DRAFT);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    window.COOEmailAgent = {
      open: next => {
        const merged = { ...EMPTY_DRAFT, ...next };
        setDraft(merged);
        setEditing(!merged.recipient || !!merged.needs_details);
        setError(''); setOpen(true);
      },
      close: () => setOpen(false),
    };
    return () => { delete window.COOEmailAgent; };
  }, []);

  const update = (field: keyof EmailDraft, value: string) => setDraft(current => ({ ...current, [field]: value }));

  const send = async (event: FormEvent) => {
    event.preventDefault();
    setSending(true); setError('');
    try {
      const response = await fetch('/api/v1/notifications/email/send', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(draft),
      });
      const result = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(result.detail || 'The email could not be sent.');
      if (!result.delivered) throw new Error('SMTP is not configured for delivery.');
      setOpen(false);
      window.dispatchEvent(new CustomEvent('coo-email-sent', { detail: { recipient: draft.recipient } }));
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'The email could not be sent.');
    } finally {
      setSending(false);
    }
  };

  if (!open) return null;
  const field = (label: string, key: keyof EmailDraft, multiline = false, placeholder = '') => (
    <label className="email-agent-field">
      <span>{label}</span>
      {multiline ?
        <textarea value={String(draft[key] || '')} onChange={event => update(key, event.target.value)} placeholder={placeholder} rows={key === 'body' ? 7 : 2} required /> :
        <input type={key === 'recipient' ? 'email' : 'text'} value={String(draft[key] || '')} onChange={event => update(key, event.target.value)} placeholder={placeholder} required />}
    </label>
  );

  return <div className="email-agent-overlay" role="dialog" aria-modal="true" aria-labelledby="email-agent-title">
    <form className="email-agent-modal" onSubmit={send}>
      <header className="email-agent-header">
        <div className="email-agent-mark">✦</div>
        <div><small>AI EMAIL AGENT</small><h2 id="email-agent-title">Review your email</h2><p>Nothing is sent until you confirm.</p></div>
        <button type="button" className="email-agent-close" onClick={() => setOpen(false)} aria-label="Cancel email">×</button>
      </header>

      {editing ? <div className="email-agent-editor">
        {(!draft.recipient || draft.needs_details) && <p className="email-agent-details-note">Complete the recipient and tell the Email Agent what you want to communicate.</p>}
        <div className="email-agent-grid">{field('Who should receive this?', 'recipient', false, 'recipient@company.com')}{field('Email subject', 'subject', false, 'Enter a clear subject')}</div>
        {field('Greeting', 'greeting')}{field('What should the email say?', 'body', true, 'Describe the update, request, or response you want to send…')}
        <div className="email-agent-grid">{field('Closing', 'closing')}{field('Signature', 'signature', true)}</div>
      </div> : <section className="email-agent-preview">
        <div className="email-agent-meta"><span><b>To</b>{draft.recipient || 'Recipient required'}</span><span><b>Subject</b>{draft.subject}</span></div>
        <article><p>{draft.greeting}</p><p className="email-agent-body">{draft.body}</p><p>{draft.closing}</p><p className="email-agent-signature">{draft.signature}</p></article>
      </section>}

      {error && <p className="email-agent-error" role="alert">{error}</p>}
      <footer className="email-agent-actions">
        <button type="button" className="email-agent-secondary" onClick={() => setEditing(value => !value)}>{editing ? 'Done Editing' : 'Edit'}</button>
        <button type="button" className="email-agent-cancel" onClick={() => setOpen(false)}>Cancel</button>
        <button type="submit" className="email-agent-send" disabled={sending || !draft.recipient}>{sending ? 'Sending…' : 'Send Email'}</button>
      </footer>
    </form>
  </div>;
}
