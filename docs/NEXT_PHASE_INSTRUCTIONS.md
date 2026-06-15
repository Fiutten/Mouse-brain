# Siguiente fase: benchmark anatómico-funcional fuera de muestra

## Punto de partida

La Fase 2c confirmó externamente `temporal_derivative` como target funcional
evocado reproducible. Esto permite evaluar modelos, pero no valida todavía
ninguna dinámica ni conectividad.

## Fase 3 propuesta

1. Integrar una matriz región-región procedente de Allen MCModels/CCF para las
   seis regiones visuales, conservando procedencia y orientación.
2. Construir controles emparejados: grafo desconectado y grafos permutados que
   conserven densidad y distribución de pesos.
3. Calibrar solo un conjunto pequeño y declarado de parámetros dinámicos usando
   las 21 sesiones de desarrollo.
4. Congelar parámetros, modelos, métricas y umbrales.
5. Evaluar una sola vez sobre las 20 sesiones confirmatorias ya selladas.
6. Comparar capacidad predictiva, robustez a perturbaciones y coste.

## Pregunta falsable

> ¿La conectividad anatómica Allen mejora la predicción fuera de muestra de la
> dinámica temporal regional frente a topologías nulas emparejadas?

La contribución potencial no es que un modelo produzca actividad parecida, sino
determinar si la restricción anatómica aporta información predictiva medible.

## Modelos permitidos inicialmente

- `LinearRateModel`, como baseline interpretable.
- `WilsonCowanModel`, como dinámica no lineal mesoscópica.
- Ningún modelo profundo hasta resolver esta puerta.

Ambos deben usar idéntico protocolo de calibración y presupuesto. No se
seleccionará retrospectivamente el modelo con mejor resultado como evidencia
única.

## Métricas primarias

- correlación con el target temporal por sesión;
- mejora frente a grafos permutados emparejados;
- generalización desarrollo-confirmación;
- sensibilidad a lesiones regionales predefinidas;
- coste computacional.

## Criterio de parada

Si Allen MCModels no mejora de forma robusta frente a controles topológicos, se
rechazará que esa conectividad mesoscópica aporte capacidad predictiva para este
target y escala. No se añadirá complejidad neuronal para rescatar el resultado.
