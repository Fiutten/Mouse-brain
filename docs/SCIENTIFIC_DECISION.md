# Decisión científica inicial

Fecha de decisión: 2026-06-12

## Veredicto sobre el briefing

El briefing es técnicamente plausible como especificación de ingeniería, pero no
es por sí mismo una propuesta científica novedosa. Agregar PPO, memoria,
`world model`, `global workspace`, estado interno y metacognición no demuestra
que la arquitectura sea cognitivamente adecuada ni que cada módulo contribuya.

Ejecutarlo literalmente presenta cuatro problemas:

1. **Novedad insuficiente.** Ya existen arquitecturas cognitivas basadas en
   Global Workspace, agentes con memoria y modelos del mundo, y combinaciones
   explícitas de Global Workspace con RL y `world models`.
2. **Constructos sin operacionalizar.** Un objeto llamado `SelfModel` o
   `MetaCognition` no constituye evidencia de auto-modelado o metacognición.
3. **Ablaciones confundidas.** Las variantes A-E propuestas cambian
   simultáneamente arquitectura, información disponible, parámetros y
   algoritmo de aprendizaje.
4. **Entorno potencialmente tautológico.** Un entorno diseñado para premiar
   exactamente los módulos propuestos puede producir una ventaja artificial.

## Reformulación aceptada

El proyecto se reformula como un banco experimental causal:

> ¿Un canal de difusión global, limitado e intervenible, mejora la adaptación
> fuera de distribución y la coordinación entre módulos frente a controles
> emparejados, y produce firmas causales específicas cuando se lesiona?

El término `global workspace` se utilizará únicamente para una implementación
que cumpla estas propiedades:

- capacidad limitada;
- competencia explícita por acceso;
- difusión a receptores independientes;
- contenido registrable;
- posibilidad de lesión, retraso, corrupción y restricción de capacidad.

## Contribución potencial

La posible contribución no es “un organismo cognitivo”. Es un protocolo
reproducible para distinguir una ventaja real de broadcast modular de mejoras
debidas a mayor capacidad, información privilegiada o ajuste específico al
entorno.

Esta contribución solo será defendible si:

- supera baselines recurrentes y de memoria emparejados;
- generaliza a regímenes y composiciones no vistos;
- conserva la ventaja en más de una familia de entornos;
- las intervenciones sobre el workspace producen efectos predichos;
- el resultado se replica entre semillas con incertidumbre cuantificada.

## Criterios de abandono

Se detendrá esta línea si ocurre cualquiera de los siguientes:

- la ventaja desaparece al emparejar parámetros o información;
- solo existe dentro de `SocialSurvivalWorld`;
- un GRU/LSTM emparejado iguala el rendimiento y la adaptación;
- el contenido difundido no media causalmente las decisiones;
- el resultado requiere escoger retrospectivamente tareas o métricas.

## Estado del arte mínimo contrastado

- LIDA ya implementa ciclos cognitivos inspirados en Global Workspace.
- VanRullen y Kanai propusieron una implementación profunda de un espacio global
  amodal.
- Maytié et al. demostraron transferencia cross-modal cero-disparo mediante un
  Global Workspace.
- `GW-Dreamer` combina explícitamente Global Workspace, world models y RL.
- DreamerV3 demuestra que los world models ya son una familia de baselines
  madura.
- AdA demuestra adaptación rápida en espacios abiertos de tareas mediante
  meta-RL y memoria basada en atención.

Por tanto, memoria + workspace + world model no puede presentarse como novedad.

## Referencias primarias iniciales

- Franklin et al. (2012), *Global Workspace Theory, its LIDA Model and the
  Underlying Neuroscience*.
- VanRullen & Kanai (2021), *Deep Learning and the Global Workspace Theory*:
  https://arxiv.org/abs/2012.10390
- Maytié et al. (2024), *Zero-shot cross-modal transfer of Reinforcement
  Learning policies through a Global Workspace*:
  https://arxiv.org/abs/2403.04588
- Maytié et al. (2025), *Multimodal Dreaming: A Global Workspace Approach to
  World Model-Based Reinforcement Learning*:
  https://arxiv.org/abs/2502.21142
- Hafner et al. (2023), *Mastering Diverse Domains through World Models*:
  https://arxiv.org/abs/2301.04104
- Adaptive Agent Team (2023), *Human-Timescale Adaptation in an Open-Ended Task
  Space*: https://arxiv.org/abs/2301.07608

Esta revisión es suficiente para rechazar el briefing literal, pero no sustituye
una revisión sistemática antes de formular una publicación.
