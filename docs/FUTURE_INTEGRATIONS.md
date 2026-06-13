# Integraciones futuras y límites

No hay adaptadores ficticios en la Fase 1. Una integración se considerará
implementada solo cuando cargue datos reales, preserve procedencia y tenga tests
contra un fixture versionado.

## Allen CCF y MCModels

El adaptador deberá producir `BrainRegion` y `ConnectivityMatrix`, documentar la
resolución y transformación espacial, y conservar IDs y versión de Allen.

La Fase 2 ya integra actividad funcional Allen Visual Behavior Neuropixels. Esto
no equivale a integrar CCF o MCModels: las etiquetas regionales se usan para
agregación funcional, pero no existe todavía conectividad anatómica Allen en el
modelo.

## BMTK y SONATA

Se usarán como motores y formatos existentes para módulos detallados. El contrato
futuro debe traducir entradas regionales a estímulos del módulo y resumir sus
salidas sin afirmar equivalencia entre escalas.

## The Virtual Brain

Será un baseline externo para modelos de masa neural. La comparación deberá
igualar conectividad, integración, parámetros y observables.

## MICrONS

Se tratará como referencia local de corteza visual, nunca como conectoma
whole-brain. Su posible uso exige definir una reducción explícita de escala.
