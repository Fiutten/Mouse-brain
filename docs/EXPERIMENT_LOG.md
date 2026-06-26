# Registro de experimentos

## 2026-06-17 — Fase 5b: Dynamic Sensorium como prueba de consistencia

### Objetivo

Comprobar si el marco Sensorium/MIS se comporta de forma consistente al pasar
de imágenes estáticas a vídeos dinámicos, sin presentar un baseline ligero como
modelo predictivo moderno.

### Datos

Se descargaron los cinco zips públicos visibles de Dynamic Sensorium 2023 desde
GIN (`dynamic29515`, `dynamic29623`, `dynamic29647`, `dynamic29712`,
`dynamic29755`). Los cinco pasaron `unzip -t`; raw ocupa `48G` y la extracción
`94G`.

### Resultado

La evaluación se realizó sobre `oracle`, porque `live_test_*` y `final_test_*`
tienen respuestas retenidas/zeroed. El tier `oracle` contiene respuestas no
nulas, pero no vídeos repetidos exactos por hash, así que la fiabilidad por
repetición no es estimable.

| Métrica | Mediana |
|---|---:|
| Best predictive correlation | `0.4094` |
| Best Δ mean | `-0.0435` |
| Best Δ scrambled | `0.0521` |
| Reliability estimable | `0/5` |
| MIS score | `0.2222` |

### Decisión

**Caso negativo útil.** El descriptor temporal colapsado captura algo de señal
frente al control scrambled, pero no supera al predictor medio. El MIS falla de
forma correcta porque no hay reproducibilidad estimable, ganancia frente a mean
ni evidencia mecanística. El siguiente paso para una contribución fuerte es
añadir un adaptador a un modelo temporal competitivo u oficial Sensorium y
evaluarlo con la misma separación entre predicción, reproducibilidad e
identificabilidad.

## 2026-06-18 — Fase 5c: adaptador residual calibrado

### Objetivo

Convertir el caso dinámico negativo en una prueba predictiva más fuerte sin
ajustar hiperparámetros sobre `oracle`.

### Cambio

Se añadió `calibrated_residual_ridge`: respuesta media de entrenamiento más un
residual de estímulo escalado por `beta`. Tanto `alpha` como `beta` se eligen
por CV interna en `train`; `oracle` se mantiene como evaluación held-out.

### Resultado

| Métrica | Mediana |
|---|---:|
| Adapter correlation | `0.4759` |
| Adapter Δ mean | `0.0222` |
| Adapter Δ scrambled | `0.0377` |
| Positive Δ mean | `4/5` |
| Positive Δ scrambled | `5/5` |
| Reliability estimable | `0/5` |

### Decisión

**Avance positivo moderado.** El adaptador mejora la mediana frente al predictor
medio y supera al control scrambled en todos los ratones. No es todavía
identificabilidad mecanística ni SOTA; sí aporta una señal predictiva defendible
para continuar hacia un modelo temporal más potente.

## 2026-06-18 — Fase 5d: descriptor temporal y prueba OOD legacy

### Objetivo

Comprobar si una representación temporal explícita de vídeo mejora el adaptador
transparente y si la mejora se sostiene en tiers OOD con respuestas públicas.

### Cambios técnicos

- `data/loaders/sensorium.py` alinea estímulos, respuestas y covariables por
  `trial_id` derivado del nombre de archivo. Esto corrige releases con trials
  no consecutivos o sin respuesta pública.
- Se añadió `feature_mode=temporal_filterbank`: conserva ventanas temporales
  gruesas, energía de movimiento y modulación baja frecuencia del vídeo.
- Se añadieron scripts reproducibles:
  - `scripts/run_dynamic_sensorium_temporal_filterbank.py`;
  - `scripts/run_dynamic_sensorium_ood_probe.py`.

### Dynamic Sensorium 2023 principal

Comparación regenerada en:

```text
results/dynamic_sensorium_adapter/summary_dynamic_sensorium2023_temporal_filterbank_mis.json
```

| Métrica | Valor |
|---|---:|
| Ratones | `5` |
| Temporal mejora frente a summary | `4/5` |
| Mediana temporal - summary | `0.00847` |
| Mediana temporal - mean | `0.03114` |
| Mediana temporal - scrambled | `0.05168` |

### Dynamic Sensorium legacy OOD

Se descargó y verificó `dynamic29156-11-10`. El loader cargó `720` ensayos,
`7440` neuronas y respuestas no nulas en `live_test_*` y `final_test_*`.

Artefacto:

```text
results/dynamic_sensorium_ood/dynamic29156-11-10_ood_temporal_comparison.json
```

| Métrica OOD | Summary | Temporal filterbank |
|---|---:|---:|
| Correlación adapter | `0.36293` | `0.39149` |
| Δ mean | `-0.00203` | `0.02653` |
| Δ scrambled | `0.02078` | `0.06196` |

### Decisión

**Evidencia positiva, no cierre mecanístico.** El descriptor temporal aporta
señal en 4/5 ratones de la cohorte principal y mejora el caso OOD legacy en el
primer animal verificado. El MIS no pasa porque la fiabilidad por repetición
no es estimable y no hay restricción estructural/causal. Esto es exactamente
útil para nuestra tesis: el marco distingue predicción, OOD y mecanismo sin
confundirlos.

## 2026-06-18 — Fase 5e: ampliación OOD legacy a tres ratones

Nota: esta sección se conserva como trazabilidad histórica. La cohorte completa
de cinco ratones y los resultados vigentes están en la Fase 5g.

### Objetivo

Evitar que la prueba OOD legacy descansara en un único animal. Se intentó
ampliar la cohorte con los zips legacy disponibles en GIN y se incorporaron
solo los archivos que pasaron validación completa.

### Datos

Entraron en análisis tres animales:

- `dynamic29156-11-10`;
- `dynamic29234-6-9`;
- `dynamic29514-2-9`.

Los tres zips pasaron `unzip -t` y tienen SHA256 registrados en
`docs/DATA_PROVENANCE.md`. Dos intentos adicionales no entraron:
`dynamic29228-2-10` quedó parcial a `760M` y `dynamic29513-3-5` quedó parcial a
`2.3G`; en ambos casos el servidor rechazó reanudación por byte ranges.

### Resultado agregado

Artefacto:

```text
results/dynamic_sensorium_ood/summary_dynamic_sensorium_legacy_ood_temporal_comparison.json
```

| Métrica OOD | Valor |
|---|---:|
| Ratones válidos | `3` |
| Temporal mejora frente a summary | `3/3` |
| Temporal mejora frente a mean | `2/3` |
| Temporal mejora frente a scrambled | `3/3` |
| Mediana summary correlation | `0.36293` |
| Mediana temporal correlation | `0.39149` |
| Mediana temporal - summary | `0.01264` |
| Mediana temporal - mean | `0.02501` |
| Mediana temporal - scrambled | `0.02095` |
| Reliability estimable | `0/3` |
| MIS passed | `0/3` |

### Resultados individuales

| Mouse | Summary | Temporal | Temporal - summary | Temporal - mean | Temporal - scrambled |
|---|---:|---:|---:|---:|---:|
| `dynamic29156-11-10` | `0.36293` | `0.39149` | `0.02857` | `0.02653` | `0.06196` |
| `dynamic29234-6-9` | `0.32288` | `0.32300` | `0.00012` | `-0.00638` | `0.01091` |
| `dynamic29514-2-9` | `0.41617` | `0.42881` | `0.01264` | `0.02501` | `0.02095` |

### Decisión

**Evidencia OOD positiva moderada.** El descriptor temporal mejora de forma
consistente frente al descriptor summary y frente al control scrambled en los
tres animales validados. La mejora frente al predictor medio es positiva en
dos de tres, lo que obliga a una lectura prudente: hay señal temporal útil y
generalización OOD, pero no una ventaja universal ni una afirmación mecanística.

El MIS hace lo correcto al no pasar: no hay fiabilidad por repetición estimable
ni restricción estructural/causal. Este resultado sirve para sostener el
argumento metodológico del proyecto, no para reclamar un modelo neuronal
explicativo completo.

## 2026-06-18 — Fase 5f: adaptador temporal SVD

### Objetivo

Probar un modelo temporal más serio que el descriptor temporal transparente,
sin saltar todavía a deep learning ni usar test/OOD para seleccionar
hiperparámetros.

### Modelo

Se añadió `temporal_svd_residual_ridge`:

1. estandariza descriptores `temporal_filterbank` solo con `train`;
2. aprende una subbase SVD solo en `train`;
3. predice residuales neuronales con ridge en esa subbase;
4. selecciona componentes, `alpha` y escala residual `beta` por CV interna;
5. evalúa `oracle` u OOD sin tocar sus respuestas durante selección.

La primera implementación era demasiado costosa porque acumulaba predicciones
CV para todos los candidatos. Se sustituyó por selección streaming, manteniendo
una matriz CV por combinación componentes/alpha y evaluando beta sin almacenar
todo el grid. Esto reduce memoria y deja el experimento operativo.

### Dynamic Sensorium 2023 principal

Artefacto:

```text
results/dynamic_sensorium_temporal_svd/summary_dynamic_sensorium2023_temporal_svd.json
```

| Métrica | Valor |
|---|---:|
| Ratones | `5` |
| SVD mejora frente a mean | `4/5` |
| SVD mejora frente a scrambled | `5/5` |
| Mediana SVD - mean | `0.03889` |
| Mediana SVD - scrambled | `0.05480` |
| SVD mejora frente al temporal-filterbank previo | `3/5` |
| Mediana SVD - temporal-filterbank previo | `0.00775` |
| Reliability estimable | `0/5` |
| MIS passed | `0/5` |

### Dynamic Sensorium legacy OOD

Artefacto:

```text
results/dynamic_sensorium_temporal_svd/summary_dynamic_sensorium_legacy_ood_temporal_svd.json
```

| Métrica OOD | Valor |
|---|---:|
| Ratones válidos | `5` |
| SVD mejora frente a mean | `5/5` |
| SVD mejora frente a scrambled | `5/5` |
| Mediana SVD - mean | `0.03091` |
| Mediana SVD - scrambled | `0.05498` |
| SVD mejora frente al temporal-filterbank previo | `5/5` |
| Mediana SVD - temporal-filterbank previo | `0.00586` |
| Reliability estimable | `0/5` |
| MIS passed | `0/5` |

### Decisión

**Avance positivo, todavía no Q1 por sí solo.** El adaptador SVD aporta una
mejora incremental pequeña pero consistente en OOD frente al baseline temporal
previo. La señal principal es que el marco detecta una mejora predictiva real
sin convertirla en identificabilidad mecanística. Para una publicación fuerte,
el siguiente paso debe comparar contra un modelo temporal externo/oficial o
un baseline profundo ligero, y buscar un dataset/tier con repeticiones que
permita estimar fiabilidad.

## 2026-06-18 — Fase 5g: cohorte OOD legacy completa

### Objetivo

Cerrar la ambigüedad sobre la cohorte OOD legacy. La fase anterior usaba tres
ratones porque dos descargas habían quedado parciales. Se repitieron esas dos
descargas desde cero, se validaron con `unzip -t` y se reejecutaron todos los
benchmarks sobre los cinco animales disponibles.

### Datos

Entraron en análisis cinco animales:

- `dynamic29156-11-10`;
- `dynamic29228-2-10`;
- `dynamic29234-6-9`;
- `dynamic29513-3-5`;
- `dynamic29514-2-9`.

Los hashes SHA256 y tamaños locales están registrados en
`docs/DATA_PROVENANCE.md`. La ejecución quedó estampada con `git_revision`
`afa91c6`.

### Baseline temporal-filterbank

Artefacto:

```text
results/dynamic_sensorium_ood/summary_dynamic_sensorium_legacy_ood_temporal_comparison.json
```

| Métrica OOD | Valor |
|---|---:|
| Ratones válidos | `5` |
| Temporal mejora frente a summary | `5/5` |
| Temporal mejora frente a mean | `4/5` |
| Temporal mejora frente a scrambled | `5/5` |
| Mediana summary correlation | `0.41113` |
| Mediana temporal correlation | `0.42178` |
| Mediana temporal - summary | `0.01106` |
| Mediana temporal - mean | `0.02501` |
| Mediana temporal - scrambled | `0.05062` |
| Reliability estimable | `0/5` |
| MIS passed | `0/5` |

### Adaptador temporal SVD

Artefacto:

```text
results/dynamic_sensorium_temporal_svd/summary_dynamic_sensorium_legacy_ood_temporal_svd.json
```

| Métrica OOD | Valor |
|---|---:|
| Ratones válidos | `5` |
| SVD mejora frente a mean | `5/5` |
| SVD mejora frente a scrambled | `5/5` |
| SVD mejora frente al temporal-filterbank previo | `5/5` |
| Mediana SVD - mean | `0.03091` |
| Mediana SVD - scrambled | `0.05498` |
| Mediana SVD - temporal-filterbank previo | `0.00586` |
| Reliability estimable | `0/5` |
| MIS passed | `0/5` |

Resultados individuales frente al baseline temporal:

| Mouse | Mean | Summary | Temporal filterbank | Temporal SVD | SVD - filterbank |
|---|---:|---:|---:|---:|---:|
| `dynamic29156-11-10` | `0.36496` | `0.36293` | `0.39149` | `0.39884` | `0.00735` |
| `dynamic29228-2-10` | `0.41257` | `0.41779` | `0.42886` | `0.43471` | `0.00586` |
| `dynamic29234-6-9` | `0.32939` | `0.32288` | `0.32300` | `0.36030` | `0.03729` |
| `dynamic29513-3-5` | `0.38856` | `0.41113` | `0.42178` | `0.42657` | `0.00479` |
| `dynamic29514-2-9` | `0.40380` | `0.41617` | `0.42881` | `0.43319` | `0.00438` |

### Decisión

**La señal predictiva se sostiene al completar la cohorte, pero no cambia la
lectura mecanística.** El SVD temporal mejora a mean, scrambled y al
temporal-filterbank en `5/5` ratones OOD, con una mejora mediana pequeña frente
al filterbank (`+0.00586` de correlación) y un caso especialmente informativo
(`dynamic29234-6-9`) donde el filterbank no superaba a mean pero el SVD sí.

Esto es una contribución metodológica plausible para el benchmark: el marco
distingue entre un modelo con mejor predicción OOD y un modelo identificable.
El MIS sigue fallando de manera correcta (`0/5`) porque no hay fiabilidad por
repetición ni restricción estructural/causal. Por tanto, el resultado positivo
debe presentarse como evaluación predictiva OOD y como control de no
identificabilidad, no como evidencia de mecanismo cerebral.

## 2026-06-18 — Fase 5h: comparador formal de modelos Sensorium

### Objetivo

Convertir las comparaciones dispersas entre `mean`, `summary`,
`temporal_filterbank` y `temporal_svd` en un artefacto único, reproducible y
auditable. El comparador no reentrena modelos: lee JSONs ya generados,
empareja ratones por su identificador estable `dynamic<id>` y calcula deltas
pareados.

### Implementación

Se añadió:

- `mousebrainbench/benchmarks/sensorium_model_comparator.py`;
- `scripts/compare_dynamic_sensorium_models.py`;
- entry point `mousebrainbench-sensorium-compare`;
- tests unitarios en `tests/test_sensorium_model_comparator.py`.

Artefactos:

```text
results/dynamic_sensorium_model_comparator/summary.json
results/dynamic_sensorium_model_comparator/summary.md
```

### Resultado

| Cohorte | n | Mejor modelo | SVD > mean | SVD > temporal-filterbank | Evidencia |
|---|---:|---|---:|---:|---|
| Dynamic Sensorium 2023 `oracle` | `5` | SVD `3/5`, filterbank `2/5` | `4/5` | `3/5` | predicción sin fiabilidad |
| Legacy OOD liberado | `5` | SVD `5/5` | `5/5` | `5/5` | OOD predictivo sin mecanismo |

Medians:

| Cohorte | Temporal - mean | SVD - mean | SVD - temporal |
|---|---:|---:|---:|
| Dynamic Sensorium 2023 `oracle` | `0.03114` | `0.03889` | `0.00775` |
| Legacy OOD liberado | `0.02501` | `0.03091` | `0.00586` |

### Decisión

**El comparador confirma la contribución metodológica, no una conclusión
mecanística.** La señal más fuerte está en OOD legacy: SVD es el mejor modelo en
`5/5` ratones y mejora a mean y temporal-filterbank de forma pareada. En la
cohorte `oracle`, SVD es competitivo pero no domina universalmente. En ambas
cohortes `MIS passed = 0`, por lo que el marco evita convertir rendimiento
predictivo en identificabilidad cerebral.

La siguiente mejora técnica debe ser incorporar un baseline externo más fuerte
u otro dataset con fiabilidad estimable. Sin una de esas dos cosas, seguir
mejorando descriptores ligeros solo aporta incrementos pequeños.

## 2026-06-18 — Fase 5i: baseline no lineal, fiabilidad y dataset cruzado

### Objetivo

Ejecutar los cuatro pasos pendientes sin inflar la interpretación:

1. probar un baseline más fuerte;
2. localizar una fuente con fiabilidad estimable;
3. contrastar el marco en otro dataset;
4. decidir si la línea actual merece escalarse o debe cambiar de evidencia.

### Baseline no lineal local

Se añadió `random_feature_residual_ridge`, un baseline de random Fourier
features que aproxima kernel ridge RBF y mantiene selección train-only. No es
un modelo oficial Sensorium ni SOTA; se usa como control local más fuerte que
los descriptores lineales.

Artefactos:

```text
results/dynamic_sensorium_random_feature/summary_dynamic_sensorium2023_random_feature.json
results/dynamic_sensorium_random_feature/summary_dynamic_sensorium_legacy_ood_random_feature.json
```

Resultado frente a SVD:

| Cohorte | Random feature > mean | Random feature > scrambled | Random feature > SVD | Mediana RF - SVD |
|---|---:|---:|---:|---:|
| Dynamic Sensorium 2023 `oracle` | `2/5` | `4/5` | `1/5` | `-0.03447` |
| Legacy OOD liberado | `3/5` | `5/5` | `1/5` | `-0.01247` |

Conclusión: el baseline no lineal local no mejora la situación. Aumentar
capacidad de forma genérica no basta; SVD sigue siendo el baseline interno más
fuerte y estable.

### Fiabilidad y dataset cruzado

Se generó un comparador para Sensorium 2022 estático usando los artefactos ya
sellados:

```text
results/sensorium_static_model_comparator/summary.json
results/sensorium_static_model_comparator/summary.md
```

| Cohorte | n | Reliability | Best corr | Best - mean | Best - scrambled | MIS score |
|---|---:|---:|---:|---:|---:|---:|
| Validation all mice | `7` | `0.0` | `0.32795` | `0.10241` | `0.07737` | `0.33333` |
| Pretraining repeated test | `5` | `0.64203` | `0.34095` | `0.09478` | `0.06835` | `0.66667` |

Sensorium 2022 estático es ahora nuestro caso positivo de fiabilidad:
hay repetición estimable y predicción estímulo-específica, pero el MIS sigue sin
pasar porque no existe restricción estructural, causal o intervencional.

### Decisión

**Punto científico actual:** la contribución es defendible como marco de
benchmarking crítico que separa predicción, OOD, fiabilidad e identificabilidad.
No es todavía una contribución mecanística fuerte. El resultado más sólido es:

- Dynamic OOD: SVD mejora a mean y filterbank en `5/5`, pero sin fiabilidad.
- Static Sensorium: hay fiabilidad positiva y predicción, pero sin causalidad.
- Baseline no lineal local: no supera a SVD; no merece más inversión inmediata.

La siguiente ruta publicable no debe ser "otro baseline interno". Debe ser una
de dos:

1. integrar un baseline externo real del ecosistema Sensorium/NN, aunque sea
costoso;
2. añadir una restricción mecanística verificable: repetición + estructura,
perturbación o causalidad.

Sin uno de esos dos elementos, el trabajo puede aspirar a paper de benchmark o
workshop/congreso, pero no a Q1 fuerte.

## 2026-06-19 — Fase 5j: restriccion mecanistica topografica

### Objetivo

Introducir una restriccion mecanistica verificable que no sea otro baseline
predictivo. Sensorium 2022 static incluye `cell_motor_coordinates`, `area` y
`layer`, por lo que permite comprobar si la similitud de tuning neuronal sigue
la organizacion topografica cortical.

### Metodo

Se implemento
`mousebrainbench/benchmarks/sensorium_topographic_constraint.py`.

Para cada raton static con tier `test` repetido:

1. se agregan respuestas por `frame_image_id`;
2. se calcula el tuning neuronal por estimulo;
3. se muestrean pares de neuronas con semilla fija;
4. se calcula Spearman entre similitud de tuning y distancia cortical inversa;
5. se compara contra nulos por permutacion de coordenadas.

La prueba pasa solo si el efecto observado supera el percentil 95 del nulo y
un umbral minimo de efecto (`0.03`).

### Resultado

Artefacto:

```text
results/sensorium_topographic_constraint/summary_static_test.json
```

| Raton | Passed | Spearman observado | Null p95 | p permutacion |
|---|---:|---:|---:|---:|
| `static21067` | `true` | `0.2034` | `0.0089` | `0.00498` |
| `static22846` | `true` | `0.1775` | `0.0078` | `0.00498` |
| `static23343` | `true` | `0.1903` | `0.0095` | `0.00498` |
| `static23656` | `true` | `0.1285` | `0.0089` | `0.00498` |
| `static23964` | `true` | `0.1637` | `0.0096` | `0.00498` |

Resumen:

- passed: `5/5`;
- Spearman mediana: `0.17748`;
- efecto mediano sobre nulo: `0.17794`;
- decision: `structural_constraint_supported`.

### Decision

**Este es el primer componente mecanistico real del proyecto.** No es causalidad
intervencional, pero si demuestra que el target neuronal de Sensorium static
preserva una organizacion anatomica verificable. Combinado con fiabilidad
repetida y prediccion estimulo-especifica, esto convierte Sensorium static en
nuestro caso positivo mas fuerte.

La propuesta final debe pivotar hacia esta formulacion: MouseBrainBench separa
prediccion, OOD, fiabilidad y restriccion estructural. Dynamic Sensorium aporta
OOD predictivo; Sensorium static aporta fiabilidad y topografia. Aun no debe
afirmarse identificabilidad causal completa.

## 2026-06-12 — Gate 1: estructura causal del entorno

### Objetivo

Comprobar antes de entrenar agentes que `SocialSurvivalWorld` contiene una
estructura resoluble, una señal social causalmente relevante y un coste medible
del engaño.

### Configuración

- 250 episodios por política.
- Semilla base: `20260612`.
- Azar y oráculo: entorno con cambio de régimen en el paso 40.
- Seguidores sociales: régimen fijo para aislar el efecto de fiabilidad.
- Comando: `.venv/bin/python scripts/validate_environment.py`.

### Resultado

| Política | Retorno | Peligros | Tasa peligro/paso | Recursos | Pasos |
|---|---:|---:|---:|---:|---:|
| azar | -0.6234 | 0.5080 | 0.0112 | 0.5160 | 63.1400 |
| oráculo privilegiado | 14.6982 | 1.3320 | 0.0170 | 16.8280 | 79.7840 |
| seguidor útil | 14.6982 | 1.3320 | 0.0170 | 16.8280 | 79.7840 |
| seguidor engañado | -2.9876 | 3.0480 | 0.2360 | 0.2040 | 14.3600 |

### Interpretación

El entorno supera el Gate 1 mínimo:

- existe una política privilegiada claramente superior al azar;
- la señal social tiene consecuencias conductuales fuertes;
- el engaño reduce retorno, acceso a recursos y supervivencia;
- las ejecuciones son reproducibles por semilla.

El seguidor útil coincide con el oráculo en régimen fijo porque la señal apunta
directamente al recurso. Esto es útil como control positivo, pero hace que el
entorno sea insuficiente como evidencia científica única.

### Hallazgo metodológico durante la validación

La primera prueba esperaba más encuentros acumulados con peligro bajo engaño.
Falló porque el seguidor engañado muere antes y tiene menos tiempo de exposición.
Se sustituyó el conteo acumulado como contraste principal por la tasa de peligro
por paso. El fallo y la corrección se conservan porque muestran un sesgo de
supervivencia que también deberá controlarse en experimentos futuros.

### Decisión

**Gate 1 aprobado con limitaciones.** Se permite avanzar a baselines simples,
pero no a módulos cognitivos complejos. El siguiente gate debe demostrar que un
agente recurrente puede inferir cambios de régimen mejor que PPO sin memoria.

## 2026-06-12 — Gate 2a: PPO frente a RecurrentPPO en el entorno original

### Objetivo

Comprobar aprendibilidad y buscar una señal recurrente exploratoria antes de
implementar componentes cognitivos.

### Configuración

- PPO: 11 142 parámetros entrenables.
- RecurrentPPO: 30 214 parámetros entrenables.
- 30 000 transiciones por algoritmo y semilla.
- Semillas: 11, 23 y 37.
- 100 episodios de evaluación compartidos por modelo.

### Resultado resumido

| Algoritmo | Semilla | Retorno | Supervivencia | Recursos | Movimiento | Entropía acciones |
|---|---:|---:|---:|---:|---:|---:|
| PPO | 11 | -0.3110 | 0.30 | 0.40 | 0.2205 | 0.7911 |
| PPO | 23 | -0.6144 | 0.02 | 0.06 | 0.2413 | 0.7282 |
| PPO | 37 | -0.6700 | 0.00 | 0.00 | 0.0285 | 0.6926 |
| RecurrentPPO | 11 | -0.6612 | 0.00 | 0.08 | 0.0513 | 0.0000 |
| RecurrentPPO | 23 | -0.6257 | 0.00 | 0.07 | 0.0375 | 0.0000 |
| RecurrentPPO | 37 | -0.6612 | 0.00 | 0.08 | 0.0889 | 0.1067 |

### Interpretación

**Gate 2a rechazado.** Ningún algoritmo aprende de manera estable. RecurrentPPO
colapsa prácticamente a una sola acción y PPO también muestra políticas de baja
movilidad que evitan amenazas, pero no encuentran recursos.

El problema no se resuelve entrenando más. En el régimen engañoso, la única señal
global apunta a la amenaza y no existe una fuente alternativa que informe dónde
está el recurso. Ignorar la señal obliga a una búsqueda casi ciega. El entorno
confunde necesidad de memoria con ausencia de información.

### Decisión

Se congela `SocialSurvivalWorld` como ejemplo negativo. Se diseñará un entorno
separado con dos fuentes observables, una útil y otra engañosa, cuya identidad
oculta cambia. No se permite implementar workspace mientras el nuevo entorno no
supere Gate 1 y Gate 2.

## 2026-06-12 — Gate 2b: dos consejeros observables en rejilla

### Cambio realizado

`SocialInferenceWorld` presenta simultáneamente dos direcciones: una conduce al
recurso y otra a la amenaza. La identidad del consejero útil es oculta y cambia.
El oráculo alcanza retorno `14.6982`; elegir consejero al azar obtiene `-0.5393`.

### Resultado de aprendizaje

Con el mismo protocolo de 30 000 transiciones y tres semillas, ningún PPO ni
RecurrentPPO aprende una política estable. Los retornos están entre `-0.6257` y
`-0.6700`, salvo variaciones menores; la supervivencia es esencialmente cero y
el seguimiento del consejero útil también.

### Decisión

**Gate 2b rechazado.** La tarea todavía confunde inferencia de fuente,
navegación, recompensa dispersa y homeostasis. No se aumentará retrospectivamente
el presupuesto. Se aislará primero la hipótesis de memoria en una tarea mínima
de cambio de consejero.

## 2026-06-12 — Gate 2c: diagnóstico aislado de memoria

### Diseño

`AdvisorSwitchTask` elimina navegación, metabolismo y recompensa dispersa. El
agente elige uno de dos consejeros. Solo observa el resultado anterior; para
aplicar una estrategia `win-stay/lose-shift` debe recordar también su acción
anterior. La identidad útil cambia antes de puntuar la acción del paso 20.

El criterio fijado antes de ejecutar fue que RecurrentPPO superase `0.80` de
precisión post-cambio en las tres semillas.

### Resultados

| Algoritmo | Semilla | Retorno | Precisión pre | Precisión post | Primeros 5 post |
|---|---:|---:|---:|---:|---:|
| PPO | 11 | -1.80 | 0.7395 | 0.2405 | 0.2020 |
| PPO | 23 | -1.80 | 0.7395 | 0.2405 | 0.2020 |
| PPO | 37 | -2.20 | 0.7342 | 0.2357 | 0.1980 |
| RecurrentPPO | 11 | 29.09 | 0.8692 | 0.8586 | 0.5050 |
| RecurrentPPO | 23 | 22.89 | 0.8421 | 0.7355 | 0.4950 |
| RecurrentPPO | 37 | 25.11 | 0.6613 | 0.9519 | 0.7980 |

La media post-cambio es aproximadamente `0.239` para PPO y `0.849` para
RecurrentPPO. La precisión máxima posible en los primeros cinco pasos post-cambio
es `0.80`, porque la primera elección ocurre antes de disponer de evidencia del
cambio.

### Decisión

**Gate 2c rechazado según el umbral preregistrado:** RecurrentPPO supera `0.80`
en dos de tres semillas, no en las tres.

Existe una señal clara de que el estado recurrente permite resolver la tarea,
pero la optimización no es suficientemente estable para usarla como baseline
científico. No se implementará workspace todavía.

El siguiente paso permitido es desarrollar una configuración recurrente estable
usando semillas distintas de 11, 23 y 37. Después se congelará la configuración
y se realizará una confirmación única con semillas nuevas.

## 2026-06-12 — Gate 2d: estabilización y confirmación independiente

### Desarrollo

Se evaluaron cuatro configuraciones con semillas 41, 43 y 47. La selección se
realizó por la peor precisión post-cambio:

| Configuración | Peor precisión post | Media post | Parámetros |
|---|---:|---:|---:|
| `shared_default` | 0.7119 | 0.8172 | 25 667 |
| `shared_low_lr` | 0.5912 | 0.6659 | 25 667 |
| `shared_long_rollout` | 0.4950 | 0.8237 | 25 667 |
| `separate_actor_critic` | 0.4243 | 0.7608 | 42 819 |

`shared_default` fue congelada antes de abrir las semillas confirmatorias. El
rollout largo tenía mejor media, pero colapsó en una semilla y fue descartado
por el criterio robusto preregistrado.

### Confirmación única

El criterio exigía superar `0.80` en las cinco semillas:

| Semilla | Precisión post | Supera 0.80 |
|---:|---:|---:|
| 101 | 0.4810 | no |
| 103 | 0.6926 | no |
| 107 | 0.8110 | sí |
| 109 | 1.0000 | sí |
| 113 | 0.5050 | no |

### Decisión

**Gate 2d rechazado.** RecurrentPPO no es un baseline estable para esta tarea
bajo el protocolo fijado. No habrá más ajuste sobre estas semillas ni se usará
su mejor ejecución como evidencia.

Para separar validez de tarea y fallo de optimización, se evalúa a continuación
un controlador determinista de memoria mínima `win-stay/lose-shift`.

## 2026-06-12 — Gate 2e: control de validez con memoria mínima

### Resultados

| Referencia | Retorno | Precisión pre | Precisión post | Primeros 5 post |
|---|---:|---:|---:|---:|
| azar | -0.3920 | 0.4943 | 0.4958 | 0.4856 |
| siempre consejero 0 | 0.0320 | 0.4920 | 0.5080 | 0.5080 |
| `win-stay/lose-shift` | 36.9240 | 0.9717 | 0.9524 | 0.8000 |

### Interpretación y decisión

La tarea diagnóstica es válida y puede resolverse casi óptimamente con memoria
funcional mínima. El fallo confirmatorio corresponde a la optimización de
RecurrentPPO, no a una tarea irresoluble.

No se continuará ajustando RecurrentPPO. El siguiente experimento deberá añadir
explícitamente la acción anterior a la observación de PPO, convirtiendo la tarea
en Markov. Esto permitirá contrastar:

- PPO reactivo sin estado suficiente;
- PPO reactivo con estado mínimo explícito;
- controlador determinista con un bit funcional de memoria;
- RecurrentPPO que debe aprender internamente ese estado.

Este control es obligatorio antes de diseñar workspace: el benchmark actual solo
requiere recordar una acción, no coordinación cognitiva global.

## 2026-06-13 — Gate 2f: PPO con estado mínimo explícito

### Diseño

`MarkovAdvisorSwitchTask` añade únicamente la acción anterior a la observación.
Se mantuvieron PPO, dinámica, presupuesto de 30 000 transiciones y evaluación de
200 episodios. El criterio exigía precisión post-cambio superior a `0.90` en las
cinco semillas selladas.

### Resultados

| Semilla | Retorno | Precisión pre | Precisión post | Supera 0.90 |
|---:|---:|---:|---:|---:|
| 127 | 18.00 | 0.7342 | 0.7167 | no |
| 131 | 18.00 | 0.7342 | 0.7167 | no |
| 137 | 18.00 | 0.7395 | 0.7119 | no |
| 139 | 18.00 | 0.7342 | 0.7167 | no |
| 149 | 37.01 | 0.9739 | 0.9524 | sí |

### Auditoría de la política

Las semillas 127, 131 y 139 aprenden tres transiciones correctas, pero cambian
erróneamente a la acción 0 después de obtener recompensa positiva con la acción
1. La semilla 137 presenta el fallo simétrico para la acción 0. La semilla 149
aprende las cuatro transiciones `win-stay/lose-shift`.

### Decisión

**Gate 2f rechazado.** Exponer el estado mínimo eleva fuertemente el rendimiento,
pero PPO continúa siendo inestable por ruptura de simetría y exploración
insuficiente de uno de los estados positivos.

Según el roadmap, se pausa el desarrollo arquitectónico. El siguiente paso no
es ajustar PPO ni construir workspace: se auditará el stack mediante un baseline
tabular exacto sobre el mismo MDP.

## 2026-06-15 — MouseBrainBench Fase 2c: confirmación funcional externa

### Diseño

Las 21 sesiones locales de desarrollo se usaron para seleccionar una única
transformación temporal. `temporal_derivative` quedó sellada antes de descargar
una cohorte confirmatoria de 20 sesiones pertenecientes a 20 ratones nuevos,
equilibrada entre Familiar y Novel.

### Confirmación única

| Métrica | Resultado | Umbral | Pasa |
|---|---:|---:|---|
| Correlación mediana entre ratones | 0.8908 | > 0.50 | sí |
| Split-half mediano | 0.9896 | > 0.70 | sí |
| Sesiones sobre nulo individual 95% | 75% | >= 50% | sí |
| Límite inferior bootstrap agrupado | 0.8417 | > 0 | sí |

Se procesaron las 20 sesiones sin fallos. El intervalo bootstrap agrupado fue
`[0.8417, 0.9214]`. El análisis se ejecutó una vez desde el commit `3b07ce3`.

### Decisión

**Target confirmado.** Puede utilizarse como variable funcional fuera de muestra
para evaluar modelos mesoscópicos. El resultado no valida un mecanismo,
conectividad efectiva ni un gemelo digital.

La siguiente puerta comprobará si conectividad Allen MCModels predice el target
mejor que topologías nulas emparejadas, calibrando únicamente sobre la cohorte de
desarrollo.

## 2026-06-15 — MouseBrainBench Fase 3: benchmark anatómico-funcional

### Diseño

Se construyó una matriz dirigida de seis áreas visuales a partir de 200
experimentos oficiales de trazado Allen. `LinearRateModel` y `WilsonCowanModel`
se calibraron sobre 21 sesiones de desarrollo. El modelo lineal fue seleccionado
y comparado contra un grafo desconectado, el grafo transpuesto y cien
permutaciones de pesos, todas recalibradas en desarrollo.

### Desarrollo

Allen obtuvo correlación mediana `0.5836`, pero solo superó el 27% de
permutaciones. El desconectado obtuvo `0.5731` y el transpuesto `0.5875`. La
configuración completa se selló en el commit `673e5cc`.

### Confirmación única

| Topología | Correlación mediana |
|---|---:|
| Allen | 0.5281 |
| Desconectada | 0.5246 |
| Transpuesta | 0.5313 |
| Mediana de permutaciones | 0.5335 |

Allen superó solo el 21% de permutaciones. La ventaja pareada frente a la
mediana de permutaciones fue negativa, con IC95%
`[-0.0075, -0.0012]`.

### Decisión

**Hipótesis anatómica rechazada bajo el protocolo.** La dinámica lineal captura
parte de la respuesta temporal, pero la topología Allen no explica ese
rendimiento. No se añadirá complejidad al mismo target para rescatar la
hipótesis.

La siguiente puerta deberá demostrar primero que existe una firma funcional
reproducible de propagación dirigida.

## 2026-06-16 — MouseBrainBench Fase 4: identificabilidad dirigida

### Diseño

Se analizaron únicamente las 21 sesiones de desarrollo. Se midieron latencias
regionales y signos lead-lag con bins de `50 ms`, comparando split-half,
leave-one-mouse-out, permutaciones de etiquetas regionales y pseudo-eventos
desplazados `+10 s`.

### Resultados

| Criterio | Resultado | Decisión |
|---|---:|---|
| Latencia cross-mouse tau | 0.0000 | falla |
| Latencia split-half tau | 0.0000 | falla |
| Latencias sobre nulo 95% | 0% | falla |
| Pares con latencia resoluble | 0.0000 | falla |
| Lead-lag cross-mouse | 1.0000 | pasa |
| Lead-lag split-half | 1.0000 | pasa |
| Lead-lag sobre nulo 95% | 0% | falla |
| Pares lead-lag no simultáneos | 0.0000 | falla |

### Decisión

**Firma dirigida no soportada.** La respuesta confirmada en Fase 2c es
reproducible, pero no identifica propagación dirigida a esta resolución. No se
debe construir un modelo anatómico más complejo sobre este target.

## 2026-06-19 — Dynamic Sensorium: baseline neuronal local

### Diseño

Se añadió `torch_residual_mlp`, una red PyTorch compacta que predice residuos
neuronales sobre la media de entrenamiento usando las mismas features
`temporal_filterbank` que los baselines transparentes. La selección de
hiperparámetros se hace dentro del conjunto `train` mediante una partición
interna 80/20. No utiliza respuestas de test para ajustar arquitectura, peso de
decaimiento ni mezcla residual.

Este baseline es deliberadamente modesto y reproducible. No es el modelo oficial
del starter kit Sensorium ni una comparación SOTA; su función es cerrar el
control metodológico mínimo de red neuronal no lineal dentro de MouseBrainBench.

### Resultados

| Cohorte | MLP > mean | MLP > SVD | Mediana MLP - mean | Mediana MLP - SVD |
|---|---:|---:|---:|---:|
| Dynamic Sensorium 2023 `oracle` | 5/5 | 3/5 | 0.04286 | 0.00386 |
| Dynamic Sensorium legacy OOD | 4/5 | 3/5 | 0.03607 | 0.00219 |

En la cohorte `oracle`, el MLP es el mejor modelo en 2/5 ratones. En legacy OOD,
es el mejor en 3/5 ratones. El resultado es positivo pero pequeño: el MLP mejora
claramente a la media, compite con SVD y no domina de forma universal.

### Decisión

El hueco de "baseline neuronal real" queda cubierto a nivel local y
reproducible. La conclusión científica sigue siendo conservadora: MouseBrainBench
puede comparar predicción, generalización OOD, modelos transparentes y modelos
neuronales no lineales sin convertir una mejora de correlación en un claim
mecanicista.

Para un Q1 fuerte todavía falta una de dos piezas: reproducir un baseline
externo oficial del ecosistema Sensorium o añadir una restricción causal /
intervencional verificable. No se recomienda seguir iterando con ajustes menores
del MLP como vía principal.

## 2026-06-25 — MICRONS estratificado y auditoría de claims

### Diseño

Se ejecutó `scripts/run_microns_stratified_structure_function.py` sobre el
piloto expandido CAVE:

- `1000` unidades co-registradas función/EM;
- `2267` sinapsis cargadas;
- `2095` pares dirigidos conectados únicos;
- `999000` pares candidatos no-self;
- `1000` permutaciones;
- `min_connected_pairs = 50`;
- `174` pruebas estrato × métrica;
- FDR Benjamini-Hochberg sobre los p-valores emparejados.

Los estratos predefinidos incluyen tipo celular coarse/fine, cuadrante de
readout, terciles de distancia anatómica y fiabilidad alta por `cc_norm`. Las
métricas funcionales separan perfil de respuesta, orientación, dirección,
`cc_norm`, ubicación de readout y agregado funcional.

### Resultados

| Resultado | Valor |
|---|---:|
| Pruebas confirmadas tras FDR | `28` |
| Señal dominante | `readout_location` |
| Global aggregate MICRONS | negativo tras distancia |
| Estratificado MICRONS | positivo tras distancia/grado/FDR |
| `q1_ready` | `False` |
| `q1_candidate_evidence_requires_replication` | `True` |

La señal más robusta indica que pares conectados sinápticamente tienden a tener
ubicaciones funcionales de readout más cercanas que nulls emparejados por
distancia anatómica y grado. También aparecen señales exploratorias en algunos
estratos de orientación/perfil funcional, pero no deben convertirse todavía en
claim principal.

### Decisión

MouseBrainBench pasa de "sin pieza empírica positiva Q1" a "pieza candidata que
requiere replicación". La evidencia actual no permite afirmar mecanismo causal,
whole-brain digital twin ni comportamiento. La siguiente puerta Q1 debe replicar
la señal MICRONS estratificada en un subconjunto CAVE mayor o hold-out.

Se añadió además `mousebrainbench.benchmarks.digital_twin_claim_audit` para
bloquear formalmente claims tipo MouseDTB cuando solo hay correlación,
predicción o señal estructura-función local.

## 2026-06-25 — MICRONS hold-out estratificado

### Diseño

Se extendió `scripts/query_microns_expanded_pilot.py` con `--offset-units` para
crear un subconjunto hold-out sin sobrescribir el piloto original. Se consultó
CAVE con:

- `limit_query_rows = 2400`;
- `offset_units = 1000`;
- `limit_units = 1000`;
- `materialization_version = 1507`;
- tabla `digital_twin_properties_bcm_coreg_v4`.

El hold-out resultante contiene `992` unidades, `2161` sinapsis y `1926` pares
dirigidos conectados únicos. Se ejecutó la misma estratificación con `1000`
permutaciones y `min_connected_pairs = 50`.

### Resultados

| Resultado | Valor |
|---|---:|
| Pruebas confirmadas tras FDR | `30` |
| Señal dominante | `readout_location` |
| `all_pairs/readout_location` distance delta | `0.021034` |
| `all_pairs/readout_location` distance q | `0.007036` |
| `all_pairs/readout_location` degree delta | `0.038002` |
| `all_pairs/readout_location` degree q | `0.006225` |

### Decisión

La señal principal replica en hold-out. MouseBrainBench ya tiene una pieza
empírica positiva candidata para Q1, siempre que el manuscrito la formule como
benchmark estructura-función local con controles, no como causalidad, whole-brain
digital twin ni modelo SOTA Sensorium.

## 2026-06-26 — Paquete Q1 MICRONS con bootstrap por unidades

### Diseño

Se ejecutó `scripts/build_microns_q1_package.py` para generar tablas definitivas
de manuscrito y estabilidad bootstrap agrupada por unidades. El endpoint primario
se fija como:

```text
all_pairs / readout_location
```

El bootstrap remuestrea unidades, no pares individuales, para evitar inflar la
precisión por dependencia entre pares dirigidos.

### Resultados

| Cohorte | Distance delta CI95 | Degree delta CI95 |
|---|---:|---:|
| Discovery | `[0.0166454, 0.0262839]` | `[0.0348647, 0.0454170]` |
| Hold-out offset1000 | `[0.0142179, 0.0262773]` | `[0.0321422, 0.0430936]` |

### Decisión

El paquete Q1 queda técnicamente listo como resultado estructura-función local
replicado. La fase siguiente es escritura/figuras/revisión de literatura, no
búsqueda exploratoria de señal. Se mantienen bloqueados los claims de mecanismo
causal, cerebro completo, comportamiento y SOTA Sensorium.
