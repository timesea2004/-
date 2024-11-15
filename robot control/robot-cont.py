import threading
from dobot_api import DobotApiDashboard, DobotApi, DobotApiMove, MyType
from time import sleep
import numpy as np

# 全局变量(当前坐标)
current_actual = None

def connect_robot():
    try:
        ip = "192.168.1.6"
        dashboard_p = 29999
        move_p = 30003
        feed_p = 30004
        print("正在建立连接...")
        dashboard = DobotApiDashboard(ip, dashboard_p)
        move = DobotApiMove(ip, move_p)
        feed = DobotApi(ip, feed_p)
        print(">.<连接成功>!<")
        return dashboard, move, feed
    except Exception as e:
        print(":(连接失败:(")
        raise e

def run_point(move: DobotApiMove, point_list: list):
    move.MovL(point_list[0], point_list[1], point_list[2], point_list[3])

def get_feed(feed: DobotApi):
    global current_actual
    hasRead = 0
    while True:
        data = bytes()
        while hasRead < 1440:
            temp = feed.socket_dobot.recv(1440 - hasRead)
            if len(temp) > 0:
                hasRead += len(temp)
                data += temp
        hasRead = 0

        a = np.frombuffer(data, dtype=MyType)
        if hex((a['test_value'][0])) == '0x123456789abcdef':

            # Refresh Properties
            current_actual = a["tool_vector_actual"][0]
            #print("tool_vector_actual:", current_actual)

        sleep(0.001)


def wait_arrive(point_list):
    global current_actual
    while True:
        is_arrive = True

        if current_actual is not None:
            for index in range(4):
                if (abs(current_actual[index] - point_list[index]) > 1):
                    is_arrive = False

            if is_arrive:
                return

        sleep(0.001)

if __name__ == '__main__':
    dashboard, move, feed = connect_robot()
    print("开始使能...")
    dashboard.EnableRobot()
    print("完成使能:)")
    feed_thread = threading.Thread(target=get_feed, args=(feed,))
    feed_thread.setDaemon(True)
    feed_thread.start()
    print("循环执行...")
    point_a = [301.8, -48.06, -100.65, 138.47]
    point_b = [305.04, 9.02, -99.29, 150.4]
    run_point(move, point_a)
        #wait_arrive(point_a)
    run_point(move, point_b)
    dashboard.DO(1,1)
    sleep(3)
    wait_arrive(point_b)
    dashboard.DO(1,0)
    dashboard.DO(2,1)
    sleep(3)
    dashboard.DO(2,0)
        #dashboard.DO(2,1)       
