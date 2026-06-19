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
- Baselines internos comparados: mean, summary adapter, temporal filterbank,
  `temporal_svd_residual_ridge`, random features y `torch_residual_mlp`.
- En OOD legacy:
  - SVD mejora a mean en `5/5`.
  - SVD mejora a temporal-filterbank en `5/5`.
  - mediana SVD - temporal-filterbank: `0.00586`.
- Baseline no lineal local `random_feature_residual_ridge` no supera a SVD:
  - Dynamic `oracle`: `1/5`.
  - Legacy OOD: `1/5`.
- Baseline neuronal local `torch_residual_mlp`:
  - Dynamic `oracle`: mejora a mean en `5/5`, mejora a SVD en `3/5`,
    mediana MLP - SVD `0.00386`.
  - Legacy OOD: mejora a mean en `4/5`, mejora a SVD en `3/5`,
    mediana MLP - SVD `0.00219`.

Lectura: hay contribucion predictiva/OOD y el marco ya compara modelos lineales,
no lineales y redes neuronales reales. El MLP no domina a SVD, por lo que no hay
claim de superioridad neuronal; si hay evidencia de que MouseBrainBench separa
rendimiento predictivo de identificabilidad mecanistica.

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
- No se ha batido ni reproducido un baseline oficial SOTA Sensorium.
- La restriccion topografica no equivale a mecanismo causal; solo aporta una
  condicion estructural verificable.
- El baseline `torch_residual_mlp` es una red neuronal local reproducible, no el
  modelo oficial del starter kit Sensorium ni una afirmacion de estado del arte.

## Contribucion publicable

La contribucion fuerte no es un modelo neuronal especifico, sino el protocolo:

1. Evaluar prediccion frente a mean y scrambled.
2. Separar in-distribution, OOD y repeticion.
3. Exigir fiabilidad antes de discutir mecanismo.
4. Anadir restricciones estructurales verificables cuando existan metadatos.
5. Reportar explicitamente cuando el MIS no permite una conclusion mecanistica.

## Siguiente decision

La fase de cierre del 19 de junio de 2026 ejecutó cinco comprobaciones:

1. Auditoría del baseline oficial Sensorium.
2. MIS sintético ampliado con casos intermedios.
3. Sensibilidad sobre Allen, Sensorium static y Dynamic Sensorium.
4. Puerta MICrONS acotada.
5. Congelado de ruta publicable.

Resultado:

- Baseline oficial Sensorium: stack integrado a nivel de forward-pass smoke
  test; falta entrenar/evaluar una configuración oficial para que cuente como
  baseline Q1.
- Baseline NN local: se mantiene `torch_residual_mlp` como control reproducible,
  sin claim SOTA.
- MIS sintético: solo pasa `directed_truth`; fallan correctamente common drive,
  topología sin dirección y dirección sin topología específica.
- Sensibilidad: Allen permanece negativo; Sensorium static mantiene evidencia
  parcial `6/9`; Dynamic mantiene ganancias NN pequeñas.
- MICrONS: deferido hasta disponer de un manifiesto pequeño estructura-función.

Ruta congelada:

```text
methodological_benchmark_paper_now_q1_requires_external_piece
```

Para cerrar un paper Q1 fuerte falta al menos uno de estos pasos:

1. Integrar un baseline externo oficial/SOTA del ecosistema Sensorium y mostrar
   que MouseBrainBench lo evalua de forma mas informativa que correlacion sola.
2. Anadir una segunda restriccion mecanistica, idealmente causal o
   intervencional, que complemente la topografia estructural.

El hueco metodologico principal se ha reducido: ya existe baseline NN local y
restriccion estructural verificable. Para una contribucion Q1 fuerte, el
siguiente salto no debe ser otro ajuste menor, sino validacion contra un baseline
externo oficial o una restriccion causal/intervencional defendible.

Artefactos de cierre:

- `results/sensorium_official_baseline_audit/summary.json`
- `results/q1_sensitivity/summary.json`
- `results/microns_pilot_gate/summary.json`
- `results/publication_freeze/summary.json`

Actualización adicional:

- El stack oficial Sensorium 2023 ya corre un forward-pass smoke test sobre
  datos locales Dynamic Sensorium.
- La auditoría actual es `official_sensorium_stack_integrated_training_pending`.
- Esto mejora la posición técnica, pero no cambia el dictamen Q1 porque todavía
  no existe un baseline oficial entrenado/evaluado.
- Documento técnico:
  `docs/SENSORIUM_OFFICIAL_BASELINE_INTEGRATION.md`.
