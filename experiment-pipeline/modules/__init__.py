"""
6. Experiment 데이터 처리 모듈.

모든 측정 종류 모듈 (amr, ahe, moke 등) 은 동일한 4 함수 인터페이스를 노출:
    - load(raw_dir) -> dict
    - fit(loaded) -> dict
    - plot(loaded, fitted, out_dir) -> list[Path]
    - export(loaded, fitted, out_dir) -> None

사용 예:
    >>> from modules import amr, common
    >>> loaded = amr.load(Path('./00_raw'))
    >>> fitted = amr.fit(loaded)
    >>> amr.plot(loaded, fitted, Path('./01_processed/plots'))
    >>> amr.export(loaded, fitted, Path('./01_processed'))
"""

__version__ = "0.1.0"

from . import common  # noqa: F401
