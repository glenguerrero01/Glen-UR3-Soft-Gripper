# Glen-UR3-Soft-Gripper
Repositorio Glen Guerrero de la simulación de una pinza de robótica blanda con el robot UR3

<img width="350" src="https://github.com/user-attachments/assets/605314a3-d461-4dd1-906a-0e9c80611680" />
<img width="350" src="https://github.com/user-attachments/assets/5e953782-97be-4d4b-83f6-717f6143be54" />


# Robótica Blanda aplicada al Cobot UR3

**Diseño CAD y análisis comparativo en ROS 2 de una pinza bioinspirada frente a efectores rígidos**

Trabajo Fin de Máster — Máster en Robótica y Automatización, Universidad Europea.
Autor: **Glen Alejandro Guerrero Burbano**.

---

## Descripción

Este repositorio contiene la celda robótica, los efectores y el marco de evaluación
desarrollados para comparar el desempeño de agarre de una **pinza blanda bioinspirada**
frente a una **pinza rígida comercial** (Robotiq 2F‑85), montadas sobre un cobot **Universal Robots UR3** y simuladas en **ROS 2 + Gazebo**.

El proyecto abarca:

- La integración de ambos efectores sobre el UR3 en ROS 2, con simulación física en
  Gazebo y planificación mediante MoveIt.
- Un nodo de automatización de ensayos de agarre (aproximación → cierre → elevación →
  registro del resultado) para objetos de geometría cilíndrica, esférica y cúbica.
- Un cuaderno de análisis estadístico reproducible (tasa de éxito, intervalos de Wilson,
  chi‑cuadrado, regresión logística) que sustenta la comparación.
---

## Requisitos

| Componente | Versión / Notas |
|------------|-----------------|
| Ubuntu | 24.04 LTS |
| ROS 2 | Jazzy Jalisco |
| Gazebo | Harmonic (gz‑sim 8) |
| MoveIt 2 | Para Jazzy |
| `ros2_control` / `gz_ros2_control` | Control en simulación |
| `ur_description` | Descripción del brazo UR (`ros-jazzy-ur-description`) |
| `robotiq_description` | Descripción de la pinza rígida (`ros-jazzy-robotiq-description`) |

Dependencias de sistema (instalación rápida):

```bash
sudo apt update
sudo apt install \
  ros-jazzy-ur-description \
  ros-jazzy-robotiq-description \
  ros-jazzy-ros-gz \
  ros-jazzy-gz-ros2-control \
  ros-jazzy-moveit \
  ros-jazzy-ros2controlcli
```

Para el **análisis de resultados** (cuaderno Jupyter) se requiere Python 3 con:

```bash
pip install numpy pandas matplotlib scipy statsmodels openpyxl jupyter
```

---

## Estructura del repositorio

El workspace se organiza en tres paquetes bajo `src/robot_cell/`, siguiendo la
estructura estándar del ecosistema UR (`*_description` / `*_control` / `*_moveit`):

```
robot_cell/
├── robot_description_ur3/      # Descripción de la celda, efectores, mundos y objetos
│   ├── urdf/
│   │   ├── robot_cell.urdf.xacro           # Punto de entrada (celda + robot + gripper)
│   │   ├── robot_cell_macro.xacro          # Macro de la celda (mesa, suelo, paredes…)
│   │   ├── soft_gripper.xacro              # Pinza blanda bioinspirada (aportación propia)
│   │   └── robotiq_2f_85_macro.urdf.xacro  # Macro del Robotiq 2F‑85 (adaptado, sin mimic)
│   ├── worlds/cell_world.sdf               # Mundo de Gazebo
│   ├── models/                             # Objetos de prueba (cilindros, esferas, cubos, huevo)
│   └── meshes/                             # Mallas de la celda y del acople del dedo blando
│
├── robot_control_ur3/         # Control en Gazebo + nodos de evaluación
│   ├── urdf/robot_cell_control.urdf.xacro  # ros2_control para gz_ros2_control
│   ├── config/controller.yaml              # ur_arm_controller + gripper_controller
│   ├── launch/gz_moveit_ur3.launch.py      # Lanzamiento unificado: Gazebo + MoveIt + RViz
│   ├── test_agarre_blando.py               # Automatización de ensayos (pinza blanda)
│   └── test_agarre_robotiq.py              # Automatización de ensayos (pinza rígida)
│
└── robot_cell_moveit_ur3/     # Configuración de MoveIt
    ├── config/robot_cell.srdf              # Grupos, poses y matriz de colisiones
    ├── config/kinematics.yaml              # Solver IK del brazo
    ├── config/joint_limits.yaml            # Límites (incl. aceleración, requeridos por MoveIt)
    └── config/moveit_controllers.yaml      # Interfaz MoveIt ↔ controladores
```

El análisis de datos se distribuye aparte:

```
analisis/
├── analisis_agarre.ipynb      # Cuaderno reproducible del análisis estadístico
├── RIG_resultados.xlsx        # Datos crudos de la pinza rígida
└── SOFT_resultados.xlsx       # Datos crudos de la pinza blanda
```

---

## Compilación

```bash
cd ~/ros2_ws
colcon build --packages-select robot_description_ur3 robot_control_ur3 robot_cell_moveit_ur3
source install/setup.bash
```

---

## Uso

### Visualizar la celda en RViz (sin simulación)

```bash
ros2 launch robot_description_ur3 view_rviz.launch.py ur_type:=ur3
```

### Lanzar la simulación completa (Gazebo + MoveIt + RViz)

```bash
ros2 launch robot_control_ur3 gz_moveit_ur3.launch.py
```

### Seleccionar el efector

El efector activo se define en `robot_cell_macro.xacro` (el *include* y la llamada de
la macro) junto con el bloque `ros2_control`, el `controller.yaml`, el SRDF y el
`moveit_controllers.yaml` correspondientes. El repositorio incluye la configuración de
ambos efectores; se documenta el procedimiento de cambio en los comentarios de dichos
archivos.

### Ejecutar los ensayos de agarre

Con la simulación en marcha y los controladores activos:

```bash
# Pinza blanda
python3 src/robot_cell/robot_control_ur3/test_agarre_blando.py
# Pinza rígida
python3 src/robot_cell/robot_control_ur3/test_agarre_robotiq.py
```

Cada nodo posiciona el brazo, genera el objeto, cierra el gripper, lo eleva, solicita
el juicio de éxito por terminal y vuelca el resultado a un CSV para su posterior análisis.
Los parámetros editables (forma, tamaño, orientación, poses) se encuentran al inicio del
archivo.

### Analizar los resultados

```bash
cd analisis
jupyter notebook analisis_agarre.ipynb
```

El cuaderno reproduce, a partir de los Excel de resultados, las tasas de éxito con sus
intervalos de confianza de Wilson, las pruebas de significación (chi‑cuadrado / Fisher),
la regresión logística y todas las figuras del análisis.

<img width="320" src="https://github.com/user-attachments/assets/e6725216-21d3-4f1b-910d-3b615759fc2b" />
<img width="320" src="https://github.com/user-attachments/assets/1eab2e0e-bab0-454b-9207-4e7d7a376176" />


---

## Los efectores

### Pinza blanda bioinspirada

Dedo bioinspirado con cámaras de aire, diseñado en CAD y modelado en simulación mediante
una **discretización pseudo‑rígida** en segmentos articulados. Dado que el motor de física
empleado (DART) no soporta restricciones de acoplamiento (`mimic`), las articulaciones del
mecanismo se **actúan de forma coordinada** desde el controlador, reproduciendo el cierre
envolvente característico de la pinza blanda.

<img width="300" src="https://github.com/user-attachments/assets/a0461edb-62b5-4cc3-8a6e-d8237eed9d06" />
<img width="300" src="https://github.com/user-attachments/assets/9e9c212e-c158-4d1b-bf3a-075e3d4882c3" />


### Pinza rígida Robotiq 2F‑85

Pinza paralela comercial de dos dedos, empleada como referencia rígida para la comparación.
Su descripción procede del paquete **`robotiq_description`** (ver *Créditos*). Para su
simulación en Gazebo se adaptó la macro eliminando las restricciones `mimic` y actuando sus
seis articulaciones de forma coordinada con los signos propios del mecanismo de cuatro barras.

<img width="300" src="https://github.com/user-attachments/assets/ed23cdae-4427-4105-ab6f-434e6c677f59" />
<img width="300" src="https://github.com/user-attachments/assets/c74bc701-0f6d-481f-a38b-aeff7a997086" />

---

## Créditos y atribución

Este proyecto se apoya en trabajo de terceros que se reconoce a continuación.

### Base de la celda robótica

Parte del tutorial oficial
[**Universal_Robots_ROS2_Tutorials / my_robot_cell**](https://github.com/UniversalRobots/Universal_Robots_ROS2_Tutorials/tree/main/my_robot_cell)
de **Universal Robots A/S**, del que se hereda la estructura de paquetes
(`*_description` / `*_control` / `*_moveit`), el patrón de instanciación del brazo UR
mediante `ur_macro.xacro` y el esqueleto del URDF de control con `ros2_control`.
Autores originales: **Felix Exner** y **Felix Durchdewald** (FZI Forschungszentrum
Informatik, Karlsruhe). Licencia **BSD‑3‑Clause**.

El brazo **UR3** y sus mallas son propiedad de **Universal Robots A/S** (paquete
`ur_description`), sujetos a sus *Terms and Conditions for Use of Graphical Documentation*.

### Adaptación docente de la celda

La celda robótica base (mesa, suelo, paredes, plato de montaje y elementos institucionales)
fue adaptada por la **Universidad Europea** para el laboratorio del Máster en Robótica y Automatización, sobre la base del tutorial de UR.

### Pinza rígida Robotiq 2F‑85

La descripción de la pinza rígida procede del paquete **`robotiq_description`**, mantenido
por **PickNik Robotics** en el repositorio
[**ros2_robotiq_gripper**](https://github.com/PickNikRobotics/ros2_robotiq_gripper),
a partir de la descripción oficial del gripper de **Robotiq Inc.** En este trabajo, la macro
se adaptó para su simulación en Gazebo (eliminación de `mimic` y actuación coordinada de las
articulaciones). Licencia del paquete original: **BSD‑3‑Clause**.

### Otros recursos de terceros

El detalle completo de licencias de terceros se encuentra en
`robot_description_ur3/CREDITS-THIRDPARTY.md`.

### Aportaciones propias

Sobre la base anterior, el presente trabajo aporta:

- **Diseño e integración de la pinza blanda bioinspirada** (`soft_gripper.xacro` y su acople),
  incluyendo su modelado pseudo‑rígido y su control sin `mimic` en Gazebo.
- **Integración y adaptación de la pinza rígida Robotiq 2F‑85** para simulación en Gazebo.
- **Paquete de control y simulación** `robot_control_ur3` para Gazebo Harmonic con
  `gz_ros2_control`, incluyendo los controladores y el lanzamiento unificado.
- **Configuración MoveIt** `robot_cell_moveit_ur3` (grupos, poses de agarre, límites y
  cinemática) para el UR3 con ambos efectores.
- **Marco de evaluación de agarre**: objetos de prueba paramétricos (cilindros, esferas y
  cubos, y un modelo de huevo) como modelos SDF, y los nodos de automatización de ensayos.
- **Análisis estadístico reproducible** de los resultados (cuaderno Jupyter).

---

## Licencias

- **Código propio:** BSD‑3‑Clause.
- **Mallas de UR:** Universal Robots A/S — *Terms & Conditions for Use of Graphical Documentation*.
- **`robotiq_description`:** BSD‑3‑Clause (PickNik Robotics / Robotiq Inc.).
- **Modelos CC BY 4.0** (pallet, mug): atribución en `CREDITS-THIRDPARTY.md`.

---

## Autor

**Glen Alejandro Guerrero Burbano**
Máster en Robótica y Automatización — Universidad Europea.
