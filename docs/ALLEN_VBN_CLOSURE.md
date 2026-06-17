# Cierre científico de la línea Allen VBN

## Veredicto

La línea Allen Visual Behavior Neuropixels queda **cerrada para validación de
conectividad anatómica dirigida**. No se continuará con más modelos, más capas
neuronales ni una tercera cohorte sobre este target.

La decisión no se debe a un fallo de ingeniería. Se debe a que el target
funcional disponible no contiene información suficiente para distinguir una
topología dirigida de controles nulos.

## Evidencia acumulada

### Resultado positivo conservado

Fase 2c confirmó externamente `temporal_derivative` como respuesta temporal
evocada reproducible:

| Métrica | Resultado |
|---|---:|
| Sesiones confirmatorias válidas | 20/20 |
| Ratones confirmatorios nuevos | 20 |
| Correlación mediana entre ratones | 0.8908 |
| Split-half mediano | 0.9896 |
| Sesiones sobre nulo individual 95% | 75% |
| IC bootstrap 95% de la mediana | [0.8417, 0.9214] |

Este resultado demuestra reproducibilidad funcional dentro de Allen VBN.

### Resultado anatómico negativo

Fase 3 evaluó si una matriz dirigida de seis áreas visuales derivada de 200
experimentos Allen de trazado mejoraba la predicción frente a controles
recalibrados:

| Topología | Correlación mediana confirmatoria |
|---|---:|
| Allen | 0.5281 |
| Desconectada | 0.5246 |
| Allen transpuesta | 0.5313 |
| Mediana de 100 permutaciones | 0.5335 |

Allen superó solo el 21% de permutaciones. La ventaja pareada frente a la
mediana de permutaciones fue negativa, con IC95% `[-0.0075, -0.0012]`.

Conclusión: la capacidad predictiva moderada del modelo no procede de la
topología anatómica Allen.

### Resultado de identificabilidad negativo

Fase 4 comprobó si el target contiene latencias o lead-lag no triviales:

| Criterio | Resultado |
|---|---:|
| Kendall tau cross-mouse de latencias | 0.0000 |
| Kendall tau split-half de latencias | 0.0000 |
| Pares con latencias resolubles | 0.0000 |
| Pares lead-lag no simultáneos | 0.0000 |
| Lead-lag sobre nulo individual 95% | 0% |

Las seis regiones tienen latencia mediana `75 ms`. La respuesta está bloqueada
al evento y no ofrece una firma dirigida robusta con bins de `50 ms`.

## Qué queda permitido

Allen VBN puede usarse como:

- caso de estudio de target funcional reproducible;
- control metodológico sobre límites de inferencia mecanística;
- benchmark negativo para mostrar que reproducibilidad no implica validez
  anatómico-dinámica.

## Qué queda prohibido para esta línea

No se debe:

- descargar una tercera cohorte Allen VBN para este target;
- añadir modelos neuronales más complejos para rescatar la hipótesis;
- presentar el resultado como conectividad efectiva;
- hablar de gemelo digital del cerebro de ratón;
- afirmar que Allen VBN invalida la anatomía visual del ratón.

## Decisión de continuidad

La continuidad científica debe desplazarse a una de dos rutas:

1. **Publicación metodológica con Allen VBN como caso cerrado.**
   La contribución sería una batería reproducible de validación/falsación para
   targets funcionales en modelos digitales parciales.
2. **Nuevo recurso funcional.**
   Solo merece la pena si tiene mejor resolución temporal, perturbaciones
   explícitas o diseño causal que permita identificar dirección o mecanismo.

La ruta recomendada inmediata es preparar la contribución metodológica antes de
descargar nuevos datos.
