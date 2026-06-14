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
