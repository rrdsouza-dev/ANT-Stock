import { limparCodigo } from "../validacoes/codigo-barras.js";
import { iniciarCamera, pararCamera } from "./camera.js";

export async function ativarScanner({ video, input, onDetectado }) {
  if (!("mediaDevices" in navigator)) {
    input.focus();
    throw new Error("Camera indisponivel neste navegador. Use o campo manual.");
  }
  await iniciarCamera(video);
  const codigoSimulado = limparCodigo(input.value);
  if (codigoSimulado) {
    pararCamera();
    onDetectado(codigoSimulado);
  }
}
