import { readFile } from 'node:fs/promises'
import { resolve } from 'node:path'

export default defineEventHandler(async () => {
  const envSession = process.env.MENTOR_LAB_SESSION
  const candidates = [
    envSession,
    resolve(process.cwd(), 'public/session.json'),
    resolve(process.cwd(), 'public/session.sample.json')
  ].filter(Boolean) as string[]

  for (const candidate of candidates) {
    try {
      const raw = await readFile(candidate, 'utf-8')
      return JSON.parse(raw)
    } catch {
      continue
    }
  }

  throw createError({
    statusCode: 404,
    statusMessage: 'Session state was not found'
  })
})
