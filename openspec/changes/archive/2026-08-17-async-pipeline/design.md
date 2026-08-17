## Context

L'arquitectura actual utilitza `ThreadPoolExecutor` per a l'adquisició d'imatges en paral·lel. Amb collages densos, el nombre de fils augmenta dràsticament, el canvi de context degrada el rendiment i augmenta el consum de recursos de CPU i RAM. A més a més, els mètodes síncrons del `CollageGenerator` poden bloquejar l'esdeveniment principal si la biblioteca s'integra dins una API web o un bot de xarxa (com un microservei). Més informació a `proposal.md`.

## Goals / Non-Goals

**Goals:**
- Proporcionar un pipeline `100% asíncron` sota AsyncIO per la creació de collages (ex. nova interfície `generate_async()`).
- Utilitzar `httpx` per a la descàrrega asíncrona d'imatges i retrieval de perfils.
- Aplicar rate limiting amb un semàfor (`asyncio.Semaphore`) a l'hora de descarregar múltiples imatges en bloc, de cara a protegir la CDN de rebuitjos HTTP 429 i gestionar connexions eficientment.

**Non-Goals:**
- Reescriure per complet el codi existent i eliminar el flux síncron (el `ThreadPoolExecutor` encara podria ser usat sota el mètode antic o se'n podrà fer un "wrapper" si s'estableix com el mètode exclusiu, però aquí no descartarem res que no sigui el necessari).
- Substituir completament la llibreria `pylast`. (Farem ús de `asyncio.to_thread` per les crides específiques de `pylast` ja que només s'executen un sol cop per collage i no generen un volum problemàtic com les imatges).

## Decisions

- **Llibreria HTTP**: `httpx` per suportar AsyncIO. Alternativament es va considerar `aiohttp`, però `httpx` ofereix una interfície més semblant a `requests` i facilita la transició i la convivència en entorns síncrons (si es mantenen amunt).
- **Semàfor i Rate Limiting**: Limitació concurrent a un nombre segur, p. ex. 20 imatges simultànies mitjançant `asyncio.Semaphore`. Això prevé la saturació d'amplada de banda i esgotament de memòria (en carregar molts buffers de cop).
- **Abstracció de pylast**: Atès que `pylast` només suporta requests síncrones, embolicarem les crides principals (p. ex. `get_top_albums`) amb `asyncio.to_thread()` dins els mètodes asíncrons. La descàrrega massiva d'imatges subseqüent, que és el veritable coll d'ampolla, serà nativament asíncrona amb `httpx`.
- **Estructura Interna**: S'introduirà mètodes `_create_async` o equivalents als constructors (Builders) existents, per mantenir la coherència amb la refactorització en 4 capes. S'hauran de duplicar funcions d'adquisició o dissenyar una classe genèrica de sessions `httpx.AsyncClient`.

## Risks / Trade-offs

- **Risk**: Duplicació de codi si mantenim una interfície síncrona al costat de l'asíncrona (ex. request vs httpx). → **Mitigation**: Es podria emprar internament només l'enfocament asíncron encapsulant-ho amb un bloc de bucle d'esdeveniments per als cridadors síncrons, o utilitzar els avantatges de `httpx` que proveeix un client síncron molt semblant.
- **Risk**: Limitacions de memòria per l'emmagatzematge simultani d'imatges (buffers bytes). → **Mitigation**: El semàfor limitarà tant el número de crides HTTP com la quantitat d'imatges processades al mateix moment.
