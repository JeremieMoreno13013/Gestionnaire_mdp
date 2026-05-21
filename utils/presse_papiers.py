import threading
import pyperclip

_timer: threading.Timer | None = None

def copier_temporaire(texte: str, duree_sec: int = 45) -> None:
    global _timer
    if _timer is not None:
        _timer.cancel()

    pyperclip.copy(texte)

    def effacer():
        try:
            if pyperclip.paste() == texte:
                pyperclip.copy("")
        except Exception:
            pass

    _timer = threading.Timer(duree_sec, effacer)
    _timer.daemon = True
    _timer.start()