# Cognitive Organism Research Benchmark

Repositorio experimental para estudiar si una arquitectura cognitiva modular con
un canal de difusión global limitado produce ventajas funcionales y firmas
causales reproducibles en entornos parcialmente observables.

Este proyecto **no** pretende construir ni demostrar consciencia. Tampoco asume
que añadir módulos con nombres cognitivos mejore un agente. Cada componente debe
tener una definición operacional, una intervención posible y una hipótesis
falsable.

## Estado actual

- Auditoría científica inicial y criterios `go/no-go`.
- Protocolo experimental preregistrado.
- Entorno mínimo `SocialSurvivalWorld`.
- Entorno diagnóstico `AdvisorSwitchTask` para aislar memoria.
- Pruebas de API, reproducibilidad y dinámica causal.
- Gate 2: existe señal recurrente aislada, pero todavía no es estable entre
  semillas.
- Confirmación independiente: RecurrentPPO rechazado como baseline estable; un
  controlador determinista de memoria mínima sí resuelve la tarea.

Todavía no se ha implementado ninguna arquitectura propuesta como contribución.
Ese trabajo solo comenzará después de estabilizar y confirmar los baselines.

## Instalación

Se requiere Python 3.11 o posterior.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
pytest
```

## Principio científico

La comparación principal será entre agentes emparejados en parámetros y
presupuesto de entrenamiento. La variable experimental será la forma de
comunicación entre módulos, no el número de módulos ni el acceso a información
adicional.

Consulta [SCIENTIFIC_DECISION.md](docs/SCIENTIFIC_DECISION.md) y
[PREREGISTRATION.md](docs/PREREGISTRATION.md) antes de ampliar el sistema.
