## Purpose

Aquesta capacitat proporciona un mecanisme 100% asíncron i concurrent basat en AsyncIO per a l'adquisició massiva d'imatges sense bloquejar els fils del sistema i aplicant límits de concurrència per evitar el rate-limiting extern.

## ADDED Requirements

### Requirement: Descàrrega d'imatges asíncrona no bloquejant
El sistema SHALL permetre la descàrrega asíncrona de cobertes i fotos d'artistes de forma concurrent mitjançant el bucle d'esdeveniments.

#### Scenario: Descàrrega exitosa en format asíncron
- **WHEN** l'usuari crida l'API asíncrona de generació de collage
- **THEN** totes les imatges es descarreguen concurrentment de manera asíncrona sense bloquejar el fil d'execució

### Requirement: Control de concurrència estricte (Rate Limiting)
El sistema MUST establir un límit màxim de peticions HTTP simultànies a l'hora d'adquirir recursos asíncronament.

#### Scenario: Generació de collages de grans dimensions
- **WHEN** el collage requereix l'adquisició massiva (e.g. 400 ítems en un 20x20)
- **THEN** el sistema limita la quantitat de descàrregues en vol (in-flight) a un valor raonable mitjançant un semàfor per no col·lapsar o saturar els recursos de xarxa i respectar la CDN.
