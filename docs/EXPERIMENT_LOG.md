# Registro de experimentos

## 2026-06-12 — Gate 1: estructura causal del entorno

### Objetivo

Comprobar antes de entrenar agentes que `SocialSurvivalWorld` contiene una
estructura resoluble, una señal social causalmente relevante y un coste medible
del engaño.

### Configuración

- 250 episodios por política.
- Semilla base: `20260612`.
- Azar y oráculo: entorno con cambio de régimen en el paso 40.
- Seguidores sociales: régimen fijo para aislar el efecto de fiabilidad.
- Comando: `.venv/bin/python scripts/validate_environment.py`.

### Resultado

| Política | Retorno | Peligros | Tasa peligro/paso | Recursos | Pasos |
|---|---:|---:|---:|---:|---:|
| azar | -0.6234 | 0.5080 | 0.0112 | 0.5160 | 63.1400 |
| oráculo privilegiado | 14.6982 | 1.3320 | 0.0170 | 16.8280 | 79.7840 |
| seguidor útil | 14.6982 | 1.3320 | 0.0170 | 16.8280 | 79.7840 |
| seguidor engañado | -2.9876 | 3.0480 | 0.2360 | 0.2040 | 14.3600 |

### Interpretación

El entorno supera el Gate 1 mínimo:

- existe una política privilegiada claramente superior al azar;
- la señal social tiene consecuencias conductuales fuertes;
- el engaño reduce retorno, acceso a recursos y supervivencia;
- las ejecuciones son reproducibles por semilla.

El seguidor útil coincide con el oráculo en régimen fijo porque la señal apunta
directamente al recurso. Esto es útil como control positivo, pero hace que el
entorno sea insuficiente como evidencia científica única.

### Hallazgo metodológico durante la validación

La primera prueba esperaba más encuentros acumulados con peligro bajo engaño.
Falló porque el seguidor engañado muere antes y tiene menos tiempo de exposición.
Se sustituyó el conteo acumulado como contraste principal por la tasa de peligro
por paso. El fallo y la corrección se conservan porque muestran un sesgo de
supervivencia que también deberá controlarse en experimentos futuros.

### Decisión

**Gate 1 aprobado con limitaciones.** Se permite avanzar a baselines simples,
pero no a módulos cognitivos complejos. El siguiente gate debe demostrar que un
agente recurrente puede inferir cambios de régimen mejor que PPO sin memoria.
