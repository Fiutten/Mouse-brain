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
- Pruebas de API, reproducibilidad y dinámica causal del entorno.

Todavía no se ha implementado ninguna arquitectura propuesta como contribución.
Ese trabajo solo comenzará después de validar el entorno y los baselines.

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
