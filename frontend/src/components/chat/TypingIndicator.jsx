export default function TypingIndicator() {
  return (
    <div className="flex items-end gap-2 px-4">
      {/* Bot avatar */}
      <div className="w-7 h-7 rounded-full bg-brand-700 flex items-center justify-center flex-shrink-0 mb-1">
        <span className="text-white text-xs font-bold">+</span>
      </div>

      <div className="bg-gray-800 rounded-2xl rounded-bl-sm px-4 py-3">
        <div className="flex items-center gap-1.5">
          <span
            className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
            style={{ animationDelay: '0ms' }}
          />
          <span
            className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
            style={{ animationDelay: '150ms' }}
          />
          <span
            className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
            style={{ animationDelay: '300ms' }}
          />
        </div>
      </div>
    </div>
  )
}
