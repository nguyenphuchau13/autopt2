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


class MasterPT:
    TK_POS_X = '179'
    TK_POS_Y = '188'
    NUM_COIN = '20'

    def __init__(self, master_hanld):
        self.app = pywinauto.application.Application().connect(handle=master_hanld)

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
        self.app.FSOnlineClass.type_keys(MasterPT.NUM_COIN)
        time.sleep(0.2)
        path_image_live = 'image/live_image/do_cam_do_page_confirm.png'
        is_success = self.action(
            path_image_live, 'image/child_cam_do_confirm.png', 20, 15, log_error=' Cam do page not found 2')
        if not is_success:
            return False
        time.sleep(0.2)
        path_image_live = 'image/live_image/do_cam_do_page_confirm_again.png'
        is_success = self.action(
            path_image_live, 'image/child_cam_do_confirm.png', 20, 15, log_error=' Cam do page not found 2')
        if not is_success:
            return False

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
        self.app.FSOnlineClass.type_keys(MasterPT.TK_POS_X)

        path_image_live = 'image/live_image/tk.png'
        is_success = self.action(
            path_image_live, 'image/child_y_pos.png', 16, 4, log_error=' Not found x_post')
        if not is_success:
            return False
        self.app.FSOnlineClass.type_keys(MasterPT.TK_POS_Y)

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

    def action(self, path_image_live, path_child_image, x_adjust, y_adjust, log_error='', debug=False,
               right_click=False):
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

    def exit_game(self):
        # self.app.FSOnlineClass.type_keys('{ESC}')
        # time.sleep(0.5)
        # path_image_live = 'image/live_image/delete_page.png'
        # is_success = self.action(path_image_live, 'image/child_chon_nv.png', 20, 15, log_error='delete_page not found')
        # if not is_success:
        #     return False
        self.app.FSOnlineClass.set_focus()
        time.sleep(0.3)
        path_image_live = 'image/live_image/delete_check_exit.png'
        is_success = self.action(path_image_live, 'image/child_delete_tk_dsd.png', 20, 15, log_error='DNP not found')
        if is_success:
            self.app.FSOnlineClass.type_keys('{ENTER}')
            time.sleep(0.3)
    def input_pass(self):
        self.app.FSOnlineClass.type_keys('')
if __name__ == "__main__":
    master_hanld = 1049674
    # mywindows = pywinauto.findwindows.find_windows(title_re="PhongThan2.Com - Version 3.32")
    # app = pywinauto.application.Application().connect(handle=1049674)
    master_pt = MasterPT(master_hanld)

    # if not master_pt.ktc_open():
    #     exit(0)
    # master_pt.use_dnp()
    # master_pt.go_pawn()
    # master_pt.pawn_coin()
    master_pt.exit_game()