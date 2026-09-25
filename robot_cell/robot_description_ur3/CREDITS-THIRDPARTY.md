# Créditos de terceros

Este paquete combina código/URDF propios (BSD-3-Clause) con recursos de terceros.

- Licencia del paquete: `LICENSES/BSD-3-Clause.txt`
- Términos UR (Graphical Documentation): `LICENSES/UR_LICENSE.txt`
- CC BY 4.0 (texto legal): `LICENSES/CC-BY-4.0.txt`

---

## Universal Robots — Graphical Documentation
**Origen:** modelos/mallas/documentación de Universal Robots  
**Términos aplicables:** ver `LICENSES/UR_LICENSE.txt`  

> © 2023 Universal Robots A/S. Use hereof is subject to Universal Robots A/S’ Terms and Conditions for Use of Graphical Documentation.

---

## Pinza Soft — v1
**Título:** Pinza de robótica blanda  
**Autor:**  Glen Guerrero 
**Fuente:** <https://fuel.gazebosim.org/1.0/jfrascon/models/Euro_pallet_w_stacked_boxes>  
 

---

## Robotiq 2F-85 Gripper (ros2_robotiq_gripper)

- **Fuente:** https://github.com/PickNikRobotics/ros2_robotiq_gripper
- **Autor:** Cory Crean
- **Mantenedores:** Alex Moriarty, Marq Rasmussen (PickNik Robotics)
- **Licencia:** BSD-3-Clause
- **Uso en este proyecto:** paquete `robotiq_description` con el modelo URDF
  y las mallas de la pinza Robotiq 2F-85, empleada como alternativa rígida al
  gripper paralelo custom del proyecto original.
- **Nota:** El repositorio de PickNik indica expresamente que no está
  patrocinado ni mantenido por Robotiq Inc.; es una implementación open
  source basada en las especificaciones públicas del fabricante.

---
## Textura de metal — Metal010 (ambientCG)

- **Fuente:** https://ambientcg.com/view?id=Metal010
- **Autor:** ambientCG (Lennart Demes)
- **Licencia:** Creative Commons CC0 1.0 Universal (dominio público)
- **Uso en este proyecto:** textura PBR aplicada a la mesa/pedestal de la celda
  robótica en la simulación de Gazebo.
- **Atribución (recomendada por ambientCG, no obligatoria):**
  Created using Metal010 from ambientCG.com, licensed under the Creative
  Commons CC0 1.0 Universal License.
  
---
## Textura de madera — WoodFloor047 (ambientCG)

- **Fuente:** https://ambientcg.com/view?id=WoodFloor047
- **Autor:** ambientCG (Lennart Demes)
- **Licencia:** Creative Commons CC0 1.0 Universal (dominio público)
- **Uso en este proyecto:** textura PBR aplicada al suelo (floor) de la celda
  robótica en la simulación de Gazebo.
- **Atribución (recomendada por ambientCG, no obligatoria):**
  Created using WoodFloor047 from ambientCG.com, licensed under the Creative
  Commons CC0 1.0 Universal License.

> Este recurso se utiliza conforme a los términos de la licencia CC BY 4.0. La atribución se incluye en este archivo y en `package.xml` (URL de la fuente).

---

## Notas de cumplimiento
- La redistribución de activos licenciados bajo **CC BY 4.0** requiere **atribución**.  
- Los materiales de **Universal Robots** se incluyen y usan conforme a sus **Términos y Condiciones para Documentación Gráfica**.  
- Cuando corresponda, cada subcarpeta de modelos puede incluir un `README` con su atribución específica.

---

