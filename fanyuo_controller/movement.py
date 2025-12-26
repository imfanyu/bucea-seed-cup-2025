# movement.py
class Movement:
    def __init__(self, robot, Kp, Kd, left_motor_name='left_motor', right_motor_name='right_motor'):
        self.left_motor = robot.getDevice(left_motor_name)
        self.right_motor = robot.getDevice(right_motor_name)
        self.left_motor.setPosition(float('inf'))
        self.right_motor.setPosition(float('inf'))
        self.left_motor.setVelocity(0.0)
        self.right_motor.setVelocity(0.0)

        # 获取电机最大速度
        self.max_speed = min(self.left_motor.getMaxVelocity(), self.right_motor.getMaxVelocity())

        self.prev_error = 0
        self.Kp = Kp
        self.Kd = Kd

    def set_speed(self, speed_left, speed_right):
        """
        设置左右轮速度，输入参数范围 -100~100，映射到实际最大速度
        """
        # 限制输入范围
        speed_left = max(-100, min(speed_left, 100))
        speed_right = max(-100, min(speed_right, 100))

        # 映射到实际最大速度
        velocity_left = speed_left / 100 * self.max_speed
        velocity_right = speed_right / 100 * self.max_speed

        self.left_motor.setVelocity(velocity_left)
        self.right_motor.setVelocity(velocity_right)

    def pid_control(self,x_vals):
        if x_vals:
            x_avg = sum(x_vals) / len(x_vals)  # 平均 x 值
            center = 188 // 2
            error = x_avg - center
            error = -error

            # 计算修正量（PD）
            derivative = error - self.prev_error
            self.prev_error = error
            correction = self.Kp * error + self.Kd * derivative

            # 限制修正量，防止左右轮速度差过大
            max_correction = 20
            correction = max(min(correction, max_correction), -max_correction)

            base_speed = 20
            left_speed = max(min(base_speed - correction, 30), 10)
            right_speed = max(min(base_speed + correction, 30), 10)
        else:
            # 没有有效中线，保持前进
            left_speed = 20
            right_speed = 20

        # 3. 设置电机速度
        self.set_speed(2 * left_speed, 2 * right_speed)
