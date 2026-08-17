## 1. Configuració de dependències

- [x] 1.1 Afegir `httpx` (i `pytest-asyncio` per a les proves) al `pyproject.toml` com a dependències
- [x] 1.2 Actualitzar el lockfile amb `uv sync`

## 2. Abstracció de pylast (Client LastFM)

- [x] 2.1 Afegir mètodes asíncrons a `LastfmClient` (`get_top_albums_async`, `get_top_artists_async`, `get_top_tracks_async`) utilitzant `asyncio.to_thread` per embolicar les crides síncrones de pylast

## 3. Lògica del Pipeline Asíncron (Builders)

- [x] 3.1 Introduir un mètode `_download_image_async` a `BaseCollageBuilder` utilitzant `httpx.AsyncClient` amb els mateixos fallbacks actuals
- [x] 3.2 Modificar o afegir `create_async()` a `BaseCollageBuilder` integrant un `asyncio.Semaphore` per limitar les peticions concurrents (e.g. max 20)
- [x] 3.3 Fer servir `asyncio.gather()` per gestionar la descàrrega asíncrona de totes les rajoles abans de cridar les funcions de processament d'imatges `_create_image`

## 4. API Pública (Façana)

- [x] 4.1 Implementar `generate_async()` al `CollageGenerator`
- [x] 4.2 Afegir els mètodes de conveniència asíncrons (`generate_top_albums_collage_async`, `generate_top_artists_collage_async`, `generate_top_tracks_collage_async`)

## 5. Proves i QA

- [x] 5.1 Crear proves unitàries `test_async_pipeline.py` amb `pytest-asyncio` garantint l'operativitat 100% offline (amb mocks)
- [x] 5.2 Executar tota la suite de proves (`uv run pytest tests/`) per confirmar absència de regressions i una cobertura òptima (≥ 90%)
