# vision.py
from controller import Camera
import numpy as np
import cv2

WHITE = 255
BLACK = 0

class Vision:
    def __init__(self, robot, camera_name, timestep, width=188, height=120):
        # ---------------- 摄像头初始化 ----------------
        self.camera = robot.getDevice(camera_name)
        self.camera.enable(timestep)
        self.width = width
        self.height = height

        # ---------------- 图像数据 ----------------
        self.img_origin = None
        self.binary_img = None

        # ---------------- 左右线点列表 ----------------
        self.points_l = [[0, 0] for _ in range(height * 3)]
        self.points_r = [[0, 0] for _ in range(height * 3)]

        # ---------------- 八领域生长方向 ----------------
        self.dir_l = [0 for _ in range(height * 3)]
        self.dir_r = [0 for _ in range(height * 3)]

        # ---------------- 中线 ----------------
        self.middle_line = [0 for _ in range(height)]

        # ---------------- 左右起点 ----------------
        self.start_point_l = [0, 0]
        self.start_point_r = [0, 0]

        # ---------------- 左右线统计 ----------------
        self.data_stastics_l = 0
        self.data_stastics_r = 0

        # ---------------- 生长方向计数 ----------------
        self.r1 = self.r2 = self.r3 = self.r4 = self.r5 = self.r6 = self.r7 = self.r8 = 0
        self.l1 = self.l2 = self.l3 = self.l4 = self.l5 = self.l6 = self.l7 = self.l8 = 0

        self.left_2_growth_direction = 0
        self.left_5_growth_direction = 0
        self.right_2_growth_direction = 0
        self.right_5_growth_direction = 0

        self.l_growth_direction_flag = 0
        self.r_growth_direction_flag = 0

        # ---------------- 左右线数组 ----------------
        self.left = [0 for _ in range(height)]
        self.right = [0 for _ in range(height)]

        # ---------------- 丢线变量 ----------------
        self.left_lost_num = 0
        self.Lost_point_L_scan_line = 0
        self.Lost_left_Flag = 0
        self.S_left_lost_num = 0
        self.S_left_lost_Flag = 0

        self.right_lost_num = 0
        self.Lost_point_R_scan_line = 0
        self.Lost_right_Flag = 0
        self.S_right_lost_num = 0
        self.S_right_lost_Flag = 0

        self.memory_circle = 0
        self.flag_circle = 0
        self.flag_cross = 0
        self.memory2state = 1

        # ------- 新增：视频录制器 -------
        # filename：输出文件名   fps：显示帧率   size：输出画面尺寸
        self.recorder = cv2.VideoWriter(
            "output.avi",                      # 保存的文件名
            cv2.VideoWriter_fourcc(*"XVID"),   # 编码格式
            30,                                # 帧率（你可以调，比如30FPS）
            (self.width*4, self.height*4)      # 输出画面大小（跟显示一致）
        )

    # ------------------- 获取摄像头图像 -------------------
    def get_image(self):
        img = self.camera.getImage()
        if img is None:
            return None

        gray_img = [[0 for _ in range(self.width)] for _ in range(self.height)]
        for y in range(self.height):
            for x in range(self.width):
                idx = 4 * (y * self.width + x)  # BGRA
                B = img[idx]
                G = img[idx + 1]
                R = img[idx + 2]
                gray_img[y][x] = int(0.299 * R + 0.587 * G + 0.114 * B)
        self.img_origin = gray_img
        return gray_img

    # ------------------- 二值化 -------------------
    def binaryzation(self, threshold=127, border=True):
        if self.img_origin is None:
            return None

        # 二值化
        self.binary_img = [[WHITE if self.img_origin[y][x] >= threshold else BLACK
                            for x in range(self.width)] for y in range(self.height)]

        # 如果需要添加边框
        if border:
            for y in range(self.height):
                for x in range(self.width):
                    # 上下边界
                    if y == 0 or y == 1 :
                        self.binary_img[y][x] = BLACK
                    # 左右边界
                    if x == 0 or x == 1 or x == self.width - 1 or x == self.width - 2:
                        self.binary_img[y][x] = BLACK

        return self.binary_img

    # ------------------- 寻找左右起点 -------------------
    def get_start_point(self, start_row, border_min=0, border_max=None):
        if border_max is None:
            border_max = self.width - 1
        l_found = r_found = 0

        # 左起点
        for i in range(self.width // 2 + 50, border_min, -1):
            if self.binary_img[start_row][i] == WHITE and self.binary_img[start_row][i - 1] == BLACK:
                self.start_point_l = [i, start_row]
                l_found = 1
                break


        # 右起点
        for i in range(self.width // 2 - 50, border_max):
            if self.binary_img[start_row][i] == WHITE and self.binary_img[start_row][i + 1] == BLACK:
                self.start_point_r = [i, start_row]
                r_found = 1
                break

        if l_found and r_found:
            return 1
        else:
            return 0

    # ------------------- 八领域搜索 -------------------
    def search_l_r(self, max_iter=100, Endline=[0]):
        l_count = 0
        r_count = 0
        center_l = self.start_point_l.copy()
        center_r = self.start_point_r.copy()

        seeds_l = [[0, 1], [-1, 1], [-1, 0], [-1, -1], [0, -1], [1, -1], [1, 0], [1, 1]]
        seeds_r = [[0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1]]

        while max_iter > 0:
            max_iter -= 1

            # -------- 左线 --------
            if l_count >= len(self.points_l):
                self.points_l.append(center_l.copy())
            else:
                self.points_l[l_count] = center_l.copy()
            l_count += 1

            temp_l = []
            for i in range(8):
                nx, ny = center_l[0] + seeds_l[i][0], center_l[1] + seeds_l[i][1]
                nx1, ny1 = center_l[0] + seeds_l[(i + 1) & 7][0], center_l[1] + seeds_l[(i + 1) & 7][1]
                if 0 <= ny < self.height and 0 <= nx < self.width and 0 <= ny1 < self.height and 0 <= nx1 < self.width:
                    if self.binary_img[ny][nx] == BLACK and self.binary_img[ny1][nx1] == WHITE:
                        temp_l.append([nx1, ny1])
                        self.dir_l[l_count - 1] = i
            if temp_l:
                center_l = min(temp_l, key=lambda p: p[1])

            # -------- 右线 --------
            if r_count >= len(self.points_r):
                self.points_r.append(center_r.copy())
            else:
                self.points_r[r_count] = center_r.copy()
            r_count += 1

            temp_r = []
            for i in range(8):
                nx, ny = center_r[0] + seeds_r[i][0], center_r[1] + seeds_r[i][1]
                nx1, ny1 = center_r[0] + seeds_r[(i + 1) & 7][0], center_r[1] + seeds_r[(i + 1) & 7][1]
                if 0 <= ny < self.height and 0 <= nx < self.width and 0 <= ny1 < self.height and 0 <= nx1 < self.width:
                    if self.binary_img[ny][nx] == BLACK and self.binary_img[ny1][nx1] == WHITE:
                        temp_r.append([nx, ny])
                        self.dir_r[r_count - 1] = i
            if temp_r:
                center_r = min(temp_r, key=lambda p: p[1])

            # -------- 退出条件 --------
            if l_count >= 3 and r_count >= 3:
                if (self.points_l[l_count - 1] == self.points_l[l_count - 2] == self.points_l[l_count - 3]) or \
                   (self.points_r[r_count - 1] == self.points_r[r_count - 2] == self.points_r[r_count - 3]):
                    break
                if abs(self.points_r[r_count - 1][0] - self.points_l[l_count - 1][0]) < 2 and \
                   abs(self.points_r[r_count - 1][1] - self.points_l[l_count - 1][1]) < 2:
                    Endline[0] = (self.points_r[r_count - 1][1] + self.points_l[l_count - 1][1]) // 2
                    break

        self.data_stastics_l = l_count
        self.data_stastics_r = r_count

    # ------------------- 生长方向统计 -------------------
    def growth_direction(self):
        self.r1 = self.r2 = self.r3 = self.r4 = self.r5 = self.r6 = self.r7 = self.r8 = 0
        self.l1 = self.l2 = self.l3 = self.l4 = self.l5 = self.l6 = self.l7 = self.l8 = 0
        self.left_2_growth_direction = 0
        self.left_5_growth_direction = 0
        self.right_2_growth_direction = 0
        self.right_5_growth_direction = 0

        # 左
        for i in range(self.data_stastics_l):
            val = self.dir_l[i]
            if val == 2: self.left_2_growth_direction += 1
            if val == 5: self.left_5_growth_direction += 1
            if val == 0: self.l8 += 1
            elif val == 1: self.l1 += 1
            elif val == 2: self.l2 += 1
            elif val == 3: self.l3 += 1
            elif val == 4: self.l4 += 1
            elif val == 5: self.l5 += 1
            elif val == 6: self.l6 += 1
            elif val == 7: self.l7 += 1

        # 右
        for i in range(self.data_stastics_r):
            val = self.dir_r[i]
            if val == 2: self.right_2_growth_direction += 1
            if val == 5: self.right_5_growth_direction += 1
            if val == 0: self.r8 += 1
            elif val == 1: self.r1 += 1
            elif val == 2: self.r2 += 1
            elif val == 3: self.r3 += 1
            elif val == 4: self.r4 += 1
            elif val == 5: self.r5 += 1
            elif val == 6: self.r6 += 1
            elif val == 7: self.r7 += 1

        # 左右判断
        self.l_growth_direction_flag = 1 if self.right_2_growth_direction > 30 and self.right_5_growth_direction > 30 else 0
        self.r_growth_direction_flag = 1 if self.right_2_growth_direction > 30 and self.right_5_growth_direction > 30 else 0

    # ------------------- 左右线提取 -------------------
    def get_left(self):
        h = self.height - 2
        self.left = [0 for _ in range(self.height)]
        for i in range(self.data_stastics_l):
            y = self.points_l[i][1]
            self.left[y] = self.points_l[i][0]

    def get_right(self):
        h = self.height - 2
        self.right = [0 for _ in range(self.height)]
        for i in range(self.data_stastics_r):
            y = self.points_r[i][1]
            self.right[y] = self.points_r[i][0]

    # ------------------- 中线 -------------------
    def get_middle_line(self):
        self.middle_line = [0 for _ in range(self.height)]
        for y in range(self.height):
            if self.left[y] != 0 and self.right[y] != 0:
                self.middle_line[y] = (self.left[y] + self.right[y]) // 2

    def adding_line1(self, choice, startX, startY, endX, endY):
        # 计算斜率和截距 (x = k*y + b)
        if endY == startY:
            return  # 防止除 0
        k = (endX - startX) / (endY - startY)
        b = startX - k * startY

        if choice == 1:  # 左补线
            for y in range(startY, endY):
                x = int(k * y + b)
                if x > 185:
                    x = 185
                elif x < 2:
                    x = 2
                self.left[y] = x

        elif choice == 2:  # 右补线
            for y in range(startY, endY):
                x = int(k * y + b)
                if x > 185:
                    x = 185
                elif x < 2:
                    x = 2
                self.right[y] = x

    def calculate_borden(self,choice):
        count = 0
        if choice == 1:  # 左边
            for i in range(2, self.height):
                if self.left[i] == 2:
                    count += 1
        else:  # 右边
            for i in range(2, self.height):
                if self.right[i] == 186:
                    count += 1
        return count

    def circle(self):
        flag_l = 0
        flag_r = 1
        flag_r2 = 1
        if not self.flag_circle:
            for i in range(self.height-1,20,-1):
                if self.left[i] - self.left[i-5] > 3 and ( self.left[i-5] == self.left[i-6] == self.left[i-7] == 2) :
                    flag_l = 1
            for i in range(self.height - 30, 20, -1):
                if self.right[i] > 170:
                    flag_r = 0
            for i in range(self.height - 1, 20, -1):
                if self.right[i]-self.right[i-1] > 1:
                    flag_r2 = 0
            if flag_l == 1 and flag_r == 1 and flag_r2 == 1:
                self.flag_circle = 1
                self.memory_circle = 1
                print("发现圆环?")

        if self.memory_circle == 1:
            print("进入状态1")#还没入环，左侧补线
            End_left = 0
            Start_left = 0
            for i in range(self.height-1,20,-1):
                if self.left[i] - self.left[i-5] > 3 and ( self.left[i-5] == self.left[i-6] == self.left[i-7] == 2) :
                    End_left = i
                    break
            if self.left[50] ==2 and self.left[118] > 2 and self.left[117] > 2 and self.left[116] > 2 :
                self.memory_circle = 2
            for i in range(1,self.height):
                if self.left[i]==2:
                    Start_left = i
                    break
            # self.adding_line1(1,self.left[Start_left]+50,Start_left-20,self.left[End_left],End_left)
            self.adding_line1(1,36,80,15,118)#左补

        if self.memory_circle == 2:
            if self.memory2state == 1:
                if self.calculate_borden(2)>80:self.memory2state=2
            if self.memory2state == 2:
                if self.calculate_borden(2) < 20:
                    self.memory_circle=3
                    self.memory2state=1
            print("进入状态2")#封右侧，入环
            Start_left = 0
            for i in range(self.height):
                if self.left[i] == 2:
                    Start_left = i
                    break
            self.adding_line1(2,self.left[Start_left]+40,Start_left,self.right[118],118)

        if self.memory_circle == 3:
            print("进入状态3")#环内
            print(f"{self.calculate_borden(1)}")
            if self.calculate_borden(1)>70:
                self.memory_circle = 4
        if self.memory_circle == 4:
            print("进入状态4")
            print(f"{self.calculate_borden(2)}")
            if self.memory2state == 1:
                if self.calculate_borden(2)>50:self.memory2state=2
            if self.memory2state == 2:
                if self.calculate_borden(2) < 20:
                    self.memory_circle=5
                    self.memory2state=1
                    return

            Start_left = 0
            for i in range(1, self.height):
                if self.left[i] == 2:
                    Start_left = i
                    break
            self.adding_line1(2, self.left[Start_left] + 100, Start_left, self.right[118], 118)
        if self.memory_circle == 5:
            print("进入状态5")
            print(f"{self.calculate_borden(1)}")
            if self.memory2state == 1:
                if self.calculate_borden(1)>90:self.memory2state=2
            if self.memory2state == 2:
                if self.calculate_borden(1) < 50:
                    self.memory_circle=0
                    self.flag_circle = 0
                    self.memory2state=1
                    return
        # if self.memory_circle == 6:
        #     print("进入状态6")
        #     print(f"{self.calculate_borden(1)}")
        #     Start_left = 0
        #     if not self.calculate_borden(1)> 30:
        #         return
        #     for i in range(1, self.height):
        #         if i < 100 and self.left[i] == 0 and self.left[i+1] > 2:
        #             Start_left = i
        #             break
        #     if Start_left == 0:
        #         return
        #     self.adding_line1(1, self.left[Start_left], Start_left,36, 118)

    # ------------------- 图像处理主函数 -------------------
    def process_image(self, threshold=127, start_row=118, max_iter=100):
        self.get_image()
        self.binaryzation(threshold)
        found = self.get_start_point(start_row)
        if found:
            Endline = [0]
            self.search_l_r(max_iter, Endline)
            self.get_left()
            self.get_right()
            self.growth_direction()

            self.circle()



            # self.adding_line1(1,36,80,15,118)#左补
            # self.adding_line1(2,151,80,175,118)#右补
            self.get_middle_line()
            # self.cross()
            # print(f"Left:{self.left}")
            # print(f"Right:{self.right}")


        else:
            print("未找到起点")

    def get_x_vals(self):
        return [self.middle_line[y] for y in range(106, 112) if self.middle_line[y] != 0]

    def img_show(self, img=None, window_name="Image", draw_lines=True, scale=4):
        if img is None:
            img = self.binary_img

        if img is None:
            print("No image to show!")
            return

        # 转为 numpy 数组
        img_np = np.array(img, dtype=np.uint8)

        # 转为 BGR 彩色图像用于绘制
        img_color = cv2.cvtColor(img_np, cv2.COLOR_GRAY2BGR)

        # 逐点绘制线条
        if draw_lines:
            for y in range(self.height):
                # 左线 - 红色 (B,G,R)
                x = self.left[y]
                if x != 0 and 0 <= x < self.width:
                    img_color[y, x] = [0, 0, 255]

                # 右线 - 绿色
                x = self.right[y]
                if x != 0 and 0 <= x < self.width:
                    img_color[y, x] = [0, 255, 0]

                # 中线 - 蓝色
                x = self.middle_line[y]
                if x != 0 and 0 <= x < self.width:
                    img_color[y, x] = [255, 0, 0]

        # 放大图像
        img_color_large = cv2.resize(
            img_color,
            (self.width * scale, self.height * scale),
            interpolation=cv2.INTER_NEAREST
        )

        cv2.imshow(window_name, img_color_large)
        cv2.waitKey(1)
        self.recorder.write(img_color_large)

