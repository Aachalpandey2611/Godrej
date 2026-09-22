import { create } from 'zustand'
import * as chatApi from '../api/chat'

const useChatStore = create((set, get) => ({
  sessions: [],          // list of SessionOut
  activeSessionId: null, // currently open session
  messages: [],          // messages for active session
  isTyping: false,       // bot is "typing"
  error: null,

  // ── Sessions ──────────────────────────────────────────────────────────────
  fetchSessions: async () => {
    try {
      const { data } = await chatApi.getSessions()
      set({ sessions: data })
    } catch {
      // silently ignore — user may not be authed yet
    }
  },

  setActiveSession: async (sessionId) => {
    if (!sessionId) {
      set({ activeSessionId: null, messages: [] })
      return
    }
    try {
      const { data } = await chatApi.getHistory(sessionId)
      set({ activeSessionId: sessionId, messages: data.messages, error: null })
    } catch {
      set({ error: 'Failed to load conversation.' })
    }
  },

  deleteSession: async (sessionId) => {
    await chatApi.deleteSession(sessionId)
    const { sessions, activeSessionId } = get()
    const remaining = sessions.filter((s) => s.id !== sessionId)
    set({ sessions: remaining })
    if (activeSessionId === sessionId) {
      set({ activeSessionId: null, messages: [] })
    }
  },

  // ── Messaging ─────────────────────────────────────────────────────────────
  sendMessage: async (text) => {
    const { activeSessionId, messages, sessions } = get()

    // Optimistically add the user message
    const optimisticUser = {
      id: `temp-${Date.now()}`,
      role: 'user',
      content: text,
      timestamp: new Date().toISOString(),
    }
    set({ messages: [...messages, optimisticUser], isTyping: true, error: null })

    try {
      const { data } = await chatApi.sendMessage(text, activeSessionId)

      // If this was a new session, add it to the list
      const updatedSessions = sessions.some((s) => s.id === data.session_id)
        ? sessions.map((s) =>
            s.id === data.session_id ? { ...s, title: data.session_title } : s
          )
        : [
            { id: data.session_id, title: data.session_title, created_at: new Date().toISOString() },
            ...sessions,
          ]

      set((state) => ({
        activeSessionId: data.session_id,
        messages: [...state.messages, data.message],
        sessions: updatedSessions,
        isTyping: false,
      }))
    } catch (err) {
      const errMsg = err.response?.data?.detail || 'Something went wrong. Please try again.'
      set((state) => ({
        isTyping: false,
        error: errMsg,
        // Remove the optimistic message on failure
        messages: state.messages.filter((m) => m.id !== optimisticUser.id),
      }))
    }
  },

  clearError: () => set({ error: null }),
  newChat: () => set({ activeSessionId: null, messages: [] }),
}))

export default useChatStore
