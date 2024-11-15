import cv2
import numpy as np

# 读取图片
image = cv2.imread('E:\python project\picture-detect\image.jpg')
# 转换为灰度图像
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# 应用高斯模糊来减少噪声和细节层次
blurred = cv2.GaussianBlur(gray, (5, 5), 0)

# 使用Canny边缘检测
edged = cv2.Canny(blurred, 50, 150)

# 查找轮廓
contours, _ = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# 在原始图像上绘制轮廓，并计算中心位置
output = image.copy()
centers = []
for contour in contours:
    # 计算轮廓的矩
    M = cv2.moments(contour)

    # 如果矩的m00不为0，则计算中心位置
    if M['m00'] != 0:
        cX = int(M['m10'] / M['m00'])
        cY = int(M['m01'] / M['m00'])
    else:
        # 如果m00为0，则选择一个默认的中心位置（这里可以选择轮廓的任意点，但这里我们简单设为(0,0)）
        cX, cY = 0, 0
        # 注意：在实际应用中，当m00为0时可能需要特殊处理，因为这意味着轮廓可能是一个点或无效轮廓

    # 将中心位置添加到列表中
    centers.append((cX, cY))

    # 在图像上绘制中心（以红色小圆点表示）
    cv2.circle(output, (cX, cY), 5, (0, 0, 255), -1)

# 显示结果
cv2.imshow('Contours with Centers', output)
cv2.waitKey(0)
cv2.destroyAllWindows()

# 打印中心位置
for i, (cX, cY) in enumerate(centers):
    print(f'Center of contour {i + 1}: ({cX}, {cY})')