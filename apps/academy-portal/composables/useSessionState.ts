export interface AcademyStage {
  code: string
  title: string
  timebox: string
  mentor_focus: string
  student_action: string
  command: string
}

export interface SkillNode {
  code: string
  title: string
  level: string
  evidence: string
}

export interface SessionEvent {
  event_type: string
  note: string
  created_at: string
}

export interface AcademySession {
  academy_version: string
  lab_name: string
  student_name: string
  created_at: string
  current_stage: AcademyStage
  stages: AcademyStage[]
  skill_graph: SkillNode[]
  commands: string[]
  events: SessionEvent[]
  portal: {
    framework: string
    app_path: string
    session_env: string
    dev_command: string
  }
}

export async function useSessionState() {
  const session = useState<AcademySession | null>('academy-session', () => null)
  const source = useState<string>('academy-session-source', () => 'not-loaded')

  const loadFrom = async (endpoint: string) => {
    const payload = await $fetch<AcademySession>(endpoint)
    session.value = payload
    source.value = endpoint
  }

  const reload = async () => {
    const endpoints = ['/api/session', '/session.json', '/session.sample.json']
    let lastError: unknown

    for (const endpoint of endpoints) {
      try {
        await loadFrom(endpoint)
        return
      } catch (error) {
        lastError = error
      }
    }

    throw lastError
  }

  if (!session.value) {
    await reload()
  }

  return {
    session,
    source,
    reload
  }
}
