import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import useChatStore from '../../stores/chatStore'
import useAuthStore from '../../stores/authStore'

export default function Sidebar() {
  const navigate = useNavigate()
  const { sessions, activeSessionId, fetchSessions, setActiveSession, deleteSession, newChat } =
    useChatStore()
  const { user, logout } = useAuthStore()

  useEffect(() => {
    fetchSessions()
  }, [fetchSessions])

  const handleNewChat = () => {
    newChat()
    navigate('/')
  }

  const handleSelectSession = (id) => {
    setActiveSession(id)
    navigate('/')
  }

  const handleDelete = async (e, id) => {
    e.stopPropagation()
    await deleteSession(id)
  }

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <aside className="w-64 flex-shrink-0 flex flex-col h-screen bg-gray-900 border-r border-gray-800">
      {/* Header */}
      <div className="px-4 py-4 border-b border-gray-800">
        <div className="flex items-center gap-2 mb-4">
          <div className="w-7 h-7 bg-brand-600 rounded-md flex items-center justify-center">
            <span className="text-white font-bold text-sm">+</span>
          </div>
          <span className="font-bold text-white text-lg">MediChat</span>
        </div>

        <button
          onClick={handleNewChat}
          className="w-full flex items-center gap-2 bg-brand-600 hover:bg-brand-700 text-white text-sm font-medium rounded-lg px-3 py-2.5 transition"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          New chat
        </button>
      </div>

      {/* Session list */}
      <nav className="flex-1 overflow-y-auto px-2 py-3 space-y-0.5">
        {sessions.length === 0 ? (
          <p className="text-gray-600 text-xs text-center mt-6 px-4">
            No conversations yet. Start a new chat!
          </p>
        ) : (
          sessions.map((session) => (
            <button
              key={session.id}
              onClick={() => handleSelectSession(session.id)}
              className={`group w-full flex items-center justify-between text-left px-3 py-2.5 rounded-lg text-sm transition ${
                activeSessionId === session.id
                  ? 'bg-gray-700 text-white'
                  : 'text-gray-400 hover:bg-gray-800 hover:text-white'
              }`}
            >
              <div className="flex items-center gap-2 min-w-0">
                <svg className="w-3.5 h-3.5 flex-shrink-0 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
                <span className="truncate">{session.title}</span>
              </div>

              {/* Delete button */}
              <button
                onClick={(e) => handleDelete(e, session.id)}
                className="opacity-0 group-hover:opacity-100 flex-shrink-0 ml-1 p-0.5 rounded hover:bg-gray-600 text-gray-500 hover:text-red-400 transition"
                title="Delete conversation"
              >
                <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </button>
          ))
        )}
      </nav>

      {/* User footer */}
      <div className="px-3 py-3 border-t border-gray-800">
        <div className="flex items-center gap-2 px-2 py-2 rounded-lg">
          <div className="w-7 h-7 rounded-full bg-brand-700 flex items-center justify-center flex-shrink-0">
            <span className="text-white text-xs font-semibold">
              {user?.name?.[0]?.toUpperCase() ?? 'U'}
            </span>
          </div>
          <span className="text-gray-300 text-sm truncate flex-1 min-w-0">
            {user?.name ?? 'User'}
          </span>
          <button
            onClick={handleLogout}
            title="Sign out"
            className="text-gray-500 hover:text-red-400 transition flex-shrink-0"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
          </button>
        </div>
      </div>
    </aside>
  )
}
