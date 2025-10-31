window.onload = function() {

  function toHHMM(t){
    if(!t) return "";
    const [h,m] = t.split(":");
    return (h.length===1?"0"+h:h)+":"+m;
  }

  function buildMsg(){
    const place = document.getElementById("place").value.trim() || "_____";
    const date = document.getElementById("date").value || "_____";
    const time = toHHMM(document.getElementById("time").value) || "__:__";
    return `⚽ Flying Dads Team υπενθύμιση!\nΠαίζουμε μπαλίτσα στο ${place} την ${date} ώρα ${time}`;
  }

  window.openPreview = function(){
    const msg = buildMsg();
    document.getElementById("preview").textContent = msg;
    document.getElementById("dlgPreview").showModal();
  }

window.sendFixed = async function(){
  const msg = buildMsg();
  const res = await fetch("/api/send_fixed", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({message: msg})
  });
  const j = await res.json();
  const link = j.link || "";
  document.getElementById("preview").textContent = msg + "\n\n👉 " + link;
  document.getElementById("previewLink").href = link;
  document.getElementById("generatedLink").innerHTML = `🔗 <a href="${link}" target="_blank" style="color:#9be9ff;">${link}</a>`;
  document.getElementById("dlgPreview").showModal();
  loadLogs();
}

  window.sendCustom = async function(){
    const msg = document.getElementById("custom").value.trim();
    const ch = document.getElementById("channel").value;
    if(!msg){ alert("Γράψε μήνυμα!"); return; }
    await fetch("/api/send_custom", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({message: msg, channel: ch})
    });
    alert("✅ Απεστάλη!");
    loadLogs();
  }

  async function loadLogs(){
    try {
      const r = await fetch("/api/get_logs");
      const j = await r.json();
      const box = document.getElementById("logs");
      if(!j.length){ box.innerHTML = "<i>Δεν υπάρχουν καταχωρήσεις</i>"; return; }
      box.innerHTML = j.map(e => `
        <div class='logrow'>
          <div><b>${e.time}</b> · <span class='pill'>${e.kind}</span></div>
          <pre>${e.message}</pre>
        </div>`).join("");
    } catch(e){
      document.getElementById("logs").innerHTML = "⚠️ Σφάλμα φόρτωσης";
    }
  }

  loadLogs();
};
