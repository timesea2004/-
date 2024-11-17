import cv2
import numpy as np

def detect_defect_contours(image_path):
    # 读取图片
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Image not found at {image_path}")

    # 转换为灰度图
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 应用高斯模糊来减少噪声
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # 使用Otsu's二值化方法自动确定阈值
    _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # 寻找轮廓
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 创建一个空白图像用于绘制瑕疵和中心点
    defect_image = image.copy()

    defect_centers = []

    for contour in contours:
        # 假设最大的轮廓是药片本身，我们可以忽略它
        # 如果你想检测药片内部的缺陷，你需要进一步处理每个轮廓内部的像素
        # 这里我们简化问题，只检测药片外部的“缺陷”（可能是背景噪声或真正的外部缺陷）
        # 或者，你可以根据轮廓大小、形状等特征来区分药片和真正的缺陷

        # 暂时，我们假设所有小轮廓都是缺陷（这是一个简化的假设）
        if cv2.contourArea(contour) < 1000:  # 这是一个示例阈值，需要根据实际情况调整
            # 计算轮廓的矩
            M = cv2.moments(contour)
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
            else:
                cX, cY = 0, 0

            # 在缺陷中心画红点
            cv2.circle(defect_image, (cX, cY), 5, (0, 0, 255), -1)
            defect_centers.append((cX, cY))

        # 如果你想进一步分析每个轮廓内部的像素来检测内部缺陷，
        # 你可以在这里添加额外的代码来处理每个轮廓内部的区域。
        # 例如，你可以使用形态学操作、连通域分析等。

    # 显示结果
    cv2.namedWindow('Defects', cv2.WINDOW_NORMAL)
    cv2.imshow("Defects", defect_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # 输出红点的位置
    for center in defect_centers:
        print(f"Defect center: ({center[0]}, {center[1]})")


image_path = "E:\python project\picture-detect\canvey.bmp"  # 替换为你的图片路径
detect_defect_contours(image_path)