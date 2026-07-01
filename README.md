# MouseBrainBench-core

**MouseBrainBench is not a full digital mouse brain.**

It is a reproducible, claim-aware framework for building, running, and evaluating
simplified mouse-brain model targets across scales. It focuses on integration,
benchmarking, evidence separation, and validation of claims constrained by public
anatomical, functional, predictive, and connectomic resources.

**MouseBrainBench no es una emulación completa del cerebro de un ratón.**

Es una plataforma reproducible para construir y evaluar modelos simplificados y
representaciones parciales del cerebro de ratón. La versión actual separa de
forma explícita reproducibilidad, predicción, especificidad topológica,
identificabilidad dirigida, asociación estructura-función y coste computacional.
No debe interpretarse como un gemelo digital completo, ni como un simulador
whole-brain, ni como una validación causal de mecanismos neuronales.

## Estado científico actual

La Fase 1 valida infraestructura mediante conectividad sintética explícitamente
no biológica. Estos experimentos prueban estabilidad numérica, reproducibilidad y
semántica del Mechanistic Identifiability Score (MIS), pero no validan un modelo
neurocientífico real.

La Fase 2 añade un extractor real para Allen Visual Behavior Neuropixels y un
benchmark de fiabilidad regional. Su primera puerta científica fue rechazada: el
target de FC espontánea es moderadamente reproducible, pero no supera el criterio
nulo fijado en suficientes sesiones. No se usa para validar simuladores.

La Fase 2b descompone esa variabilidad y evalúa perfiles espontáneos y evocados.
Ninguno de los tres targets candidatos supera la puerta fijada. El proyecto
conserva estos resultados negativos y no ajusta simuladores contra ellos como
métrica primaria.

La Fase 2c confirma externamente una representación temporal evocada en 20
ratones nuevos. El resultado permite iniciar un benchmark anatómico-funcional,
pero no valida todavía ningún modelo ni constituye un gemelo digital.

La Fase 3 demuestra que un modelo lineal simple predice moderadamente esa
representación, pero rechaza que la topología regional Allen aporte valor
específico frente a grafos desconectados, transpuestos y permutados
recalibrados. El resultado negativo se conserva como decisión científica.

La Fase 4 comprueba identificabilidad dirigida y vuelve a cerrar la puerta
anatómico-dinámica para este target: la señal confirmada es reproducible, pero no
contiene latencias o lead-lag no triviales suficientes con bins de `50 ms`.

La Fase 5 introduce adaptadores y comparadores Sensorium/Dynamic Sensorium. Estos
resultados se interpretan como evidencia predictiva y de interoperabilidad, no
como evidencia mecanística ni como un resultado SOTA. El baseline oficial
acotado se mantiene como control interno hasta reproducir una configuración o
checkpoint comparable a los protocolos publicados.

La línea MICRONS introduce un piloto estructura-función local con CAVE y
`digital_twin_properties_bcm_coreg_v4`. El análisis agregado inicial es negativo
o inconcluso bajo control por distancia. El resultado publicable actual es más
estrecho: un endpoint `all_pairs/readout_location`, fijado tras discovery y
confirmado en dos hold-outs no solapados, muestra una asociación local
observacional entre pares conectados y mayor similitud de readout-location frente
a controles no conectados emparejados por distancia y grado. Este resultado no
es causal, no es whole-brain y no constituye una regla biológica nueva.

La línea Allen VBN queda cerrada como caso metodológico en
[ALLEN_VBN_CLOSURE.md](docs/ALLEN_VBN_CLOSURE.md). El paquete publicable actual
está resumido en [PUBLICATION_PACKAGE.md](docs/PUBLICATION_PACKAGE.md). La
estrategia Q1 actual formaliza el
[Mechanistic Identifiability Score](docs/MECHANISTIC_IDENTIFIABILITY_SCORE.md)
y la ruta de evidencias se congela en `results/publication_freeze/summary.json`.

## Capacidades de la Fase 1

- Contratos validados para regiones, conectividad y estados simulados.
- Grafos dirigidos ponderados y normalización configurable.
- Modelos transparentes `LinearRateModel` y `WilsonCowanModel`.
- Integración Euler y RK4, ruido reproducible y estímulos regionales.
- Perturbaciones reversibles: lesión, inhibición, estimulación, aumento de ruido
  y escalado de conectividad.
- Métricas anatómicas, funcionales, perturbacionales y de coste.
- Runner YAML y artefactos reproducibles con configuración, versión y semilla.

## Instalación y uso

```bash
python -m pip install -e ".[dev]"
python -m pip install -e ".[microns]"  # solo para workflows MICRONS/CAVE
mousebrainbench-run configs/default.yaml
mousebrainbench-allen-benchmark configs/allen_vbn_phase2.yaml
mousebrainbench-allen-phase2b configs/allen_vbn_phase2b.yaml
mousebrainbench-allen-phase2c develop configs/allen_vbn_phase2c.yaml
mousebrainbench-allen-phase2c confirm configs/allen_vbn_phase2c.yaml
mousebrainbench-allen-phase3 develop configs/allen_visual_phase3.yaml
mousebrainbench-allen-phase4
mousebrainbench-allen-mis
mousebrainbench-sensorium-smoke
mousebrainbench-sensorium-mis /path/to/unzipped/sensorium_mouse --max-trials 1000
mousebrainbench-sensorium-compare
mousebrainbench-sensorium-official-audit
mousebrainbench-synthetic-mis
mousebrainbench-q1-sensitivity
mousebrainbench-publication-freeze
pytest
```

Los resultados se guardan bajo `outputs/<run_id>/` o `results/<analysis>/`, según
el benchmark. Consulta [SCIENTIFIC_SCOPE.md](docs/SCIENTIFIC_SCOPE.md) antes de
interpretar cualquier resultado.

## Reproducibilidad antes de envío

Antes de enviar un manuscrito, los artifacts deben regenerarse desde un commit
limpio y trazable. Cualquier `git_revision` terminado en `-dirty` indica que el
artefacto fue generado con cambios locales no confirmados y debe considerarse
provisional hasta ser regenerado.

Las regeneraciones por lotes deben capturar primero el SHA del commit limpio y
exportarlo mediante `MOUSEBRAINBENCH_GIT_REVISION`. El valor solo admite un
identificador hexadecimal de Git. De este modo, todos los artefactos de una
misma ejecución quedan vinculados a la misma versión de código aunque los
primeros archivos generados modifiquen posteriormente el árbol de trabajo.

## Lo que no demuestra

Una simulación sintética que funciona no valida un modelo neurocientífico. Los
parámetros de la Fase 1 son arbitrarios y sirven para probar ingeniería,
estabilidad numérica y reproducibilidad. La validación científica empieza al
integrar conectividad y actividad de referencia reales.

El resultado MICRONS actual es una asociación local observacional confirmada en
hold-outs internos del mismo recurso, no una replicación entre animales, no una
intervención causal y no una validación de un gemelo digital completo.

El repositorio no respalda afirmaciones de causalidad, equivalencia conductual,
simulación whole-brain ni un gemelo digital completo del cerebro de ratón.
