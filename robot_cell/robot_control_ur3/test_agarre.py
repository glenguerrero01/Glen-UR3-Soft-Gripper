#!/usr/bin/env python3
# ============================================================================
# test_agarre.py  -  Automatizacion de pruebas de agarre (manual asistida)
#

#
# Comanda brazo y gripper DIRECTO a los controladores (FollowJointTrajectory),
# sin MoveIt/CHOMP, para evitar errores de planificacion.
#
# ------------------- VARIABLES CAMBIAR ENTRE PRUEBAS -------------------
SHAPE   = "esfera"     # forma (para nombre de carpeta/archivo y CSV)
SIZE    = 100             # <<< CAMBIA el tamano: 35, 40, 45, 50, 55, 60, 65
N_REPS  = 1             # repeticiones por tipo de agarre
CLOSE_ANGLE = 0.45      # angulo de cierre del gripper (rad)
OPEN_ANGLE  = 0.0        # angulo de apertura

# Orientacion con la que se spawnea el objeto (en radianes)
SPAWN_RPY = (0.0, 0.0, 0.0)   # roll=90 grados, pitch=0, yaw=0
#SPAWN_RPY = (1.5708, 0.0, 0.0)   # roll=90 grados, pitch=0, yaw=0

# Tipos de agarre: nombre de la pose (del SRDF) y posicion de spawn del objeto.
GRASPS = [
    {"tipo": "cenital", "pose": "init_1",    "xyz": (0.27, 0.195, 0.97)}, #0.27 , 0.195 , 0.97  #Esfera y cilindro inclinado
    #{"tipo": "cenital", "pose": "init_1",    "xyz": (0.271, 0.195, 0.97)}, #0.27 , 0.195 , 0.97  #Cilindro pie
    #{"tipo": "cenital", "pose": "init",    "xyz": (0.27, 0.195, 0.97)}, #0.195
    #{"tipo": "lateral", "pose": "cerca_C", "xyz": (0.31, 0.28,  0.97)}, #0.29
    #0.3150 para 40
    #0.3125 para >30
    #0.31 para 25
    #0.307 para 20

]

DROP_POSE1 = "drop_off_C"   # pose a la que va tras cerrar (para probar si aguanta) LATERAL
DROP_POSE2 = "drop_off_L"   # pose a la que va tras cerrar (para probar si aguanta) CENITAL

INTER_POSE1 = "inter_C"   # pose INTERMEDIA CENITAL
INTER_POSE2 = "inter_L"   # pose INTERMEDIA LATERA
ACERCAMIENTO_LATERAL = "cerca_B"   # pose ACERCAMIENTO LATERAL
ACERCAMIENTO_CENITAL ="cerca_A" # pose ACERCAMIENTO CENITAL
HOME_POSE = "home"       # pose segura de inicio de cada intento

WORLD_NAME = "cell_world"                       # nombre del <world> en tu .sdf
ARM_MOVE_TIME = 4.0      # segundos que tarda cada movimiento del brazo
GRIP_MOVE_TIME = 2.0     # segundos que tarda abrir/cerrar
SETTLE_TIME = 1.5        # espera tras spawnear para que el objeto se asiente
# ----------------------------------------------------------------

import os
import csv
import time
import subprocess
import xml.etree.ElementTree as ET

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from control_msgs.action import FollowJointTrajectory
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration

# Rutas (dependen de os, por eso van tras los imports)
WS = os.path.expanduser("~/ros2_ws")            # raiz del workspace
CSV_PATH = os.path.expanduser("~/resultados_agarre.csv")

ARM_JOINTS = [
    "ur3_shoulder_pan_joint", "ur3_shoulder_lift_joint", "ur3_elbow_joint",
    "ur3_wrist_1_joint", "ur3_wrist_2_joint", "ur3_wrist_3_joint",
]
GRIP_JOINTS = [
    "g_left_joint", "g_left_j23", "g_left_j34",
    "g_right_joint", "g_right_j23", "g_right_j34",
]

SRDF_PATH = os.path.join(
    WS, "install", "robot_cell_moveit_ur3", "share",
    "robot_cell_moveit_ur3", "config", "robot_cell.srdf"
)


def load_arm_poses(srdf_path):
    """Lee los group_state del SRDF -> {nombre: {joint: valor}}."""
    poses = {}
    root = ET.parse(srdf_path).getroot()
    for gs in root.findall("group_state"):
        if gs.get("group") != "ur_arm":
            continue
        name = gs.get("name")
        vals = {j.get("name"): float(j.get("value")) for j in gs.findall("joint")}
        poses[name] = vals
    return poses


class GraspTester(Node):
    def __init__(self):
        super().__init__("test_agarre")
        self.arm = ActionClient(self, FollowJointTrajectory,
                                "/ur_arm_controller/follow_joint_trajectory")
        self.grip = ActionClient(self, FollowJointTrajectory,
                                 "/gripper_controller/follow_joint_trajectory")
        self.get_logger().info("Esperando controladores...")
        self.arm.wait_for_server()
        self.grip.wait_for_server()
        self.get_logger().info("Controladores listos.")
        self.poses = load_arm_poses(SRDF_PATH)

    def _send(self, client, joints, positions, secs):
        traj = JointTrajectory()
        traj.joint_names = joints
        pt = JointTrajectoryPoint()
        pt.positions = [float(p) for p in positions]
        pt.time_from_start = Duration(sec=int(secs), nanosec=int((secs % 1) * 1e9))
        traj.points = [pt]
        goal = FollowJointTrajectory.Goal()
        goal.trajectory = traj
        fut = client.send_goal_async(goal)
        rclpy.spin_until_future_complete(self, fut)
        gh = fut.result()
        if not gh.accepted:
            self.get_logger().error("Goal rechazado.")
            return False
        res_fut = gh.get_result_async()
        rclpy.spin_until_future_complete(self, res_fut)
        return True

    def go_arm(self, pose_name):
        if pose_name not in self.poses:
            self.get_logger().error(f"Pose '{pose_name}' no esta en el SRDF.")
            return False
        vals = self.poses[pose_name]
        positions = [vals[j] for j in ARM_JOINTS]
        self.get_logger().info(f"Brazo -> {pose_name}")
        return self._send(self.arm, ARM_JOINTS, positions, ARM_MOVE_TIME)

    def go_grip(self, angle):
        self.get_logger().info(f"Gripper -> {angle:.2f} rad")
        return self._send(self.grip, GRIP_JOINTS, [angle] * 6, GRIP_MOVE_TIME)

    def spawn_obj(self, name, xyz, rpy=(0.0, 0.0, 0.0)):
        sdf = os.path.join(WS, "src", "robot_cell", "robot_description_ur3", "models",
                        name, f"{name}.sdf")
        # borra por si quedo una instancia previa (ignora error)
        self.delete_obj(name, quiet=True)
        subprocess.run(
            ["ros2", "run", "ros_gz_sim", "create", "-file", sdf,
            "-name", name,
            "-x", str(xyz[0]), "-y", str(xyz[1]), "-z", str(xyz[2]),
            "-R", str(rpy[0]), "-P", str(rpy[1]), "-Y", str(rpy[2])],
            check=False,
        )
    def delete_obj(self, name, quiet=False):
            subprocess.run(
                ["gz", "service", "-s", f"/world/{WORLD_NAME}/remove",
                 "--reqtype", "gz.msgs.Entity", "--reptype", "gz.msgs.Boolean",
                 "--timeout", "3000", "--req", f'name: "{name}" type: MODEL'],
                check=False,
                stdout=(subprocess.DEVNULL if quiet else None),
                stderr=(subprocess.DEVNULL if quiet else None),
            )

"""    def spawn_obj(self, name, xyz):
        sdf = os.path.join(WS, "src","robot_cell", "robot_description_ur3", "models",
                           name, f"{name}.sdf")
        # borra por si quedo una instancia previa (ignora error)
        self.delete_obj(name, quiet=True)
        subprocess.run(
            ["ros2", "run", "ros_gz_sim", "create", "-file", sdf,
             "-name", name, "-x", str(xyz[0]), "-y", str(xyz[1]), "-z", str(xyz[2])],
            check=False,
        )
"""
  


def main():
    rclpy.init()
    node = GraspTester()

    obj_name = f"{SHAPE}_{SIZE}"
    new_file = not os.path.exists(CSV_PATH)
    f = open(CSV_PATH, "a", newline="")
    writer = csv.writer(f)
    if new_file:
        writer.writerow(["tipo_agarre", "forma", "tamano_mm", "intento", "exito"])

    try:
        for g in GRASPS:
            for rep in range(1, N_REPS + 1):
                print("\n" + "=" * 60)
                print(f" {g['tipo'].upper()}  |  {obj_name}  |  intento {rep}/{N_REPS}")
                print("=" * 60)

                node.go_arm(HOME_POSE)
                #node.spawn_obj(obj_name, g["xyz"])  # 0) spawnea el objeto
                node.spawn_obj(obj_name, g["xyz"], SPAWN_RPY)   # 0) spawnea el objeto
                node.go_grip(OPEN_ANGLE)

                if(g["pose"]=="init" or g["pose"]=="init_1"):
                    node.go_arm(ACERCAMIENTO_CENITAL) 
                else:
                    node.go_arm(ACERCAMIENTO_LATERAL) 

                node.go_arm(g["pose"])          # 1) posiciona el brazo

                time.sleep(SETTLE_TIME)
                node.go_grip(CLOSE_ANGLE)        # 3) cierra

                if(g["pose"]=="init" or g["pose"]=="init_1"):
                    node.go_arm(ACERCAMIENTO_CENITAL) 
                    node.go_arm(INTER_POSE1) 
                    node.go_arm(DROP_POSE1)  # 4) levanta/mueve
                else:
                    node.go_arm(INTER_POSE2) 
                    node.go_arm(DROP_POSE2)  # 4) levanta/mueve
        
                

                # 5) juicio manual
                ans = ""
                while ans not in ("0", "1"):
                    ans = input(">>> Exito del agarre? (1 = si, 0 = no): ").strip()
                writer.writerow([g["tipo"], SHAPE, SIZE, rep, ans])
                f.flush()

                
                node.go_grip(OPEN_ANGLE)
                node.delete_obj(obj_name)
        node.go_arm(HOME_POSE)
        print(f"\nListo. Resultados en: {CSV_PATH}")
    except KeyboardInterrupt:
        print("\nInterrumpido por el usuario.")
    finally:
        f.close()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
