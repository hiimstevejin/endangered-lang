import { useState, useRef, useEffect, useCallback } from "react";
import { floatTo16BitPCM } from "../utils/audioUtils";

const VAD_THRESHOLD = -45; // Volume threshold in dB (adjust if too sensitive)
const SILENCE_DURATION = 1000; // How long to wait before stopping (ms)

export const useVolumeVAD = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [status, setStatus] = useState("Idle");
  const [volume, setVolume] = useState(0); // For UI visualization

  const socketRef = useRef<WebSocket | null>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const silenceTimerRef = useRef<number | null>(null);
  const isSpeakingRef = useRef(false);

  // 1. WebSocket Connection
  useEffect(() => {
    socketRef.current = new WebSocket("ws://127.0.0.1:8000/ws/audio");

    socketRef.current.onopen = () => console.log("WS Connected");
    socketRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.status === "sealed") {
        setStatus(`Sealed (${data.size} bytes). Ready.`);
        setIsRecording(false);
      }
    };

    return () => socketRef.current?.close();
  }, []);

  const startRecording = useCallback(async () => {
    if (!socketRef.current || socketRef.current.readyState !== WebSocket.OPEN) {
      alert("Server not connected");
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaStreamRef.current = stream;

      const audioContext = new AudioContext();
      audioContextRef.current = audioContext;
      const source = audioContext.createMediaStreamSource(stream);

      // Use a ScriptProcessor for raw audio access (simpler than AudioWorklet for this use case)
      const processor = audioContext.createScriptProcessor(4096, 1, 1);

      source.connect(processor);
      processor.connect(audioContext.destination);

      setStatus("Listening...");
      setIsRecording(true);
      isSpeakingRef.current = false;

      processor.onaudioprocess = (e) => {
        const inputData = e.inputBuffer.getChannelData(0);

        // A. Calculate Volume (Root Mean Square)
        let sum = 0;
        for (let i = 0; i < inputData.length; i++) {
          sum += inputData[i] * inputData[i];
        }
        const rms = Math.sqrt(sum / inputData.length);
        const db = 20 * Math.log10(rms); // Convert to decibels
        setVolume(Math.max(0, db + 100)); // Normalize for UI (0-100)

        // B. Stream Audio if "Speaking" or just started
        // (We stream everything once triggered to catch the start of the sentence)
        if (socketRef.current?.readyState === WebSocket.OPEN) {
          socketRef.current.send(floatTo16BitPCM(inputData));
        }

        // C. VAD Logic
        if (db > VAD_THRESHOLD) {
          // SPEECH DETECTED
          isSpeakingRef.current = true;
          setStatus("Speaking...");

          // Clear any pending stop timer
          if (silenceTimerRef.current) {
            clearTimeout(silenceTimerRef.current);
            silenceTimerRef.current = null;
          }
        } else if (isSpeakingRef.current) {
          // SILENCE DETECTED (After speech)
          if (!silenceTimerRef.current) {
            setStatus("Silence detected... waiting");
            silenceTimerRef.current = window.setTimeout(() => {
              stopRecording();
            }, SILENCE_DURATION);
          }
        }
      };
    } catch (err) {
      console.error("Error:", err);
      setStatus("Error accessing mic");
    }
  }, []);

  const stopRecording = useCallback(() => {
    // 1. Stop Tracks
    mediaStreamRef.current?.getTracks().forEach((track) => track.stop());
    audioContextRef.current?.close();

    // 2. Clear Timers
    if (silenceTimerRef.current) clearTimeout(silenceTimerRef.current);

    // 3. Send Signal
    if (socketRef.current?.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify({ type: "speech_end" }));
    }

    setIsRecording(false);
    setStatus("Processing...");
  }, []);

  return { isRecording, startRecording, stopRecording, status, volume };
};
