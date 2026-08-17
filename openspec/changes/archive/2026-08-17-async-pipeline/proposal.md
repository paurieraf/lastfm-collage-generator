## Why

La descàrrega d'imatges síncrona utilitzant `ThreadPoolExecutor` pot causar colls d'ampolla i un consum excessiu de recursos en el sistema quan es generen collages de grans dimensions (p. ex. 20x20). La transició a un model d'entrada/sortida asíncron (AsyncIO natiu) amb `httpx` permetrà adquirir totes les imatges de forma concurrent i no bloquejant, millorant significativament la velocitat de generació.

## What Changes

- Transició del mecanisme de descàrrega de les imatges a `httpx` de forma asíncrona.
- S'implementarà un semàfor asíncron per controlar i limitar la concurrència d'adquisició i així evitar col·lapses o bloqueigs (rate limiting) per part de les APIs i els CDNs subjacents.
- Introducció d'una nova API (per exemple, `generate_async()`) al `CollageGenerator` que s'executarà en el bucle d'esdeveniments d'AsyncIO.
- **BREAKING**: Els mètodes interns que obtenien imatges (com el procés dins de `BaseCollageBuilder`) s'hauran d'adaptar al context asíncron si s'utilitza la nova API.

## Capabilities

### New Capabilities
- `async-pipeline`: Suport per la generació de collages 100% asíncrona i concurrència basada en semàfors, evitant el bloqueig de fils del sistema.

### Modified Capabilities
- `collage-core-engine`: Modificació dels constructors de collage base per suportar un flux d'execució asíncron opcional al costat de l'actual síncron (o substitució si s'escau).

## Impact

Afectarà principalment al mòdul `collage.py` on hi ha l'actual `ThreadPoolExecutor`. També afectarà l'`API` pública del `CollageGenerator` que haurà d'exposar mètodes asíncrons. S'hauran d'introduir noves dependències com `httpx` (i `asyncio` que forma part de la biblioteca estàndard de Python).
