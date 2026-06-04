export function TypingIndicator() {
  return (
    <div className="flex gap-1.5 px-4 py-3 glass rounded-2xl rounded-tl-sm w-fit">
      <div className="w-2 h-2 rounded-full bg-violet-400 typing-dot" />
      <div className="w-2 h-2 rounded-full bg-violet-400 typing-dot" />
      <div className="w-2 h-2 rounded-full bg-violet-400 typing-dot" />
    </div>
  );
}
