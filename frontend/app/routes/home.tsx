import type { Route } from "./+types/home";
import { useVolumeVAD } from "../hooks/useVolumeVAD";

export function meta({}: Route.MetaArgs) {
  return [
    { title: "New React Router App" },
    { name: "description", content: "Welcome to React Router!" },
  ];
}

export default function Home() {
  const { isRecording, startRecording, stopRecording, status, volume } =
    useVolumeVAD();

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-6">
      <div className="bg-white p-8 rounded-2xl shadow-xl w-full max-w-md text-center space-y-6">
        <h1 className="text-3xl font-bold text-gray-800">Voice Agent</h1>

        {/* Volume Visualizer */}
        <div className="h-4 w-full bg-gray-200 rounded-full overflow-hidden">
          <div
            className="h-full bg-green-500 transition-all duration-75 ease-out"
            style={{ width: `${Math.min(100, volume * 1.5)}%` }} // Scale up slightly
          />
        </div>

        <div
          className={`p-4 rounded-lg font-mono text-sm ${
            status.includes("Speaking")
              ? "bg-green-100 text-green-700"
              : status.includes("Silence")
                ? "bg-yellow-100 text-yellow-700"
                : "bg-gray-100 text-gray-600"
          }`}
        >
          {status}
        </div>

        <div className="flex gap-4 justify-center">
          {!isRecording ? (
            <button
              onClick={startRecording}
              className="px-8 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold"
            >
              Start Mic
            </button>
          ) : (
            <button
              onClick={stopRecording}
              className="px-8 py-3 bg-red-500 hover:bg-red-600 text-white rounded-lg font-semibold"
            >
              Force Stop
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
