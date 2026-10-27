run_python() {
  if python3 -c 'import sys; raise SystemExit(sys.version_info.major != 3)' >/dev/null 2>&1; then
    python3 "$@"
  elif python -c 'import sys; raise SystemExit(sys.version_info.major != 3)' >/dev/null 2>&1; then
    python "$@"
  elif py -3 -c 'import sys' >/dev/null 2>&1; then
    py -3 "$@"
  else
    echo "Python 3 is required but no working interpreter was found (tried python3, python, and py -3)." >&2
    return 127
  fi
}
