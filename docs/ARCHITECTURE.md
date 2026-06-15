# Arquitectura de MouseBrainBench-core

La orientación de conectividad es siempre `weights[target, source]`. Los modelos
dinámicos reciben esa matriz y producen actividad regional `time x region`.

1. `schemas.py`: contratos validados y neutrales respecto a la fuente.
2. `connectivity/`: fixture sintético, normalización y conversión a grafo.
3. `dynamics/`: modelos transparentes intercambiables.
4. `simulation/`: integración, estímulos y perturbaciones reversibles.
5. `validation/`: métricas descriptivas, funcionales, perturbacionales y coste.
6. `config.py` y `cli.py`: construcción estricta y ejecución reproducible.
7. `artifacts.py`: configuración, procedencia, métricas y arrays portables.
8. `visualization/`: gráficos opcionales, desacoplados del runner para CI y servidores.
9. `data/loaders/allen_vbn.py`: extracción NWB read-only y cualificación por metadatos.
10. `benchmarks/allen_vbn.py`: fiabilidad empírica leave-one-mouse-out y controles nulos.
11. `benchmarks/allen_vbn_phase2b.py`: selección preregistrada de targets,
    sensibilidad temporal y diagnósticos agrupados por ratón.
12. `benchmarks/allen_vbn_phase2c.py`: desarrollo, sellado y confirmación externa
    de un target temporal evocado, con bloqueo explícito ante deriva del plan.
13. `data/loaders/allen_connectivity.py`: matriz regional derivada de
    experimentos oficiales de trazado Allen con orientación y procedencia.
14. `benchmarks/allen_visual_phase3.py`: calibración en desarrollo y evaluación
    externa sellada frente a controles topológicos recalibrados.

La simulación basal y la intervenida parten de la misma semilla. Las
perturbaciones trabajan sobre copias y nunca alteran la conectividad de entrada.
Los directorios de salida se identifican por un hash de configuración.
