#!/bin/sh
set -euo pipefail

TEMPLATE=/etc/alertmanager/config.tmpl
OUT=/etc/alertmanager/config.yml
GOMPLATE_BIN=/usr/local/bin/gomplate

# download gomplate if not present (lightweight single binary)
if [ ! -x "$GOMPLATE_BIN" ]; then
  echo "gomplate not found, downloading..."
  mkdir -p /tmp/gomplate
  # pick linux-amd64 binary (works on typical x86_64 hosts); for other platforms adjust accordingly
  wget -q -O /tmp/gomplate/gomplate.tar.gz https://github.com/hairyhenderson/gomplate/releases/download/v3.11.0/gomplate_linux-amd64.tar.gz
  tar -xzf /tmp/gomplate/gomplate.tar.gz -C /tmp/gomplate
  mv /tmp/gomplate/gomplate $GOMPLATE_BIN
  chmod +x $GOMPLATE_BIN
fi

if [ -f "$TEMPLATE" ]; then
  echo "Rendering Alertmanager config from template"
  # render with gomplate; template uses file() and env() functions
  $GOMPLATE_BIN -f $TEMPLATE -o $OUT
  if [ ! -s "$OUT" ]; then
    echo "Rendered config is empty or missing: $OUT" >&2
    exit 1
  fi
  echo "Rendered config at $OUT"
else
  echo "Template $TEMPLATE not found, expected to render config" >&2
  exit 1
fi

# Basic validation: try to start Alertmanager (it will exit on config errors)
echo "Starting Alertmanager..."
exec /bin/alertmanager --config.file=$OUT --storage.path=/alertmanager
