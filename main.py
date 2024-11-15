import cv2
import numpy as np

# -- coding: utf-8 --

import sys
import time
from ctypes import *

#---------------------------------------------------------------------------------------------------------------
sys.path.append("E:\python project\picture-detect\MvImport")
from MvCameraControl_class import *

if __name__ == "__main__":
    deviceList = MV_CC_DEVICE_INFO_LIST()
    tlayerType = MV_GIGE_DEVICE | MV_USB_DEVICE

    # ch:枚举设备 | en:Enum device
    ret = MvCamera.MV_CC_EnumDevices(tlayerType, deviceList)
    if ret != 0:
        print("enum devices fail! ret[0x%x]" % ret)
        sys.exit()

    if deviceList.nDeviceNum == 0:
        print("find no device!")
        sys.exit()

    print("find %d devices!" % deviceList.nDeviceNum)

    for i in range(0, deviceList.nDeviceNum):
        mvcc_dev_info = cast(deviceList.pDeviceInfo[i], POINTER(MV_CC_DEVICE_INFO)).contents
        if mvcc_dev_info.nTLayerType == MV_GIGE_DEVICE:
            print("\ngige device: [%d]" % i)
            strModeName = ""
            for per in mvcc_dev_info.SpecialInfo.stGigEInfo.chModelName:
                strModeName = strModeName + chr(per)
            print("device model name: %s" % strModeName)

            nip1 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0xff000000) >> 24)
            nip2 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x00ff0000) >> 16)
            nip3 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x0000ff00) >> 8)
            nip4 = (mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x000000ff)
            print("current ip: %d.%d.%d.%d\n" % (nip1, nip2, nip3, nip4))
        elif mvcc_dev_info.nTLayerType == MV_USB_DEVICE:
            print("\nu3v device: [%d]" % i)
            strModeName = ""
            for per in mvcc_dev_info.SpecialInfo.stUsb3VInfo.chModelName:
                if per == 0:
                    break
                strModeName = strModeName + chr(per)
            print("device model name: %s" % strModeName)

            strSerialNumber = ""
            for per in mvcc_dev_info.SpecialInfo.stUsb3VInfo.chSerialNumber:
                if per == 0:
                    break
                strSerialNumber = strSerialNumber + chr(per)
            print("user serial number: %s" % strSerialNumber)

    nConnectionNum = input("please input the number of the device to connect:")

    if int(nConnectionNum) >= deviceList.nDeviceNum:
        print("intput error!")
        sys.exit()

    # ch:创建相机实例 | en:Creat Camera Object
    cam = MvCamera()

    # ch:选择设备并创建句柄 | en:Select device and create handle
    stDeviceList = cast(deviceList.pDeviceInfo[int(nConnectionNum)], POINTER(MV_CC_DEVICE_INFO)).contents

    ret = cam.MV_CC_CreateHandle(stDeviceList)
    if ret != 0:
        print("create handle fail! ret[0x%x]" % ret)
        sys.exit()

    # ch:打开设备 | en:Open device
    ret = cam.MV_CC_OpenDevice(MV_ACCESS_Exclusive, 0)
    if ret != 0:
        print("open device fail! ret[0x%x]" % ret)
        sys.exit()

    # ch:探测网络最f佳包大小(只对GigE相机有效) | en:Detection network optimal package size(It only works for the GigE camera)
    if stDeviceList.nTLayerType == MV_GIGE_DEVICE:
        nPacketSize = cam.MV_CC_GetOptimalPacketSize()
        if int(nPacketSize) > 0:
            ret = cam.MV_CC_SetIntValue("GevSCPSPacketSize", nPacketSize)
            if ret != 0:
                print("Warning: Set Packet Size fail! ret[0x%x]" % ret)
        else:
            print("Warning: Get Packet Size fail! ret[0x%x]" % nPacketSize)

    # ch:设置触发模式为off | en:Set trigger mode as off
    ret = cam.MV_CC_SetEnumValue("TriggerMode", MV_TRIGGER_MODE_OFF)
    if ret != 0:
        print("set trigger mode fail! ret[0x%x]" % ret)
        sys.exit()

    # ch:获取数据包大小 | en:Get payload size
    stParam = MVCC_INTVALUE()
    memset(byref(stParam), 0, sizeof(MVCC_INTVALUE))

    ret = cam.MV_CC_GetIntValue("PayloadSize", stParam)
    if ret != 0:
        print("get payload size fail! ret[0x%x]" % ret)
        sys.exit()
    nPayloadSize = stParam.nCurValue

    # ch:开始取流 | en:Start grab image
    start_time = time.time()

    ret = cam.MV_CC_StartGrabbing()
    if ret != 0:
        print("start grabbing fail! ret[0x%x]" % ret)
        sys.exit()
    stDeviceList = MV_FRAME_OUT_INFO_EX()
    memset(byref(stDeviceList), 0, sizeof(stDeviceList))
    data_buf = (c_ubyte * nPayloadSize)()
    ret = cam.MV_CC_GetOneFrameTimeout(byref(data_buf), nPayloadSize, stDeviceList, 1000)
    if ret == 0:
        # Stop = time()
        # print(Stop - start)
        print("get one frame: Width[%d], Height[%d], nFrameNum[%d]" % (
        stDeviceList.nWidth, stDeviceList.nHeight, stDeviceList.nFrameNum))

        stConvertParam = MV_SAVE_IMAGE_PARAM_EX()
        stConvertParam.nWidth = stDeviceList.nWidth
        stConvertParam.nHeight = stDeviceList.nHeight
        stConvertParam.pData = data_buf
        stConvertParam.nDataLen = stDeviceList.nFrameLen
        stConvertParam.enPixelType = stDeviceList.enPixelType

        # MV_Image_Undefined  = 0, //未定义
        #   MV_Image_Bmp        = 1, //BMP图片
        #   MV_Image_Jpeg       = 2, //JPEG图片
        #   MV_Image_Png        = 3, //PNG图片，暂不支持
        #   MV_Image_Tif        = 4, //TIF图片，暂不支持

        # jpg参数
        # stConvertParam.nJpgQuality   = 99  # 压缩质量选择范围[50-99]
        # file_path = "save.jpg"
        # stConvertParam.enImageType = MV_Image_Jpeg
        # bmpsize = nPayloadSize

        file_path = "save.bmp"
        stConvertParam.enImageType = MV_Image_Bmp

        bmpsize = stDeviceList.nWidth * stDeviceList.nHeight * 3 + 54

        stConvertParam.nBufferSize = bmpsize
        bmp_buf = (c_ubyte * bmpsize)()
        stConvertParam.pImageBuffer = bmp_buf

        ret = cam.MV_CC_SaveImageEx2(stConvertParam)
        if ret != 0:
            print("save file executed failed0:! ret[0x%x]" % ret)
            del data_buf
            sys.exit()
        end_time = time.time()
        print(start_time - end_time)
        # print(stop - start)
        file_open = open(file_path.encode('ascii'), 'wb+')
        try:
            img_buff = (c_ubyte * stConvertParam.nImageLen)()
            cdll.msvcrt.memcpy(byref(img_buff), stConvertParam.pImageBuffer, stConvertParam.nImageLen)
            file_open.write(img_buff, )
            print(img_buff)
        except:
            raise Exception("save file executed failed1::%s" % e.message)
        finally:
            file_open.close()


    else:
        print("get one frame fail, ret[0x%x]" % ret)

    # ch:停止取流 | en:Stop grab image
    ret = cam.MV_CC_StopGrabbing()
    if ret != 0:
        print("stop grabbing fail! ret[0x%x]" % ret)
        del data_buf
        sys.exit()

    # ch:关闭设备 | Close device
    ret = cam.MV_CC_CloseDevice()
    if ret != 0:
        print("close deivce fail! ret[0x%x]" % ret)
        del data_buf
        sys.exit()

    # ch:销毁句柄 | Destroy handle
    ret = cam.MV_CC_DestroyHandle()
    if ret != 0:
        print("destroy handle fail! ret[0x%x]" % ret)
        del data_buf
        sys.exit()

    del data_buf

# --------------------------------------------------------------------------------------------------------------

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