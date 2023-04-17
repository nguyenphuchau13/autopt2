import pywinauto
from pywinauto import mouse
from pywinauto.application import Application
import time
import ctypes
from pywinauto.keyboard import send_keys
from pywinauto import keyboard as ks
import cv2
import cv2
import numpy as np
import pyautogui
import os

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


class SlavePT:
    TK_POS_X = '179'
    TK_POS_Y = '188'
    NUM_COIN = '1'
    PASS = '0964892408a'
    NUMBER_NV = 101
    NAME_NV = 'mrslave102'
    PT_LOGO = 'image/child_chon_nv_page_pt_viet.png'

    # PT_LOGO = 'image/child_chon_nv_page_pt_2.png'

    def __init__(self, master_handle, bill_gates_handle=None):
        self.name_nv = ''
        self.app = pywinauto.application.Application().connect(handle=master_handle)
        if bill_gates_handle:
            self.app_bill_gates = pywinauto.application.Application().connect(handle=bill_gates_handle)

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
            path_image_live, 'image/child_cam_do.png', 20, 15, log_error=' Cam do not found')
        if not is_success:
            return False
        time.sleep(2)
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
        self.app.FSOnlineClass.type_keys(SlavePT.NUM_COIN)
        time.sleep(0.2)
        path_image_live = 'image/live_image/do_cam_do_page_confirm.png'
        is_success = self.action(
            path_image_live, 'image/child_cam_do_confirm.png', 20, 15, log_error=' Cam do page not found 2')
        if not is_success:
            return False
        time.sleep(0.5)
        path_image_live = 'image/live_image/do_cam_do_page_confirm_again.png'
        is_success = self.action(
            path_image_live, 'image/child_cam_do_confirm.png', 20, 15, log_error=' Cam do page not found 2')
        if not is_success:
            return False
        time.sleep(0.5)
        self.app.FSOnlineClass.type_keys('{ESC}')

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
        time.sleep(1)
        # self.app.FSOnlineClass.type_keys('{F4}')
        # time.sleep(0.2)

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
        time.sleep(25)
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
        time.sleep(1)
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

    def action_open_out_page(self):
        print('action_open_out_page .....')
        is_success = False
        for index in range(0, 3):
            time.sleep(0.5)
            self.app.FSOnlineClass.type_keys('{ESC}')
            time.sleep(0.2)
            path_image_live = 'image/live_image/delete_page.png'
            is_success = self.action(path_image_live, 'image/child_chon_nv.png', 20, 15,
                                     log_error='delete_page not found cos the bo qua')
            if is_success:
                return is_success
        return is_success

    def exit_game(self):
        print('Thoat Game ...')
        self.action_open_out_page()
        time.sleep(0.5)
        self.app.FSOnlineClass.type_keys('{ESC}')
        time.sleep(0.5)
        path_image_live = 'image/live_image/delete_page.png'
        is_success = self.action(path_image_live, 'image/child_chon_nv.png', 20, 15, log_error='delete_page not found')
        if not is_success:
            return False
        self.app.FSOnlineClass.set_focus()
        time.sleep(0.3)
        path_image_live = 'image/live_image/delete_check_exit.png'
        is_success = self.action(path_image_live, 'image/child_delete_tk_dsd.png', 20, 15,
                                 log_error='child_delete_tk_dsd not found')
        if is_success:
            self.app.FSOnlineClass.type_keys('{ENTER}')
            self.loggin_tk()
            time.sleep(0.3)
        time.sleep(2)
        print(' Thoat Game thanh cong')

    def delete_nv(self):
        time.sleep(2)
        print('Xoa nhan vat ...')
        is_success = False
        for idx in range(0, 1000):
            path_image_live = 'image/live_image/delete_nv_page.png'
            is_success = self.action(path_image_live, self.PT_LOGO, 20, 15,
                                     log_error='child_chon_nv_page not found')
            if is_success:
                break
        if not is_success:
            return False
        print('Tim xoa nv buttom ...')
        path_image_live = 'image/live_image/delete_nv_page.png'
        is_success = self.action(path_image_live, 'image/child_xoa_nv_buttom.png', 20, 15,
                                 log_error='child_xoa_nv_buttom not found')
        if not is_success:
            return False
        time.sleep(0.5)
        self.app.FSOnlineClass.type_keys(self.PASS)
        time.sleep(0.2)
        self.app.FSOnlineClass.type_keys('{ENTER}')
        time.sleep(0.2)
        self.app.FSOnlineClass.type_keys('{TAB}')
        time.sleep(0.2)
        self.app.FSOnlineClass.type_keys('{ENTER}')
        time.sleep(0.2)
        is_success = True
        for idx in range(0, 1000):
            time.sleep(0.2)
            path_image_live = 'image/live_image/delete_nv_page.png'
            is_success = self.action(path_image_live, 'image/child_wait_delete_nv.png', 20, 15,
                                     log_error='child_xoa_nv_buttom not found', no_click=True)
            if not is_success:
                break
            time.sleep(0.2)
            path_image_live = 'image/live_image/delete_nv_page.png'
            print('Kien tra bao tri')
            is_success = self.action(path_image_live, 'image/child_bao_tri.png', 20, 15,
                                     log_error='child_bao_tri not found', no_click=True)
            if is_success:
                self.app.FSOnlineClass.type_keys('{ENTER}')
                break
        print('Xoa nhan vat Thanh cong....')
        return True

    def create_nv(self):
        time.sleep(0.5)
        print('Tao nhan vat ...')
        path_image_live = 'image/live_image/create_nv_page.png'
        is_success = self.action(path_image_live, 'image/child_create_nv_buttom.png', 20, 15,
                                 log_error='child_create_nv_buttom not found')
        if not is_success:
            return False
        time.sleep(1)
        print('Dat ten nhan viet ...')
        path_image_live = 'image/live_image/create_name_nv_page.png'
        is_success = self.action(path_image_live, 'image/child_name_nv_page.png', 20, 15,
                                 log_error='child_create_nv_buttom not found')
        if not is_success:
            return False

        for idx in range(0, 40):
            self.app.FSOnlineClass.type_keys('{BACKSPACE}')
        time.sleep(0.2)
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
        for elem in range(0, 1000):
            time.sleep(0.2)
            path_image_live = 'image/live_image/login_page.png'
            is_success = self.action(path_image_live, 'image/child_vao_game_button.png', 20, 15,
                                     log_error='child_vao_game_button not found', no_click=True)
            if is_success:
                break
            time.sleep(0.2)
            path_image_live = 'image/live_image/login_page.png'
            is_success = self.action(path_image_live, 'image/child_server_bao_tri.png', 20, 15,
                                     log_error='child_vao_game_button not found', no_click=True)
            if is_success:
                self.app.FSOnlineClass.type_keys('{ENTER}')
                if not self.login_button_action():
                    return False
        print('Nhap pass ')
        time.sleep(0.2)
        self.app.FSOnlineClass.type_keys(self.PASS)
        time.sleep(1)
        print('Nhap ENTER pass ')
        self.app.FSOnlineClass.type_keys('{ENTER}')
        for idx in range(0, 1000):
            time.sleep(0.2)
            is_success = self.action(path_image_live, self.PT_LOGO, 20, 15,
                                     log_error='child_chon_nv_page not found', no_click=True)
            if is_success == True:
                break
        if self.delete_nv():
            self.create_nv()
            self.check_tao_nv_failed()
            print('Login Thanh cong')
        else:
            print('Login That bai')

        return True

    def input_pass(self):
        self.app.FSOnlineClass.type_keys('')

    def check_login_success(self, num_loop=1000):
        for idx in range(0, num_loop):
            time.sleep(0.2)
            path_image_live = 'image/live_image/game_windown.png'
            is_success = self.action(path_image_live, 'image/child_check_login_success.png', 20, 15,
                                     log_error='check_login_success not found', no_click=True)
            if is_success:
                print('Da vao game')
                break
        print('Chua vao game')


if __name__ == "__main__":
    slave_handle = 1640344
    bill_gates_handle = 3015796
    mywindows = pywinauto.findwindows.find_windows(title_re="PhongThan2.Com -")
    print(mywindows)
    [1640344, 3015796]
    app = pywinauto.application.Application().connect(handle=slave_handle)
    # app.FSOnlineClass.set_focus()
    slave_pt = SlavePT(slave_handle, bill_gates_handle)

# for elem in range(0, 10):
#     slave_pt.check_login_success()
#     if not slave_pt.ktc_open():
#         exit(0)
#     slave_pt.use_dnp()
#     slave_pt.go_pawn()
#     slave_pt.pawn_coin()
#     slave_pt.exit_game()
#     if not slave_pt.loggin_tk():
#         if slave_pt.delete_nv():
#             slave_pt.create_nv()
#             slave_pt.check_tao_nv_failed()
#     slave_pt.loggin_tk()
#     os.system('cls')
# slave_pt.loggin_tk()
# slave_pt.delete_nv()
