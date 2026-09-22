import { useEffect, useRef } from 'react'
import useChatStore from '../../stores/chatStore'
import MessageBubble from './MessageBubble'
import TypingIndicator from './TypingIndicator'
import InputBox from './InputBox'
import Disclaimer from './Disclaimer'

function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center flex-1 px-6 text-center">
      <div className="w-16 h-16 bg-brand-600/20 rounded-2xl flex items-center justify-center mb-4">
        <svg className="w-8 h-8 text-brand-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
        </svg>
      </div>
      <h2 className="text-white font-semibold text-lg mb-2">How can I help you today?</h2>
      <p className="text-gray-400 text-sm max-w-sm mb-6">
        Ask me anything about symptoms, conditions, medications, anatomy, or general health topics.
      </p>
      <div className="grid grid-cols-1 gap-2 w-full max-w-sm">
        {[
          'What are the symptoms of diabetes?',
          'How does ibuprofen work?',
          'What is the difference between a cold and the flu?',
        ].map((suggestion) => (
          <SuggestionChip key={suggestion} text={suggestion} />
        ))}
      </div>
    </div>
  )
}

function SuggestionChip({ text }) {
  const { sendMessage } = useChatStore()
  return (
    <button
      onClick={() => sendMessage(text)}
      className="text-left bg-gray-800 hover:bg-gray-750 border border-gray-700 hover:border-brand-600 text-gray-300 hover:text-white text-sm rounded-xl px-4 py-2.5 transition"
    >
      {text}
    </button>
  )
}

export default function ChatWindow() {
  const { messages, isTyping, error, clearError } = useChatStore()
  const bottomRef = useRef(null)

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isTyping])

  return (
    <div className="flex flex-col h-screen flex-1 min-w-0">
      {/* Disclaimer banner */}
      <div className="px-4 pt-4 pb-1">
        <Disclaimer />
      </div>

      {/* Message list */}
      <div className="flex-1 overflow-y-auto py-4 space-y-4">
        {messages.length === 0 ? (
          <EmptyState />
        ) : (
          messages.map((msg) => <MessageBubble key={msg.id} message={msg} />)
        )}

        {isTyping && <TypingIndicator />}

        {/* Error toast */}
        {error && (
          <div className="mx-4 bg-red-500/10 border border-red-500/30 text-red-400 text-sm rounded-lg px-4 py-3 flex items-center justify-between">
            <span>{error}</span>
            <button onClick={clearError} className="ml-3 text-red-400 hover:text-red-300">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <InputBox />
    </div>
  )
}
