import json
import os
import random
import time
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

Window.clearcolor = (0.058, 0.09, 0.165, 1)

try:
    from jnius import autoclass
    ANDROID_ENV = True
except ImportError:
    ANDROID_ENV = False


class RoundedButton(Button):
    def __init__(self, bg_color=(0.38, 0.4, 0.94, 1), **kwargs):
        super(RoundedButton, self).__init__(**kwargs)
        self.bg_color = bg_color
        self.background_color = (0, 0, 0, 0)
        self.bind(pos=self.update_canvas, size=self.update_canvas)

    def update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.bg_color)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(12)])


class DashboardScreen(Screen):
    def __init__(self, **kwargs):
        super(DashboardScreen, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        header = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(80), spacing=dp(5))
        title = Label(
            text="[b]STUDY COMMAND CENTER[/b]", 
            markup=True, 
            font_size=dp(22), 
            color=(0.9, 0.93, 1, 1),
            halign='left'
        )
        title.bind(size=title.setter('text_size'))
        subtitle = Label(
            text="Master your syllabus and crush your goals", 
            font_size=dp(14), 
            color=(0.58, 0.64, 0.76, 1),
            halign='left'
        )
        subtitle.bind(size=subtitle.setter('text_size'))
        header.add_widget(title)
        header.add_widget(subtitle)
        self.layout.add_widget(header)
        
        self.progress_card = BoxLayout(
            orientation='vertical', 
            size_hint_y=None, 
            height=dp(110), 
            padding=dp(15), 
            spacing=dp(8)
        )
        self.progress_card.bind(pos=self.update_card_bg, size=self.update_card_bg)
        
        self.progress_label = Label(text="Overall Syllabus Progress: 0%", font_size=dp(16), bold=True, color=(1, 1, 1, 1))
        self.progress_label.bind(size=self.progress_label.setter('text_size'))
        
        self.stats_label = Label(text="Completed: 0 / Total: 0 Chapters", font_size=dp(13), color=(0.7, 0.75, 0.85, 1))
        self.stats_label.bind(size=self.stats_label.setter('text_size'))
        
        self.progress_card.add_widget(self.progress_label)
        self.progress_card.add_widget(self.stats_label)
        self.layout.add_widget(self.progress_card)
        
        btn_syllabus = RoundedButton(
            text="Manage and Track Syllabus", 
            bg_color=(0.24, 0.31, 0.7, 1), 
            size_hint_y=None, 
            height=dp(55)
        )
        btn_syllabus.bind(on_press=self.go_to_syllabus)
        self.layout.add_widget(btn_syllabus)
        
        btn_focus = RoundedButton(
            text="Hard Lockdown and Focus Session", 
            bg_color=(0.86, 0.2, 0.2, 1), 
            size_hint_y=None, 
            height=dp(55)
        )
        btn_focus.bind(on_press=self.go_to_focus)
        self.layout.add_widget(btn_focus)
        
        self.layout.add_widget(Label())
        self.add_widget(self.layout)

    def update_card_bg(self, instance, *args):
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(0.117, 0.165, 0.278, 1)
            RoundedRectangle(pos=instance.pos, size=instance.size, radius=[dp(16)])

    def on_enter(self):
        self.update_stats()

    def update_stats(self):
        app = App.get_running_app()
        data = app.load_data()
        topics = data.get("topics", [])
        total = len(topics)
        done = sum(1 for t in topics if t["done"])
        percent = int((done / total) * 100) if total > 0 else 0
        
        self.progress_label.text = f"Overall Syllabus Progress: {percent}%"
        self.stats_label.text = f"Completed: {done} / Total: {total} Chapters"

    def go_to_syllabus(self, instance):
        self.manager.current = 'syllabus'

    def go_to_focus(self, instance):
        self.manager.current = 'focus'


class SyllabusScreen(Screen):
    def __init__(self, **kwargs):
        super(SyllabusScreen, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        top_bar = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        back_btn = RoundedButton(text="<- Back", bg_color=(0.3, 0.35, 0.45, 1), size_hint_x=None, width=dp(90))
        back_btn.bind(on_press=self.go_back)
        
        header_lbl = Label(text="[b]Syllabus and Chapter Tracker[/b]", markup=True, font_size=dp(18), color=(1,1,1,1))
        header_lbl.bind(size=header_lbl.setter('text_size'))
        
        top_bar.add_widget(back_btn)
        top_bar.add_widget(header_lbl)
        self.layout.add_widget(top_bar)
        
        input_box = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        self.text_input = TextInput(
            hint_text="Add Subject / Chapter (e.g. Accountancy - Partnership)",
            multiline=False,
            background_color=(0.117, 0.165, 0.278, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(1, 1, 1, 1),
            padding=[dp(12), dp(12)]
        )
        add_btn = RoundedButton(text="Add", bg_color=(0.13, 0.7, 0.45, 1), size_hint_x=None, width=dp(90))
        add_btn.bind(on_press=self.add_topic)
        
        input_box.add_widget(self.text_input)
        input_box.add_widget(add_btn)
        self.layout.add_widget(input_box)
        
        self.scroll = ScrollView()
        self.topic_list_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(10))
        self.topic_list_layout.bind(minimum_height=self.topic_list_layout.setter('height'))
        self.scroll.add_widget(self.topic_list_layout)
        self.layout.add_widget(self.scroll)
        
        self.add_widget(self.layout)

    def on_enter(self):
        self.refresh_list()

    def refresh_list(self):
        self.topic_list_layout.clear_widgets()
        app = App.get_running_app()
        data = app.load_data()
        
        for idx, topic in enumerate(data.get("topics", [])):
            row = BoxLayout(size_hint_y=None, height=dp(55), spacing=dp(10), padding=[dp(10), dp(5)])
            row.bind(pos=self.update_row_bg, size=self.update_row_bg)
            
            chk = CheckBox(active=topic["done"], size_hint_x=None, width=dp(40))
            chk.bind(active=lambda inst, val, i=idx: app.toggle_topic(i, val))
            
            lbl = Label(text=topic["name"], font_size=dp(15), color=(0.9, 0.93, 1, 1), halign='left', valign='middle')
            lbl.bind(size=lbl.setter('text_size'))
            
            del_btn = RoundedButton(text="X", bg_color=(0.8, 0.2, 0.2, 1), size_hint_x=None, width=dp(45))
            del_btn.bind(on_press=lambda inst, i=idx: app.delete_topic(i, self.refresh_list))
            
            row.add_widget(chk)
            row.add_widget(lbl)
            row.add_widget(del_btn)
            self.topic_list_layout.add_widget(row)

    def update_row_bg(self, instance, *args):
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(0.117, 0.165, 0.278, 1)
            RoundedRectangle(pos=instance.pos, size=instance.size, radius=[dp(10)])

    def add_topic(self, instance):
        text = self.text_input.text.strip()
        if text:
            app = App.get_running_app()
            data = app.load_data()
            data["topics"].append({"name": text, "done": False})
            app.save_data(data)
            self.text_input.text = ""
            self.refresh_list()

    def go_back(self, instance):
        self.manager.current = 'dashboard'


class FocusScreen(Screen):
    def __init__(self, **kwargs):
        super(FocusScreen, self).__init__(**kwargs)
        self.total_seconds = 3600  # Default 1 hour
        self.seconds_left = 3600
        self.timer_running = False
        self.timer_event = None
        self.quote_event = None
        
        self.motivations = [
            "Discipline over motivation. Stay locked in.",
            "Your future in Tech and AI starts with mastering today's syllabus.",
            "Scrolling will not pass your exams. Studying will.",
            "Pain of discipline or pain of regret. Choose one.",
            "Every minute you focus right now brings you closer to your dreams.",
            "Close the distractions. Open your mind.",
            "You are building your own destiny right now. Keep pushing."
        ]
        
        layout = BoxLayout(orientation='vertical', padding=dp(25), spacing=dp(15))
        
        top_bar = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        self.back_btn = RoundedButton(text="<- Exit", bg_color=(0.3, 0.35, 0.45, 1), size_hint_x=None, width=dp(90))
        self.back_btn.bind(on_press=self.go_back)
        
        header_lbl = Label(text="[b]Hard Lockdown and Focus[/b]", markup=True, font_size=dp(18), color=(1,1,1,1))
        header_lbl.bind(size=header_lbl.setter('text_size'))
        top_bar.add_widget(self.back_btn)
        top_bar.add_widget(header_lbl)
        layout.add_widget(top_bar)
        
        # Timer Adjust Layout (Before Lockdown)
        self.adjust_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        self.minus_btn = RoundedButton(text="- 15m", bg_color=(0.4, 0.4, 0.5, 1))
        self.minus_btn.bind(on_press=lambda x: self.adjust_time(-900))
        
        self.time_display_lbl = Label(text="Duration: 60 mins", font_size=dp(15), color=(1, 1, 1, 1), bold=True)
        
        self.plus_btn = RoundedButton(text="+ 15m", bg_color=(0.4, 0.4, 0.5, 1))
        self.plus_btn.bind(on_press=lambda x: self.adjust_time(900))
        
        self.adjust_layout.add_widget(self.minus_btn)
        self.adjust_layout.add_widget(self.time_display_lbl)
        self.adjust_layout.add_widget(self.plus_btn)
        layout.add_widget(self.adjust_layout)
        
        self.timer_card = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(220), padding=dp(20), spacing=dp(10))
        self.timer_card.bind(pos=self.update_card_bg, size=self.update_card_bg)
        
        self.timer_label = Label(text="60:00", font_size=dp(50), bold=True, color=(1, 0.3, 0.3, 1))
        self.motivation_label = Label(
            text="Set duration above and tap below to lock phone and ignite deep focus.", 
            font_size=dp(14), 
            color=(0.85, 0.9, 1, 1),
            halign='center',
            valign='middle'
        )
        self.motivation_label.bind(size=self.motivation_label.setter('text_size'))
        
        self.timer_card.add_widget(self.timer_label)
        self.timer_card.add_widget(self.motivation_label)
        layout.add_widget(self.timer_card)
        
        self.action_btn = RoundedButton(text="START HARD LOCKDOWN", bg_color=(0.86, 0.2, 0.2, 1), size_hint_y=None, height=dp(60))
        self.action_btn.bind(on_press=self.toggle_lockdown)
        layout.add_widget(self.action_btn)
        
        layout.add_widget(Label())
        self.add_widget(layout)

    def update_card_bg(self, instance, *args):
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(0.117, 0.165, 0.278, 1)
            RoundedRectangle(pos=instance.pos, size=instance.size, radius=[dp(16)])

    def adjust_time(self, seconds):
        if not self.timer_running:
            self.total_seconds = max(900, self.total_seconds + seconds)  # Minimum 15 mins
            self.seconds_left = self.total_seconds
            mins = self.total_seconds // 60
            self.time_display_lbl.text = f"Duration: {mins} mins"
            self.timer_label.text = f"{mins:02d}:00"

    def toggle_lockdown(self, instance):
        if not self.timer_running:
            self.start_lockdown_session(self.seconds_left)
        else:
            self.motivation_label.text = "Session locked! You cannot escape discipline now."

    def start_lockdown_session(self, duration_secs):
        self.timer_running = True
        self.total_seconds = duration_secs
        self.seconds_left = duration_secs
        
        app = App.get_running_app()
        app.focus_active = True
        
        # Save persistent state to survive reboots/power off attempts
        end_time = time.time() + self.seconds_left
        app.save_lockdown_state(True, end_time)
        
        self.adjust_layout.opacity = 0
        self.adjust_layout.disabled = True
        self.action_btn.text = "HARD LOCKDOWN ACTIVE"
        self.action_btn.bg_color = (0.3, 0.3, 0.3, 1)
        self.back_btn.disabled = True
        
        if ANDROID_ENV:
            try:
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                activity = PythonActivity.mActivity
                activity.startLockTask()
            except Exception as e:
                print(f"Android LockTask error: {e}")

        self.timer_event = Clock.schedule_interval(self.update_timer, 1)
        self.quote_event = Clock.schedule_interval(self.rotate_motivation, 8)
        self.rotate_motivation(0)

    def rotate_motivation(self, dt):
        self.motivation_label.text = random.choice(self.motivations)

    def update_timer(self, dt):
        if self.seconds_left > 0:
            self.seconds_left -= 1
            mins = self.seconds_left // 60
            secs = self.seconds_left % 60
            self.timer_label.text = f"{mins:02d}:{secs:02d}"
        else:
            self.end_lockdown_session()

    def end_lockdown_session(self):
        if self.timer_event:
            self.timer_event.cancel()
        if self.quote_event:
            self.quote_event.cancel()
            
        self.timer_running = False
        app = App.get_running_app()
        app.focus_active = False
        app.save_lockdown_state(False, 0)
        
        self.adjust_layout.opacity = 1
        self.adjust_layout.disabled = False
        self.back_btn.disabled = False
        self.action_btn.text = "START HARD LOCKDOWN"
        self.action_btn.bg_color = (0.86, 0.2, 0.2, 1)
        
        mins = self.total_seconds // 60
        self.timer_label.text = f"{mins:02d}:00"
        self.motivation_label.text = "Session complete! You conquered the distraction."
        
        if ANDROID_ENV:
            try:
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                activity = PythonActivity.mActivity
                activity.stopLockTask()
            except Exception as e:
                print(f"Stop LockTask error: {e}")

    def go_back(self, instance):
        if not self.timer_running:
            self.manager.current = 'dashboard'


class StudyTrackerApp(App):
    def build(self):
        self.focus_active = False
        Window.bind(on_keyboard=self.on_keyboard)
        
        self.sm = ScreenManager()
        self.sm.add_widget(DashboardScreen(name='dashboard'))
        self.sm.add_widget(SyllabusScreen(name='syllabus'))
        self.sm.add_widget(FocusScreen(name='focus'))
        
        # Check persistent lockdown state on startup (handles reboot/power off resumption)
        state = self.load_lockdown_state()
        if state["active"]:
            remaining = int(state["end_time"] - time.time())
            if remaining > 0:
                self.focus_active = True
                self.sm.current = 'focus'
                Clock.schedule_once(lambda dt: self.resume_active_lockdown(remaining), 0.5)
            else:
                self.save_lockdown_state(False, 0)
                
        return self.sm

    def resume_active_lockdown(self, remaining_seconds):
        focus_screen = self.sm.get_screen('focus')
        focus_screen.start_lockdown_session(remaining_seconds)

    def on_keyboard(self, window, key, scancode, codepoint, modifier):
        if getattr(self, 'focus_active', False) and key == 27:
            return True
        return False

    def on_pause(self):
        if getattr(self, 'focus_active', False):
            if ANDROID_ENV:
                try:
                    PythonActivity = autoclass('org.kivy.android.PythonActivity')
                    activity = PythonActivity.mActivity
                    Intent = autoclass('android.content.Intent')
                    intent = Intent(activity, activity.getClass())
                    intent.addFlags(Intent.FLAG_ACTIVITY_REORDER_TO_FRONT | Intent.FLAG_ACTIVITY_SINGLE_TOP)
                    activity.startActivity(intent)
                except Exception as e:
                    print(f"Anti-exit intercept error: {e}")
            return True
        return False

    def load_data(self):
        if os.path.exists('syllabus_data.json'):
            try:
                with open('syllabus_data.json', 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return {"topics": []}

    def save_data(self, data):
        with open('syllabus_data.json', 'w') as f:
            json.dump(data, f)

    def load_lockdown_state(self):
        if os.path.exists('lockdown_state.json'):
            try:
                with open('lockdown_state.json', 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return {"active": False, "end_time": 0}

    def save_lockdown_state(self, active, end_time):
        with open('lockdown_state.json', 'w') as f:
            json.dump({"active": active, "end_time": end_time}, f)

    def toggle_topic(self, index, value):
        data = self.load_data()
        if 0 <= index < len(data["topics"]):
            data["topics"][index]["done"] = value
            self.save_data(data)

    def delete_topic(self, index, callback):
        data = self.load_data()
        if 0 <= index < len(data["topics"]):
            data.pop(index)
            self.save_data(data)
            callback()


if __name__ == '__main__':
    StudyTrackerApp().run()