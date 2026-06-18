# Fase 5c: adaptador calibrado para Dynamic Sensorium

## Objetivo

El baseline dinámico inicial era deliberadamente débil: una regresión ridge
directa sobre descriptores de vídeo colapsados. Perdía frente al predictor
medio en Dynamic Sensorium, aunque superaba al control con estímulos permutados.

El objetivo de esta fase es añadir un adaptador predictivo más razonable sin
convertirlo en una caja negra ni usar el tier `oracle` para ajustar
hiperparámetros.

## Adaptador implementado

Se añadió `calibrated_residual_ridge` en
`mousebrainbench/surrogate/sensorium_adapters.py`.

La idea es:

1. calcular la respuesta media de entrenamiento;
2. modelar solo el residual dependiente del estímulo;
3. seleccionar por CV interna en `train`:
   - regularización ridge `alpha`;
   - escala residual `beta`;
4. predecir en held-out como:

```text
prediction = train_mean_response + beta * ridge_residual(video_features)
```

Esto evita que un residual ruidoso degrade la predicción respecto al predictor
medio, que era el fallo del ridge directo en vídeo.

La grid usada fue:

```text
alpha in {0.1, 0.3, 1, 3, 10, 30, 100}
beta  in linspace(0, 1.5, 61)
```

La selección se hace solo con `train`; `oracle` queda como evaluación held-out.

## Comando reproducible

```bash
.venv/bin/python -m mousebrainbench.benchmarks.sensorium_predictive_mis \
  data/dynamic_sensorium/extracted/<mouse-dir> \
  --modality dynamic \
  --eval-tier oracle \
  --adapter calibrated_residual_ridge \
  --adapter-alpha-grid 0.1,0.3,1,3,10,30,100 \
  --git-revision ff333fd \
  --output results/dynamic_sensorium_adapter/<mouse>_oracle_calibrated_residual_mis.json
```

## Resultados agregados

Artefacto agregado:

```text
results/dynamic_sensorium_adapter/summary_dynamic_sensorium2023_calibrated_residual_mis.json
```

| Métrica | n | Mediana | Mínimo | Máximo |
|---|---:|---:|---:|---:|
| Adapter correlation | `5` | `0.4759` | `0.3902` | `0.5009` |
| Adapter Δ mean | `5` | `0.0222` | `-0.0013` | `0.0330` |
| Adapter Δ scrambled | `5` | `0.0377` | `0.0327` | `0.0445` |
| Adapter selected as best stimulus model | `5` | `5/5` | `5/5` | `5/5` |
| Positive Δ mean | `5` | `4/5` | `4/5` | `4/5` |
| Reliability estimable | `5` | `0/5` | `0/5` | `0/5` |

Resultados individuales:

| Mouse | Mean | Adapter | Δ mean | Δ scrambled | alpha | beta |
|---|---:|---:|---:|---:|---:|---:|
| `dynamic29515` | `0.4238` | `0.4224` | `-0.0013` | `0.0377` | `100` | `0.575` |
| `dynamic29623` | `0.3680` | `0.3902` | `0.0222` | `0.0327` | `100` | `0.625` |
| `dynamic29647` | `0.4472` | `0.4801` | `0.0330` | `0.0445` | `100` | `0.675` |
| `dynamic29712` | `0.4530` | `0.4759` | `0.0230` | `0.0337` | `100` | `0.600` |
| `dynamic29755` | `0.4806` | `0.5009` | `0.0203` | `0.0415` | `100` | `0.725` |

## Interpretación crítica

Este resultado es positivo, pero no debe exagerarse.

Lo que sí demuestra:

1. El marco permite mejorar un caso negativo sin cambiar la métrica.
2. La mejora frente a mean es positiva en 4/5 ratones y positiva en mediana.
3. La mejora frente al control scrambled es positiva en 5/5 ratones.
4. El adaptador fue seleccionado con CV interna en `train`, no ajustado usando
   `oracle`.
5. El MIS sigue evitando una conclusión mecanística fuerte.

Lo que no demuestra:

1. No es un modelo SOTA Sensorium.
2. No resuelve el problema de fiabilidad, porque `oracle` no tiene vídeos
   repetidos exactos.
3. No aporta por sí solo mecanismo biológico.
4. No reemplaza un modelo temporal profundo u oficial.

## Decisión

**Avance positivo moderado.** Ya no estamos ante un caso puramente negativo:
existe una mejora predictiva reproducible en la mayoría de ratones y robusta
frente a scrambled. Para una contribución fuerte, el siguiente paso debe ser
comparar este adaptador contra un modelo temporal más competente y, en paralelo,
buscar una fuente de evaluación con repeticiones, OOD o restricciones
estructurales.
