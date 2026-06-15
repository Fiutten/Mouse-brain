# Resultado de desarrollo de Fase 2c

## Cohorte de desarrollo

- 21 sesiones locales.
- 19 ratones.
- Ningún dato confirmatorio descargado o abierto antes del sellado.

## Resultados

| Transformación | Entre ratones | Split-half | Sobre nulo 95% | IC bootstrap 95% | Pasa |
|---|---:|---:|---:|---:|---|
| Baseline restado | 0.901 | 0.996 | 52.4% | [0.882, 0.934] | sí |
| Pico regional normalizado | 0.931 | 0.994 | 71.4% | [0.886, 0.956] | sí |
| Derivada temporal | 0.901 | 0.991 | 76.2% | [0.864, 0.929] | sí |

## Selección congelada

Se selecciona `temporal_derivative` por la regla fijada: mayor fracción de
sesiones sobre el control nulo. La transformación, ventanas, bins, métricas y
umbrales quedan congelados en
`configs/allen_vbn_phase2c_confirmation_sealed.json`.

La cohorte confirmatoria contiene 20 sesiones de 20 ratones nuevos, equilibrada
entre diez Familiar y diez Novel. La lista fue generada y sellada antes de
descargar sus archivos NWB.
