const ws = new WebSocket((location.protocol === "https:" ? "wss://" : "ws://") + location.host + "/ws");
const chat = document.getElementById("chat");
const status = document.getElementById("status");
const talkBtn = document.getElementById("talkBtn");
const player = document.getElementById("player");

let audioCtx, processor, stream, source;
let active = false;

ws.onmessage = (e) => {
  const msg = JSON.parse(e.data);
  if (msg.type === "status") status.textContent = msg.msg;
  if (msg.type === "user") addMsg("user", msg.text);
  if (msg.type === "assistant") addMsg("bot", msg.text);
  if (msg.type === "audio") {
    player.src = msg.url + "?t=" + Date.now();
    player.play().catch(()=>{});
  }
  if (msg.type === "error") addMsg("bot", "⚠️ " + msg.msg);
};

function addMsg(role, text){
  const wrap = document.createElement("div");
  wrap.className = "msg " + role;
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = text;
  wrap.appendChild(bubble);
  chat.appendChild(wrap);
  chat.scrollTo({ top: chat.scrollHeight, behavior: "smooth" });
}

talkBtn.addEventListener("click", startStream);

async function startStream(){
  if (active) return;
  try {
    active = true;
    talkBtn.classList.add("active");
    status.textContent = "جاهز للاستماع...";
    stream = await navigator.mediaDevices.getUserMedia({ audio: { channelCount: 1, sampleRate: 16000, echoCancellation: true, noiseSuppression: true } });
    audioCtx = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 16000 });
    await audioCtx.resume();
    source = audioCtx.createMediaStreamSource(stream);
    processor = audioCtx.createScriptProcessor(480, 1, 1);
    source.connect(processor);
    processor.connect(audioCtx.destination);
    processor.onaudioprocess = (ev) => {
      if (!active) return;
      const input = ev.inputBuffer.getChannelData(0);
      const buf = new ArrayBuffer(input.length * 2);
      const view = new DataView(buf);
      for (let i=0;i<input.length;i++){
        let s = Math.max(-1, Math.min(1, input[i]));
        view.setInt16(i*2, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
      }
      if (ws.readyState === WebSocket.OPEN) ws.send(buf);
    };
  } catch(err){
    active = false;
    talkBtn.classList.remove("active");
    status.textContent = "خطأ بالميكروفون";
    addMsg("bot", "تعذّر الوصول للميكروفون: " + err.message);
  }
}

window.addEventListener("beforeunload", () => {
  active = false;
  try { processor?.disconnect(); source?.disconnect(); stream?.getTracks().forEach(t=>t.stop()); audioCtx?.close(); } catch(e){}
});
