"""
Async Runner – runs a single asyncio event loop on a background daemon thread.
Use AsyncRunner.run(coroutine) from any Tkinter callback to schedule async work
without blocking the UI thread.
"""

import asyncio
import threading
import concurrent.futures
from typing import Coroutine, Any


class AsyncRunner:
    """Singleton that owns a background asyncio event loop."""

    _loop: asyncio.AbstractEventLoop | None = None
    _thread: threading.Thread | None = None
    _executor = concurrent.futures.ThreadPoolExecutor(max_workers=8)

    @classmethod
    def start(cls) -> None:
        """Start the background event loop (called once on app startup)."""
        if cls._loop is not None and not cls._loop.is_closed():
            return
        cls._loop = asyncio.new_event_loop()
        cls._loop.set_default_executor(cls._executor)
        cls._thread = threading.Thread(
            target=cls._loop.run_forever, daemon=True, name="AsyncRunnerLoop"
        )
        cls._thread.start()

    @classmethod
    def run(cls, coro: Coroutine, callback=None) -> concurrent.futures.Future:
        """Schedule a coroutine on the background event loop.

        Args:
            coro: The async coroutine to run.
            callback: Optional callable(result, exception) invoked when done.
                      Called on the background loop thread – use root.after()
                      to marshal the result back to the Tkinter main thread.
        Returns:
            A concurrent.futures.Future for the coroutine result.
        """
        if cls._loop is None or cls._loop.is_closed():
            cls.start()

        future = asyncio.run_coroutine_threadsafe(coro, cls._loop)

        if callback:
            def _done(f: concurrent.futures.Future):
                exc = f.exception()
                result = None if exc else f.result()
                callback(result, exc)
            future.add_done_callback(_done)

        return future

    @classmethod
    def stop(cls) -> None:
        """Gracefully stop the background event loop."""
        if cls._loop and not cls._loop.is_closed():
            cls._loop.call_soon_threadsafe(cls._loop.stop)
        cls._executor.shutdown(wait=False)
