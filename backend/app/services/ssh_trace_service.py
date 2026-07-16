"""Secure per-attempt SSH session tracing."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
import re


_SAFE_NAME_RE = re.compile(r"[^A-Za-z0-9_.-]+")
_ANSI_ESCAPE_RE = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")


class SSHTraceSession:
    """Write a redacted trace file for one SSH backup attempt."""

    def __init__(
        self,
        *,
        directory: Path,
        device_name: str,
        attempt: int,
        secrets: list[str | None],
        max_output_chars: int,
    ) -> None:
        self._write_failed = False
        try:
            directory.mkdir(parents=True, exist_ok=True)
        except OSError:
            self._write_failed = True
        safe_device = _SAFE_NAME_RE.sub("_", device_name).strip("._") or "device"
        timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S.%fZ")
        self.path = directory / f"{safe_device}-{timestamp}-attempt{attempt}.log"
        self.max_output_chars = max(256, max_output_chars)
        self._secrets = sorted(
            {str(value) for value in secrets if value is not None and str(value)},
            key=len,
            reverse=True,
        )
        self.event("TRACE_START", device=device_name, attempt=attempt)

    def _redact(self, value: object) -> str:
        text = str(value)
        for secret in self._secrets:
            text = text.replace(secret, "[REDACTED]")
        return text

    def event(self, event: str, **fields: object) -> None:
        """Append one structured trace event."""
        if self._write_failed:
            return
        timestamp = datetime.now(UTC).isoformat()
        details = " ".join(
            f"{key}={self._redact(value)!r}" for key, value in fields.items() if value is not None
        )
        line = f"{timestamp} {event}"
        if details:
            line = f"{line} {details}"
        try:
            with self.path.open("a", encoding="utf-8") as trace_file:
                trace_file.write(f"{line}\n")
        except OSError:
            # Tracing is diagnostic only and must never interrupt a backup.
            self._write_failed = True

    def received(self, output: str, *, context: str) -> None:
        """Record normalized terminal output with redaction and size limits."""
        if not output:
            return
        normalized = _ANSI_ESCAPE_RE.sub("", output).replace("\r\n", "\n").replace("\r", "\n")
        redacted = self._redact(normalized)
        if len(redacted) > self.max_output_chars:
            redacted = redacted[-self.max_output_chars :]
            redacted = f"[TRUNCATED TO LAST {self.max_output_chars} CHARACTERS]\n{redacted}"
        self.event("RECEIVED", context=context, output=redacted)

    def raw_received(self, output: str, *, context: str) -> None:
        """Record one received stream chunk with control characters escaped."""
        if not output:
            return
        redacted = self._redact(output)
        if len(redacted) > self.max_output_chars:
            redacted = redacted[: self.max_output_chars]
            redacted = f"{redacted}[TRUNCATED AFTER {self.max_output_chars} CHARACTERS]"
        self.event("RAW_RECV", context=context, data=ascii(redacted))

    def raw_sent(self, output: str, *, context: str, secret: bool = False) -> None:
        """Record one stream write with control characters escaped."""
        rendered = "[REDACTED]" if secret else self._redact(output)
        self.event("RAW_SEND", context=context, data=ascii(rendered))

    def close(self, *, status: str, error: object | None = None) -> None:
        """Finish the trace with an outcome marker."""
        self.event("TRACE_END", status=status, error=error)
