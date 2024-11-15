import cv2
import numpy as np

def detect_defects(image_path):
    # 读取图像
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("图像加载失败，请检查路径是否正确")

    # 转换为灰度图
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 应用高斯模糊来减少噪声
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # 使用Otsu's二值化方法将图像转换为二值图像
    _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # 反转图像，使得药片区域为白色，背景为黑色（假设药片是亮的）
    binary = cv2.bitwise_not(binary)

    # 查找轮廓
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 创建一个用于绘制瑕疵的副本图像
    defect_image = image.copy()

    # 存储瑕疵药片的位置（假设为轮廓的边界框）
    defect_positions = []

    for contour in contours:
        # 计算轮廓的边界框
        x, y, w, h = cv2.boundingRect(contour)

        # 假设药片区域应该有一定的尺寸范围，过滤掉太小的区域（可能是噪声）
        if w > 10 and h > 10:  # 这些值可能需要根据实际情况调整
            # 在原图上绘制轮廓（用于可视化瑕疵）
            cv2.rectangle(defect_image, (x, y), (x + w, y + h), (0, 0, 255), 2)

            # 在药片内部查找瑕疵（例如，暗斑或亮点）
            # 这里简单地使用阈值分割来找到与药片主体颜色不同的区域
            mask = np.zeros_like(gray)
            cv2.drawContours(mask, [contour], -1, 255, -1)  # 填充轮廓内部为白色
            mask_inv = cv2.bitwise_not(mask)  # 反转掩码，得到药片外部区域

            # 计算药片内部区域的灰度值直方图，并找到可能的瑕疵阈值
            # 这里为了简化，直接使用全局阈值进行分割，可能需要根据实际情况调整
            drug_area = cv2.bitwise_and(gray, gray, mask=mask)
            _, defect_binary = cv2.threshold(drug_area, 200, 255, cv2.THRESH_BINARY_INV)  # 假设瑕疵比药片暗

            # 查找瑕疵轮廓
            defect_contours, _ = cv2.findContours(defect_binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            for defect_contour in defect_contours:
                # 在副本图像上绘制瑕疵轮廓
                cv2.drawContours(defect_image, [defect_contour], -1, (0, 255, 0), 1)

            # 保存瑕疵药片的位置
            defect_positions.append((x, y, w, h))

    # 显示结果图像
    cv2.namedWindow('Defective Pills',cv2.WINDOW_NORMAL)
    cv2.imshow('Defective Pills', defect_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # 输出瑕疵药片的位置
    for pos in defect_positions:
        print(f"Defective pill position: x={pos[0]}, y={pos[1]}, width={pos[2]}, height={pos[3]}")

# 调用函数并传入图像路径
detect_defects('E:\python project\picture-detect\image.png')  # 替换为你的图像路径