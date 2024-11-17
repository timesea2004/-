import cv2
import numpy as np

def detect_black_circle_centers(image_path, black_threshold=30):
    """
    检测图像中的黑色圆形并输出圆心坐标。

    :param image_path: 输入图像的路径。
    :param black_threshold: 判断黑色的颜色阈值（0-255），默认值为30。
    :return: 圆心坐标的列表。
    """
    # 读取图像
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Image not found at {image_path}")

    # 转换为灰度图像
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 应用高斯模糊来减少噪声
    blurred = cv2.GaussianBlur(gray, (9, 9), 2)

    # 使用霍夫圆变换检测圆形
    circles = cv2.HoughCircles(
        blurred,
        cv2.HOUGH_GRADIENT,
        dp=1.2,
        minDist=30,
        param1=50,
        param2=30,
        minRadius=10,
        maxRadius=0
    )

    # 如果检测到了圆，则处理它们
    if circles is not None:
        # 将检测到的圆参数转换为整数
        circles = np.round(circles[0, :]).astype("int")
        black_centers = []

        # 遍历所有检测到的圆
        for (x, y, r) in circles:
            # 获取圆心坐标
            center = (x, y)
            # 获取圆心处的像素颜色（B, G, R）
            b, g, r = image[center]
            # 判断圆心是否为黑色
            if b < black_threshold and g < black_threshold and r < black_threshold:
                black_centers.append(center)

        # 输出黑色圆心的坐标
        for center in black_centers:
            print(f"Black circle center detected at: {center}")

        return black_centers
    else:
        print("No circles detected.")
        return []

image_path = "E:\python project\picture-detect\canvey.bmp"  # 替换为你的图片路径
black_centers = detect_black_circle_centers(image_path)