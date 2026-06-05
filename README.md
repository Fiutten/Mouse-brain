# Neurotwin MVP

Prototipo modular para un gemelo funcional regional de cerebro de raton.

Este MVP no intenta simular conciencia ni un cerebro completo a escala celular. Implementa una primera version falsable:

- grafo regional funcional de raton;
- dinamica Nivel 0 con nodos continuos;
- fixture sintetico tipo Neuropixels;
- contratos de adaptadores Allen/IBL;
- registro reproducible de experimentos;
- contrato de artefactos normalizados entre entornos Python;
- baselines conductuales simples;
- tarea visual con memoria corta;
- lesiones virtuales;
- grafo de conocimiento minimo;
- agentes deterministas para hipotesis y revision;
- pruebas basicas.

## Entorno

```bash
python3 -m venv .venv
.venv/bin/pip install -e .
```

El entorno virtual ya ha sido creado en `.venv/` durante esta fase de trabajo.

## Comandos

```bash
make test
make run
make register
make export-synthetic
make allen-smoke-s3
make allen-select
make verify
```

## Modulos

- `neurotwin_mvp/config.py`: carga y valida configuracion JSON.
- `neurotwin_mvp/artifacts.py`: contrato de artefactos normalizados entre entornos.
- `neurotwin_mvp/allen_normalization.py`: normalizacion Allen/NWB a `Session`.
- `neurotwin_mvp/data.py`: interfaz de sesiones y fixture sintetico.
- `neurotwin_mvp/datasets/`: adaptadores opcionales Allen/IBL.
- `neurotwin_mvp/baselines.py`: baselines conductuales iniciales.
- `neurotwin_mvp/metrics.py`: metricas basicas.
- `neurotwin_mvp/registry.py`: registro local de experimentos y hashes.
- `neurotwin_mvp/regional_model.py`: modelo dinamico regional.
- `neurotwin_mvp/experiments.py`: evaluacion y lesiones.
- `neurotwin_mvp/knowledge.py`: grafo de conocimiento ligero.
- `neurotwin_mvp/agents.py`: agentes MVP sin llamadas externas.
- `neurotwin_mvp/workflow.py`: orquestacion estilo grafo.

## Documentacion de gestion

- `envs/README.md`: estrategia multi-entorno.
- `envs/core.md`: entorno core.
- `envs/allen.md`: entorno Allen.
- `docs/ARCHITECTURE.md`: arquitectura y restricciones de diseno.
- `docs/ROADMAP.md`: fases del proyecto y criterios de salida.
- `docs/RISKS.md`: registro de riesgos.
- `docs/HYPOTHESES.md`: hipotesis iniciales y criterios de medicion.
- `docs/EXPERIMENT_MANAGEMENT.md`: politica de datos, artefactos y ejecuciones.
- `docs/ALLEN_METADATA_SMOKE_TEST.md`: resultado del smoke test de metadata Allen.
- `docs/SCIENTIFIC_LAYERS.md`: capas cientificas del gemelo cerebral.

## Estructura de artefactos

- `data/allen/`: cache local AllenSDK. No se versiona.
- `data/ibl/`: cache local IBL/ONE. No se versiona.
- `artifacts/experiments/`: ejecuciones registradas. No se versionan por defecto.
- `artifacts/datasets/`: sesiones normalizadas exportadas entre entornos. No se versionan por defecto.
- `artifacts/reports/`: informes derivados. No se versionan por defecto.

Cada ejecucion registrada guarda:

- `manifest.json`;
- `report.json`;
- `config_snapshot.json`;
- hash SHA-256 de la configuracion.

## Verificacion actual

Estado verificado:

- paquete instalado en editable dentro de `.venv`;
- `python -m unittest discover -s tests`: 22 tests OK;
- `run_prototype.py`: genera hipotesis, revision y barrido de lesiones.

## Datos reales

Hay contratos iniciales para:

- Allen Visual Behavior Neuropixels mediante AllenSDK.
- IBL brain-wide map mediante ONE/OpenAlyx.

Todavia no hay normalizacion completa NWB/ONE a `Session`. El objetivo del siguiente bloque es seleccionar una sesion concreta, instalar dependencias opcionales y convertir trials/spikes/regiones al contrato interno.

Smoke test Allen:

- backend directo S3 ejecutado correctamente;
- 153 sesiones ecephys detectadas;
- CSV cacheado en `data/allen/project_metadata/ecephys_sessions.csv`;
- AllenSDK queda pendiente de un entorno Python 3.10/3.11 compatible.

## Multi-entorno

El proyecto queda integrado mediante artefactos, no mediante un unico runtime Python.

- `.venv`: entorno core para simulacion, tests, baselines, registry y consumo de artefactos.
- `.venv-allen`: entorno futuro para AllenSDK/NWB y exportacion de sesiones reales.

Contrato compartido:

```text
artifacts/datasets/<source>/<session_id>/session.json
```

## Lesiones virtuales

Las lesiones virtuales son intervenciones in-silico: una region se fija a cero durante un experimento para comprobar si la arquitectura regional produce un contrafactual coherente.

Uso correcto:

- diagnosticar si una region importa en el modelo;
- medir sensibilidad a perturbaciones;
- formular hipotesis contrastables.

Uso incorrecto:

- tratarlas como simulaciones clinicas;
- usarlas como prueba de causalidad biologica sin validacion empirica;
- usarlas para sostener claims sobre conciencia.

## Siguiente paso

Integrar un dataset real, empezando por Allen Visual Behavior Neuropixels o IBL, y reemplazar la tarea sintetica por eventos, spikes y conducta observados.
