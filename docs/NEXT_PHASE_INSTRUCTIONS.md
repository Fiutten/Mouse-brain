# Siguiente fase: comprobar identificabilidad de propagación dirigida

## Punto de partida

La Fase 3 rechazó que la topología anatómica Allen aporte valor predictivo
específico para `temporal_derivative`. La correlación moderada del modelo se
conserva con grafos desconectados, transpuestos y permutados.

## Fase 4 propuesta

1. Trabajar solo con la cohorte de desarrollo.
2. Medir latencias regionales y estructura lead-lag por sesión.
3. Evaluar fiabilidad split-half y entre ratones.
4. Comparar contra eventos desplazados y etiquetas regionales permutadas.
5. Determinar antes de modelar si existe una señal reproducible que una
   topología dirigida pueda explicar.
6. Solo si existe, sellar el target y obtener una tercera cohorte independiente.

## Pregunta falsable

> ¿Contiene Allen VBN una firma regional reproducible de propagación dirigida
> que pueda distinguir una topología anatómica de controles nulos?

Esta puerta evita añadir capas dinámicas a un target que quizá sea incapaz de
identificar topología por construcción.

## Métricas necesarias

- fiabilidad de latencias y lead-lag;
- separación frente a controles nulos;
- estabilidad por experiencia y ratón;
- cobertura temporal suficiente respecto al bin de 50 ms.

## Criterio de parada

Si no existe una firma dirigida fiable, se detendrá esta línea con Allen VBN y
se buscará un recurso funcional con resolución temporal o diseño perturbacional
adecuado. No se construirá un modelo más complejo sobre un target no
identificable.
