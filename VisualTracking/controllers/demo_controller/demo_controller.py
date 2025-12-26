"""demo controller."""
from controller import Robot, Motor, Camera

# ---------------------------
# 创建机器人实例
# ---------------------------
robot = Robot()
timestep = int(robot.getBasicTimeStep())

# ---------------------------
# 获取左右电机
# ---------------------------
left_motor = robot.getDevice('MotorLeft')
right_motor = robot.getDevice('MotorRight')
left_motor.setPosition(float('inf'))
right_motor.setPosition(float('inf'))
left_motor.setVelocity(0.0)
right_motor.setVelocity(0.0)

# ---------------------------
# 启用摄像头
# ---------------------------
camera = robot.getDevice('camera')
camera.enable(timestep)

# ---------------------------
# 主循环
# ---------------------------
max_speed = min(left_motor.getMaxVelocity(), right_motor.getMaxVelocity())

while robot.step(timestep) != -1:
    # 前进
    left_motor.setVelocity(0.1*max_speed)
    right_motor.setVelocity(-0.1*max_speed)

    # 获取图像缓冲区
    image = camera.getImage()