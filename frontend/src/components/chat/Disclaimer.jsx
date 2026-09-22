export default function Disclaimer() {
  return (
    <div className="flex items-start gap-2 bg-amber-500/10 border border-amber-500/20 rounded-lg px-4 py-2.5 text-amber-300 text-xs">
      <svg className="w-3.5 h-3.5 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
        <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
      </svg>
      <span>
        MediChat provides general health information only —{' '}
        <strong className="font-semibold">not a substitute for professional medical advice.</strong>{' '}
        Always consult a qualified healthcare provider for diagnosis and treatment.
      </span>
    </div>
  )
}
