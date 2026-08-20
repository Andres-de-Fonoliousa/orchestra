import { fileURLToPath } from "node:url"
import { spawn } from "node:child_process"

export const VoiceReport = async ({ client }) => {
  const MAIN = {
    build: { voice: "David", rate: 1, sound: "Notification.Reminder", color: "0969DA" },
    plan: { voice: "Zira", rate: 0, sound: "Notification.SMS", color: "8250DF" },
    explore: { voice: "David", rate: 2, sound: "Notification.Mail", color: "1A7F37" },
    general: { voice: "Zira", rate: -1, sound: "Notification.Default", color: "6B7280" },
  }
  const SUB_POOL = [
    { voice: "David", rate: 2, sound: "Notification.Alarm", color: "0969DA" },
    { voice: "Zira", rate: 2, sound: "Notification.SMS", color: "8250DF" },
    { voice: "David", rate: -2, sound: "Notification.Mail", color: "1A7F37" },
    { voice: "Zira", rate: -2, sound: "Notification.Reminder", color: "D29922" },
    { voice: "David", rate: 1, sound: "Notification.Message", color: "3D8FBF" },
    { voice: "Zira", rate: 1, sound: "Notification.Looping.Call", color: "E5534B" },
  ]
  const TTS = fileURLToPath(new URL("./tts.ps1", import.meta.url))
  const NOTIFY = fileURLToPath(new URL("./notify.ps1", import.meta.url))

  const log = async (level, message, extra = {}) => {
    try {
      await client.app.log({ body: { service: "voice-report", level, message, extra } })
    } catch {}
  }

  const hash = (s) => {
    let h = 0
    for (const c of s) h = (h * 31 + c.charCodeAt(0)) >>> 0
    return h
  }
  const clean = (t) =>
    t
      .replace(/```[\s\S]*?```/g, " code ")
      .replace(/`([^`]+)`/g, "$1")
      .replace(/!\[[^\]]*\]\([^)]*\)/g, "")
      .replace(/\[([^\]]+)\]\([^)]*\)/g, "$1")
      .replace(/https?:\/\/\S+/g, "")
      .replace(/[\u{1F300}-\u{1FAFF}\u{2600}-\u{27BF}]/gu, "")
      .replace(/[#>*_~|]/g, " ")
      .replace(/\s+/g, " ")
      .trim()
      .split(" ")
      .slice(0, 10)
      .join(" ")

  const extractReport = (text) => {
    const m = text.match(/^[*-]?\s*(?:Report|Result|Done)\s*:\s*(.+)$/im)
    if (m) {
      const r = clean(m[1])
      if (r) return r
    }
    const sentences = text
      .split(/(?<=[.!?])\s+|\n+/)
      .map((s) => s.trim())
      .filter(Boolean)
    const last = sentences[sentences.length - 1] || text
    let r = clean(last)
    if (r.split(" ").length < 2 && sentences.length > 1) {
      r = clean(sentences.slice(-2).join(" "))
    }
    return r || clean(text)
  }

  const runTTS = (voice, rate, text) =>
    new Promise((resolve) => {
      const child = spawn(
        "powershell",
        ["-NoProfile", "-ExecutionPolicy", "Bypass", "-File", TTS,
         "-Voice", voice, "-Rate", String(rate), "-Text", text],
        { stdio: "ignore", windowsHide: true }
      )
      const timer = setTimeout(() => { child.kill(); resolve() }, 30000)
      child.on("exit", () => { clearTimeout(timer); resolve() })
      child.on("error", () => { clearTimeout(timer); resolve() })
    })

  const notify = (title, message, sound, color) => {
    const child = spawn(
      "powershell",
      ["-NoProfile", "-ExecutionPolicy", "Bypass", "-File", NOTIFY,
       "-Title", title, "-Message", message, "-Sound", sound, "-Color", color],
      { stdio: "ignore", windowsHide: true }
    )
    const timer = setTimeout(() => child.kill(), 15000)
    child.on("exit", () => clearTimeout(timer))
    child.on("error", () => clearTimeout(timer))
  }

  let queue = Promise.resolve()
  const speak = (voice, rate, text) => {
    queue = queue.then(async () => {
      try {
        await log("info", "speaking", { voice, rate, text })
        await runTTS(voice, rate, text)
        await log("info", "spoken ok", { voice, text })
      } catch (e) {
        await log("error", "tts failed", { voice, text, error: String(e) })
      }
    })
    return queue
  }

  const streamText = new Map()
  const lastSpoken = new Map()

  const fetchReport = async (sessionID) => {
    try {
      const session = await client.session.get({ path: { id: sessionID } })
      const messages = await client.session.messages({ path: { id: sessionID } })
      let agent = "build"
      let text = ""
      for (let i = messages.length - 1; i >= 0; i--) {
        const { info, parts } = messages[i]
        if (info.role !== "assistant" || info.summary) continue
        agent = info.mode || agent
        for (let j = parts.length - 1; j >= 0; j--) {
          const p = parts[j]
          if (p.type === "text" && !p.synthetic && !p.ignored) {
            text = p.text
            break
          }
        }
        if (text) break
      }
      if (!text) return null
      return { agent, text }
    } catch (e) {
      await log("error", "fetch failed", { sessionID, error: String(e) })
      return null
    }
  }

  const speakReport = async (sessionID, agent, text) => {
    const report = extractReport(text)
    if (!report) return
    const cfg = MAIN[agent] || MAIN.general
    const session = await client.session.get({ path: { id: sessionID } }).catch(() => null)
    const title = session?.parentID ? agent : session?.title || "opencode"
    const styled = session?.parentID
      ? SUB_POOL[hash(agent) % SUB_POOL.length]
      : (MAIN[agent] || MAIN.general)
    notify(title, `${agent}: ${report}`, styled.sound, styled.color)
    try {
      await client.tui.showToast({ body: { message: `${agent}: ${report}`, variant: "info" } })
    } catch {}
    if (session?.parentID) {
      const sub = SUB_POOL[hash(agent) % SUB_POOL.length]
      speak(sub.voice, sub.rate, `${agent}: ${report}`)
    } else {
      speak(cfg.voice, cfg.rate, report)
    }
  }

  const onIdle = async (sessionID) => {
    const cached = streamText.get(sessionID)
    if (cached && cached.messageID !== lastSpoken.get(sessionID)) {
      lastSpoken.set(sessionID, cached.messageID)
      await log("info", "from stream cache", { sessionID, agent: cached.agent })
      await speakReport(sessionID, cached.agent, cached.text)
      return
    }
    let found = await fetchReport(sessionID)
    if (!found) {
      await new Promise((r) => setTimeout(r, 1000))
      found = await fetchReport(sessionID)
    }
    if (!found) {
      await log("info", "no report text", { sessionID })
      return
    }
    const messages = await client.session.messages({ path: { id: sessionID } }).catch(() => [])
    const lastID = messages[messages.length - 1]?.info?.id
    if (lastID && lastID === lastSpoken.get(sessionID)) {
      await log("info", "already spoken, skipping", { sessionID })
      return
    }
    lastSpoken.set(sessionID, lastID)
    await log("info", "from sdk fetch", { sessionID, agent: found.agent })
    await speakReport(sessionID, found.agent, found.text)
  }

  return {
    event: async ({ event }) => {
      const { type, properties } = event
      if (type === "message.part.updated" && properties.part) {
        const p = properties.part
        const sid = properties.sessionID || p.sessionID
        if (p.type === "text" && !p.synthetic && !p.ignored && sid) {
          const prev = streamText.get(sid)
          let text
          if (properties.delta) {
            text = prev && prev.messageID === p.messageID ? prev.text + properties.delta : properties.delta
          } else {
            text = p.text || ""
          }
          streamText.set(sid, { messageID: p.messageID, agent: prev?.agent || "build", text })
        }
      }
      if (type === "message.updated" && properties.info && properties.info.role === "assistant" && !properties.info.summary) {
        const sid = properties.info.sessionID
        const prev = streamText.get(sid)
        if (!prev?.agent) {
          streamText.set(sid, { messageID: prev?.messageID, agent: properties.info.mode || "build", text: prev?.text || "" })
        }
      }
      if (type === "session.idle" && properties.sessionID) {
        await log("info", "idle event", { sessionID: properties.sessionID })
        onIdle(properties.sessionID)
      }
      if (type === "session.error") {
        speak("Zira", -2, "Error")
      }
    },
  }
}