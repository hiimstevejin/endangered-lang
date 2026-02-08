// Converts the Float32Array (range -1.0 to 1.0) from the VAD to Int16Array (range -32768 to 32767)
// This is standard PCM audio format.
export function floatTo16BitPCM(float32Array: Float32Array): ArrayBuffer {
  const buffer = new ArrayBuffer(float32Array.length * 2);
  const view = new DataView(buffer);

  for (let i = 0; i < float32Array.length; i++) {
    let s = Math.max(-1, Math.min(1, float32Array[i])); // Clamp to [-1, 1]
    // Convert to 16-bit integer (multiply by 32767)
    s = s < 0 ? s * 0x8000 : s * 0x7fff;
    view.setInt16(i * 2, s, true); // Little-endian
  }
  return buffer;
}
