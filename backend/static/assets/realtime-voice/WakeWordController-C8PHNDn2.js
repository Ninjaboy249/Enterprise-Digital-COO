import { r as e, t } from "./react-CxZb3FHy.js";
//#region src/WakeWordController.tsx
var n = /* @__PURE__ */ e(t(), 1), r = "hey enterprise digital coo";
function i(e) {
	return e.toLowerCase().replace(/[^a-z0-9 ]/g, " ").replace(/\s+/g, " ").trim();
}
function a() {
	let e = new AudioContext(), t = e.createOscillator(), n = e.createGain();
	t.type = "sine", t.frequency.setValueAtTime(620, e.currentTime), t.frequency.exponentialRampToValueAtTime(920, e.currentTime + .18), n.gain.setValueAtTime(1e-4, e.currentTime), n.gain.exponentialRampToValueAtTime(.07, e.currentTime + .025), n.gain.exponentialRampToValueAtTime(1e-4, e.currentTime + .24), t.connect(n).connect(e.destination), t.start(), t.stop(e.currentTime + .25), t.onended = () => e.close().catch(() => void 0);
}
async function o(e) {
	let t = await fetch("/api/v1/metrics/chat", {
		method: "POST",
		headers: { "Content-Type": "application/json" },
		body: JSON.stringify({
			message: e,
			context: "general"
		})
	});
	if (!t.ok) throw Error("AI request failed");
	return (await t.json()).answer || "I could not find an answer for that.";
}
function s() {
	let e = (0, n.useRef)(null), t = (0, n.useRef)("wake"), s = (0, n.useRef)(null), c = (0, n.useRef)(!0), l = (0, n.useRef)(!0);
	return (0, n.useEffect)(() => {
		c.current = !0;
		let n = window.SpeechRecognition || window.webkitSpeechRecognition;
		if (!n) {
			console.warn("Wake word mode requires a browser with Web Speech API support.");
			return;
		}
		let u = new n();
		e.current = u, u.continuous = !0, u.interimResults = !1, u.lang = document.documentElement.lang || navigator.language || "en-US";
		let d = () => {
			s.current !== null && clearTimeout(s.current), s.current = null;
		}, f = () => {
			d(), t.current = "wake", l.current = !0, document.body.classList.remove("coo-wake-active", "coo-wake-thinking");
			try {
				u.start();
			} catch {}
		}, p = () => {
			t.current = "command", document.body.classList.add("coo-wake-active"), a(), d(), s.current = window.setTimeout(f, 1e4);
		}, m = (e) => {
			t.current = "speaking", document.body.classList.remove("coo-wake-thinking"), document.body.classList.add("coo-wake-speaking"), speechSynthesis.cancel();
			let n = new SpeechSynthesisUtterance(e);
			n.rate = 1, n.pitch = 1, n.volume = 1;
			let r = speechSynthesis.getVoices();
			n.voice = r.find((e) => /en/i.test(e.lang) && /natural|aria|samantha|google/i.test(e.name)) || r.find((e) => /en/i.test(e.lang)) || null, n.onend = n.onerror = () => {
				document.body.classList.remove("coo-wake-speaking"), c.current && f();
			}, speechSynthesis.speak(n);
		}, h = async (e) => {
			d(), t.current = "processing", l.current = !1, document.body.classList.remove("coo-wake-active"), document.body.classList.add("coo-wake-thinking");
			try {
				u.stop();
			} catch {}
			try {
				m(await o(e));
			} catch {
				m("Sorry, I could not reach the AI service. Please try again.");
			}
		};
		u.onresult = (e) => {
			for (let n = e.resultIndex; n < e.results.length; n += 1) {
				if (!e.results[n].isFinal) continue;
				let a = e.results[n][0].transcript.trim();
				if (a) {
					if (t.current === "wake") i(a).includes(r) && p();
					else if (t.current === "command") {
						h(a);
						break;
					}
				}
			}
		}, u.onerror = (e) => {
			(e.error === "not-allowed" || e.error === "service-not-allowed") && (l.current = !1);
		}, u.onend = () => {
			!c.current || !l.current || t.current === "processing" || t.current === "speaking" || window.setTimeout(() => {
				try {
					u.start();
				} catch {}
			}, 250);
		};
		let g = () => {
			d(), l.current = !1, t.current = "wake", document.body.classList.remove("coo-wake-active", "coo-wake-thinking", "coo-wake-speaking");
			try {
				u.abort();
			} catch {}
		}, _ = () => {
			c.current && (t.current = "wake", l.current = !0, window.setTimeout(() => {
				try {
					u.start();
				} catch {}
			}, 350));
		};
		return window.addEventListener("coo-compose-voice-start", g), window.addEventListener("coo-compose-voice-end", _), navigator.mediaDevices.getUserMedia({ audio: !0 }).then((e) => {
			e.getTracks().forEach((e) => e.stop()), c.current && u.start();
		}).catch(() => {
			l.current = !1;
		}), () => {
			c.current = !1, l.current = !1, d(), window.removeEventListener("coo-compose-voice-start", g), window.removeEventListener("coo-compose-voice-end", _), speechSynthesis.cancel(), document.body.classList.remove("coo-wake-active", "coo-wake-thinking", "coo-wake-speaking"), u.onend = null, u.abort(), e.current = null;
		};
	}, []), null;
}
//#endregion
export { s as default };
