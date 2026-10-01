# Anomaly Wheel Sim

Questo progetto dimostra l'integrazione tra l'inferenza AI on-edge e l'ecosistema ROS 2. Analizzando i dati di accelerometro e giroscopio direttamente sull'hardware, il sistema rileva le anomalie vibrazionali e sincronizza i risultati con un Digital Twin, offrendo un'applicazione pratica di Condition Monitoring industriale.

## Il Flusso di Funzionamento
1. Una scheda fisica (Arduino Nicla Vision) campiona l'accelerometro e il giroscopio a 100Hz ed elabora i dati localmente tramite una rete neurale (Edge Impulse).
2. Quando l'IA classifica lo spettro vibrazionale (Norma, Anomalia1 o Anomalia2), emette un payload JSON via seriale contenente lo stato, la confidenza e i tempi di inferenza hardware.
3. Un nodo bridge in ROS 2 acquisisce il dato e aggiorna un Digital Twin 3D (URDF). L'interfaccia grafica (RViz2) riceve il segnale e adatta visivamente la cinematica della ruota, fornendo un riscontro visivo immediato della telemetria.

Per garantire la massima riproducibilità, l'infrastruttura è interamente containerizzata e ottimizzata per un ambiente Windows/WSL2.

## Struttura del Repository
* **`nicla_code/`**: Firmware C++ (`.ino`) da caricare sulla scheda Nicla Vision. Gestisce l'acquisizione IMU e l'inferenza AI.
* **`src/`**: Pacchetto ROS 2 (`anomaly_wheel_sim`) contenente:
  * Nodi Python (`serial_bridge.py` per l'acquisizione USB, `sim_controller.py` per la logica HIL).
  * Il modello cinematico URDF del macchinario (`wheel.urdf`).
  * Le configurazioni di visualizzazione RViz2 (`wheel_view.rviz`).
* **Infrastruttura **: `Dockerfile` (ROS 2 Jazzy) e `docker-compose.yml`, preconfigurati per il passthrough grafico (X11/WSLg) e la comunicazione CycloneDDS.

