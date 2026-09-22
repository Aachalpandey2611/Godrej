import { useState, useRef } from 'react'
import useChatStore from '../../stores/chatStore'

export default function InputBox() {
  const [text, setText] = useState('')
  const { sendMessage, isTyping } = useChatStore()
  const textareaRef = useRef(null)

  const disabled = isTyping || !text.trim()

  const handleSubmit = async () => {
    if (disabled) return
    const msg = text.trim()
    setText('')
    // Reset textarea height
    if (textareaRef.current) textareaRef.current.style.height = 'auto'
    await sendMessage(msg)
  }

  const handleKeyDown = (e) => {
    // Send on Enter (not Shift+Enter)
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  const handleInput = (e) => {
    setText(e.target.value)
    // Auto-grow textarea up to ~6 lines
    const ta = textareaRef.current
    if (ta) {
      ta.style.height = 'auto'
      ta.style.height = Math.min(ta.scrollHeight, 160) + 'px'
    }
  }

  return (
    <div className="px-4 pb-4 pt-2">
      <div className="flex items-end gap-2 bg-gray-800 border border-gray-700 rounded-2xl px-4 py-3 focus-within:border-brand-500 transition">
        <textarea
          ref={textareaRef}
          value={text}
          onChange={handleInput}
          onKeyDown={handleKeyDown}
          disabled={isTyping}
          placeholder="Ask a medical question…"
          rows={1}
          className="flex-1 bg-transparent text-white placeholder-gray-500 text-sm resize-none focus:outline-none leading-relaxed max-h-40 disabled:opacity-50"
        />
        <button
          onClick={handleSubmit}
          disabled={disabled}
          className="flex-shrink-0 w-8 h-8 rounded-xl bg-brand-600 hover:bg-brand-700 disabled:bg-gray-700 disabled:cursor-not-allowed flex items-center justify-center transition mb-0.5"
          title="Send message"
        >
          <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
          </svg>
        </button>
      </div>
      <p className="text-gray-600 text-xs text-center mt-2">
        Press <kbd className="bg-gray-800 px-1 rounded text-gray-500">Enter</kbd> to send ·{' '}
        <kbd className="bg-gray-800 px-1 rounded text-gray-500">Shift+Enter</kbd> for new line
      </p>
    </div>
  )
}
