# Roadmap experimental finito

Este documento limita explícitamente la secuencia experimental. No se crearán
gates adicionales para rescatar retrospectivamente una hipótesis rechazada.

## Antes del workspace

1. **Gate 2f — Estado mínimo explícito: RECHAZADO.** PPO mejora, pero solo una
   de cinco semillas alcanza el umbral.
2. **Gate 2g — Transferencia de regla mínima.** Evaluar sin reentrenar cambios en
   horizonte, momento y número de switches.
3. **Gate 2h — Tarea rica escalonada.** Reintroducir primero navegación y después
   homeostasis, manteniendo controles de estado explícito.

Solo se permite avanzar si cada gate supera su criterio fijado previamente.

## Experimentos causales del workspace

4. **Gate 3a — Comparación emparejada.** Workspace frente a concatenación,
   recurrencia y módulos aislados con información y parámetros comparables.
5. **Gate 3b — Intervenciones.** Lesión, retraso, corrupción y capacidad del
   broadcast con predicciones previas.
6. **Gate 4 — Generalización externa.** Repetir la ventaja en otra familia de
   tareas no diseñada alrededor del workspace.

## Reglas de parada

- Si Gate 2f falla, se pausa el desarrollo arquitectónico y se revisa el stack
  de aprendizaje.
- Si Gate 2g falla, la política se considera memorización específica.
- Si Gate 2h falla, no existe justificación para construir workspace.
- Si Gate 3a o 3b falla, se rechaza la contribución de workspace.
- Si Gate 4 falla, el resultado se considera específico del benchmark y no una
  contribución general.

Máximo restante desde 2026-06-13: **seis gates decisivos**.

Estado actual: el desarrollo arquitectónico está pausado. Antes de reactivar los
cinco gates restantes se realizará una auditoría metodológica tabular, que no se
considera un nuevo gate de publicación.
