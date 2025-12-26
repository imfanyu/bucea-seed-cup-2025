"""fanyuo controller."""

from controller import Robot
from movement import Movement
from vision import Vision

# ---------------------------
# 创建机器人实例
# ---------------------------
robot = Robot()
timestep = int(robot.getBasicTimeStep())

# ---------------------------
# 初始化机器人及电机控制
# ---------------------------
movement = Movement(robot, Kp=0.8, Kd=0.1 ,left_motor_name='MotorLeft', right_motor_name='MotorRight')

# ---------------------------
# 初始化视觉模块
# ---------------------------
vision = Vision(robot, camera_name='camera', timestep=timestep)

# ---------------------------
# 主循环
# ---------------------------
while robot.step(timestep) != -1:
    # 1. 图像处理
    vision.process_image()
    vision.img_show()
    # 2. PD 调整速度
    movement.pid_control(vision.get_x_vals())