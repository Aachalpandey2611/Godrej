import { useEffect } from 'react'
import { useParams } from 'react-router-dom'
import Sidebar from '../components/sidebar/Sidebar'
import ChatWindow from '../components/chat/ChatWindow'
import useChatStore from '../stores/chatStore'
import useAuthStore from '../stores/authStore'

export default function ChatPage() {
  const { sessionId } = useParams()
  const { setActiveSession } = useChatStore()
  const { hydrateUser } = useAuthStore()

  // Hydrate user profile on mount (handles page refresh case)
  useEffect(() => {
    hydrateUser()
  }, [hydrateUser])

  // Load session from URL param if present
  useEffect(() => {
    if (sessionId) {
      setActiveSession(sessionId)
    }
  }, [sessionId, setActiveSession])

  return (
    <div className="flex h-screen overflow-hidden bg-gray-950">
      <Sidebar />
      <main className="flex-1 min-w-0">
        <ChatWindow />
      </main>
    </div>
  )
}
