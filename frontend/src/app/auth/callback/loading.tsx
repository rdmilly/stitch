export default function Loading() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-[#0f0f17]">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500 mx-auto mb-4"></div>
        <p className="text-gray-400">Loading...</p>
      </div>
    </div>
  );
}
