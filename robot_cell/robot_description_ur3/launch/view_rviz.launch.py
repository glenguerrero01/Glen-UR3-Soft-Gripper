from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command, PathJoinSubstitution, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    ur_type = LaunchConfiguration("ur_type")

    pkg_share = FindPackageShare("robot_description_ur3")
    xacro_file = PathJoinSubstitution([pkg_share, "urdf", "robot_cell.urdf.xacro"])
    rviz_config = PathJoinSubstitution([pkg_share, "rviz", "urdf.rviz"])

    robot_description = ParameterValue(
        Command(["xacro ", xacro_file, " ", "ur_type:=", ur_type]),
        value_type=str,
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            "ur_type",
            default_value="ur30",
            description="Modelo de UR a usar (ur3, ur5, ur10, ur16e, ur20, ur30, ...)",
        ),
        """Node(
            package="joint_state_publisher_gui",
            executable="joint_state_publisher_gui",
            name="joint_state_publisher_gui",
        ),"""
       Node(
            package="joint_state_publisher_gui",
            executable="joint_state_publisher_gui",
            name="joint_state_publisher_gui",
            parameters=[{
                "zeros": {
                    "ur3_shoulder_lift_joint": -1.5708,
                    "ur3_elbow_joint": 0.0,
                    "ur3_wrist_1_joint": -1.5708,
                    "ur3_wrist_2_joint": 0.0,
                    "ur3_wrist_3_joint": 0.0,
                }
            }],
        ),
        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            name="robot_state_publisher",
            parameters=[{"robot_description": robot_description}],
        ),
        Node(
            package="rviz2",
            executable="rviz2",
            name="rviz2",
            output="screen",
            arguments=["-d", rviz_config],
        ),
    ])
