import ReactMarkdown from 'react-markdown'

export default function MessageBubble({ message }) {
  const isUser = message.role === 'user'

  const time = new Date(message.timestamp).toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit',
  })

  if (isUser) {
    return (
      <div className="flex justify-end px-4">
        <div className="max-w-[75%]">
          <div className="bg-brand-600 text-white rounded-2xl rounded-br-sm px-4 py-2.5 text-sm leading-relaxed">
            {message.content}
          </div>
          <p className="text-gray-600 text-xs mt-1 text-right">{time}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex items-end gap-2 px-4">
      {/* Bot avatar */}
      <div className="w-7 h-7 rounded-full bg-brand-700 flex items-center justify-center flex-shrink-0 mb-5">
        <span className="text-white text-xs font-bold">+</span>
      </div>

      <div className="max-w-[75%]">
        <div className="bg-gray-800 text-gray-100 rounded-2xl rounded-bl-sm px-4 py-3 text-sm leading-relaxed prose-medical">
          <ReactMarkdown>{message.content}</ReactMarkdown>
        </div>
        <p className="text-gray-600 text-xs mt-1">{time}</p>
      </div>
    </div>
  )
}
