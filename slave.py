import pywinauto
import time
from datetime import datetime
import signal
import ctypes
import cv2
import numpy as np
import pyautogui
import os
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

PT_INFO = {
    'PTQH': 'Phong Than 2 Quan Hung Tranh',
    'PT2': 'PhongThan2.Com',
    'PTV': 'PhongThanViet.com'
}


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
            pass
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


class SlavePT:
    TK_POS_X = '178'
    TK_POS_Y = '189'
    NUM_COIN = '20'
    PASS = '0964892408a'
    NUMBER_NV = 101
    NAME_NV = 'mrslave102'
    # PT_LOGO = 'image/child_chon_nv_page_pt_viet.png'
    # CLIENT_NAME = 'BillGatePT'
    CLIENT_NAME = 'SlavePT'
    TK = 'acnhansat1'
    # BILL_GATES_NAME = 'image/child_bill_gate_name.png'
    # PT_LOGO = 'image/child_chon_nv_page_pt_2.png'

    def __init__(self, master_handle=None, name_pt='PTV'):
        self.name_nv = ''
        self.pip_handle = master_handle
        try:
            self.app = pywinauto.application.Application().connect(handle=master_handle)
        except:
            if not self.find_slave_window():
                self.init_game_windown()

        self.socket_client = client.SocketClient(self.CLIENT_NAME)
        if name_pt == 'PTV':
            self.BILL_GATES_NAME = 'image/child_bill_gate_name_pt_viet.png'
            self.PT_LOGO = 'image/child_chon_nv_page_pt_viet.png'
        elif name_pt == 'PT2':
            self.BILL_GATES_NAME = 'image/child_bill_gate_name.png'
            self.PT_LOGO = 'image/child_chon_nv_page_pt_2.png'
            self.bill_gates_name = 'image/bill_gates_image.png'
            self.slave_name = 'image/slave_image.png'
        elif name_pt == 'PTQH':
            self.BILL_GATES_NAME = 'image/child_bill_gate_name_pt_viet.png'
            self.PT_LOGO = 'image/child_chon_nv_page_pt_qh.png'

    def find_slave_window(self):
        self.close_all_login_page()
        path_image_live = 'image/live_image/find_slave_window.png'
        pt_windows = pywinauto.findwindows.find_windows(title_re=PT_INFO[PT_NAME])
        is_success = False
        for pt_window in pt_windows:
            self.app = pywinauto.application.Application().connect(handle=pt_window)
            is_success = self.action(path_image_live, 'image/slave_image.png', 20, 10,
                                     log_error='slave_image not found', no_click=True)
            if is_success:
                break
        if not is_success:
            self.app = None
        return is_success

    def close_all_login_page(self):
        path_image_live = 'image/live_image/close_all_login_page.png'
        pt_windows = pywinauto.findwindows.find_windows(title_re=PT_INFO[PT_NAME])
        for pt_window in pt_windows:
            self.app = pywinauto.application.Application().connect(handle=pt_window)
            is_login_page = self.action(
                path_image_live, 'image/dang_nhap_page.png', 20, 10, log_error='dang_nhap_page not found', no_click=True
            )
            if is_login_page:
                self.exit_game_windown()

    def ktc_open(self):
        self.app.FSOnlineClass.set_focus()
        print('Open ky tran cac ...')
        self.app.FSOnlineClass.type_keys('{F2}')
        time.sleep(0.2)
        if not self.ktc_check():
            return False
        else:
            if not self.ktc_by_dnp_item():
                return False
            self.app.FSOnlineClass.type_keys('{F2}')
            print('Close KTC')
            return True

    def pawn_coin(self):
        print('Cam do')
        path_image_live = 'image/live_image/cam_do.png'
        is_success = self.action(
            path_image_live, 'image/child_cam_do_new.png', 20, 15, log_error=' Cam do not found')
        if not is_success:
            return False
        time.sleep(0.5)
        print('Go Cam do')
        path_image_live = 'image/live_image/cam_do_page.png'
        is_success = self.action(
            path_image_live, 'image/child_go_cam_do.png', 20, 15, log_error=' Cam do page not found')
        if not is_success:
            return False

        time.sleep(0.5)
        path_image_live = 'image/live_image/do_cam_do_page.png'
        is_success = self.action(
            path_image_live, 'image/child_do_cam_do.png', 20, 15, log_error=' Cam do page not found 2')
        if not is_success:
            return False
        time.sleep(0.5)
        print('Nhap so xu cam')
        self.app.FSOnlineClass.type_keys(SlavePT.NUM_COIN)
        time.sleep(0.2)
        path_image_live = 'image/live_image/do_cam_do_page_confirm.png'
        is_success = self.action(
            path_image_live, 'image/child_cam_do_confirm.png', 20, 15, log_error=' Cam do page not found 2')
        if not is_success:
            return False
        time.sleep(0.5)
        print('Xac nhan cam do')
        path_image_live = 'image/live_image/do_cam_do_page_confirm_again.png'
        is_success = self.action(
            path_image_live, 'image/child_cam_do_confirm.png', 20, 15, log_error=' Cam do page not found 2')
        if not is_success:
            return False
        for idx in range(0, 100):
            is_success = self.action(
                path_image_live, 'image/child_cam_do_page.png', 20, 15,
                log_error=' child_cam_do_page not found', no_click=True)
            if not is_success:
                break
            self.app.FSOnlineClass.type_keys('{ESC}')
            time.sleep(0.2)
        self.exit_dang_doi_thoai()
        print('Cam xu Thanh COng')
        return True

    def exit_dang_doi_thoai(self):
        path_image_live = 'image/live_image/exit_dang_doi_thoai.png'
        is_success = self.action(path_image_live, 'image/check_ktdt.png', 20, 15,
                                 log_error=' check_ktdt not found')

        time.sleep(0.2)
        return is_success

    def use_dnp(self):
        print('Open hanh trang')
        self.app.FSOnlineClass.type_keys('{F4}')
        time.sleep(0.2)
        print('Open DNP')
        path_image_live = 'image/live_image/use_dnp.png'
        is_success = self.action(
            path_image_live, 'image/child_use_dnp.png', 20, 15, log_error=' DNP not found in F4', right_click=True)
        if not is_success:
            return False
        time.sleep(0.5)
        print('Go tk')
        path_image_live = 'image/live_image/use_dnp_tk.png'
        is_success = self.action(
            path_image_live, 'image/child_tk.png', 20, 5, log_error=' Tay Ky not found in DNP')
        if not is_success:
            return False
        for idx in range(0, 100):
            path_image_live = 'image/live_image/use_dnp_tk.png'
            is_success = self.action(
                path_image_live, 'image/child_tay_ky.png', 20, 5, log_error='CHua toi Tay Ky', no_click=True)
            if is_success:
                break
            time.sleep(0.2)
        time.sleep(1)
        # self.app.FSOnlineClass.type_keys('{F4}')
        # time.sleep(0.2)
        return True

    def go_pawn(self):
        path_image_live = 'image/live_image/tk.png'
        is_success = self.action(
            path_image_live, 'image/child_x_pos.png', 18, 7, log_error=' Not found x_post')
        if not is_success:
            return False
        self.app.FSOnlineClass.type_keys(SlavePT.TK_POS_X)

        path_image_live = 'image/live_image/tk.png'
        is_success = self.action(
            path_image_live, 'image/child_y_pos.png', 16, 4, log_error=' Not found x_post')
        if not is_success:
            return False
        self.app.FSOnlineClass.type_keys(SlavePT.TK_POS_Y)

        path_image_live = 'image/live_image/tk.png'
        is_success = self.action(
            path_image_live, 'image/child_go.png', 18, 8, log_error=' Not found GO')
        if not is_success:
            return False
        print('Dang di chuyen ...')
        time.sleep(22)
        print('Da Den')

    def ktc_check(self):
        print('Check KTC ....')
        self.app.FSOnlineClass.set_focus()
        time.sleep(0.2)
        path_image_live = 'image/live_image/ktc_live.png'
        take_screen_shot(path_image_live)
        time.sleep(0.1)
        x_pos, y_pos = find_post_image('image/child_ktc.png', path_image_live)
        # print()
        if x_pos is None:
            print('KTC not found aaaaaa')
            return False
        print('KTC was opening')
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
        self.app.FSOnlineClass.set_focus()
        time.sleep(0.1)
        take_screen_shot(path_image_live)
        time.sleep(0.1)
        x_pos, y_pos = find_post_image(path_child_image, path_image_live)
        if x_pos is None:
            print(log_error)
            return False
        if debug is True:
            print(x_pos, y_pos)
            pass
        if no_click:
            return True
        x_pos, y_pos = adjust_pos(x_pos, y_pos, x_adjust, y_adjust)

        if not right_click:
            move_and_click_left(x_pos, y_pos)
        else:
            move_and_click_right(x_pos, y_pos)
        time.sleep(0.1)
        return True

    def ktc_by_dnp_item(self):
        print('By Di Nguyen Phu .....')
        path_image_live = 'image/live_image/ktc_truyen.png'
        is_success = self.action(path_image_live, 'image/child_truyen.png', 24, 15, log_error=' Truyen not found')
        if not is_success:
            return False

        path_image_live = 'image/live_image/ktc_dnp.png'
        is_success = self.action(path_image_live, 'image/child_end.png', 10, 5, log_error=' DNP page not found')
        if not is_success:
            return False
        time.sleep(0.5)
        print('Mua DNP')
        path_image_live = 'image/live_image/ktc_dnp_page.png'
        is_success = self.action(path_image_live, 'image/child_dnp.png', 164, 51, log_error='DNP not found')
        if not is_success:
            return False
        time.sleep(0.4)
        path_image_live = 'image/live_image/ktc_dnp_buy.png'
        is_success = self.action(path_image_live, 'image/child_confirm.png', 10, 5, log_error='Buy not found',
                                 debug=True)
        if not is_success:
            return False
        return True

    def nhap_tk(self):
        path_image_live = 'image/live_image/nhap_tk.png'
        print('Nhap TK')

        is_success = self.action(path_image_live, 'image/input_tk.png', 20, 15,
                                 log_error='input_tk not found')
        if is_success:
            time.sleep(0.1)
            for idx in range(0, 30):
                self.app.FSOnlineClass.type_keys('{BACKSPACE}')
            time.sleep(0.1)
            self.app.FSOnlineClass.type_keys(self.TK)
            time.sleep(0.1)
            self.app.FSOnlineClass.type_keys('{TAB}')
            print('Nhap pass ')
            time.sleep(0.2)
            self.app.FSOnlineClass.type_keys(self.PASS)
            time.sleep(0.1)
            print('Nhap ENTER pass ')
            self.app.FSOnlineClass.type_keys('{ENTER}')
        return is_success
    def action_open_out_page(self):
        print('action_open_out_page .....')
        is_success = False
        for index in range(0, 100):
            self.exit_dang_doi_thoai()
            self.app.FSOnlineClass.type_keys('{ESC}')
            time.sleep(0.2)
            path_image_live = 'image/live_image/delete_page.png'
            is_success = self.action(path_image_live, 'image/child_chon_nv.png', 20, 15,
                                     log_error='delete_page not found cos the bo qua')
            if is_success:
                return is_success
        return is_success

    def exit_game(self):
        time.sleep(0.2)
        self.app.FSOnlineClass.set_focus()
        print('Thoat Game ...')
        is_success = self.action_open_out_page()
        # time.sleep(0.5)
        # self.app.FSOnlineClass.type_keys('{ESC}')
        # time.sleep(0.5)
        # path_image_live = 'image/live_image/delete_check_exit.png'
        # is_success = self.action(path_image_live, 'image/child_chon_nv.png', 20, 15,
        #                          log_error='child_chon_nv not found')
        if not is_success:
            self.exit_game_windown()
            print('Thoat game action_open_out_page ... ')
            self.init_game_windown(skip_delete_nv=True)
            return True
        num_exit_failed = 0
        for idx in range(0, 500):
            path_image_live = 'image/live_image/delete_check_exit.png'
            is_success = self.action(path_image_live, 'image/child_delete_tk_dsd.png', 20, 15,
                                     log_error='child_delete_tk_dsd not found')
            if is_success:
                self.app.FSOnlineClass.type_keys('{ENTER}')
                print(' Xuat hien tai khoan dang su dung dang nhap lai ')
                self.loggin_tk()
                time.sleep(0.3)
                return -1

            time.sleep(0.2)
            print('Check thoat game ....')
            path_image_live = 'image/live_image/delete_check_exit.png'
            is_success = self.action(path_image_live, 'image/child_check_exit_game.png', 20, 15,
                                     log_error='child_check_exit_game not found', no_click=True)
            if not is_success:
                break
            else:
                num_exit_failed += 1

            if num_exit_failed == 10:
                self.exit_game_windown()
                print('Thoat game num_exit_failed ... ')
                self.init_game_windown(skip_delete_nv=True)
                break
            time.sleep(0.2)
        print(' Thoat Game thanh cong')
        return True

    def delete_nv(self):
        time.sleep(0.2)
        print('check da xoa nv')
        path_image_live = 'image/live_image/delete_nv_page.png'
        is_success = self.action(path_image_live, 'image/child_tao_nv_only.png', 20, 15,
                                 log_error='child_tao_nv_only not found', no_click=True)
        if not is_success:
            return True
        print('Xoa nhan vat ...')
        is_success = False
        for idx in range(0, 500):
            print('Tim xoa nv buttom ...')
            path_image_live = 'image/live_image/delete_nv_page.png'
            is_success = self.action(path_image_live, 'image/child_xoa_nv_buttom.png', 20, 15,
                                     log_error='child_xoa_nv_buttom not found')
            if is_success:
                break
        if not is_success:
            return False
        time.sleep(0.2)
        self.app.FSOnlineClass.type_keys(self.PASS)
        time.sleep(0.2)
        self.app.FSOnlineClass.type_keys('{ENTER}')
        time.sleep(0.2)
        self.app.FSOnlineClass.type_keys('{TAB}')
        time.sleep(0.2)
        self.app.FSOnlineClass.type_keys('{ENTER}')

        is_success = True
        for idx in range(0, 1000):
            path_image_live = 'image/live_image/delete_nv_page.png'
            is_success = self.action(path_image_live, 'image/child_wait_delete_nv.png', 20, 15,
                                     log_error='child_xoa_nv_buttom not found', no_click=True)
            if not is_success:
                break
            time.sleep(0.1)
            path_image_live = 'image/live_image/delete_nv_page.png'
            print('Kien tra bao tri')
            is_success = self.action(path_image_live, 'image/child_bao_tri.png', 20, 15,
                                     log_error='child_bao_tri not found', no_click=True)
            if is_success:
                self.app.FSOnlineClass.type_keys('{ENTER}')
                break
            time.sleep(0.2)
        print('Xoa nhan vat Thanh cong....')
        return True

    def create_nv(self):
        time.sleep(0.2)
        print('Tao nhan vat ...')
        path_image_live = 'image/live_image/create_nv_page.png'
        is_success = self.action(path_image_live, 'image/child_create_nv_buttom.png', 20, 15,
                                 log_error='child_create_nv_buttom not found')
        if not is_success:
            return False
        time.sleep(0.2)

        for idx in range(0, 30):
            self.app.FSOnlineClass.type_keys('{BACKSPACE}')
        self.app.FSOnlineClass.type_keys(self.NAME_NV)
        time.sleep(0.1)
        print('Xac nhan dat ten ')
        path_image_live = 'image/live_image/create_name_nv_page.png'
        is_success = self.action(path_image_live, 'image/child_create_nv_confirm_buttom.png', 20, 15,
                                 log_error='child_create_nv_confirm_buttom not found')
        if not is_success:
            return False

    def check_tao_nv_failed(self):
        time.sleep(0.2)
        path_image_live = 'image/live_image/create_name_nv_page.png'
        is_success = self.action(path_image_live, 'image/child_failed_create_nv.png', 20, 15,
                                 log_error='child_create_nv_confirm_buttom not found')

        if is_success:
            self.app.FSOnlineClass.type_keys('{ENTER}')
            self.name_nv = ''
            return False
        else:
            self.name_nv = self.NAME_NV.format(self.NUMBER_NV)
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

    def loggin_tk(self, check_delete_buttom=False, skip_delete_nv=False):
        if check_delete_buttom:
            print('Tim xoa nv buttom ...')
            path_image_live = 'image/live_image/delete_nv_page.png'
            is_success = self.action(path_image_live, 'image/child_xoa_nv_buttom.png', 20, 15,
                                     log_error='child_xoa_nv_buttom not found', no_click=True)
            if is_success:
                return False
        time.sleep(0.2)
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
                self.app.FSOnlineClass.type_keys('{ENTER}')
                if not self.login_button_action():
                    return False
            time.sleep(0.2)

        for idx2 in range(0, 100):
            is_input_tk = self.nhap_tk()
            if not is_input_tk:
                self.init_game_windown(skip_delete_nv=True)
                break

            is_success = False
            for idx_3 in range(0, 1000):
                is_success = self.action(path_image_live, 'image/child_xoa_nv_buttom.png', 20, 15,
                                         log_error='child_chon_nv_page not found', no_click=True)
                if is_success:
                    print('tim thay child_chon_nv_page')
                    break

                is_tkdsd = self.action(path_image_live, 'image/child_login_tkdsd.png', 20, 15,
                                       log_error='child_login_tkdsd not found', no_click=True)
                if is_tkdsd:
                    print('TK dang sung dung dang nhap lai')
                    time.sleep(0.2)
                    self.app.FSOnlineClass.type_keys('{ENTER}')
                    break

                path_image_live = 'image/live_image/login_page.png'
                is_svbt = self.action(path_image_live, 'image/child_server_bao_tri.png', 20, 15,
                                      log_error='child_server_bao_tri not found', no_click=True)
                if is_svbt:
                    print('Server dang bao tri dang nhap lai')
                    time.sleep(0.2)
                    self.app.FSOnlineClass.type_keys('{ENTER}')
                    self.loggin_tk(skip_delete_nv=True)
                    is_success = True
                    break
                time.sleep(0.2)
            if is_success:
                break
        if not skip_delete_nv:
            if self.delete_nv():
                self.create_nv()
                self.check_tao_nv_failed()
                print('Login Thanh cong')
            else:
                pass
                print('Login That bai')

        return True

    def input_pass(self):
        self.app.FSOnlineClass.type_keys('')

    def check_login_success(self, num_loop=1000):
        self.app.FSOnlineClass.set_focus()
        for idx in range(0, num_loop):

            path_image_live = 'image/live_image/game_windown.png'
            is_success = self.action(path_image_live, 'image/child_check_login_success.png', 20, 15,
                                     log_error='check_login_success not found', no_click=True)

            if is_success:
                print('Da vao game')
                break
            path_image_live = 'image/live_image/game_windown.png'
            is_success = self.action(path_image_live, 'image/check_login_bao_tri.png', 20, 15,
                                     log_error='check_login_success not found', no_click=True)
            time.sleep(0.1)
            path_image_live = 'image/live_image/game_windown.png'
            is_cmc = self.action(path_image_live, 'image/check_chon_may_chu.png', 20, 15,
                                 log_error='check_chon_may_chu not found', no_click=True)
            if is_success or is_cmc:
                self.app.FSOnlineClass.type_keys('{ENTER}')
                time.sleep(0.2)
                self.loggin_tk()
            time.sleep(0.2)

        print('Chua vao game')

    def slave_gd_enter(self):
        self.app.FSOnlineClass.set_focus()
        for idx in range(0, 100):
            path_image_live = 'image/live_image/game_windown.png'
            is_success = self.action(path_image_live, 'image/check_cam_do.png', 20, 15,
                                     log_error='check_cam_do not found', no_click=True)
            if not is_success:
                break
            else:
                self.app.FSOnlineClass.type_keys('{ESC}')
                time.sleep(0.2)

        path_image_live = 'image/live_image/game_windown.png'
        is_success = self.action(path_image_live, 'image/child_gd_slave_button.png', 20, 15,
                                 log_error='child_gd_slave_button not found')
        if not is_success:
            return False
        time.sleep(0.2)
        print('Kiem tra ten NV')
        path_image_live = 'image/live_image/game_windown.png'
        is_success = self.action(path_image_live, self.BILL_GATES_NAME, 20, 15,
                                 log_error='{} not found'.format(self.BILL_GATES_NAME), no_click=False)
        if not is_success:
            return False
        print('Xac nhan bat dau gd')
        path_image_live = 'image/live_image/game_windown.png'
        is_success = self.action(path_image_live, 'image/child_slave_gd_button.png', 20, 10,
                                 log_error='child_slave_gd_button not found')
        if not is_success:
            return False

        print('Kiem tra gd page')
        time.sleep(0.3)
        path_image_live = 'image/live_image/game_windown.png'
        is_success = self.action(path_image_live, 'image/child_gd_page.png', 20, 10,
                                 log_error='child_gd_page not found', no_click=True)
        if not is_success:
            return False
        return True

    def slave_gd(self):
        self.app.FSOnlineClass.set_focus()
        path_image_live = 'image/live_image/game_windown.png'
        is_success = self.action(path_image_live, 'image/child_input_money.png', 30, 10,
                                 log_error='child_input_money not found')
        if not is_success:
            self.app.FSOnlineClass.type_keys('{ESC}')
            return False
        self.app.FSOnlineClass.type_keys('9999999999')
        print('Khoa GD')
        path_image_live = 'image/live_image/game_windown.png'
        is_success = self.action(path_image_live, 'image/child_gd_khoa_buton.png', 20, 10,
                                 log_error='child_gd_khoa_buton not found')
        if not is_success:
            self.app.FSOnlineClass.type_keys('{ESC}')
            return False
        self.socket_client.send_message('KHOA', 'BillGatePT')

        msg = self.socket_client.recv_msg()
        self.app.FSOnlineClass.set_focus()
        if msg == 'CONFIRM':
            print('CONFIRM .....')
            for idx in range(0, 50):
                path_image_live = 'image/live_image/game_windown.png'
                is_success = self.action(path_image_live, 'image/child_gd_xac_dinh.png', 20, 10,
                                         log_error='child_gd_xac_dinh not found')
                if is_success:
                    break
                time.sleep(0.2)
            if not is_success:
                self.app.FSOnlineClass.type_keys('{ESC}')
                return False

        return True

    def exit_dnp_opening(self):
        path_image_live = 'image/live_image/game_windown.png'
        is_success = self.action(path_image_live, 'image/child_dnp_open.png', 20, 10,
                                 log_error='child_dnp_open not found')

        return is_success

    def exit_game_windown(self):
        self.app.kill()

    def init_game_windown(self, first_init=False, skip_delete_nv=False):
        print('Chay lai game')
        path_image_live = 'image/live_image/init_game_windown.png'

        self.app = pywinauto.application.Application().start(cmd_line=r'C:\PhongThan2\game.exe')
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
            pt_windows = pywinauto.findwindows.find_windows(title_re=PT_INFO[PT_NAME])
        else:
            pt_windows = pywinauto.findwindows.find_windows(title_re=PT_INFO[PT_NAME])
            for pt_window in pt_windows:
                self.app = pywinauto.application.Application().connect(handle=pt_window)
                is_success = self.action(path_image_live, 'image/init_game.png', 20, 10,
                                         log_error='init_game not found', no_click=True)
                if is_success:
                    break
        if not is_success:
            exit(0)
        print('Start game ......')
        self.app.FSOnlineClass.type_keys('{ENTER}')
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
        self.loggin_tk(skip_delete_nv=skip_delete_nv)
        return is_success


if __name__ == "__main__":
    slave_handle = 1246168  # PTHB
    PT_NAME = 'PT2'
    # slave_handle = 3952 #pt2
    mywindows = pywinauto.findwindows.find_windows(title_re=PT_INFO[PT_NAME])
    print(mywindows)

    start = datetime.now()
    # app = pywinauto.application.Application().connect(handle=slave_handle)
    # app.FSOnlineClass.set_focus()
    slave_pt = SlavePT(slave_handle, name_pt=PT_NAME)

    slave_pt.NUM_COIN = '20'
    TOTAL_COIN = 4000
    LOOP_TIME = int(TOTAL_COIN / int(slave_pt.NUM_COIN))
    print('LOOP_TIME : ', LOOP_TIME)
    print('sO TIEN DU KIEN : ', TOTAL_COIN * 50 - (LOOP_TIME * 0.2 * 50))
    time.sleep(2)
    for elem in range(0, LOOP_TIME):
        # try:
        print('Giao dich lan thu ', elem)
        slave_pt.check_login_success()
        if slave_pt.ktc_open():
            slave_pt.use_dnp()
            slave_pt.exit_dnp_opening()
            slave_pt.go_pawn()
            if slave_pt.pawn_coin():
                slave_pt.socket_client.send_message('GD', 'BillGatePT')
                print('Cho Bill Gate phan hoi')
                msg = slave_pt.socket_client.recv_msg()
                is_success = True
                if msg == 'THGD':
                    for idx in range(0, 500):
                        if not is_success:
                            msg = slave_pt.socket_client.recv_msg()
                        is_success = slave_pt.slave_gd_enter()
                        if is_success:
                            print('Goi message san sang gd')
                            slave_pt.socket_client.send_message('GD_OK', 'BillGatePT')
                            break
                        else:
                            slave_pt.socket_client.send_message('GD_FAILED', 'BillGatePT')
                            is_success = False

                    time.sleep(1)
                    is_success = slave_pt.slave_gd()
        if slave_pt.exit_game() != -1:
            if not slave_pt.loggin_tk(check_delete_buttom=True):
                if slave_pt.delete_nv():
                    slave_pt.create_nv()
                    slave_pt.check_tao_nv_failed()
        slave_pt.loggin_tk()
        # except Exception as e:
        #     print(str(e))
        #     pass
    # slave_pt.loggin_tk()
    # slave_pt.delete_nv()
    slave_pt.socket_client.send_message(DISCONNECT_MSG, 'init')
    print('Time running : ', datetime.now() - start)
