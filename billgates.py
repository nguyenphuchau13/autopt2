import pywinauto
import time
import ctypes
import cv2
import numpy as np
import pyautogui
from socket_msg import client

"""It simulates the mouse"""
MOUSEEVENTF_MOVE = 0x0001  # mouse move
MOUSEEVENTF_LEFTDOWN = 0x0002  # left button down
MOUSEEVENTF_LEFTUP = 0x0004  # left button up
MOUSEEVENTF_RIGHTDOWN = 0x0008  # right button down
MOUSEEVENTF_RIGHTUP = 0x0010  # right button up
MOUSEEVENTF_MIDDLEDOWN = 0x0020  # middle button down
MOUSEEVENTF_MIDDLEUP = 0x0040  # middle button up
MOUSEEVENTF_WHEEL = 0x0800  # wheel button rolled
MOUSEEVENTF_ABSOLUTE = 0x8000  # absolute move
DISCONNECT_MSG = "!DISCONNECT"


def take_screen_shot(path_image_live):
    # time.sleep(5)
    screen_shot = pyautogui.screenshot()
    screen_shot.save(path_image_live)


def is_template_in_image(img, templ):
    # Template matching using TM_SQDIFF: Perfect match => minimum value around 0.0
    result = cv2.matchTemplate(img, templ, cv2.TM_SQDIFF)

    # Get value of best match, i.e. the minimum value
    print(cv2.minMaxLoc(result))
    min_val = cv2.minMaxLoc(result)[0]
    print(min_val)
    # Set up threshold for a "sufficient" match
    thr = 10e-6

    return min_val <= thr


def spam_ordinates():
    ''' function to determin the mouse coordinates'''

    print('press "x" key to lock position...')
    pre_x = 0
    pre_y = 0
    while True:
        # Check if x key is pressed
        time.sleep(0.1)

        x, y = pyautogui.position()

        if x != pre_x or y != pre_y:
            print(f'spam at position: {x}, {y}')
        pre_x = x
        pre_y = y


def find_post_image(root_image_path, child_image_path):
    img_rgb = cv2.imread(root_image_path)
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
    template = cv2.imread(child_image_path, 0)
    w, h = template.shape[::-1]

    res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
    threshold = 0.8
    loc = np.where(res >= threshold)
    # print((loc))
    # print(loc[0][0])
    # print(loc[1][0])
    for pt in zip(*loc[::-1]):
        return pt[0], pt[1]
    return None, None


def move_and_click_left(x_pos, y_post):
    ctypes.windll.user32.SetCursorPos(int(x_pos), int(y_post))
    ctypes.windll.user32.mouse_event(2, 0, 0, 0, 0)
    ctypes.windll.user32.mouse_event(4, 0, 0, 0, 0)


def move_and_click_right(x_pos, y_post):
    ctypes.windll.user32.SetCursorPos(int(x_pos), int(y_post))
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)


def adjust_pos(x_pos, y_pos, x_adjust, y_adjust):
    x_pos = x_pos + x_adjust
    y_pos = y_pos + y_adjust
    return x_pos, y_pos


class BillGatePT:
    TK_POS_X = '179'
    TK_POS_Y = '188'
    NUM_COIN = '1'
    PASS = '0964892408a'
    NUMBER_NV = 101
    NAME_NV = 'mrslave102'
    # PT_LOGO = 'image/child_chon_nv_page_pt_viet.png'
    CLIENT_NAME = 'BillGatePT'
    PT_LOGO = 'image/child_chon_nv_page_pt_2.png'

    def __init__(self, bill_gates_handle):
        self.name_nv = ''
        self.app_bill_gates = pywinauto.application.Application().connect(handle=bill_gates_handle)
        self.socket_client = client.SocketClient(self.CLIENT_NAME)

    def action(self,
               path_image_live,
               path_child_image,
               x_adjust,
               y_adjust,
               log_error='',
               debug=False,
               right_click=False,
               no_click=False
               ):
        time.sleep(0.1)
        take_screen_shot(path_image_live)
        time.sleep(0.1)
        x_pos, y_pos = find_post_image(path_child_image, path_image_live)
        if x_pos is None:
            print(log_error)
            return False
        x_pos, y_pos = adjust_pos(x_pos, y_pos, x_adjust, y_adjust)
        if debug is True:
            print(x_pos, y_pos)
        if no_click:
            return True
        if not right_click:
            move_and_click_left(x_pos, y_pos)
        else:
            move_and_click_right(x_pos, y_pos)
        time.sleep(0.1)
        return True

    def bill_gates_gd(self):
        self.app_bill_gates.FSOnlineClass.set_focus()
        time.sleep(0.2)
        path_image_live = 'image/live_image/bill_gates_tim_nv.png'
        for idx in range(0, 10):
            is_success = self.action(path_image_live, 'image/child_chuc_name.png', 20, 15,
                                     log_error='child_tim_nv_page not found', no_click=True)

            if is_success:
                time.sleep(0.2)
                print('Thoat child_tim_nv_page')
                self.app_bill_gates.FSOnlineClass.type_keys('{ESC}')
                time.sleep(0.2)
            else:
                break
        time.sleep(0.2)
        self.app_bill_gates.FSOnlineClass.set_focus()
        time.sleep(0.2)
        self.app_bill_gates.FSOnlineClass.type_keys('{F6}')
        time.sleep(0.2)
        path_image_live = 'image/live_image/bill_gates_tim_nv.png'
        is_success = self.action(path_image_live, 'image/child_tim_nv.png', 20, 15,
                                 log_error='child_tim_nv not found')

        if not is_success:
            return False
        path_image_live = 'image/live_image/bill_gates_tim_nv.png'
        is_success = self.action(path_image_live, 'image/child_chuc_name.png', -90, 10,
                                 log_error='child_tim_nv not found', debug=True)
        if not is_success:
            return False
        time.sleep(0.5)
        for idx in range(0, 30):
            self.app_bill_gates.FSOnlineClass.type_keys('{BACKSPACE}')
        self.app_bill_gates.FSOnlineClass.type_keys(self.NAME_NV)

        path_image_live = 'image/live_image/bill_gates_tim_nv.png'
        is_success = self.action(path_image_live, 'image/child_gd_button.png', 20, 10,
                                 log_error='child_tim_nv not found')
        if not is_success:
            return False

        return True

    def confirm_gd(self):
        print('confirm_gd ......')
        msg = master_pt.socket_client.recv_msg()
        self.app_bill_gates.FSOnlineClass.set_focus()
        path_image_live = 'image/live_image/game_windown.png'
        is_success = self.action(path_image_live, 'image/child_gd_page.png', 20, 10,
                                 log_error='child_gd_page not found', no_click=True)
        if not is_success:
            return False
        if msg == 'KHOA':
            path_image_live = 'image/live_image/game_windown.png'
            is_success = self.action(path_image_live, 'image/child_gd_khoa_buton.png', 20, 10,
                                     log_error='child_gd_khoa_buton not found')
            if not is_success:
                self.app_bill_gates.FSOnlineClass.type_keys('{ESC}')
                return False
            for idx in range(0, 50):
                time.sleep(0.2)
                path_image_live = 'image/live_image/game_windown.png'
                is_success = self.action(path_image_live, 'image/child_gd_xac_dinh.png', 20, 10,
                                         log_error='child_gd_xac_dinh not found')
                if is_success:
                    break
            if not is_success:
                self.app_bill_gates.FSOnlineClass.type_keys('{ESC}')
                return False
            print(' Goi message CONFIRM')
            master_pt.socket_client.send_message('CONFIRM', 'SlavePT')
            return True
PT_INFO = {
    'PTQH': 'Phong Than 2 Quan Hung Tranh',
    'PT2': 'PhongThan2.Com - ',
    'PTV': 'PhongThanViet.com'
}
if __name__ == "__main__":
    bill_gates_handle = 460110 # pthb
    PT_NAME = 'PT2'
    # bill_gates_handle = 460768 # pt 2
    mywindows = pywinauto.findwindows.find_windows(title_re=PT_INFO[PT_NAME])
    print(mywindows)
    [1640344, 3015796]
    app = pywinauto.application.Application().connect(handle=bill_gates_handle)
    app.FSOnlineClass.set_focus()

    master_pt = BillGatePT(bill_gates_handle)
    while True:
        print('Waiting msg')
        msg = master_pt.socket_client.recv_msg()
        if msg == 'GD':
            for idx in range(0, 100):
                time.sleep(0.2)
                is_success = master_pt.bill_gates_gd()
                if is_success:
                    master_pt.socket_client.send_message('THGD', 'SlavePT')
                    print('Dang cho GD ...')
                    msg = master_pt.socket_client.recv_msg()
                    if msg == 'GD_OK':
                        print('Chuan bi gd')
                        if master_pt.confirm_gd():
                            break

    # master_pt.socket_client.send_message(DISCONNECT_MSG, 'init')
