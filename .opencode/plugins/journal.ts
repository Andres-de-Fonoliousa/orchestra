import { homedir } from "node:os"
import { join } from "node:path"
import { mkdir, readFile, writeFile } from "node:fs/promises"

const USER_MAX = 240
const ASST_MAX = 300
const MAX_LINES = 60

function brainDir(): string {
  return process.env.ORCHESTRA_HOME || join(homedir(), ".config", "opencode")
}

function textOf(part: any): string | null {
  if (part && part.type === "text" && typeof part.text === "string") {
    return part.text
  }
  return null
}

function roleOf(msg: any): string {
  return msg?.info?.role ?? msg?.role ?? "user"
}

function sessionOf(msg: any): string | null {
  return msg?.info?.sessionID ?? msg?.sessionID ?? null
}

function clip(text: string, max: number): string {
  const clean = text.replace(/\s+/g, " ").trim()
  if (!clean) return ""
  return clean.length > max ? clean.slice(0, max) + "…" : clean
}

export const AutoJournal = async ({ client, project, directory }: any) => {
  const pending = new Map<string, { lines: string[]; at: number }>()

  const log = async (level: string, message: string) => {
    try {
      await client?.app?.log?.({
        body: { service: "orchestra-journal", level, message },
      })
    } catch {
      /* never break the session over journaling */
    }
  }

  return {
    "message.updated": async (input: any) => {
      try {
        const msg = input?.event?.properties?.message ?? input?.message ?? input
        const sid = sessionOf(msg)
        if (!sid) return
        const parts = Array.isArray(msg?.parts) ? msg.parts : []
        const texts = parts.map(textOf).filter(Boolean)
        if (!texts.length) return
        const role = roleOf(msg)
        const max = role === "user" ? USER_MAX : ASST_MAX
        const buf = pending.get(sid) ?? { lines: [], at: 0 }
        for (const t of texts) {
          const line = clip(t, max)
          if (line) buf.lines.push(role + ": " + line)
        }
        buf.at = Date.now()
        pending.set(sid, buf)
      } catch (e: any) {
        await log("error", "message.updated: " + String(e))
      }
    },

    "session.idle": async (input: any) => {
      try {
        const sid =
          input?.event?.properties?.sessionID ?? input?.event?.sessionID ?? null
        if (!sid) return
        const buf = pending.get(sid)
        pending.delete(sid)
        if (!buf || !buf.lines.length) return

        const lines = buf.lines.slice(-MAX_LINES)
        const now = new Date()
        const date = now.toISOString().slice(0, 10)
        const hhmm = now.toTimeString().slice(0, 5)
        const dirName = String(directory ?? project?.path ?? "project")
          .split(/[\\/]/)
          .filter(Boolean)
          .pop()

        const jdir = join(brainDir(), "memory", "journal")
        await mkdir(jdir, { recursive: true })
        const file = join(jdir, date + ".md")
        const block =
          "\n## " +
          dirName +
          " — " +
          hhmm +
          " (auto)\n\n" +
          lines.map((l) => "- " + l).join("\n") +
          "\n"

        let existing = ""
        try {
          existing = await readFile(file, "utf8")
        } catch {
          /* first entry of the day */
        }
        const content = existing
          ? existing.replace(/\s*$/, "") + block
          : "# Journal " + date + "\n" + block
        await writeFile(file, content, "utf8")
        await log("info", "journaled " + lines.length + " lines to " + date + ".md")
      } catch (e: any) {
        await log("error", "session.idle: " + String(e))
      }
    },
  }
}