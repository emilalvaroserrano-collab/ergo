#!/bin/bash
# Start a ZONOS3 server on port 7453 (serves the built-in studio at /, /studio, /lite and the v2 API).
# macOS/Apple Silicon: uses the MLX backend and the GGUFs in servers/ggml/gguf (download separately).
# Linux/NVIDIA: uses the SGL/CUDA backend if available.
set -euo pipefail

repo_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
cd "$repo_root"
PORT="${PORT:-7453}"
HOST="${HOST:-127.0.0.1}"

if [[ "$(uname -s)" == "Darwin" && "$(uname -m)" == "arm64" ]]; then
  export LACI_ALL="${LACI_ALL:-1}"
  export STEER_BUNDLE="${STEER_BUNDLE:-$repo_root/assets/steering/studio_bundle_mect60k_x10.json}"
  # The edit-capable checkpoint carries the speech-edit rows (speech editing, pronunciation input).
  edit_model="$repo_root/servers/ggml/gguf/backbone-ptq-edit.gguf"
  [[ -f "$edit_model" ]] && export SERVE_MODEL="${SERVE_MODEL:-$edit_model}"
  export ZONOS3_STUDIO_PROJECTS="${ZONOS3_STUDIO_PROJECTS:-$HOME/Library/Application Support/Ergo-V3/projects}"
  edit_args=()
  accents="$repo_root/servers/ggml/gguf/edit/accents.gguf"
  [[ -f "$accents" ]] && edit_args=(--accent-adapters "$accents")
  exec servers/mlx/scripts/serve.sh --port "$PORT" --host "$HOST" ${edit_args[@]+"${edit_args[@]}"} "$@"
elif [[ -x "servers/ggml/build/zonos3-server" || -x "servers/ggml/build-cuda/zonos3-server" ]]; then
  bin="servers/ggml/build/zonos3-server"
  [[ -x "servers/ggml/build-cuda/zonos3-server" ]] && bin="servers/ggml/build-cuda/zonos3-server"
  models="${MODELS_DIR:-$repo_root/servers/ggml/gguf}"
  edit_model="$models/backbone-ptq-edit.gguf"
  [[ -f "$edit_model" ]] && export SERVE_MODEL="${SERVE_MODEL:-$edit_model}"
  backbone="${SERVE_MODEL:-$models/backbone-ptq.gguf}"
  args=("$backbone" --host "$HOST" --port "$PORT")
  [[ -d "$repo_root/assets/default_voices" ]] && args+=(--tts-default-voices-dir "$repo_root/assets/default_voices")
  [[ -f "$models/zac-keep2.gguf" ]] && args+=(--zac "$models/zac-keep2.gguf")
  [[ -f "$models/zac.gguf" ]] && args+=(--zac "$models/zac.gguf")
  [[ -f "$models/spk-encoder.gguf" ]] && args+=(--spk-encoder "$models/spk-encoder.gguf")
  [[ -f "$models/zac-encoder.gguf" ]] && args+=(--zac-encoder "$models/zac-encoder.gguf")
  [[ -f "$models/ssl-teacher.gguf" ]] && args+=(--ssl-teacher "$models/ssl-teacher.gguf")
  [[ -f "$models/steer.gguf" ]] && args+=(--steer "$models/steer.gguf")
  for accents in "$models/edit/accents.gguf" "$models/accents.gguf"; do
    [[ -f "$accents" ]] && { args+=(--accent-adapters "$accents"); break; }
  done
  exec "$bin" "${args[@]}" "$@"
else
  export LACI_ALL="${LACI_ALL:-1}"
  exec servers/sgl/scripts/serve.sh --port "$PORT" --host "$HOST" "$@"
fi
