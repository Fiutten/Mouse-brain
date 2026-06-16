# Protocolo de Fase 4: identificabilidad de propagación dirigida

## Pregunta

¿Contiene Allen Visual Behavior Neuropixels una firma regional reproducible de
propagación dirigida capaz de distinguir identidades regionales y eventos
reales de controles nulos?

Esta fase no ajusta ni evalúa modelos. Trabaja exclusivamente con las 21
sesiones de desarrollo y decide si existe un target adecuado para una futura
prueba anatómica.

## Resolución y ventana

- Respuesta peri-evento: `[-250, +750] ms`.
- Bin temporal: `50 ms`.
- Ventana de firma dirigida: `[0, +525] ms`.
- Lags evaluados: de `-150` a `+150 ms`.

Una diferencia de latencia solo se considera resoluble si abarca al menos un
bin completo (`50 ms`). Esta resolución permite estudiar orden temporal
mesoscópico grueso, no velocidades de conducción ni retardos sinápticos.

## Firmas

### Orden de latencias

Para cada región se toma el bin postevento de máximo incremento respecto al
baseline. La firma es el orden regional de esas latencias. Se evalúa con
Kendall tau, que admite empates.

### Lead-lag

Para cada pareja regional se calcula el lag entero que maximiza la correlación
cruzada dentro de la ventana postevento. La firma usa el signo del lag:
anterior, simultáneo o posterior. Se evalúa por acuerdo exacto entre pares.

## Fiabilidad

- `split-half`: comparación odd/even dentro de sesión;
- `cross-mouse`: comparación con la media leave-one-mouse-out;
- control de identidad: mil permutaciones de etiquetas regionales;
- control temporal: los mismos eventos desplazados exactamente `+10 s`.

El control desplazado conserva el contexto de grabación, pero rompe el anclaje
al cambio visual. No se interpreta como baseline espontáneo puro.

## Puerta de identificabilidad

La firma pasa solo si cumple simultáneamente:

- Kendall tau split-half mediano de latencias `> 0.50`;
- Kendall tau cross-mouse mediano de latencias `> 0.30`;
- al menos 50% de sesiones sobre su nulo individual de latencias;
- acuerdo split-half lead-lag mediano `> 0.70`;
- acuerdo cross-mouse lead-lag mediano `> 0.65`;
- al menos 50% de sesiones sobre su nulo individual lead-lag;
- ventaja lead-lag real frente a eventos desplazados `> 0.10`;
- al menos 50% de pares regionales con latencias separadas por `>= 50 ms`.
- al menos 25% de pares lead-lag no simultáneos.

Si falla cualquier criterio, no se confirmará ni se desarrollarán nuevos
modelos sobre este target. El resultado indicará qué propiedad concreta falta.
