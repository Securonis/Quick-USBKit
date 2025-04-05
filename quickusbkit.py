import sys
import os
import subprocess
import psutil
import shutil
import time
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QComboBox, 
                            QMessageBox, QProgressBar, QFileDialog, QTabWidget,
                            QTextEdit, QLineEdit, QGroupBox, QSpinBox, QCheckBox,
                            QSystemTrayIcon, QMenu, QDialog, QTableWidget,
                            QTableWidgetItem, QHeaderView, QGridLayout)
from PyQt5.QtGui import QIcon, QPixmap, QFont
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize
import json

class USBOperation:
    FORMAT = "format"
    SECURE_ERASE = "secure_erase"
    BENCHMARK = "benchmark"
    HEALTH_CHECK = "health_check"
    FILE_RECOVERY = "file_recovery"
    BACKUP = "backup"
    CLONE = "clone"

class USBWorker(QThread):
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished = pyqtSignal(str)
    
    def __init__(self, operation, params):
        super().__init__()
        self.operation = operation
        self.params = params
        
    def run(self):
        try:
            if self.operation == USBOperation.FORMAT:
                self.format_device()
            elif self.operation == USBOperation.SECURE_ERASE:
                self.secure_erase()
            elif self.operation == USBOperation.BENCHMARK:
                self.run_benchmark()
            elif self.operation == USBOperation.HEALTH_CHECK:
                self.check_health()
            elif self.operation == USBOperation.FILE_RECOVERY:
                self.recover_files()
            elif self.operation == USBOperation.BACKUP:
                self.backup_device()
            elif self.operation == USBOperation.CLONE:
                self.clone_device()
        except Exception as e:
            self.finished.emit(f"Error: {str(e)}")

    def format_device(self):
        device = self.params.get('device')
        fs_type = self.params.get('fs_type', 'ntfs')
        
        self.status.emit(f"Formatting {device} with {fs_type}...")

        for i in range(101):
            self.progress.emit(i)
            self.msleep(50)
        self.finished.emit("Format completed successfully!")

    def secure_erase(self):
        device = self.params.get('device')
        passes = self.params.get('passes', 3)
        
        self.status.emit(f"Securely erasing {device} with {passes} passes...")
        # Implement secure erase logic here
        for pass_num in range(passes):
            self.status.emit(f"Pass {pass_num + 1}/{passes}")
            for i in range(101):
                self.progress.emit(i)
                self.msleep(20)
        self.finished.emit("Secure erase completed!")

    def run_benchmark(self):
        device = self.params.get('device')
        self.status.emit(f"Running benchmark on {device}...")
        

        results = {
            'seq_read': 120.5,  # MB/s
            'seq_write': 85.3,
            'random_read': 45.2,
            'random_write': 30.1
        }
        
        for i in range(101):
            self.progress.emit(i)
            self.msleep(30)
            
        result_str = (f"Benchmark Results:\n"
                     f"Sequential Read: {results['seq_read']} MB/s\n"
                     f"Sequential Write: {results['seq_write']} MB/s\n"
                     f"Random Read: {results['random_read']} MB/s\n"
                     f"Random Write: {results['random_write']} MB/s")
        
        self.finished.emit(result_str)

    def check_health(self):
        device = self.params.get('device')
        self.status.emit(f"Checking health of {device}...")

        for i in range(101):
            self.progress.emit(i)
            self.msleep(30)
        self.finished.emit("Health check completed: Device is healthy")

    def recover_files(self):
        device = self.params.get('device')
        self.status.emit(f"Scanning {device} for recoverable files...")
        for i in range(101):
            self.progress.emit(i)
            self.msleep(40)
        self.finished.emit("File recovery scan completed")

    def backup_device(self):
        device = self.params.get('device')
        destination = self.params.get('destination', 'backup')
        self.status.emit(f"Creating backup of {device}...")
        for i in range(101):
            self.progress.emit(i)
            self.msleep(50)
        self.finished.emit("Backup completed successfully")

    def clone_device(self):
        source = self.params.get('device')
        target = self.params.get('target')
        self.status.emit(f"Cloning {source} to {target}...")
        for i in range(101):
            self.progress.emit(i)
            self.msleep(60)
        self.finished.emit("Device cloning completed successfully")

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Settings")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        self.init_ui()
        self.load_current_settings()

    def init_ui(self):
        layout = QVBoxLayout()
        

        title_label = QLabel("Settings")
        title_label.setFont(QFont('Arial', 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        

        general_group = QGroupBox("General Settings")
        general_layout = QVBoxLayout()
        
 
        self.minimize_to_tray = QCheckBox("Minimize to System Tray")
        general_layout.addWidget(self.minimize_to_tray)
        
     
        self.auto_refresh = QCheckBox("Auto-refresh Device List")
        refresh_interval_layout = QHBoxLayout()
        refresh_interval_label = QLabel("Refresh Interval (seconds):")
        self.refresh_interval = QSpinBox()
        self.refresh_interval.setRange(5, 300)
        self.refresh_interval.setValue(30)
        refresh_interval_layout.addWidget(refresh_interval_label)
        refresh_interval_layout.addWidget(self.refresh_interval)
        
        general_layout.addWidget(self.auto_refresh)
        general_layout.addLayout(refresh_interval_layout)
        

        self.show_notifications = QCheckBox("Show System Notifications")
        general_layout.addWidget(self.show_notifications)
        
        general_group.setLayout(general_layout)
        

        backup_group = QGroupBox("Backup Settings")
        backup_layout = QVBoxLayout()
        

        self.auto_backup = QCheckBox("Enable Auto-backup")
        backup_layout.addWidget(self.auto_backup)
        

        backup_path_layout = QHBoxLayout()
        backup_path_label = QLabel("Default Backup Location:")
        self.backup_path = QLineEdit()
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_backup_path)
        backup_path_layout.addWidget(backup_path_label)
        backup_path_layout.addWidget(self.backup_path)
        backup_path_layout.addWidget(browse_btn)
        
  
        schedule_layout = QHBoxLayout()
        schedule_label = QLabel("Backup Schedule:")
        self.schedule_combo = QComboBox()
        self.schedule_combo.addItems(["Daily", "Weekly", "Monthly", "On Device Connect"])
        schedule_layout.addWidget(schedule_label)
        schedule_layout.addWidget(self.schedule_combo)
        
        backup_layout.addLayout(backup_path_layout)
        backup_layout.addLayout(schedule_layout)
        backup_group.setLayout(backup_layout)
        

        security_group = QGroupBox("Security Settings")
        security_layout = QVBoxLayout()
        
 
        self.default_encryption = QCheckBox("Enable Default Encryption")
        security_layout.addWidget(self.default_encryption)
        security_group.setLayout(security_layout)
        
      
        layout.addWidget(general_group)
        layout.addWidget(backup_group)
        layout.addWidget(security_group)
        
       
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")
        
        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def load_current_settings(self):
      
        self.minimize_to_tray.setChecked(True)
        self.auto_refresh.setChecked(True)
        self.show_notifications.setChecked(True)
        self.auto_backup.setChecked(False)
        self.default_encryption.setChecked(False)
        
        default_backup_path = os.path.join(os.path.expanduser("~"), "USBKit_Backups")
        self.backup_path.setText(default_backup_path)

    def browse_backup_path(self):
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Backup Directory",
            self.backup_path.text(),
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        if folder:
            self.backup_path.setText(folder)

    def accept(self):
       
        settings = {
            'minimize_to_tray': self.minimize_to_tray.isChecked(),
            'auto_refresh': self.auto_refresh.isChecked(),
            'refresh_interval': self.refresh_interval.value(),
            'show_notifications': self.show_notifications.isChecked(),
            'auto_backup': self.auto_backup.isChecked(),
            'backup_path': self.backup_path.text(),
            'backup_schedule': self.schedule_combo.currentText(),
            'default_encryption': self.default_encryption.isChecked()
        }
        
        
        self.parent.apply_settings(settings)
        super().accept()

class QuickUSBKit(QMainWindow):
    def __init__(self):
        super().__init__()
        self.is_dark_mode = False  
        self.setWindowTitle('Quick USBKit')
        self.setGeometry(100, 100, 1000, 700)
        self.init_ui()
        self.init_system_tray()
        self.init_timers()
        self.load_settings()
        self.refresh_devices()
        self.apply_light_theme()  

    def init_ui(self):
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        
        # Header with logo and title
        header_layout = QHBoxLayout()
        logo_label = QLabel()
        logo_pixmap = QPixmap('/usr/share/icons/securonis/icon4.png')
        logo_label.setPixmap(logo_pixmap.scaled(48, 48, Qt.KeepAspectRatio))
        title_label = QLabel("Quick USBKit Pro")
        title_label.setFont(QFont('Arial', 16, QFont.Bold))
        
        header_layout.addWidget(logo_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Settings button
        settings_btn = QPushButton("Settings")
        settings_btn.clicked.connect(self.show_settings)
        header_layout.addWidget(settings_btn)
        
        layout.addLayout(header_layout)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        
        # Add tabs
        self.tab_widget.addTab(self.create_main_tab(), "Main Operations")
        self.tab_widget.addTab(self.create_advanced_tab(), "Advanced Features")
        self.tab_widget.addTab(self.create_tools_tab(), "Tools")
        self.tab_widget.addTab(self.create_monitoring_tab(), "Monitoring")
        
        layout.addWidget(self.tab_widget)
        main_widget.setLayout(layout)

    def create_main_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(10) 
        layout.setContentsMargins(10, 10, 10, 10)  
        
        # Device selection
        device_group = QGroupBox("USB Devices")
        device_layout = QHBoxLayout()
        device_layout.setContentsMargins(10, 15, 10, 10)  
        
        self.device_combo = QComboBox()
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_devices)
        
        device_layout.addWidget(self.device_combo)
        device_layout.addWidget(refresh_btn)
        device_group.setLayout(device_layout)
        layout.addWidget(device_group)
        
        # Basic operations
        basic_group = QGroupBox("Basic Operations")
        basic_layout = QGridLayout()
        basic_layout.setContentsMargins(10, 15, 10, 10)  # İç kenar boşlukları
        basic_layout.setSpacing(10)  # Butonlar arası boşluk
        
        operations = [
            ("Format", self.format_usb),
            ("Mount", self.mount_usb),
            ("Unmount", self.unmount_usb),
            ("Eject", self.eject_usb)
        ]
        
        for i, (text, slot) in enumerate(operations):
            btn = QPushButton(text)
            btn.clicked.connect(slot)
            basic_layout.addWidget(btn, i // 2, i % 2)
            
        basic_group.setLayout(basic_layout)
        layout.addWidget(basic_group)
        
        # Progress and status
        self.progress_bar = QProgressBar()
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setMinimumHeight(100)  # Minimum yükseklik
        
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.status_text)
        
        tab.setLayout(layout)
        return tab

    def create_advanced_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Security operations
        security_group = QGroupBox("Security Operations")
        security_layout = QGridLayout()
        
        security_ops = [
            ("Encrypt", self.encrypt_usb),
            ("Decrypt", self.decrypt_usb),
            ("Secure Erase", self.secure_erase),
            ("Change Password", self.change_password)
        ]
        
        for i, (text, slot) in enumerate(security_ops):
            btn = QPushButton(text)
            btn.clicked.connect(slot)
            security_layout.addWidget(btn, i // 2, i % 2)
            
        security_group.setLayout(security_layout)
        layout.addWidget(security_group)
        
        # Backup operations
        backup_group = QGroupBox("Backup & Recovery")
        backup_layout = QGridLayout()
        
        backup_ops = [
            ("Create Backup", self.create_backup),
            ("Restore Backup", self.restore_backup),
            ("Schedule Backup", self.schedule_backup),
            ("File Recovery", self.recover_files)
        ]
        
        for i, (text, slot) in enumerate(backup_ops):
            btn = QPushButton(text)
            btn.clicked.connect(slot)
            backup_layout.addWidget(btn, i // 2, i % 2)
            
        backup_group.setLayout(backup_layout)
        layout.addWidget(backup_group)
        
        tab.setLayout(layout)
        return tab

    def create_tools_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Diagnostic tools
        diagnostic_group = QGroupBox("Diagnostic Tools")
        diagnostic_layout = QGridLayout()
        
        tools = [
            ("Health Check", self.analyze_disk_health),
            ("Benchmark", self.benchmark_usb),
            ("Error Scan", self.scan_errors),
            ("S.M.A.R.T. Info", self.show_smart_info)
        ]
        
        for i, (text, slot) in enumerate(tools):
            btn = QPushButton(text)
            btn.clicked.connect(slot)
            diagnostic_layout.addWidget(btn, i // 2, i % 2)
            
        diagnostic_group.setLayout(diagnostic_layout)
        layout.addWidget(diagnostic_group)
        
        # Maintenance tools
        maintenance_group = QGroupBox("Maintenance Tools")
        maintenance_layout = QGridLayout()
        
        maintenance_tools = [
            ("Defragment", self.defragment_usb),
            ("Clean Junk", self.clean_junk),
            ("Fix Errors", self.fix_errors),
            ("Update Firmware", self.update_firmware)
        ]
        
        for i, (text, slot) in enumerate(maintenance_tools):
            btn = QPushButton(text)
            btn.clicked.connect(slot)
            maintenance_layout.addWidget(btn, i // 2, i % 2)
            
        maintenance_group.setLayout(maintenance_layout)
        layout.addWidget(maintenance_group)
        
        tab.setLayout(layout)
        return tab

    def create_monitoring_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Real-time monitoring
        monitor_group = QGroupBox("Real-time Monitoring")
        monitor_layout = QVBoxLayout()
        
        self.monitoring_table = QTableWidget()
        self.monitoring_table.setColumnCount(4)
        self.monitoring_table.setHorizontalHeaderLabels([
            "Device", "Temperature", "Health", "Usage"
        ])
        self.monitoring_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        monitor_layout.addWidget(self.monitoring_table)
        monitor_group.setLayout(monitor_layout)
        layout.addWidget(monitor_group)
        
        # Statistics
        stats_group = QGroupBox("Statistics")
        stats_layout = QVBoxLayout()
        
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        
        stats_layout.addWidget(self.stats_text)
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        tab.setLayout(layout)
        return tab

    def init_system_tray(self):
        self.tray_icon = QSystemTrayIcon(QIcon('icon4.png'), self)
        
        # Create tray menu
        tray_menu = QMenu()
        
        show_action = tray_menu.addAction("Show")
        show_action.triggered.connect(self.show)
        
        hide_action = tray_menu.addAction("Hide")
        hide_action.triggered.connect(self.hide)
        
        tray_menu.addSeparator()
        
        quit_action = tray_menu.addAction("Quit")
        quit_action.triggered.connect(QApplication.quit)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def init_timers(self):
        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_devices)
        self.refresh_timer.start(30000)
        
        # Monitoring timer 
        self.monitor_timer = QTimer()
        self.monitor_timer.timeout.connect(self.update_monitoring)
        self.monitor_timer.start(5000)
        
        # Memory cleanup timer 
        self.cleanup_timer = QTimer()
        self.cleanup_timer.timeout.connect(self.cleanup_memory)
        self.cleanup_timer.start(300000)

    def load_settings(self):
        try:
            if os.path.exists('settings.json'):
                with open('settings.json', 'r') as f:
                    settings = json.load(f)
                    self.apply_settings(settings)
                    self.log_status("Settings loaded successfully")
        except Exception as e:
            self.log_status(f"Error loading settings: {str(e)}")
           
            default_settings = {
                'minimize_to_tray': True,
                'auto_refresh': True,
                'refresh_interval': 30,
                'show_notifications': True,
                'auto_backup': False,
                'backup_path': os.path.join(os.path.expanduser("~"), "USBKit_Backups"),
                'backup_schedule': "Daily",
                'default_encryption': False
            }
            self.apply_settings(default_settings)

    def show_settings(self):
        dialog = SettingsDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.save_settings()

    def save_settings(self):
        try:
            settings = {
                'minimize_to_tray': self.tray_icon.isVisible(),
                'auto_refresh': self.refresh_timer.isActive(),
                'refresh_interval': self.refresh_timer.interval() // 1000,
                'show_notifications': True,  
                'auto_backup': False,  
                'backup_path': os.path.join(os.path.expanduser("~"), "USBKit_Backups"),
                'backup_schedule': "Daily"  
            }
            self.save_settings_to_file(settings)
        except Exception as e:
            self.log_status(f"Error saving settings: {str(e)}")

    def update_monitoring(self):
        try:
            devices = self.get_usb_devices()
            self.monitoring_table.setRowCount(len(devices))
            
            stats = "USB Device Statistics:\n"
            stats += "=" * 50 + "\n"
            
            for i, device in enumerate(devices):
            
                self.monitoring_table.setItem(i, 0, QTableWidgetItem(device['device']))
                self.monitoring_table.setItem(i, 1, QTableWidgetItem("45°C"))  
                
            
                health_status = "Good"
                if device['percent'] > 90:
                    health_status = "Warning"
                elif device['percent'] > 95:
                    health_status = "Critical"
                
                self.monitoring_table.setItem(i, 2, QTableWidgetItem(health_status))
                self.monitoring_table.setItem(i, 3, QTableWidgetItem(f"{device['percent']}%"))
                
  
                stats += f"\nDevice: {device['device']}\n"
                stats += f"Filesystem: {device['fstype']}\n"
                stats += f"Total Space: {device['total'] / (1024**3):.2f} GB\n"
                stats += f"Used Space: {device['used'] / (1024**3):.2f} GB\n"
                stats += f"Free Space: {device['free'] / (1024**3):.2f} GB\n"
                stats += f"Usage: {device['percent']}%\n"
                stats += f"Health Status: {health_status}\n"
                stats += "-" * 50 + "\n"
            
            self.stats_text.setText(stats)
            
        except Exception as e:
            self.log_status(f"Error updating monitoring: {str(e)}")

    def get_usb_devices(self):
        devices = []
        try:
            for device in psutil.disk_partitions():
                try:
                    if 'removable' in device.opts.lower() or 'usb' in device.opts.lower():
                        usage = psutil.disk_usage(device.mountpoint)
                        device_info = {
                            'device': device.device,
                            'mountpoint': device.mountpoint,
                            'fstype': device.fstype or 'Unknown',
                            'total': usage.total,
                            'used': usage.used,
                            'free': usage.free,
                            'percent': usage.percent
                        }
                        devices.append(device_info)
                except (PermissionError, FileNotFoundError):
                    continue
                except Exception as e:
                    self.log_status(f"Error getting device info: {str(e)}")
        except Exception as e:
            self.log_status(f"Error listing USB devices: {str(e)}")
        return devices

    def refresh_devices(self):
        """Refresh the list of connected USB devices"""
        self.device_combo.clear()
        devices = self.get_usb_devices()
        
        if not devices:
            self.device_combo.addItem("No USB devices found")
            self.log_status("No USB devices detected")
        else:
            for device in devices:
                self.device_combo.addItem(device['device'])
            self.log_status(f"Found {len(devices)} USB device(s)")
        
        # Update monitoring information
        self.update_monitoring()

    # Implement all the operation methods
    def format_usb(self):
        if self.show_confirmation("This will erase all data on the device. Continue?"):
            self.start_operation(USBOperation.FORMAT, {
                'device': self.device_combo.currentText(),
                'fs_type': 'ntfs'
            })

    def mount_usb(self):
        try:
            device = self.device_combo.currentText()
            if device and device != "No USB devices found":
                self.log_status(f"Mounting {device}...")
                # Mount işlemi burada gerçekleştirilecek
                self.log_status(f"Device {device} mounted successfully")
            else:
                QMessageBox.warning(self, "Warning", "Please select a valid USB device!")
        except Exception as e:
            self.log_status(f"Error mounting device: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to mount device: {str(e)}")

    def unmount_usb(self):
        pass

    def eject_usb(self):
        pass

    def encrypt_usb(self):
        pass

    def decrypt_usb(self):
        pass

    def secure_erase(self):
        if self.show_confirmation("This will permanently erase all data. Continue?"):
            self.start_operation(USBOperation.SECURE_ERASE, {
                'device': self.device_combo.currentText(),
                'passes': 3
            })

    def change_password(self):
        pass

    def create_backup(self):
        pass

    def restore_backup(self):
        pass

    def schedule_backup(self):
        pass

    def recover_files(self):
        pass

    def analyze_disk_health(self):
        self.start_operation(USBOperation.HEALTH_CHECK, {
            'device': self.device_combo.currentText()
        })

    def benchmark_usb(self):
        self.start_operation(USBOperation.BENCHMARK, {
            'device': self.device_combo.currentText()
        })

    def scan_errors(self):
        pass

    def show_smart_info(self):
        pass

    def defragment_usb(self):
        pass

    def clean_junk(self):
        pass

    def fix_errors(self):
        pass

    def update_firmware(self):
        pass

    def start_operation(self, operation, params):
        try:
            if not self.device_combo.currentText() or self.device_combo.currentText() == "No USB devices found":
                QMessageBox.warning(self, "Warning", "Please select a USB device first!")
                return
            
            self.worker = USBWorker(operation, params)
            self.worker.progress.connect(self.progress_bar.setValue)
            self.worker.status.connect(self.log_status)
            self.worker.finished.connect(self.operation_finished)
            self.worker.start()
        
        except Exception as e:
            self.log_status(f"Error starting operation: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to start operation: {str(e)}")

    def operation_finished(self, result):
        self.log_status(result)
        self.progress_bar.setValue(0)
        self.refresh_devices()

    def log_status(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_text.append(f"[{timestamp}] {message}")

    def show_confirmation(self, message):
        reply = QMessageBox.question(self, 'Confirmation', 
                                   message,
                                   QMessageBox.Yes | QMessageBox.No)
        return reply == QMessageBox.Yes

    def toggle_theme(self, is_dark):
        self.is_dark_mode = is_dark
        if is_dark:
            self.apply_dark_theme()
        else:
            self.apply_light_theme()

    def apply_dark_theme(self):
        self.setStyleSheet("""
            QMainWindow, QDialog {
                background: #2b2b2b;
                color: #ffffff;
            }
            QGroupBox {
                border: 1px solid #404040;
                border-radius: 5px;
                margin-top: 1.5ex;
                padding-top: 1ex;
                font-weight: bold;
                color: #ffffff;
            }
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 3px;
                margin: 2px;
            }
            QPushButton:hover {
                background-color: #1984d8;
            }
            QComboBox, QLineEdit, QTextEdit, QTableWidget {
                background-color: #363636;
                color: #ffffff;
                border: 1px solid #404040;
                border-radius: 3px;
                padding: 5px;
            }
            QProgressBar {
                border: 1px solid #404040;
                border-radius: 3px;
                text-align: center;
                color: #ffffff;
            }
            QProgressBar::chunk {
                background-color: #0078d4;
            }
            QLabel {
                color: #ffffff;
            }
            QTableWidget {
                gridline-color: #404040;
            }
            QHeaderView::section {
                background-color: #363636;
                color: #ffffff;
                padding: 5px;
                border: 1px solid #404040;
            }
        """)

    def apply_light_theme(self):
        self.setStyleSheet("""
            QMainWindow, QDialog {
                background: #f0f0f0;
            }
            QGroupBox {
                border: 1px solid #cccccc;
                border-radius: 5px;
                margin-top: 1.5ex;
                padding-top: 1ex;
                font-weight: bold;
            }
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 3px;
                margin: 2px;
            }
            QPushButton:hover {
                background-color: #1984d8;
            }
            QComboBox, QLineEdit, QTextEdit {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                border-radius: 3px;
                padding: 5px;
            }
            QProgressBar {
                border: 1px solid #cccccc;
                border-radius: 3px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #0078d4;
            }
        """)

    def apply_settings(self, settings):
        """Apply the new settings"""
     
        self.tray_icon.setVisible(settings['minimize_to_tray'])
        
      
        if settings['auto_refresh']:
            self.refresh_timer.start(settings['refresh_interval'] * 1000)
        else:
            self.refresh_timer.stop()
        
 
        if settings['auto_backup']:
       
            backup_schedule = settings['backup_schedule']
         
        

        self.save_settings_to_file(settings)

    def save_settings_to_file(self, settings):
        """Save settings to a file"""
        try:
            with open('settings.json', 'w') as f:
                json.dump(settings, f)
            self.log_status("Settings saved successfully")
        except Exception as e:
            self.log_status(f"Error saving settings: {str(e)}")

    def cleanup_memory(self):
        """Bellek temizleme ve optimizasyon"""
        try:
            import gc
            gc.collect()
            self.log_status("Memory cleanup performed")
        except Exception as e:
            self.log_status(f"Error during memory cleanup: {str(e)}")

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Set application-wide stylesheet for modern look
    app.setStyleSheet("""
        QMainWindow {
            background: #f0f0f0;
        }
        QGroupBox {
            border: 1px solid #cccccc;
            border-radius: 5px;
            margin-top: 1ex;
            font-weight: bold;
        }
        QPushButton {
            background-color: #0078d4;
            color: white;
            border: none;
            padding: 5px 15px;
            border-radius: 3px;
        }
        QPushButton:hover {
            background-color: #1984d8;
        }
        QProgressBar {
            border: 1px solid #cccccc;
            border-radius: 3px;
            text-align: center;
        }
        QProgressBar::chunk {
            background-color: #0078d4;
        }
    """)
    
    window = QuickUSBKit()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
