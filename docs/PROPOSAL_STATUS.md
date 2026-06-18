# Estado tecnico de la propuesta

## Tesis defendible

MouseBrainBench ya no debe presentarse como un intento de simular un cerebro de
raton. La propuesta defendible es:

> Un marco reproducible para separar prediccion neuronal, generalizacion OOD,
> fiabilidad experimental y restricciones mecanisticas en benchmarks de cerebro
> de raton, evitando que una mejora predictiva se confunda con identificabilidad.

## Evidencia actual

### Dynamic Sensorium

- Cohorte principal `oracle`: 5 ratones.
- Cohorte legacy OOD con respuestas liberadas: 5 ratones.
- Mejor baseline interno: `temporal_svd_residual_ridge`.
- En OOD legacy:
  - SVD mejora a mean en `5/5`.
  - SVD mejora a temporal-filterbank en `5/5`.
  - mediana SVD - temporal-filterbank: `0.00586`.
- Baseline no lineal local `random_feature_residual_ridge` no supera a SVD:
  - Dynamic `oracle`: `1/5`.
  - Legacy OOD: `1/5`.

Lectura: hay contribucion predictiva/OOD, pero no mecanismo por falta de
fiabilidad repetida y restriccion causal en Dynamic Sensorium.

### Sensorium 2022 static

- Fiabilidad repetida positiva en test:
  - mediana reliability: `0.64203`.
  - mediana best - mean: `0.09478`.
  - mediana best - scrambled: `0.06835`.
- Restriccion topografica estructural:
  - pasa en `5/5` ratones test repetidos.
  - Spearman mediana tuning-similitud vs distancia inversa: `0.17748`.
  - efecto mediano sobre nulo: `0.17794`.

Lectura: aqui si hay prediccion, fiabilidad y estructura anatomica verificable.
No es causalidad intervencional, pero es una restriccion mecanistica real.

## Lo que no se debe afirmar

- No hay gemelo digital de cerebro de raton.
- No hay conectoma funcional completo.
- No hay identificabilidad causal completa.
- No se ha batido un baseline oficial SOTA Sensorium.
- La restriccion topografica no equivale a mecanismo causal; solo aporta una
  condicion estructural verificable.

## Contribucion publicable

La contribucion fuerte no es un modelo neuronal especifico, sino el protocolo:

1. Evaluar prediccion frente a mean y scrambled.
2. Separar in-distribution, OOD y repeticion.
3. Exigir fiabilidad antes de discutir mecanismo.
4. Anadir restricciones estructurales verificables cuando existan metadatos.
5. Reportar explicitamente cuando el MIS no permite una conclusion mecanistica.

## Siguiente decision

Para cerrar un paper Q1 fuerte falta uno de estos dos pasos:

1. Integrar un baseline externo oficial/SOTA del ecosistema Sensorium y mostrar
   que MouseBrainBench lo evalua de forma mas informativa que correlacion sola.
2. Anadir una segunda restriccion mecanistica, idealmente causal o
   intervencional, que complemente la topografia estructural.

Sin uno de esos dos pasos, la version actual es mas adecuada para workshop,
congreso metodologico o articulo de benchmark reproducible, pero no para una
afirmacion Q1 fuerte sobre mecanismo cerebral.
