# MouseBrainBench-core

**MouseBrainBench is not a full digital mouse brain.**

It is a reproducible framework for building, running, and evaluating simplified
mouse-brain models across scales. It focuses on integration, benchmarking, and
validation of models constrained by public anatomical and functional resources.

**MouseBrainBench no es una emulación completa del cerebro de un ratón.**

Es una plataforma reproducible para construir y evaluar modelos simplificados
del cerebro de ratón. La primera versión valida la infraestructura mediante
conectividad sintética explícitamente no biológica. Todavía no integra Allen
MCModels, BMTK/SONATA, The Virtual Brain ni MICrONS.

La Fase 2 añade un extractor real para Allen Visual Behavior Neuropixels y un
benchmark de fiabilidad regional. Su primera puerta científica fue rechazada:
el target de FC espontánea es moderadamente reproducible, pero no supera el
criterio nulo fijado en suficientes sesiones. No se usa todavía para validar
simuladores.

La Fase 2b descompone esa variabilidad y evalúa perfiles espontáneos y evocados.
Ninguno de los tres targets candidatos supera la puerta fijada. El proyecto
conserva estos resultados negativos y no ajustará simuladores contra ellos como
métrica primaria.

La Fase 2c confirma externamente una representación temporal evocada en 20
ratones nuevos. El resultado permite iniciar un benchmark anatómico-funcional,
pero no valida todavía ningún modelo ni constituye un gemelo digital.

La Fase 3 demuestra que un modelo lineal simple predice moderadamente esa
representación, pero rechaza que la topología regional Allen aporte valor
específico frente a grafos desconectados, transpuestos y permutados
recalibrados. El resultado negativo se conserva como decisión científica.

La Fase 4 comprueba identificabilidad dirigida y vuelve a cerrar la puerta
anatómico-dinámica para este target: la señal confirmada es reproducible, pero
no contiene latencias o lead-lag no triviales suficientes con bins de `50 ms`.

La línea Allen VBN queda cerrada como caso metodológico en
[ALLEN_VBN_CLOSURE.md](docs/ALLEN_VBN_CLOSURE.md). El paquete publicable actual
está resumido en [PUBLICATION_PACKAGE.md](docs/PUBLICATION_PACKAGE.md).
La estrategia Q1 actual formaliza el
[Mechanistic Identifiability Score](docs/MECHANISTIC_IDENTIFIABILITY_SCORE.md)
y prioriza Sensorium/Dynamic Sensorium como siguiente caso real en
[Q1_TECHNICAL_STRATEGY.md](docs/Q1_TECHNICAL_STRATEGY.md).

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
mousebrainbench-run configs/default.yaml
mousebrainbench-allen-benchmark configs/allen_vbn_phase2.yaml
mousebrainbench-allen-phase2b configs/allen_vbn_phase2b.yaml
mousebrainbench-allen-phase2c develop configs/allen_vbn_phase2c.yaml
mousebrainbench-allen-phase2c confirm configs/allen_vbn_phase2c.yaml
mousebrainbench-allen-phase3 develop configs/allen_visual_phase3.yaml
mousebrainbench-allen-mis
mousebrainbench-synthetic-mis
pytest
```

Los resultados se guardan bajo `outputs/<run_id>/`. Consulta
[SCIENTIFIC_SCOPE.md](docs/SCIENTIFIC_SCOPE.md) antes de interpretar cualquier
resultado.

Consulta [PHASE2_ACCEPTANCE.md](docs/PHASE2_ACCEPTANCE.md) para el resultado
empírico y la decisión de continuidad.

## Lo que no demuestra

Una simulación sintética que funciona no valida un modelo neurocientífico. Los
parámetros de la Fase 1 son arbitrarios y sirven para probar ingeniería,
estabilidad numérica y reproducibilidad. La validación científica empieza al
integrar conectividad y actividad de referencia reales.
