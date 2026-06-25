# MouseBrainBench frente a MouseDTB

## Decisión

MouseBrainBench no debe competir como otro intento de construir un cerebro
digital completo de ratón. Esa dirección queda debilitada por trabajos tipo
MouseDTB, que ya formulan modelos whole-brain a escala de neurona individual,
aunque su conectividad sea inferida y su validación dependa de BOLD/data
assimilation.

La posición defendible es distinta:

```text
MouseBrainBench audita claims de modelos digitales parciales del cerebro de
ratón separando predicción, reproducibilidad, plausibilidad estructural,
coste e identificabilidad mecanística.
```

## Qué nos pisa MouseDTB

- El framing de "mouse digital twin brain".
- La narrativa whole-brain.
- La simulación spiking LIF a gran escala.
- La validación BOLD resting/task.
- Lesiones y rewiring como pruebas internas.

## Qué no nos pisa

- Un benchmark reproducible y ligero para comparar claims.
- Una auditoría formal de si una correlación BOLD/predicción justifica mecanismo.
- La separación explícita entre predicción y mecanismo mediante MIS.
- La evaluación con controles espaciales, grado, FDR y coste computacional.
- Un caso MICRONS local con synapses CAVE reales y función co-registrada.

## Implicación técnica

MouseBrainBench debe mantener bloqueadas estas frases:

- "complete mouse-brain digital twin";
- "measured whole-brain single-neuron connectome";
- "causal mechanistic model";
- "SOTA Sensorium predictor".

Y puede usar estas frases si los artefactos actuales se mantienen:

- "reproducible benchmark for auditing mouse-brain digital-model claims";
- "methodological framework separating prediction from mechanistic evidence";
- "MICRONS local structure-function pilot with distance/degree/FDR controls";
- "Sensorium/Dynamic Sensorium predictive cases without SOTA claim".

## Estado tras la estratificación MICRONS

La estratificación expandida encuentra señal positiva tras controles de
distancia, grado y FDR, dominada por similitud de `readout_location`.

Interpretación estricta:

- positivo: pares conectados localmente tienden a tener ubicaciones funcionales
  de readout más cercanas que nulls emparejados;
- no probado: causalidad, mecanismo completo, comportamiento, whole-brain twin;
- requisito Q1: replicar en un subconjunto CAVE mayor o hold-out antes de tratar
  esta señal como eje principal de un paper Q1.
