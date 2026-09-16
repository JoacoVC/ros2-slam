# Mobile Robot — SLAM + Regla de la Mano Derecha

Proyecto ROS 2 para un robot móvil diferencial en Gazebo que construye un mapa automáticamente usando SLAM mientras navega siguiendo la regla de la mano derecha.

## Requisitos

```bash
sudo apt update && sudo apt install -y \
  ros-humble-ros-gz \
  ros-humble-slam-toolbox \
  ros-humble-navigation2 \
  ros-humble-nav2-bringup \
  ros-humble-robot-state-publisher \
  ros-humble-joint-state-publisher \
  ros-humble-xacro \
  ros-humble-teleop-twist-keyboard
```

## Estructura del proyecto

```
ws_mobile/
└── src/
    └── mobile_robot/
        ├── launch/
        │   ├── gazebo_model.launch.py   # Lanza Gazebo con el robot
        │   ├── slam.launch.py           # Lanza todo: Gazebo + SLAM + RViz + mano derecha
        │   └── localization.launch.py   # Localización con mapa ya creado (AMCL)
        ├── mobile_robot/
        │   ├── __init__.py
        │   └── lidar_min.py             # Nodo de navegación mano derecha
        ├── model/
        │   ├── robot.xacro              # Modelo del robot
        │   └── robot.gazebo             # Plugins de Gazebo
        ├── parameters/
        │   ├── bridge_parameters.yaml   # Mapeo de topics ROS 2 ↔ Gazebo
        │   ├── slam_params.yaml         # Parámetros de SLAM Toolbox
        │   └── amcl_params.yaml         # Parámetros de localización AMCL
        ├── maps/
        │   ├── mi_mapa.pgm              # Mapa guardado
        │   └── mi_mapa.yaml             # Metadata del mapa
        └── rviz/
            └── mi_configuracion.rviz    # Configuración de RViz
```

## Compilación

Siempre desde la raíz del workspace:

```bash
cd ~/ws_mobile
source /opt/ros/humble/setup.bash
colcon build --symlink-install
source install/setup.bash
```

> Con `--symlink-install` no necesitas recompilar al editar archivos `.py`,
> solo cuando modifiques `setup.py` o archivos de configuración.

## Ejecución — SLAM + Mano Derecha

### Terminal 1 — Lanzar Gazebo + SLAM + RViz

```bash
cd ~/ws_mobile
source install/setup.bash
ros2 launch mobile_robot slam.launch.py
```

Esto abre:
- **Gazebo** con el robot en un mundo vacío
- **SLAM Toolbox** construyendo el mapa en tiempo real
- **RViz2** para visualizar el mapa y el robot

### Terminal 2 — Activar navegación automática (mano derecha)

```bash
cd ~/ws_mobile
source install/setup.bash
ros2 run mobile_robot lidar_min
```

El robot comenzará a moverse solo, siguiendo la pared derecha y mapeando el entorno.

Deberías ver logs como:
```
Frente: 2.34m | Derecha: 0.61m
Frente: 2.34m | Derecha: 0.58m
```

## Verificación — Diagnóstico rápido

Si el robot no se mueve, verifica en terminales separadas:

```bash
# ¿El LiDAR publica datos?
ros2 topic echo /scan --once

# ¿El nodo está corriendo?
ros2 node info /lidar_right_hand_rule

# ¿Se publican comandos de velocidad?
ros2 topic echo /cmd_vel

# ¿El árbol TF está completo?
ros2 run tf2_ros tf2_echo odom base_footprint
```

El árbol TF correcto es:
```
map → odom → base_footprint → body_link → lidar_link
                                         → wheel1_link
                                         → wheel2_link
                                         → caster_link
```

## Configurar RViz manualmente

Si RViz abre sin configuración, agregar estos displays:

| Display | Configuración |
|---|---|
| **Fixed Frame** | `map` |
| **RobotModel** | Topic: `/robot_description` |
| **LaserScan** | Topic: `/scan`, Size: `0.05` |
| **Map** | Topic: `/map` |
| **TF** | activar |

Guardar con **File → Save As** en `rviz/mi_configuracion.rviz`.

## Guardar el mapa generado

Cuando el mapa esté completo, en una terminal nueva:

```bash
cd ~/ws_mobile
source install/setup.bash
ros2 run nav2_map_server map_saver_cli -f src/mobile_robot/maps/mi_mapa
```

Esto genera `mi_mapa.pgm` y `mi_mapa.yaml`.

## Notas importantes

- Asegúrate de hacer `source install/setup.bash` en **cada terminal nueva**.
- Si `ws_mobile1` existe como carpeta separada, no la pongas dentro de `ws_mobile/` — colcon detectaría paquetes duplicados y fallaría el build.
- El modo de localización con AMCL (`localization.launch.py`) está en fase de pruebas y puede dar errores.