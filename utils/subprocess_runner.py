from __future__ import annotations

import asyncio
import logging
import os
import shlex
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = int(os.environ.get("SUBPROCESS_TIMEOUT", "120"))


@dataclass
class RunResult:
    command: str
    exit_code: int
    stdout: str
    stderr: str
    timed_out: bool = False
    elapsed_ms: float = 0.0
    extra: dict = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return self.exit_code == 0 and not self.timed_out

    def summary(self) -> str:
        status = "OK" if self.ok else f"FAIL(rc={self.exit_code})"
        if self.timed_out:
            status = "TIMEOUT"
        lines = [
            f"[{status}] {self.command}",
            f"  elapsed: {self.elapsed_ms:.0f}ms",
        ]
        if self.stderr.strip():
            lines.append(f"  stderr: {self.stderr.strip()[:500]}")
        return "\n".join(lines)


async def run(
    args: list[str],
    *,
    cwd: str | None = None,
    env: dict[str, str] | None = None,
    timeout: int = DEFAULT_TIMEOUT,
    input_data: bytes | None = None,
) -> RunResult:
    """Run a subprocess asynchronously with timeout and structured output."""
    cmd_str = shlex.join(args)
    logger.info("Running: %s (timeout=%ds, cwd=%s)", cmd_str, timeout, cwd)

    merged_env = {**os.environ, **(env or {})}

    import time

    t0 = time.monotonic()
    timed_out = False

    try:
        proc = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            stdin=asyncio.subprocess.PIPE if input_data else asyncio.subprocess.DEVNULL,
            cwd=cwd,
            env=merged_env,
        )
        stdout_bytes, stderr_bytes = await asyncio.wait_for(
            proc.communicate(input=input_data),
            timeout=timeout,
        )
    except asyncio.TimeoutError:
        timed_out = True
        try:
            proc.kill()
            stdout_bytes, stderr_bytes = await proc.communicate()
        except Exception:
            stdout_bytes, stderr_bytes = b"", b"process kill failed"
        elapsed = (time.monotonic() - t0) * 1000
        result = RunResult(
            command=cmd_str,
            exit_code=-1,
            stdout=stdout_bytes.decode("utf-8", errors="replace"),
            stderr=stderr_bytes.decode("utf-8", errors="replace"),
            timed_out=True,
            elapsed_ms=elapsed,
        )
        logger.warning("Timeout: %s", result.summary())
        return result

    elapsed = (time.monotonic() - t0) * 1000
    result = RunResult(
        command=cmd_str,
        exit_code=proc.returncode or 0,
        stdout=stdout_bytes.decode("utf-8", errors="replace"),
        stderr=stderr_bytes.decode("utf-8", errors="replace"),
        timed_out=False,
        elapsed_ms=elapsed,
    )
    if result.ok:
        logger.info("Success: %s (%.0fms)", cmd_str, elapsed)
    else:
        logger.warning("Failed: %s", result.summary())
    return result
