from kivy.lang import Builder
from kivy.properties import StringProperty, ObjectProperty, BooleanProperty
from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.list import OneLineListItem, ThreeLineListItem
from core import Database

KV = """
ScreenManager:
    LoginScreen:
    HomeScreen:
    BorrowScreen:
    ReturnScreen:
    RecordsScreen:
    SecurityLogScreen:
    ChangePasswordScreen:

<LoginScreen>:
    name: 'login'
    MDFloatLayout:
        MDCard:
            size_hint: .92, None
            height: '360dp'
            pos_hint: {'center_x': .5, 'center_y': .5}
            padding: '18dp'
            spacing: '12dp'
            orientation: 'vertical'
            MDLabel:
                text: '儀器借還系統 APK 版'
                font_style: 'H5'
                adaptive_height: True
            MDLabel:
                text: '支援 NFC 預留接口、SQLite、本地登入。預設 admin / admin1234。'
                theme_text_color: 'Secondary'
                adaptive_height: True
            MDTextField:
                id: username
                hint_text: 'Username'
            MDTextField:
                id: password
                hint_text: 'Password'
                password: True
            MDRaisedButton:
                text: '登入'
                pos_hint: {'center_x': .5}
                on_release: root.do_login()
            MDTextButton:
                text: '載入示範資料'
                pos_hint: {'center_x': .5}
                on_release: root.seed_demo()

<HomeScreen>:
    name: 'home'
    MDBoxLayout:
        orientation: 'vertical'
        MDTopAppBar:
            title: app.app_title
            right_action_items: [['logout', lambda x: root.do_logout()]]
        ScrollView:
            MDBoxLayout:
                orientation: 'vertical'
                adaptive_height: True
                padding: '12dp'
                spacing: '10dp'
                MDCard:
                    orientation: 'vertical'
                    adaptive_height: True
                    padding: '14dp'
                    MDLabel:
                        text: root.user_summary
                        adaptive_height: True
                    MDLabel:
                        text: root.staff_summary
                        adaptive_height: True
                    MDLabel:
                        text: root.nfc_summary
                        adaptive_height: True
                        theme_text_color: 'Secondary'
                MDRaisedButton:
                    text: '借出'
                    on_release: root.go_borrow()
                MDRaisedButton:
                    text: '還機'
                    on_release: root.go_return()
                MDRaisedButton:
                    text: '我的借還記錄'
                    on_release: root.go_records()
                MDRaisedButton:
                    text: '改密碼'
                    on_release: app.root.current = 'change_password'
                MDRaisedButton:
                    text: 'Security Log（Admin）'
                    disabled: not root.is_admin
                    on_release: root.go_security_log()

<BorrowScreen>:
    name: 'borrow'
    MDBoxLayout:
        orientation: 'vertical'
        padding: '12dp'
        spacing: '10dp'
        MDTopAppBar:
            title: '借出'
            left_action_items: [['arrow-left', lambda x: root.go_back()]]
            right_action_items: [['cellphone-nfc', lambda x: root.mock_nfc_borrower()]]
        MDTextField:
            id: equipment
            hint_text: '儀器編碼 / NFC UID'
        MDTextField:
            id: borrower
            hint_text: '借用人員工編號 / 姓名 / NFC UID'
            text: root.borrower_code
            readonly: root.borrower_locked
        MDTextField:
            id: borrower_name
            hint_text: '借用人姓名'
            text: root.borrower_name
            readonly: True
        MDTextField:
            id: witness
            hint_text: '見證人員工編號 / 姓名 / NFC UID'
        MDRaisedButton:
            text: '提交借出'
            on_release: root.submit_borrow()

<ReturnScreen>:
    name: 'return'
    MDBoxLayout:
        orientation: 'vertical'
        padding: '12dp'
        spacing: '10dp'
        MDTopAppBar:
            title: '還機'
            left_action_items: [['arrow-left', lambda x: root.go_back()]]
            right_action_items: [['cellphone-nfc', lambda x: root.mock_nfc_borrower()]]
        MDTextField:
            id: equipment
            hint_text: '儀器編碼 / NFC UID'
        MDTextField:
            id: borrower
            hint_text: '還機人員工編號 / 姓名 / NFC UID'
            text: root.borrower_code
            readonly: root.borrower_locked
        MDTextField:
            id: borrower_name
            hint_text: '還機人姓名'
            text: root.borrower_name
            readonly: True
        MDTextField:
            id: witness
            hint_text: '見證人員工編號 / 姓名 / NFC UID'
        MDRaisedButton:
            text: '提交還機'
            on_release: root.submit_return()

<RecordsScreen>:
    name: 'records'
    MDBoxLayout:
        orientation: 'vertical'
        MDTopAppBar:
            title: '我的借還記錄'
            left_action_items: [['arrow-left', lambda x: root.go_back()]]
            right_action_items: [['refresh', lambda x: root.load_records()]]
        ScrollView:
            MDList:
                id: records_list

<SecurityLogScreen>:
    name: 'security_logs'
    MDBoxLayout:
        orientation: 'vertical'
        MDTopAppBar:
            title: 'Security Audit Log'
            left_action_items: [['arrow-left', lambda x: root.go_back()]]
            right_action_items: [['refresh', lambda x: root.load_logs()]]
        ScrollView:
            MDList:
                id: logs_list

<ChangePasswordScreen>:
    name: 'change_password'
    MDBoxLayout:
        orientation: 'vertical'
        padding: '12dp'
        spacing: '10dp'
        MDTopAppBar:
            title: '修改密碼'
            left_action_items: [['arrow-left', lambda x: root.go_back()]]
        MDTextField:
            id: old_password
            hint_text: '舊密碼'
            password: True
        MDTextField:
            id: new_password
            hint_text: '新密碼'
            password: True
        MDTextField:
            id: confirm_password
            hint_text: '確認新密碼'
            password: True
        MDRaisedButton:
            text: '儲存新密碼'
            on_release: root.change_password()
"""

def toast(msg):
    Snackbar(text=msg, duration=2).open()

class LoginScreen(Screen):
    def do_login(self):
        app = MDApp.get_running_app()
        try:
            user = app.db.login(self.ids.username.text.strip(), self.ids.password.text)
            app.current_user = user
            app.sync_user_profile()
            toast(f"登入成功：{user['display_name']}")
            app.root.current = 'change_password' if user['must_change_password'] else 'home'
        except Exception as e:
            toast(str(e))

    def seed_demo(self):
        app = MDApp.get_running_app()
        app.db.seed_demo_data()
        toast('已載入示範資料')

class HomeScreen(Screen):
    user_summary = StringProperty('')
    staff_summary = StringProperty('')
    nfc_summary = StringProperty('')
    is_admin = BooleanProperty(False)

    def on_pre_enter(self):
        app = MDApp.get_running_app()
        user = app.current_user
        self.is_admin = bool(user and user['role'] == 'admin')
        self.user_summary = f"登入中：{user['display_name']}（{user['username']} / {user['role']}）" if user else ''
        if app.current_staff:
            self.staff_summary = f"綁定員工：{app.current_staff['staff_code']}｜{app.current_staff['staff_name']}｜{app.current_staff['department'] or ''}"
            self.nfc_summary = f"員工 NFC UID：{app.current_staff['nfc_uid'] or '未設定'}"
        else:
            self.staff_summary = '此帳戶未綁定 staff_code 或找不到員工資料'
            self.nfc_summary = '可由 admin 在後續版本管理'

    def go_borrow(self):
        MDApp.get_running_app().root.current = 'borrow'

    def go_return(self):
        MDApp.get_running_app().root.current = 'return'

    def go_records(self):
        scr = MDApp.get_running_app().root.get_screen('records')
        scr.load_records()
        MDApp.get_running_app().root.current = 'records'

    def go_security_log(self):
        scr = MDApp.get_running_app().root.get_screen('security_logs')
        scr.load_logs()
        MDApp.get_running_app().root.current = 'security_logs'

    def do_logout(self):
        app = MDApp.get_running_app()
        if app.current_user:
            app.db.logout(app.current_user)
        app.current_user = None
        app.current_staff = None
        app.root.current = 'login'
        toast('已登出')

class BorrowScreen(Screen):
    borrower_code = StringProperty('')
    borrower_name = StringProperty('')
    borrower_locked = BooleanProperty(False)

    def on_pre_enter(self):
        app = MDApp.get_running_app()
        self.ids.equipment.text = ''
        self.ids.witness.text = ''
        if app.current_user and app.current_user['role'] == 'user' and app.current_staff:
            self.borrower_code = app.current_staff['staff_code']
            self.borrower_name = app.current_staff['staff_name']
            self.borrower_locked = True
        else:
            self.borrower_code = ''
            self.borrower_name = app.current_staff['staff_name'] if app.current_staff else ''
            self.borrower_locked = False
        self.ids.borrower.text = self.borrower_code
        self.ids.borrower_name.text = self.borrower_name

    def mock_nfc_borrower(self):
        app = MDApp.get_running_app()
        if app.current_staff and app.current_staff['nfc_uid']:
            self.ids.borrower.text = app.current_staff['nfc_uid']
            self.ids.borrower_name.text = app.current_staff['staff_name']
            toast('已模擬讀取借用人 NFC UID')
        else:
            toast('此登入帳戶未綁定帶有 NFC UID 的員工')

    def submit_borrow(self):
        app = MDApp.get_running_app()
        try:
            tx_uuid = app.db.borrow(
                self.ids.equipment.text,
                self.ids.borrower.text,
                self.ids.witness.text,
                app.current_user
            )
            toast(f'借出成功：{tx_uuid[:8]}')
            self.go_back()
        except Exception as e:
            toast(str(e))

    def go_back(self):
        MDApp.get_running_app().root.current = 'home'

class ReturnScreen(Screen):
    borrower_code = StringProperty('')
    borrower_name = StringProperty('')
    borrower_locked = BooleanProperty(False)

    def on_pre_enter(self):
        app = MDApp.get_running_app()
        self.ids.equipment.text = ''
        self.ids.witness.text = ''
        if app.current_user and app.current_user['role'] == 'user' and app.current_staff:
            self.borrower_code = app.current_staff['staff_code']
            self.borrower_name = app.current_staff['staff_name']
            self.borrower_locked = True
        else:
            self.borrower_code = ''
            self.borrower_name = app.current_staff['staff_name'] if app.current_staff else ''
            self.borrower_locked = False
        self.ids.borrower.text = self.borrower_code
        self.ids.borrower_name.text = self.borrower_name

    def mock_nfc_borrower(self):
        app = MDApp.get_running_app()
        if app.current_staff and app.current_staff['nfc_uid']:
            self.ids.borrower.text = app.current_staff['nfc_uid']
            self.ids.borrower_name.text = app.current_staff['staff_name']
            toast('已模擬讀取還機人 NFC UID')
        else:
            toast('此登入帳戶未綁定帶有 NFC UID 的員工')

    def submit_return(self):
        app = MDApp.get_running_app()
        try:
            tx_uuid = app.db.return_item(
                self.ids.equipment.text,
                self.ids.borrower.text,
                self.ids.witness.text,
                app.current_user
            )
            toast(f'還機成功：{tx_uuid[:8]}')
            self.go_back()
        except Exception as e:
            toast(str(e))

    def go_back(self):
        MDApp.get_running_app().root.current = 'home'

class RecordsScreen(Screen):
    def load_records(self):
        app = MDApp.get_running_app()
        self.ids.records_list.clear_widgets()
        borrower_code = None if app.current_user['role'] == 'admin' else app.current_user['staff_code']
        rows = app.db.list_transactions(borrower_code=borrower_code, limit=200)
        if not rows:
            self.ids.records_list.add_widget(OneLineListItem(text='無借還記錄'))
            return
        for r in rows:
            self.ids.records_list.add_widget(
                ThreeLineListItem(
                    text=f"{r['tx_type']}｜{r['equipment_code']}｜{r['equipment_name'] or ''}",
                    secondary_text=f"借用人：{r['borrower_name'] or ''}｜見證人：{r['witness_name'] or ''}",
                    tertiary_text=f"時間：{r['tx_time']}｜操作：{r['operator_display_name'] or ''}"
                )
            )

    def go_back(self):
        MDApp.get_running_app().root.current = 'home'

class SecurityLogScreen(Screen):
    def load_logs(self):
        app = MDApp.get_running_app()
        self.ids.logs_list.clear_widgets()
        if app.current_user['role'] != 'admin':
            self.ids.logs_list.add_widget(OneLineListItem(text='只有 admin 可查看 Security Log'))
            return
        rows = app.db.list_security_logs(200)
        if not rows:
            self.ids.logs_list.add_widget(OneLineListItem(text='無 Security Log'))
            return
        for r in rows:
            self.ids.logs_list.add_widget(
                ThreeLineListItem(
                    text=f"{r['event_type']}｜{'成功' if r['success'] else '失敗'}",
                    secondary_text=f"actor: {r['actor_username'] or '-'}｜target: {r['target_username'] or '-'}",
                    tertiary_text=f"{r['created_at']}｜{r['message'] or ''}"
                )
            )

    def go_back(self):
        MDApp.get_running_app().root.current = 'home'

class ChangePasswordScreen(Screen):
    def change_password(self):
        app = MDApp.get_running_app()
        oldp = self.ids.old_password.text
        newp = self.ids.new_password.text
        conf = self.ids.confirm_password.text
        try:
            if len(newp) < 6:
                raise ValueError('新密碼至少 6 個字元')
            if newp != conf:
                raise ValueError('確認密碼不一致')
            app.db.change_own_password(app.current_user['id'], oldp, newp)
            app.current_user = app.db.get_user_by_id(app.current_user['id'])
            self.ids.old_password.text = ''
            self.ids.new_password.text = ''
            self.ids.confirm_password.text = ''
            toast('已成功修改密碼')
            app.root.current = 'home'
        except Exception as e:
            toast(str(e))

    def go_back(self):
        MDApp.get_running_app().root.current = 'home'

class EquipmentLendingMobileApp(MDApp):
    app_title = '儀器借還系統 APK 版'
    current_user = ObjectProperty(None)
    current_staff = ObjectProperty(None)

    def build(self):
        self.theme_cls.primary_palette = 'Teal'
        self.db = Database()
        return Builder.load_string(KV)

    def sync_user_profile(self):
        if self.current_user and self.current_user['staff_code']:
            self.current_staff = self.db.get_staff(self.current_user['staff_code'])
        else:
            self.current_staff = None

if __name__ == '__main__':
    EquipmentLendingMobileApp().run()