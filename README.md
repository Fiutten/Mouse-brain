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
pytest
```

Los resultados se guardan bajo `outputs/<run_id>/`. Consulta
[SCIENTIFIC_SCOPE.md](docs/SCIENTIFIC_SCOPE.md) antes de interpretar cualquier
resultado.

## Lo que no demuestra

Una simulación sintética que funciona no valida un modelo neurocientífico. Los
parámetros de la Fase 1 son arbitrarios y sirven para probar ingeniería,
estabilidad numérica y reproducibilidad. La validación científica empieza al
integrar conectividad y actividad de referencia reales.
