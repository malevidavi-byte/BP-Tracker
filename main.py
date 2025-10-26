import sys
import json
import requests
import os
import shutil
import subprocess
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, QPushButton,
    QScrollArea, QFrame, QScrollBar, QInputDialog, QLineEdit  # <-- добавляем QLineEdit
)
from PySide6.QtCore import Qt, QEasingCurve, Property
from PySide6.QtGui import QFont, QMouseEvent
from PySide6.QtCore import QPropertyAnimation

# ---------------------- АВТООБНОВЛЕНИЕ ----------------------
APP_VERSION = "v3"
UPDATE_JSON_URL = "https://raw.githubusercontent.com/malevidavi-byte/BP-Tracker/main/version.json"
LOCAL_EXE = "BPT.exe"  # Имя твоего exe

def check_for_updates():
    try:
        resp = requests.get(UPDATE_JSON_URL, timeout=5)
        if resp.status_code != 200:
            return
        data = resp.json()
        latest_version = data.get("version", "")
        download_url = data.get("download_url", "")
        if latest_version and latest_version != APP_VERSION and download_url:
            print(f"[Update] Доступна новая версия: {latest_version}")
            tmp_file = LOCAL_EXE + ".tmp"

            # Скачиваем новую версию
            r = requests.get(download_url, stream=True)
            if not r.content:
                print("[Update] Ошибка: пустой файл!")
                return

            with open(tmp_file, "wb") as f:
                f.write(r.content)

            # Заменяем старый exe
            os.replace(tmp_file, LOCAL_EXE)

            print("[Update] Обновление завершено. Перезапуск...")
            subprocess.Popen([os.path.abspath(LOCAL_EXE)])
            sys.exit()

    except Exception as e:
        print(f"[Update] Ошибка автообновления: {e}")


# ---------------------- ДАННЫЕ ----------------------
DATA_FILE = 'bp_data.json'

DEFAULT_TASKS = [
    ("Посетить любой сайт в браузере", 1, 2),
    ("Зайти в любой канал в Brawl", 1, 2),
    ("Поставить лайк любой анкете в Match", 1, 2),
    ("Прокрутить за DP серебрянный или золотой кейс", 10, 20),
    ("Кинуть мяч питомцу 15 раз", 2, 4),
    ("15 выполненных питомцем команд", 2, 4),
    ("Ставка в колесе удачи в казино (межсерверное колесо)", 3, 6),
    ("Проехать 1 станцию на метро", 2, 4),
    ("Поймать 20 рыб", 4, 8),
    ("Выполнить 2 квеста любых клубов", 4, 8),
    ("Починить деталь в автосервисе", 1, 2),
    ("Забросить 2 мяча в баскетболе", 1, 2),
    ("Забить 2 гола в футболе", 1, 2),
    ("Победить в армрестлинге", 1, 2),
    ("Победить в дартс", 1, 2),
    ("Забить 10 голов в волейболе", 1, 2),
    ("Поиграть 1 минуту в настольный теннис", 1, 2),
    ("Поиграть 1 минуту в большой теннис", 1, 2),
    ("Сыграть в мафию в казино", 3, 6),
    ("Сделать платеж по лизингу", 1, 2),
    ("Посадить траву в теплице", 4, 8),
    ("Запустить переработку обезболивающих в лаборатории", 4, 8),
    ("Принять участие в двух аирдропах", 2, 4),
    ("3 часа в онлайне (можно выполнять многократно за день)", 2, 4),
    ("Нули в казино", 2, 4),
    ("25 действий на стройке", 2, 4),
    ("25 действий в порту", 2, 4),
    ("25 действий в шахте", 2, 4),
    ("3 победы в Дэнс Баттлах", 2, 4),
    ("Заказ материалов для бизнеса вручную", 1, 2),
    ("20 подходов в тренажерном зале", 1, 2),
    ("Успешная тренировка в тире", 1, 2),
    ("10 посылок на почте", 1, 2),
    ("Арендовать киностудию", 2, 4),
    ("Купить лотерейный билет", 1, 2),
    ("Выиграть гонку в картинге", 1, 2),
    ("10 действий на ферме", 1, 2),
    ("Потушить 25 'огоньков' пожарным", 1, 2),
    ("Выкопать 1 сокровище (не мусор)", 1, 2),
    ("Проехать 1 уличную гонку", 1, 2),
    ("Выполнить 3 заказа дальнобойщиком", 2, 4),
    ("Два раза оплатить смену внешности у хирурга в EMS", 2, 4),
    ("Добавить 5 видео в кинотеатре", 1, 2),
    ("Выиграть 5 игр в тренировочном комплексе со ставкой (от 100$)", 1, 2),
    ("Выиграть 3 любых игры на арене со ставкой (от 100$)", 1, 2),
    ("2 круга на любом маршруте автобусника", 2, 4),
    ("5 раз снять 100% шкуру с животных", 2, 4),
]


# ---------------------- Анимация и стили ----------------------
class AnimatedLabel(QLabel):
    def __init__(self, text=""):
        super().__init__(text)
        self._color = 255
        self.setStyleSheet(f"color: rgb(255,255,255);")

    def get_color(self):
        return self._color

    def set_color(self, value):
        self._color = value
        r, g, b = 106, 156, 255
        self.setStyleSheet(f"color: rgb({int(r * (1 - value / 255) + 255 * value / 255)}, "
                           f"{int(g * (1 - value / 255) + 255 * value / 255)}, "
                           f"{int(b * (1 - value / 255) + 255 * value / 255)});")

    color = Property(int, get_color, set_color)

def animate_bp_change(label: AnimatedLabel):
    animation = QPropertyAnimation(label, b"color")
    animation.setStartValue(0)
    animation.setEndValue(255)
    animation.setDuration(400)
    animation.setEasingCurve(QEasingCurve.OutCubic)
    animation.start()

class PremiumScrollBar(QScrollBar):
    def __init__(self, parent=None):
        super().__init__(Qt.Vertical, parent)
        self.setStyleSheet("""
            QScrollBar:vertical {
                background: #2b2d30;
                width: 12px;
                margin: 0px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #6a9cff;
                min-height: 20px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background: #95baff;
            }
            QScrollBar::add-line, QScrollBar::sub-line { height: 0px; }
            QScrollBar::add-page, QScrollBar::sub-page { background: none; }
        """)

# ---------------------- Класс приложения ----------------------
class PremiumBPTracker(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BP Tracker — by Teodor")
        self.resize(900, 700)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, False)

        self.vip_enabled = False
        self.total_bp = 0
        self.task_checkboxes = []
        self.tasks_data = []
        self.old_pos = self.pos()

        self.init_ui()
        self.load_state()
        self.update_total_bp()

    def filter_tasks(self):
        query = self.search_input.text().lower()
        for (cb, _, _), task in zip(self.task_checkboxes, self.tasks_data):
            if query in task['name'].lower():
                cb.show()
            else:
                cb.hide()

    # ---------------------- Задачи ----------------------
    def add_task_checkbox(self, name, base, vip):
        cb = QCheckBox(f"{name} ({base}/{vip} BP)")
        cb.setStyleSheet('''
            QCheckBox {
                color: #e0e0e0; font-size: 14px; padding: 4px;
            }
            QCheckBox::indicator {
                width: 20px; height: 20px; border-radius: 6px;
                border: 2px solid #888; background: transparent;
            }
            QCheckBox::indicator:checked {
                background-color: #6a9cff; border: 2px solid #6a9cff;
            }
            QCheckBox:hover { color: #ffffff; }
        ''')
        cb.stateChanged.connect(self.update_total_bp)
        self.scroll_layout.addWidget(cb)
        self.tasks_data.append({"name": name, "base": base, "vip": vip})
        self.task_checkboxes.append((cb, base, vip))

    # ---------------------- Диалоги добавления/удаления ----------------------
    def add_task_dialog(self):
        dialog = QInputDialog(self)
        dialog.setWindowTitle("Новое задание")
        dialog.setLabelText("Введите текст задания:")
        if dialog.exec() != QInputDialog.Accepted: return
        text = dialog.textValue().strip()
        if not text: return
        bp_dialog = QInputDialog(self)
        bp_dialog.setWindowTitle("BP")
        bp_dialog.setLabelText("Введите BP (base/vip):")
        if bp_dialog.exec() != QInputDialog.Accepted: return
        bp_text = bp_dialog.textValue()
        if "/" not in bp_text: return
        try: base, vip = map(int, bp_text.split("/"))
        except ValueError: return
        self.add_task_checkbox(text, base, vip)
        self.update_total_bp()
        self.save_state()

    def delete_task_dialog(self):
        task_names = [task['name'] for task in self.tasks_data]
        if not task_names: return
        dialog = QInputDialog(self)
        dialog.setWindowTitle("Удалить задание")
        dialog.setLabelText("Выберите задание для удаления:")
        dialog.setComboBoxItems(task_names)
        if dialog.exec() != QInputDialog.Accepted: return
        task_name = dialog.textValue()
        if task_name not in task_names: return
        index = task_names.index(task_name)
        cb, _, _ = self.task_checkboxes.pop(index)
        self.scroll_layout.removeWidget(cb)
        cb.deleteLater()
        self.tasks_data.pop(index)
        self.update_total_bp()

    # ---------------------- Состояние ----------------------
    def save_state(self):
        state = {
            'vip': self.vip_enabled,
            'tasks': [
                {"name": task['name'], "base": task['base'], "vip": task['vip'], "checked": cb.isChecked()}
                for (cb, _, _), task in zip(self.task_checkboxes, self.tasks_data)
            ]
        }
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

    def load_state(self):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                state = json.load(f)
            self.vip_enabled = state.get('vip', False)
            self.vip_checkbox.setChecked(self.vip_enabled)
            saved_tasks = state.get('tasks', [])
            if saved_tasks:
                for task in saved_tasks:
                    self.add_task_checkbox(task['name'], task['base'], task['vip'])
                    if task.get('checked'):
                        self.task_checkboxes[-1][0].setChecked(True)
            else:
                for name, base, vip in DEFAULT_TASKS:
                    self.add_task_checkbox(name, base, vip)
        except FileNotFoundError:
            for name, base, vip in DEFAULT_TASKS:
                self.add_task_checkbox(name, base, vip)

    # ---------------------- UI ----------------------
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setSpacing(0)

        # Верхняя панель
        self.title_bar = QFrame()
        self.title_bar.setFixedHeight(40)
        self.title_bar.setStyleSheet("background-color: #2b2d30;")
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(10,0,10,0)
        self.title_label = QLabel("BP Tracker — by Teodor")
        self.title_label.setStyleSheet("color: white; font-weight: bold;")
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()
        self.min_button = QPushButton("—")
        self.min_button.setFixedSize(30,30)
        self.min_button.setStyleSheet("color:white; background-color: transparent; border: none; font-size:18px;")
        self.min_button.clicked.connect(self.showMinimized)
        self.close_button = QPushButton("✕")
        self.close_button.setFixedSize(30,30)
        self.close_button.setStyleSheet("color:white; background-color: transparent; border: none; font-size:18px;")
        self.close_button.clicked.connect(self.close)
        title_layout.addWidget(self.min_button)
        title_layout.addWidget(self.close_button)
        main_layout.addWidget(self.title_bar)

        # Контент
        content = QFrame()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(20,20,20,20)
        content_layout.setSpacing(10)

        # Верхняя панель BP + VIP справа
        top_panel = QHBoxLayout()
        self.total_label = AnimatedLabel("BP: 0")
        self.total_label.setFont(QFont("Inter",20,QFont.Bold))
        self.total_label.setStyleSheet("background-color: #3b3d42; border-radius:10px; padding:8px 16px;")
        top_panel.addWidget(self.total_label)
        top_panel.addStretch()
        self.vip_checkbox = QCheckBox("Gold/Platinum VIP")
        self.vip_checkbox.setStyleSheet('''
            QCheckBox {
                color: #e0e0e0; font-size: 14px; padding: 4px;
            }
            QCheckBox::indicator {
                width: 20px; height: 20px; border-radius: 6px;
                border: 2px solid #888; background: transparent;
            }
            QCheckBox::indicator:checked {
                background-color: #6a9cff; border: 2px solid #6a9cff;
            }
            QCheckBox:hover { color: #ffffff; }
        ''')
        self.vip_checkbox.stateChanged.connect(self.toggle_vip)
        top_panel.addWidget(self.vip_checkbox)
        content_layout.addLayout(top_panel)
        # Поисковая строка
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по заданиям...")
        self.search_input.setStyleSheet('''
            QLineEdit {
                padding: 6px 12px;
                border-radius: 8px;
                border: 1px solid #555;
                background-color: #2b2d30;
                color: #fff;
                font-size: 14px;
            }
            QLineEdit:focus { border: 1px solid #6a9cff; }
        ''')
        self.search_input.textChanged.connect(self.filter_tasks)
        content_layout.addWidget(self.search_input)

        # Список заданий
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setVerticalScrollBar(PremiumScrollBar(self.scroll))
        container = QWidget()
        self.scroll_layout = QVBoxLayout(container)
        self.scroll_layout.setSpacing(5)
        self.scroll.setWidget(container)
        content_layout.addWidget(self.scroll)

        # Нижняя панель кнопок
        bottom_panel = QHBoxLayout()
        self.clear_button = QPushButton("Сбросить отмеченные")
        self.clear_button.setStyleSheet('''
            QPushButton {
                background-color: #3b3d42; color: white; font-weight: bold; padding: 8px 20px; border-radius:6px;
            }
            QPushButton:hover { background-color: #4a4c51; }
        ''')
        self.clear_button.clicked.connect(self.clear_checked)
        self.add_button = QPushButton("Добавить задание")
        self.add_button.setStyleSheet(self.clear_button.styleSheet())
        self.add_button.clicked.connect(self.add_task_dialog)
        self.delete_button = QPushButton("Удалить задание")
        self.delete_button.setStyleSheet(self.clear_button.styleSheet())
        self.delete_button.clicked.connect(self.delete_task_dialog)
        bottom_panel.addWidget(self.add_button)
        bottom_panel.addWidget(self.delete_button)
        bottom_panel.addStretch()
        bottom_panel.addWidget(self.clear_button)
        content_layout.addLayout(bottom_panel)

        main_layout.addWidget(content)
        self.setStyleSheet("background-color: #1c1d20;")

    # ---------------------- Логика ----------------------
    def toggle_vip(self):
        self.vip_enabled = self.vip_checkbox.isChecked()
        self.update_total_bp()

    def update_total_bp(self):
        total = 0
        for cb, base, vip in self.task_checkboxes:
            if cb.isChecked():
                total += vip if self.vip_enabled else base
        self.total_bp = total
        self.total_label.setText(f"BP: {self.total_bp}")
        animate_bp_change(self.total_label)
        self.save_state()

    def clear_checked(self):
        for cb, _, _ in self.task_checkboxes:
            if cb.isChecked():
                cb.setChecked(False)

    # Перетаскивание окна
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton and event.position().y() < 40:
            self.old_pos = event.globalPosition()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.LeftButton and event.position().y() < 40:
            delta = event.globalPosition() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition()
            event.accept()

# ---------------------- ЗАПУСК ----------------------
if __name__ == "__main__":
    check_for_updates()  # Проверяем автообновление перед запуском
    app = QApplication(sys.argv)
    window = PremiumBPTracker()
    window.show()
    sys.exit(app.exec())
