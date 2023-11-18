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
PT_INFO = {
    'PTQH': 'Phong Than 2 Quan Hung Tranh',
    'PT2': 'PhongThan2.Com - ',
    'PTV': 'PhongThanViet.com'
}
NV_INFO = {
    'Failer': {
        'TK': 'acnhansat2',
        'BILL_GATES_NAME': 'image/bill_gates_image.png',
        'NAME_NV': 'mrslave102',
        'PASS': '0964892408a',
        'PT_PATH': r'C:\PhongThan2\game.exe',
        'PT_NAME': 'PhongThan2.Com'
    },
    'Zero': {
        'TK': 'acnhansat99999',
        'BILL_GATES_NAME': 'image/bill_gates_image_zero.png',
        'NAME_NV': 'mrslave103',
        'PASS': '0964892408a',
        'PT_PATH': r'C:\PhongThan2\game.exe',
        'PT_NAME': 'PhongThan2.Com'
    },
    'Slave': {
        'TK': 'acnhansat2',
        'BILL_GATES_NAME': 'image/bill_gates_image_qh_slave.png',
        'NAME_NV': 'mrslave102',
        'PASS': '0964892408a',
        'PT_PATH': r'C:\PhongThan3\PhongThan_II_QuanHung\game.exe',
        'PT_NAME': 'Phong Than 2 Quan Hung Tranh'
    },
    'MrFailer': {
        'TK': 'acnhansat1',
        'BILL_GATES_NAME': 'image/bill_gates_image_mrfailer.png',
        'NAME_NV': 'mrslave102',
        'PASS': '0964892408a',
        'PT_PATH': r'C:\PhongThan2\game.exe',
        'PT_NAME': 'PhongThan2.Com'
    },
}

class BillGatePT:

    CLIENT_NAME = 'BillGatePT'

    def __init__(self, bill_gates_handle=None, nv_key_info='Failer'):
        self.NV_INFO = NV_INFO[nv_key_info]
        self.PASS = self.NV_INFO['PASS']
        self.NAME_NV = self.NV_INFO['NAME_NV']
        self.TK = self.NV_INFO['TK']
        self.BILL_GATES_NAME = self.NV_INFO['BILL_GATES_NAME']
        self.PT_PATH = self.NV_INFO['PT_PATH']
        self.PT_NAME = self.NV_INFO['PT_NAME']
        try:
            if bill_gates_handle:
                self.app_bill_gates = pywinauto.application.Application().connect(handle=bill_gates_handle)
            else:
                raise
        except:
            if not self.find_bill_gates_window():
                self.init_game_windown()
        self.socket_client = client.SocketClient(self.CLIENT_NAME)

    def find_bill_gates_window(self):
        self.close_all_login_page()
        path_image_live = 'image/live_image/find_slave_window.png'
        pt_windows = pywinauto.findwindows.find_windows(title_re=self.PT_NAME)
        is_success = False
        print(pt_windows)
        for pt_window in pt_windows:
            self.app_bill_gates = pywinauto.application.Application().connect(handle=pt_window)
            print(self.BILL_GATES_NAME)
            is_success = self.action(path_image_live, self.BILL_GATES_NAME, 20, 10,
                                     log_error='bill_gates_image not found', no_click=True)

            if is_success:
                print('Da tim thay bill gates ..')
                break
        if not is_success:
            print('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
            self.app_bill_gates = None
        return is_success

    def exit_game_windown(self):
        self.app_bill_gates.kill()

    def close_all_login_page(self):
        path_image_live = 'image/live_image/close_all_login_page.png'
        pt_windows = pywinauto.findwindows.find_windows(title_re=self.PT_NAME)
        for pt_window in pt_windows:
            self.app_bill_gates = pywinauto.application.Application().connect(handle=pt_window)
            is_login_page = self.action(
                path_image_live, 'image/dang_nhap_page.png', 20, 10, log_error='dang_nhap_page not found', no_click=True
            )
            if is_login_page:
                self.exit_game_windown()

    def init_game_windown(self, first_init=False):
        path_image_live = 'image/live_image/init_game_windown.png'

        self.app_bill_gates = pywinauto.application.Application().start(cmd_line=self.PT_PATH)
        time.sleep(1)
        is_success = False
        for idx in range(0, 100):
            is_success = self.action(path_image_live, 'image/init_game.png', 20, 10,
                                     log_error='init_game not found', no_click=True)
            if is_success:
                break
        if not is_success:
            exit(0)

        if first_init:
            pt_windows = pywinauto.findwindows.find_windows(title_re=self.PT_NAME)
        else:
            pt_windows = pywinauto.findwindows.find_windows(title_re=self.PT_NAME)
            for pt_window in pt_windows:
                self.app_bill_gates = pywinauto.application.Application().connect(handle=pt_window)
                is_success = self.action(path_image_live, 'image/init_game.png', 20, 10,
                                         log_error='init_game not found', no_click=True)
                if is_success:
                    break
        if not is_success:
            exit(0)
        print('Start game ......')
        self.app_bill_gates.FSOnlineClass.type_keys('{ENTER}')
        time.sleep(0.2)
        is_success = self.action(path_image_live, 'image/init_game_btn.png', 20, 10,
                                 log_error='init_game_btn not found')
        if not is_success:
            exit(0)
        time.sleep(0.2)
        is_success = self.action(path_image_live, 'image/chon_server.png', 20, 10,
                                 log_error='chon_server not found')
        if not is_success:
            exit(0)
        self.loggin_tk()
        return is_success

    def nhap_tk(self):
        path_image_live = 'image/live_image/nhap_tk.png'
        print('Nhap TK')

        is_success = self.action(path_image_live, 'image/input_tk.png', 20, 15,
                                 log_error='input_tk not found')
        time.sleep(0.1)
        if not is_success:
            print('Khong the nhap TK')
            exit(-1)
        for idx in range(0, 30):
            self.app_bill_gates.FSOnlineClass.type_keys('{BACKSPACE}')
        time.sleep(0.1)
        self.app_bill_gates.FSOnlineClass.type_keys(self.TK)
        time.sleep(0.1)
        self.app_bill_gates.FSOnlineClass.type_keys('{TAB}')

    def loggin_tk(self):
        print(' loggin_tk ... ')
        path_image_live = 'image/live_image/login_page.png'
        skip_enter_server = self.action(path_image_live, 'image/child_vao_game_button.png', 20, 15,
                                        log_error='child_vao_game_button not found', no_click=True)
        if not skip_enter_server:
            if not self.login_button_action():
                return False
        else:
            print('Nhap pass luon')
            pass
        for elem in range(0, 1000):
            path_image_live = 'image/live_image/login_page.png'
            is_success = self.action(path_image_live, 'image/child_vao_game_button.png', 20, 15,
                                     log_error='child_vao_game_button 2 not found', no_click=True)
            if is_success:
                break
            time.sleep(0.2)
            path_image_live = 'image/live_image/login_page.png'
            is_success = self.action(path_image_live, 'image/child_server_bao_tri.png', 20, 15,
                                     log_error='child_server_bao_tri not found', no_click=True)
            if is_success:
                time.sleep(0.2)
                self.app_bill_gates.FSOnlineClass.type_keys('{ENTER}')
                if not self.login_button_action():
                    return False
            time.sleep(0.2)

        for idx2 in range(0, 100):
            self.nhap_tk()

            print('Nhap pass ')
            # time.sleep(0.2)
            self.app_bill_gates.FSOnlineClass.type_keys(self.PASS)
            time.sleep(0.2)
            print('Nhap ENTER pass ')
            self.app_bill_gates.FSOnlineClass.type_keys('{ENTER}')
            is_success = False
            for idx_3 in range(0, 1000):

                is_success = self.action(path_image_live, 'image/child_xoa_nv_buttom.png', 20, 15,
                                         log_error='child_chon_nv_page not found', no_click=True)
                if is_success:
                    break

                is_tkdsd = self.action(path_image_live, 'image/child_login_tkdsd.png', 20, 15,
                                       log_error='child_login_tkdsd not found', no_click=True)
                if is_tkdsd:
                    time.sleep(0.2)
                    self.app_bill_gates.FSOnlineClass.type_keys('{ENTER}')
                    break

                path_image_live = 'image/live_image/login_page.png'
                is_svbt = self.action(path_image_live, 'image/child_server_bao_tri.png', 20, 15,
                                      log_error='child_server_bao_tri not found', no_click=True)
                if is_svbt:
                    time.sleep(0.2)
                    self.app_bill_gates.FSOnlineClass.type_keys('{ENTER}')
                    if self.loggin_tk():
                        return True
                    break
                time.sleep(0.2)
            if is_success:
                break
        for idx in range(0, 500):
            print('Tim xoa nv buttom ...')
            path_image_live = 'image/live_image/delete_nv_page.png'
            is_success = self.action(path_image_live, 'image/child_xoa_nv_buttom.png', 20, 15,
                                     log_error='child_xoa_nv_buttom not found', no_click=True)
            if is_success:
                break
        if is_success:
            self.app_bill_gates.FSOnlineClass.type_keys('{ENTER}')

        return True

    def login_button_action(self):
        time.sleep(0.2)
        path_image_live = 'image/live_image/login_page.png'
        is_success = self.action(path_image_live, 'image/child_login_server_page.png', 20, 15,
                                 log_error='child_login_server_page not found', no_click=True)
        if not is_success:
            return False
        print(' Chuan bi login ')
        is_success = self.action(path_image_live, 'image/child_login_button.png', 20, 15,
                                 log_error='child_login_button not found')
        if not is_success:
            return False
        return True

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
        self.app_bill_gates.FSOnlineClass.set_focus()
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
                                     log_error='child_chuc_name not found', no_click=True)

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
                                 log_error='child_chuc_name not found', debug=True)
        if not is_success:
            return False

        for idx in range(0, 30):
            self.app_bill_gates.FSOnlineClass.type_keys('{BACKSPACE}')
        self.app_bill_gates.FSOnlineClass.type_keys(self.NAME_NV)

        path_image_live = 'image/live_image/bill_gates_tim_nv.png'
        is_success = self.action(path_image_live, 'image/child_gd_button.png', 20, 10,
                                 log_error='child_gd_button not found')
        if not is_success:
            return False

        return True

    def confirm_gd(self):
        print('confirm_gd ......')
        path_image_live = 'image/live_image/game_windown.png'
        msg = master_pt.socket_client.recv_msg()
        self.app_bill_gates.FSOnlineClass.set_focus()
        # self.app_bill_gates.FSOnlineClass.type_keys('{F6}')
        # time.sleep(0.2)

        # is_success = self.action(path_image_live, 'image/full_2b.png', 20, 10,
        #                          log_error='full_2b not found', no_click=True)
        # if is_success:
        #     print('Da du 2b thoat')
        #     master_pt.socket_client.send_message('OUT', 'SlavePT')
        #     exit(0)

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

                path_image_live = 'image/live_image/game_windown.png'
                is_success = self.action(path_image_live, 'image/child_gd_xac_dinh.png', 20, 10,
                                         log_error='child_gd_xac_dinh not found')
                if is_success:
                    break
                time.sleep(0.2)
            if not is_success:
                self.app_bill_gates.FSOnlineClass.type_keys('{ESC}')
                return False
            print(' Goi message CONFIRM')
            master_pt.socket_client.send_message('CONFIRM', 'SlavePT')
            return True

    def exit_gd_page(self):
        path_image_live = 'image/live_image/game_windown.png'
        is_success = self.action(path_image_live, 'image/child_gd_page.png', 20, 10,
                                 log_error='child_gd_xac_dinh not found', no_click=False)
        if is_success:
            time.sleep(0.2)
            self.app_bill_gates.FSOnlineClass.type_keys('{ESC}')
            print('Da close gd page')



if __name__ == "__main__":

    master_pt = BillGatePT(nv_key_info='MrFailer')
    num_gd = 1
    while True:
        print('Waiting msg')
        msg = master_pt.socket_client.recv_msg()
        if msg == 'GD':
            count_failed = 0
            for idx in range(0, 1000):
                is_success = master_pt.bill_gates_gd()
                if is_success:
                    master_pt.socket_client.send_message('THGD', 'SlavePT')
                    print('Dang cho GD ...')
                    msg = master_pt.socket_client.recv_msg()
                    if msg == 'GD_OK':
                        count_failed = 0
                        print('Chuan bi gd')
                        if master_pt.confirm_gd():
                            print('Giao Dich Lan thu ', num_gd)
                            num_gd += 1
                            break
                    else:
                        master_pt.exit_gd_page()
                        print('GD that bai tien hanh gd lai')
                        count_failed += 1
                        print('Failed time : ',count_failed)
                else:
                    count_failed += 1
                    print('Failed time : ', count_failed)
                if count_failed == 10:
                    print('Thoat gamne va dn lai')
                    master_pt.exit_game_windown()
                    master_pt.init_game_windown()
                    count_failed = 0
                time.sleep(0.2)

    # master_pt.socket_client.send_message(DISCONNECT_MSG, 'init')
