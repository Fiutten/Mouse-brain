# Aceptación de Fase 2b

## Ejecución del 14 de junio de 2026

- Sesiones: 21.
- Ratones únicos: 19.
- Regiones: seis áreas visuales corticales.
- Fallos de extracción: 0.
- Controles nulos por candidato: 21.000.
- Remuestras bootstrap agrupadas por ratón por candidato: 5.000.

## Selección confirmatoria de target

| Candidato | Mediana entre ratones | IC bootstrap 95% | Split-half | Sobre nulo 95% | Pasa |
|---|---:|---:|---:|---:|---|
| FC espontánea | 0.520 | [0.345, 0.731] | 0.754 | 38.1% | no |
| Perfil de tasa espontánea | 0.687 | [0.404, 0.761] | 0.986 | 38.1% | no |
| Respuesta a cambio visual | 0.564 | [0.377, 0.706] | 0.991 | 33.3% | no |

**Decisión: ningún candidato seleccionado.** Los tres superan los criterios de
mediana y estabilidad interna, pero ninguno supera el control de identidad
regional en al menos la mitad de sesiones.

## Descomposición exploratoria

- La FC mejora al usar bins de 0.5 s (`0.592`) y empeora con bins de 5 s
  (`0.350`).
- La mediana FC aumenta desde `0.441` con 60 s hasta `0.560` con 240 s. Más
  duración reduce ruido, pero no elimina la heterogeneidad.
- La asociación de fiabilidad con número mínimo y medio de unidades es débil:
  Spearman `0.243` y `0.269`.
- Las dos parejas de sesiones del mismo ratón tienen FC baja: `0.121` y `0.229`.
- Familiar presenta medianas mayores que Novel, pero las permutaciones a nivel
  de ratón no respaldan una diferencia: `p=0.394` para FC y `p=0.293` para
  respuesta evocada.

## Interpretación científica

Los observables son muy estables dentro de sesión, especialmente los perfiles
regionales, pero la identidad relativa de las seis regiones cambia demasiado
entre sesiones/ratones. Ni duración, bin temporal ni número de unidades explican
por sí solos el problema. Con solo dos ratones repetidos no puede separarse de
forma fiable variabilidad animal, sesión, trayectoria de sondas y estado.

No es defendible usar estos targets como métrica primaria para ajustar o validar
un simulador. Sí pueden conservarse como métricas secundarias descriptivas.
