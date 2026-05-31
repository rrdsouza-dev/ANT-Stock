let streamAtual = null;

export async function iniciarCamera(video) {
  streamAtual = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } });
  video.srcObject = streamAtual;
  await video.play();
  return streamAtual;
}

export function pararCamera() {
  if (streamAtual) {
    streamAtual.getTracks().forEach((track) => track.stop());
    streamAtual = null;
  }
}
