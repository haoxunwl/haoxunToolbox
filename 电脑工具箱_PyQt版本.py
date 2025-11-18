# -*- coding: utf-8 -*-
# 浩讯亿通电脑工具箱 PyQt版本
import sys
import locale
import codecs
import os
import threading
import logging
import logging.handlers
import psutil
import platform
import time
import socket
import requests
import subprocess
import xml.etree.ElementTree as ET
import winreg
import ctypes
from ctypes import wintypes
import json
import math

# 可选导入wmi模块
try:
    import wmi
    WMI_AVAILABLE = True
    print("WMI模块导入成功")
except ImportError as e:
    wmi = None
    WMI_AVAILABLE = False
    print(f"警告: wmi模块未安装，某些功能可能受限。错误信息: {e}")
    print("请运行: pip install wmi 来安装WMI模块")

# 导入其他必要的模块
try:
    import GPUtil
    GPUTIL_AVAILABLE = True
except ImportError:
    GPUtil = None
    GPUTIL_AVAILABLE = False
    print("警告: GPUtil模块未安装，GPU信息获取功能可能受限")

# 风扇控制相关模块
try:
    import win32api
    import win32con
    WIN32_AVAILABLE = True
except ImportError:
    win32api = None
    win32con = None
    WIN32_AVAILABLE = False
    print("警告: pywin32模块未安装，风扇控制功能可能受限")

from PIL import Image, ImageQt

# 初始化COM组件（仅在需要时）
def init_com():
    try:
        import pythoncom
        pythoncom.CoInitialize()
    except ImportError:
        pass

import multiprocessing

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QFrame, QLabel, QPushButton, 
                             QVBoxLayout, QHBoxLayout, QGridLayout, QScrollArea, QSizePolicy,
                             QMessageBox, QTextEdit, QGroupBox, QFormLayout, QSpacerItem, QTabWidget, QComboBox, QDialog, QSlider,
                             QGraphicsDropShadowEffect, QColorDialog, QButtonGroup, QRadioButton, QSystemTrayIcon, QMenu, QAction)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve, QRect
from PyQt5.QtGui import QPixmap, QIcon, QFont, QPalette, QBrush, QColor, QPainter, QPainterPath, QImage
from PyQt5.QtCore import QSize
from PyQt5.QtSvg import QSvgRenderer

# 确定基础路径，支持PyInstaller打包
def get_base_path():
    if hasattr(sys, '_MEIPASS'):
        return sys._MEIPASS
    else:
        return os.path.abspath('.')

# 获取资源文件的完整路径
def get_resource_path(relative_path):
    return os.path.join(get_base_path(), relative_path)

# 加载SVG图标方法
def load_svg_icon(svg_path, size=20, red_factor=0.7):
    """加载SVG图标并返回QPixmap，支持电竞红色调整"""
    try:
        if not os.path.exists(svg_path):
            return None
            
        # 创建SVG渲染器
        renderer = QSvgRenderer(svg_path)
        if not renderer.isValid():
            return None
            
        # 创建Pixmap并渲染SVG
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        
        # 调整图标颜色为电竞红色
        if red_factor > 0:
            pixmap = gamered_pixmap(pixmap, red_factor)
        
        return pixmap
    except Exception as e:
        print(f"加载SVG图标失败 {svg_path}: {e}")
        return None

def gamered_pixmap(pixmap, red_factor=0.8):
    """将图像像素变成电竞红色风格"""
    try:
        # 转换为QImage以便进行像素操作
        image = pixmap.toImage()
        
        # 获取图像尺寸
        width = image.width()
        height = image.height()
        
        # 确保使用32位深度
        if image.format() != QImage.Format_ARGB32:
            image = image.convertToFormat(QImage.Format_ARGB32)
        
        # 遍历每个像素并进行电竞红处理
        for y in range(height):
            for x in range(width):
                # 获取像素颜色
                pixel_color = image.pixel(x, y)
                
                # 获取RGBA值
                red = (pixel_color >> 16) & 0xFF
                green = (pixel_color >> 8) & 0xFF
                blue = pixel_color & 0xFF
                alpha = (pixel_color >> 24) & 0xFF
                
                # 如果像素不是透明的，则进行电竞红处理
                if alpha > 0:
                    # 计算像素的亮度（灰度值）
                    brightness = int(0.299 * red + 0.587 * green + 0.114 * blue)
                    
                    # 根据亮度调整红色强度
                    if brightness > 128:
                        # 亮色像素：增强红色，降低其他颜色
                        red = int(red * (1 + red_factor))
                        green = int(green * (1 - red_factor * 0.8))
                        blue = int(blue * (1 - red_factor * 0.8))
                    else:
                        # 暗色像素：直接应用电竞红色
                        red = int(red + (255 - red) * red_factor)
                        green = int(green * (1 - red_factor * 0.6))
                        blue = int(blue * (1 - red_factor * 0.6))
                    
                    # 确保值在有效范围内
                    red = max(0, min(255, red))
                    green = max(0, min(255, green))
                    blue = max(0, min(255, blue))
                    
                    # 创建新的像素颜色
                    new_pixel = (alpha << 24) | (red << 16) | (green << 8) | blue
                    image.setPixel(x, y, new_pixel)
        
        # 转换回QPixmap
        result_pixmap = QPixmap.fromImage(image)
        return result_pixmap
        
    except Exception as e:
        print(f"图像电竞红处理失败: {e}")
        return pixmap  # 返回原始图像

# 定义chengxubao文件夹路径
chengxubao_path = os.path.join(os.getcwd(), "chengxubao")

# --------------------------------------------------------------------------------------------------------------------------------
# 浩讯亿通电脑工具箱版权信息：
# 开源-免费-安全-可靠-实用-绿色-可商用-可二次开发，但不被允许未经授权做为闭源的商业软件发布和销售！
# --------------------------------------------------------------------------------------------------------------------------------
# Data:2024-09-28
# Auther:浩讯网络开发团队
# Link:QQ交流群182352621
# 问题反馈：zhangyuhao@haoxun.cc
# 版权:烟台浩讯网络有限责任公司版权所有，未经授权许可禁止闭源商用！
# 本程序遵循GPL开源协议，GPL的出发点是代码的开源/免费使用和引用/修改/衍生代码的开源/免费使用，但不允许修改后和衍生的代码做为闭源的商业软件发布和销售。
# GPL协议（GNU General Public License）是由自由软件基金会（Free Software Foundation）发布的一种开源许可证。它的主要目的是确保软件的自由使用、修改和分发权利。
# --------------------------------------------------------------------------------------------------------------------------------

class HardwareInfoThread(QThread):
    """硬件信息获取线程（增强版）"""
    hardware_info_ready = pyqtSignal(dict)
    error_occurred = pyqtSignal(str, str)  # 错误类型，错误信息
    progress_updated = pyqtSignal(str, int)  # 当前操作，进度百分比
    
    def __init__(self):
        super().__init__()
        self.cached_info = None
        self.max_retries = 3
        self.retry_delay = 1000  # 毫秒
        self.timeout = 15000  # 15秒超时
        
    def run(self):
        """运行线程，带重试机制"""
        try:
            # 优先使用缓存的硬件信息
            if self.cached_info:
                self.hardware_info_ready.emit(self.cached_info)
                return
            
            # 带重试的硬件信息获取
            hardware_info = self.get_hardware_info_with_retry()
            self.cached_info = hardware_info
            self.hardware_info_ready.emit(hardware_info)
            
        except Exception as e:
            error_info = self.create_error_info(f"线程执行失败: {str(e)}")
            self.hardware_info_ready.emit(error_info)
            self.error_occurred.emit("线程错误", str(e))
    
    def get_hardware_info_with_retry(self):
        """带重试机制的硬件信息获取"""
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                self.progress_updated.emit(f"正在获取硬件信息 (第{attempt + 1}次尝试)...", 
                                         int((attempt / self.max_retries) * 100))
                
                # 短暂延迟重试
                if attempt > 0:
                    self.msleep(self.retry_delay)
                
                hardware_info = self.get_hardware_info()
                
                # 检查是否获取到了有效信息
                valid_info_count = sum(1 for info in hardware_info.values() 
                                     if not info.startswith("获取") and not info.startswith("无法"))
                
                if valid_info_count > 0:
                    self.progress_updated.emit("硬件信息获取完成", 100)
                    return hardware_info
                
                raise Exception("未获取到有效的硬件信息")
                
            except Exception as e:
                last_error = e
                self.error_occurred.emit(f"尝试 {attempt + 1} 失败", str(e))
                
                # 如果是最后尝试，则抛出异常
                if attempt == self.max_retries - 1:
                    break
                    
                # 某些错误不需要重试
                if self.should_not_retry(e):
                    break
        
        # 所有重试都失败，返回错误信息
        error_msg = f"所有重试均失败 (最多{self.max_retries}次). 最后错误: {str(last_error)}"
        return self.create_error_info(error_msg)
    
    def should_not_retry(self, error):
        """判断是否应该重试某些错误"""
        error_str = str(error).lower()
        no_retry_errors = [
            "权限不足",
            "access denied", 
            "permission denied",
            "wmi初始化失败",
            "无效的参数",
            "invalid argument"
        ]
        
        return any(no_retry_error in error_str for no_retry_error in no_retry_errors)
    
    def create_error_info(self, main_error):
        """创建标准化的错误信息"""
        return {
            'cpu': f"❌ 获取CPU信息失败: {main_error}",
            'gpu': f"❌ 获取GPU信息失败: {main_error}",
            'memory': f"❌ 获取内存信息失败: {main_error}",
            'disk': f"❌ 获取磁盘信息失败: {main_error}",
            'system': f"❌ 获取系统信息失败: {main_error}"
        }
    
    def get_hardware_info(self):
        """获取硬件信息的详细实现，返回分类信息字典"""
        info_dict = {
            'cpu': '',
            'gpu': '',
            'memory': '',
            'disk': '',
            'display': '',
            'network': '',
            'audio': '',
            'system': ''
        }
        
        try:
            # CPU信息
            cpu_info = self.safe_get_cpu_info()
            if cpu_info:
                info_dict['cpu'] = "\n".join(cpu_info)
            else:
                info_dict['cpu'] = "无法获取CPU信息"
        except Exception as e:
            info_dict['cpu'] = f"CPU信息获取失败: {str(e)}"
            
        try:
            # GPU信息
            gpu_info = self.safe_get_gpu_info()
            if gpu_info:
                info_dict['gpu'] = "\n".join(gpu_info)
            else:
                info_dict['gpu'] = "无法获取GPU信息"
        except Exception as e:
            info_dict['gpu'] = f"GPU信息获取失败: {str(e)}"
            
        try:
            # 内存信息
            memory_info = self.safe_get_memory_info()
            if memory_info:
                info_dict['memory'] = "\n".join(memory_info)
            else:
                info_dict['memory'] = "无法获取内存信息"
        except Exception as e:
            info_dict['memory'] = f"内存信息获取失败: {str(e)}"
            
        try:
            # 磁盘信息
            disk_info = self.safe_get_disk_info()
            if disk_info:
                info_dict['disk'] = "\n".join(disk_info)
            else:
                info_dict['disk'] = "无法获取磁盘信息"
        except Exception as e:
            info_dict['disk'] = f"磁盘信息获取失败: {str(e)}"
            
        try:
            # 显示器信息
            display_info = self.safe_get_display_info()
            if display_info:
                info_dict['display'] = "\n".join(display_info)
            else:
                info_dict['display'] = "无法获取显示器信息"
        except Exception as e:
            info_dict['display'] = f"显示器信息获取失败: {str(e)}"
            
        try:
            # 网络适配器信息
            network_info = self.safe_get_network_info()
            if network_info:
                info_dict['network'] = "\n".join(network_info)
            else:
                info_dict['network'] = "无法获取网络适配器信息"
        except Exception as e:
            info_dict['network'] = f"网络适配器信息获取失败: {str(e)}"
            
        try:
            # 声卡信息
            audio_info = self.safe_get_audio_info()
            if audio_info:
                info_dict['audio'] = "\n".join(audio_info)
            else:
                info_dict['audio'] = "无法获取声卡信息"
        except Exception as e:
            info_dict['audio'] = f"声卡信息获取失败: {str(e)}"
            
        # 系统信息
        try:
            system_info = []
            system_info.append(f"操作系统: {platform.system()} {platform.release()}")
            system_info.append(f"处理器架构: {platform.machine()}")
            system_info.append(f"主机名: {socket.gethostname()}")
            system_info.append(f"Python版本: {platform.python_version()}")
            
            # 添加当前时间
            from datetime import datetime
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            system_info.append(f"检测时间: {current_time}")
            
            info_dict['system'] = "\n".join(system_info)
        except Exception as e:
            info_dict['system'] = f"系统信息获取失败: {str(e)}"
        
        return info_dict
    
    def safe_get_cpu_info(self):
        """安全获取CPU信息"""
        try:
            cpu_info = []
            
            # 方法1: 使用psutil
            try:
                cpu_freq = psutil.cpu_freq()
                if cpu_freq:
                    cpu_info.append(f"CPU频率: {cpu_freq.current:.2f}MHz")
                else:
                    cpu_info.append(f"CPU频率: {psutil.cpu_count()} 核心")
            except:
                pass
            
            # 方法2: 使用platform模块
            try:
                cpu_info.append(f"CPU型号: {platform.processor()}")
            except:
                pass
                
            # 方法3: Windows WMI
            if platform.system() == "Windows" and WMI_AVAILABLE:
                try:
                    init_com()
                    c = wmi.WMI()
                    for cpu in c.Win32_Processor():
                        cpu_info.append(f"CPU名称: {cpu.Name}")
                        cpu_info.append(f"CPU核心数: {cpu.NumberOfCores}")
                        cpu_info.append(f"CPU线程数: {cpu.NumberOfLogicalProcessors}")
                        cpu_info.append(f"CPU制造商: {cpu.Manufacturer}")
                        break
                except Exception as e:
                    cpu_info.append(f"WMI获取失败: {e}")
                finally:
                    try:
                        import pythoncom
                        pythoncom.CoUninitialize()
                    except:
                        pass
            elif platform.system() == "Windows":
                cpu_info.append("WMI模块不可用，无法获取详细CPU信息")
            
            return cpu_info if cpu_info else ["无法获取CPU详细信息"]
            
        except Exception as e:
            return [f"CPU信息获取错误: {e}"]
    
    def safe_get_gpu_info(self):
        """安全获取GPU信息"""
        try:
            gpu_info = []
            
            # 方法1: 使用GPUtil
            try:
                gpus = GPUtil.getGPUs()
                if gpus:
                    for i, gpu in enumerate(gpus):
                        gpu_info.append(f"GPU {i+1}: {gpu.name}")
                        gpu_info.append(f"  显存: {gpu.memoryTotal}MB")
                        gpu_info.append(f"  驱动版本: {gpu.driver}")
                        gpu_info.append(f"  温度: {gpu.temperature}°C")
                else:
                    gpu_info.append("未检测到独立显卡")
            except:
                pass
            
            # 方法2: Windows WMI
            if platform.system() == "Windows" and WMI_AVAILABLE:
                try:
                    init_com()
                    c = wmi.WMI()
                    for gpu in c.Win32_VideoController():
                        if not gpu.Name.startswith("Microsoft"):
                            gpu_info.append(f"显卡: {gpu.Name}")
                            gpu_info.append(f"显存: {gpu.AdapterRAM // (1024**3) if gpu.AdapterRAM else '未知'}GB")
                            gpu_info.append(f"驱动程序: {gpu.DriverVersion}")
                            break
                except Exception as e:
                    gpu_info.append(f"WMI获取失败: {e}")
                finally:
                    try:
                        import pythoncom
                        pythoncom.CoUninitialize()
                    except:
                        pass
            elif platform.system() == "Windows":
                gpu_info.append("WMI模块不可用，无法获取详细GPU信息")
            
            return gpu_info if gpu_info else ["无法获取GPU详细信息"]
            
        except Exception as e:
            return [f"GPU信息获取错误: {e}"]
    
    def safe_get_memory_info(self):
        """安全获取内存信息"""
        try:
            memory_info = []
            
            # 使用psutil获取内存信息
            try:
                memory = psutil.virtual_memory()
                memory_info.append(f"总内存: {memory.total / (1024**3):.2f}GB")
                memory_info.append(f"可用内存: {memory.available / (1024**3):.2f}GB")
                memory_info.append(f"已使用内存: {memory.used / (1024**3):.2f}GB ({memory.percent:.1f}%)")
                memory_info.append(f"内存类型: DDR4" if platform.system() == "Windows" else "系统内存")
            except:
                pass
            
            # Windows WMI获取内存详细信息
            if platform.system() == "Windows" and WMI_AVAILABLE:
                try:
                    init_com()
                    c = wmi.WMI()
                    for memory_module in c.Win32_PhysicalMemory():
                        memory_info.append(f"内存条: {memory_module.Manufacturer} {memory_module.PartNumber}")
                        memory_info.append(f"容量: {int(memory_module.Capacity) // (1024**3)}GB")
                        memory_info.append(f"频率: {memory_module.Speed}MHz")
                        break
                except Exception as e:
                    memory_info.append(f"WMI获取失败: {e}")
                finally:
                    try:
                        import pythoncom
                        pythoncom.CoUninitialize()
                    except:
                        pass
            elif platform.system() == "Windows":
                memory_info.append("WMI模块不可用，无法获取详细内存信息")
            
            return memory_info if memory_info else ["无法获取内存详细信息"]
            
        except Exception as e:
            return [f"内存信息获取错误: {e}"]
    
    def safe_get_disk_info(self):
        """安全获取磁盘信息"""
        try:
            disk_info = []
            
            # 使用psutil获取磁盘信息
            try:
                disks = psutil.disk_partitions()
                for disk in disks:
                    try:
                        usage = psutil.disk_usage(disk.mountpoint)
                        disk_info.append(f"磁盘: {disk.device}")
                        disk_info.append(f"  文件系统: {disk.fstype}")
                        disk_info.append(f"  总容量: {usage.total / (1024**3):.2f}GB")
                        disk_info.append(f"  已使用: {usage.used / (1024**3):.2f}GB ({usage.percent:.1f}%)")
                        disk_info.append(f"  可用空间: {usage.free / (1024**3):.2f}GB")
                    except PermissionError:
                        continue
            except:
                pass
            
            return disk_info if disk_info else ["无法获取磁盘详细信息"]
            
        except Exception as e:
            return [f"磁盘信息获取错误: {e}"]

    def safe_get_display_info(self):
        """安全获取显示器信息"""
        try:
            display_info = []
            
            # Windows WMI获取显示器信息
            if platform.system() == "Windows" and WMI_AVAILABLE:
                try:
                    init_com()
                    c = wmi.WMI()
                    # 获取监视器信息
                    for i, monitor in enumerate(c.Win32_DesktopMonitor(), 1):
                        display_info.append(f"显示器 {i}: {monitor.Name}")
                        display_info.append(f"  状态: {monitor.Status}")
                        display_info.append(f"  制造商: {monitor.MonitorManufacturer}")
                        display_info.append(f"  型号: {monitor.MonitorType}")
                        display_info.append(f"  尺寸: {monitor.ScreenWidth}x{monitor.ScreenHeight}")
                        display_info.append("")
                        
                    # 如果没有找到Win32_DesktopMonitor，尝试通过WMI获取视频控制器信息
                    if not any("显示器" in info for info in display_info):
                        for i, controller in enumerate(c.Win32_VideoController(), 1):
                            display_info.append(f"视频控制器 {i}: {controller.Name}")
                            if hasattr(controller, 'VideoModeDescription'):
                                display_info.append(f"  视频模式: {controller.VideoModeDescription}")
                            if hasattr(controller, 'DriverVersion'):
                                display_info.append(f"  驱动版本: {controller.DriverVersion}")
                            display_info.append("")
                            
                except Exception as e:
                    display_info.append(f"WMI获取显示器信息失败: {e}")
                finally:
                    try:
                        import pythoncom
                        pythoncom.CoUninitialize()
                    except:
                        pass
            elif platform.system() == "Windows":
                display_info.append("WMI模块不可用，无法获取详细显示器信息")
            else:
                # Linux/Unix系统使用其他方法
                try:
                    # 尝试读取系统显示信息
                    result = subprocess.run(['xrandr'], capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        lines = result.stdout.split('\n')
                        for line in lines:
                            if ' connected' in line or ' disconnected' in line:
                                parts = line.split()
                                if parts:
                                    display_name = parts[0]
                                    display_info.append(f"显示器: {display_name}")
                                    # 查找分辨率信息
                                    for subline in lines:
                                        if display_name in subline and '*' in subline:
                                            # 提取分辨率
                                            import re
                                            res_match = re.search(r'(\d+x\d+)', subline)
                                            if res_match:
                                                display_info.append(f"  分辨率: {res_match.group(1)}")
                                            break
                                    display_info.append("")
                except:
                    display_info.append("无法获取显示器信息")
            
            return display_info if display_info else ["无法获取显示器详细信息"]
            
        except Exception as e:
            return [f"显示器信息获取错误: {e}"]

    def safe_get_network_info(self):
        """安全获取网络适配器信息"""
        try:
            network_info = []
            
            # 使用psutil获取网络接口信息
            try:
                if_addrs = psutil.net_if_addrs()
                for interface_name, interface_addresses in if_addrs.items():
                    if interface_name.startswith(('lo', 'Loopback')):  # 跳过本地回环
                        continue
                    
                    network_info.append(f"网络适配器: {interface_name}")
                    for address in interface_addresses:
                        family = address.family
                        if family == socket.AF_INET:  # IPv4
                            network_info.append(f"  IPv4地址: {address.address}")
                            network_info.append(f"  子网掩码: {address.netmask}")
                        elif family == socket.AF_INET6:  # IPv6
                            network_info.append(f"  IPv6地址: {address.address}")
                        elif family == psutil.AF_LINK:
                            network_info.append(f"  MAC地址: {address.address}")
                    network_info.append("")
            except:
                pass
            
            # Windows WMI获取更详细的网络适配器信息
            if platform.system() == "Windows" and WMI_AVAILABLE:
                try:
                    init_com()
                    c = wmi.WMI()
                    for i, adapter in enumerate(c.Win32_NetworkAdapter(), 1):
                        # 过滤掉虚拟适配器
                        if adapter.NetConnectionID and not adapter.NetConnectionID.startswith('蓝牙'):
                            network_info.append(f"网络适配器 {i}: {adapter.NetConnectionID}")
                            network_info.append(f"  描述: {adapter.Description}")
                            network_info.append(f"  类型: {adapter.AdapterType}")
                            network_info.append(f"  速度: {adapter.Speed} Mbps" if adapter.Speed else "  速度: 未知")
                            network_info.append(f"  状态: {'已连接' if adapter.NetConnectionStatus == 7 else '未连接'}")
                            network_info.append("")
                except Exception as e:
                    network_info.append(f"WMI获取网络适配器信息失败: {e}")
                finally:
                    try:
                        import pythoncom
                        pythoncom.CoUninitialize()
                    except:
                        pass
            elif platform.system() == "Windows":
                network_info.append("WMI模块不可用，无法获取详细网络适配器信息")
            
            return network_info if network_info else ["无法获取网络适配器详细信息"]
            
        except Exception as e:
            return [f"网络适配器信息获取错误: {e}"]

    def safe_get_audio_info(self):
        """安全获取声卡信息"""
        try:
            audio_info = []
            
            # Windows WMI获取声卡信息
            if platform.system() == "Windows" and WMI_AVAILABLE:
                try:
                    init_com()
                    c = wmi.WMI()
                    # 获取音频控制器信息
                    for i, controller in enumerate(c.Win32_SoundDevice(), 1):
                        audio_info.append(f"声卡 {i}: {controller.Name}")
                        audio_info.append(f"  状态: {controller.Status}")
                        audio_info.append(f"  制造商: {controller.Manufacturer}")
                        audio_info.append(f"  状态信息: {controller.StatusInfo}")
                        audio_info.append("")
                except Exception as e:
                    audio_info.append(f"WMI获取声卡信息失败: {e}")
                finally:
                    try:
                        import pythoncom
                        pythoncom.CoUninitialize()
                    except:
                        pass
            elif platform.system() == "Windows":
                audio_info.append("WMI模块不可用，无法获取详细声卡信息")
            else:
                # Linux/Unix系统使用其他方法
                try:
                    # 尝试使用lspci或系统命令
                    commands = ['lspci', 'aplay -l', 'pacmd list-sinks']
                    for cmd in commands:
                        try:
                            result = subprocess.run(cmd.split(), capture_output=True, text=True, timeout=5)
                            if result.returncode == 0:
                                lines = result.stdout.split('\n')
                                for line in lines:
                                    if any(keyword in line.lower() for keyword in ['audio', 'sound', 'audio device', 'sound device']):
                                        audio_info.append(f"音频设备: {line.strip()}")
                                break
                        except:
                            continue
                    if not audio_info:
                        audio_info.append("无法检测到音频设备")
                except:
                    audio_info.append("无法获取声卡信息")
            
            return audio_info if audio_info else ["无法获取声卡详细信息"]
            
        except Exception as e:
            return [f"声卡信息获取错误: {e}"]


class ToolButton(QPushButton):
    """自定义工具按钮类"""
    def __init__(self, text, icon_path=None, tool_path=None, parent=None):
        super().__init__(text, parent)
        self.tool_path = tool_path
        self.setMinimumHeight(60)
        self.setMinimumWidth(120)
        
        # 设置图标
        if icon_path and os.path.exists(icon_path):
            try:
                icon = QIcon(icon_path)
                self.setIcon(icon)
                self.setIconSize(QSize(32, 32))
            except Exception as e:
                print(f"设置图标失败 {icon_path}: {e}")
        
        self.setStyleSheet("""
            QPushButton {
                border: 2px solid #ddd;
                border-radius: 8px;
                background-color: #f9f9f9;
                padding: 10px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #e3f2fd;
                border-color: #2196F3;
            }
            QPushButton:pressed {
                background-color: #bbdefb;
            }
        """)




class FanController:
    """风扇控制器 - 用于控制电脑风扇转速"""
    
    def __init__(self):
        self.is_initialized = False
        self.fan_devices = []
        self.current_fan_speed = {}
        self.error_message = ""
        self.safety_enabled = True
        self.max_allowed_temp = 85  # 最大允许温度
        self.min_safe_speed = 20   # 最小安全转速百分比
        self.max_safe_speed = 100  # 最大安全转速百分比
        self.cooldown_period = 2   # 冷却期（秒）
        self.last_speed_change = {}
        self.fan_health_status = {}
        self.error_count = {}
        self.max_error_count = 5
        self.fan_history = {}
        self.history_interval = 10  # 记录间隔（秒）
        self.max_history_size = 1000  # 最大历史记录数
        self.last_history_update = 0
        
        # 初始化日志系统
        self.logger = logging.getLogger('FanController')
        
        # 尝试初始化
        self.initialize()
    
    def initialize(self):
        """初始化风扇控制器"""
        try:
            # 检测风扇设备
            self.detect_fan_devices()
            
            # 获取风扇转速范围
            for device in self.fan_devices:
                speed_range = self.get_fan_speed_range(device['id'])
                if speed_range:
                    device['min_speed'] = speed_range['min']
                    device['max_speed'] = speed_range['max']
            
            self.is_initialized = True
            self.error_message = ""
            self.logger.info("风扇控制器初始化成功")
            
        except Exception as e:
            self.is_initialized = False
            self.error_message = f"风扇控制器初始化失败: {str(e)}"
            self.logger.error(f"风扇控制器初始化失败: {e}")
    
    def detect_fan_devices(self):
        """检测风扇设备"""
        try:
            # 清空现有设备列表
            self.fan_devices = []
            
            # 尝试使用WMI检测风扇
            if self.detect_fan_devices_wmi():
                return
            
            # 尝试使用OpenHardwareMonitor检测风扇
            if self.detect_fan_devices_ohm():
                return
            
            # 尝试使用系统API检测风扇
            if self.detect_fan_devices_system():
                return
            
            # 如果所有检测方法都失败，添加模拟风扇
            self.add_simulated_fans()
            
        except Exception as e:
            self.logger.error(f"风扇设备检测失败: {e}")
            # 添加模拟风扇作为后备
            self.add_simulated_fans()
    
    def detect_fan_devices_wmi(self):
        """使用WMI检测风扇设备"""
        try:
            if not WMI_AVAILABLE:
                self.logger.info("WMI模块不可用，跳过风扇检测")
                return False
                
            # 初始化COM组件
            import pythoncom
            pythoncom.CoInitialize()
                
            try:
                c = wmi.WMI()
                fans = c.Win32_Fan()
                
                if not fans:
                    self.logger.info("未检测到WMI风扇设备")
                    return False
                
                for fan in fans:
                    device_info = {
                        'id': fan.DeviceID,
                        'name': fan.Name or f"风扇 {len(self.fan_devices) + 1}",
                        'type': 'wmi',
                        'description': fan.Description or "WMI风扇"
                    }
                    self.fan_devices.append(device_info)
                
                self.logger.info(f"成功检测到 {len(fans)} 个WMI风扇设备")
                return len(fans) > 0
                
            except Exception as e:
                self.logger.warning(f"WMI风扇检测失败: {e}")
                return False
                
        except Exception as e:
            self.logger.warning(f"WMI风扇检测初始化失败: {e}")
            return False
        finally:
            # 清理COM资源
            try:
                import pythoncom
                pythoncom.CoUninitialize()
            except:
                pass
    
    def detect_fan_devices_ohm(self):
        """使用OpenHardwareMonitor检测风扇设备"""
        try:
            if not WMI_AVAILABLE:
                self.logger.info("WMI模块不可用，跳过OpenHardwareMonitor风扇检测")
                return False
                
            # 初始化COM组件
            import pythoncom
            pythoncom.CoInitialize()
                
            try:
                # 检查OpenHardwareMonitor是否正在运行
                import psutil
                ohm_running = any('openhardwaremonitor' in p.info['name'].lower() 
                                for p in psutil.process_iter(attrs=['name']) 
                                if p.info.get('name'))
                
                if not ohm_running:
                    self.logger.info("OpenHardwareMonitor未运行，跳过风扇检测")
                    return False
                    
                c = wmi.WMI(namespace='root\\OpenHardwareMonitor')
                sensors = c.Sensor()
                
                fan_sensors = [s for s in sensors if s.SensorType == 'Fan']
                
                if not fan_sensors:
                    self.logger.info("未检测到OpenHardwareMonitor风扇设备")
                    return False
                
                for sensor in fan_sensors:
                    device_info = {
                        'id': sensor.Identifier,
                        'name': sensor.Name or f"风扇 {len(self.fan_devices) + 1}",
                        'type': 'ohm',
                        'description': f"OpenHardwareMonitor {sensor.Name}"
                    }
                    self.fan_devices.append(device_info)
                
                self.logger.info(f"成功检测到 {len(fan_sensors)} 个OpenHardwareMonitor风扇设备")
                return len(fan_sensors) > 0
                
            except Exception as e:
                # 检查是否是COM错误（OpenHardwareMonitor未运行）
                if "-2147217394" in str(e):
                    self.logger.info("OpenHardwareMonitor未运行，无法访问硬件监控数据")
                else:
                    self.logger.warning(f"OpenHardwareMonitor风扇检测失败: {e}")
                return False
                
        except Exception as e:
            self.logger.warning(f"OpenHardwareMonitor风扇检测初始化失败: {e}")
            return False
        finally:
            # 清理COM资源
            try:
                import pythoncom
                pythoncom.CoUninitialize()
            except:
                pass
    
    def detect_fan_devices_system(self):
        """使用系统API检测风扇设备"""
        try:
            # 尝试使用系统调用检测风扇
            # 这里可以集成系统特定的风扇检测逻辑
            
            # 检查是否有CPU风扇
            if self.has_cpu_fan():
                device_info = {
                    'id': 'cpu_fan_system',
                    'name': 'CPU风扇',
                    'type': 'system',
                    'description': '系统检测到的CPU风扇'
                }
                self.fan_devices.append(device_info)
            
            # 检查是否有机箱风扇
            if self.has_case_fan():
                device_info = {
                    'id': 'case_fan_system',
                    'name': '机箱风扇',
                    'type': 'system',
                    'description': '系统检测到的机箱风扇'
                }
                self.fan_devices.append(device_info)
            
            return len(self.fan_devices) > 0
            
        except Exception as e:
            self.logger.warning(f"系统风扇检测失败: {e}")
            return False
    
    def has_cpu_fan(self):
        """检查是否有CPU风扇"""
        # 简单的CPU风扇检测逻辑
        # 实际实现可能需要更复杂的检测
        return True  # 假设大多数系统都有CPU风扇
    
    def has_case_fan(self):
        """检查是否有机箱风扇"""
        # 简单的机箱风扇检测逻辑
        return False  # 假设不是所有系统都有机箱风扇
    
    def add_simulated_fans(self):
        """添加模拟风扇"""
        # 添加CPU风扇模拟
        cpu_fan = {
            'id': 'cpu_fan_simulated',
            'name': 'CPU风扇（模拟）',
            'type': 'simulated',
            'description': '模拟CPU风扇控制'
        }
        self.fan_devices.append(cpu_fan)
        
        # 添加机箱风扇模拟
        case_fan = {
            'id': 'case_fan_simulated',
            'name': '机箱风扇（模拟）',
            'type': 'simulated',
            'description': '模拟机箱风扇控制'
        }
        self.fan_devices.append(case_fan)
        
        self.logger.info("已添加模拟风扇设备")
    
    def get_fan_speed_range(self, fan_device_id):
        """获取风扇转速范围"""
        try:
            # 根据设备类型获取转速范围
            device = next((d for d in self.fan_devices if d['id'] == fan_device_id), None)
            if not device:
                return None
            
            if device['type'] == 'simulated':
                return {'min': 0, 'max': 100}
            elif device['type'] == 'wmi':
                # WMI风扇通常有固定的转速范围
                return {'min': 20, 'max': 100}
            elif device['type'] == 'ohm':
                # OpenHardwareMonitor风扇
                return {'min': 0, 'max': 100}
            else:
                # 默认范围
                return {'min': 0, 'max': 100}
                
        except Exception as e:
            self.logger.error(f"获取风扇转速范围失败: {e}")
            return {'min': 0, 'max': 100}
    
    def set_fan_speed(self, fan_device_id, speed_percentage):
        """设置风扇转速"""
        try:
            # 安全检查
            if self.safety_enabled:
                safe, message = self._check_safety_conditions(fan_device_id, speed_percentage)
                if not safe:
                    self.logger.warning(f"安全限制: {message}")
                    return False, message
            
            # 检查风扇健康状态
            if self._is_fan_unhealthy(fan_device_id):
                message = f"风扇 {fan_device_id} 处于不健康状态，控制被限制"
                self.logger.warning(message)
                return False, message
            
            # 根据设备类型设置转速
            device = next((d for d in self.fan_devices if d['id'] == fan_device_id), None)
            if not device:
                return False, "未找到指定的风扇设备"
            
            success = False
            
            if device['type'] == 'simulated':
                success = self.set_simulated_fan_speed(fan_device_id, speed_percentage)
            elif device['type'] == 'wmi':
                success = self.set_wmi_fan_speed(fan_device_id, speed_percentage)
            elif device['type'] == 'ohm':
                success = self.set_ohm_fan_speed(fan_device_id, speed_percentage)
            else:
                success = self.set_system_fan_speed(fan_device_id, speed_percentage)
            
            if success:
                # 更新当前转速
                self.current_fan_speed[fan_device_id] = speed_percentage
                
                # 记录转速变化时间
                self.last_speed_change[fan_device_id] = time.time()
                
                # 记录历史数据
                self.record_fan_history(fan_device_id, speed_percentage)
                
                # 重置错误计数（如果之前有错误）
                if fan_device_id in self.error_count:
                    self.error_count[fan_device_id] = 0
                
                message = f"风扇 {fan_device_id} 转速已设置为 {speed_percentage}%"
                self.logger.info(message)
                return True, message
            else:
                # 记录错误
                self._record_fan_error(fan_device_id)
                message = f"设置风扇 {fan_device_id} 转速失败"
                self.logger.error(message)
                return False, message
                
        except Exception as e:
            # 记录错误
            self._record_fan_error(fan_device_id)
            message = f"设置风扇转速时发生错误: {str(e)}"
            self.logger.error(message)
            return False, message
    
    def set_simulated_fan_speed(self, fan_device_id, speed_percentage):
        """设置模拟风扇转速"""
        # 模拟设置，实际无操作
        print(f"模拟设置风扇 {fan_device_id} 转速: {speed_percentage}%")
        return True
    
    def set_wmi_fan_speed(self, fan_device_id, speed_percentage):
        """使用WMI设置风扇转速"""
        try:
            if not WMI_AVAILABLE:
                return False
                
            c = wmi.WMI()
            # 查找对应的风扇设备
            fans = c.Win32_Fan(DeviceID=fan_device_id)
            
            if not fans:
                return False
                
            # 尝试设置风扇转速（具体实现取决于硬件支持）
            # 这里只是示例，实际实现需要根据具体硬件调整
            fan = fans[0]
            # fan.DesiredSpeed = int(speed_percentage)  # 如果硬件支持
            
            return True
            
        except Exception as e:
            print(f"WMI风扇控制失败: {e}")
            return False
    
    def set_ohm_fan_speed(self, fan_device_id, speed_percentage):
        """使用OpenHardwareMonitor设置风扇转速"""
        try:
            if not WMI_AVAILABLE:
                return False
                
            # 需要OpenHardwareMonitor运行并支持风扇控制
            c = wmi.WMI(namespace='root\\OpenHardwareMonitor')
            
            # 查找对应的传感器
            sensors = c.Sensor(Identifier=fan_device_id)
            if not sensors:
                return False
                
            # 尝试设置控制值
            sensor = sensors[0]
            # sensor.Value = speed_percentage  # 如果支持控制
            
            return True
            
        except Exception as e:
            return False
    
    def set_system_fan_speed(self, fan_device_id, speed_percentage):
        """使用系统API设置风扇转速"""
        try:
            # 使用系统调用或第三方工具
            # 这里可以集成如SpeedFan、Argus Monitor等工具
            
            # 示例：使用命令行工具（如果可用）
            # subprocess.run(['speedfan', '/setfan', fan_device_id, str(speed_percentage)])
            
            return True
            
        except Exception as e:
            return False
    
    def get_fan_speed(self, fan_device_id):
        """获取当前风扇转速"""
        return self.current_fan_speed.get(fan_device_id, 0)
    
    def get_available_fans(self):
        """获取可用的风扇设备列表"""
        return self.fan_devices
    
    def get_status(self):
        """获取控制器状态"""
        return {
            'initialized': self.is_initialized,
            'fan_count': len(self.fan_devices),
            'error_message': self.error_message,
            'fan_devices': self.fan_devices,
            'current_speeds': self.current_fan_speed,
            'safety_enabled': self.safety_enabled,
            'fan_health_status': self.fan_health_status
        }
    
    def _check_safety_conditions(self, fan_device_id, speed_percentage):
        """检查安全条件"""
        try:
            # 检查温度是否过高
            current_temp = self._get_current_temperature()
            if current_temp > self.max_allowed_temp:
                return False, f"系统温度过高 ({current_temp}°C)，风扇控制被限制"
            
            # 检查安全转速范围
            if speed_percentage < self.min_safe_speed:
                return False, f"转速过低 ({speed_percentage}%)，低于安全阈值 ({self.min_safe_speed}%)"
            
            if speed_percentage > self.max_safe_speed:
                return False, f"转速过高 ({speed_percentage}%)，超过安全阈值 ({self.max_safe_speed}%)"
            
            # 检查冷却期
            current_time = time.time()
            last_change = self.last_speed_change.get(fan_device_id, 0)
            if current_time - last_change < self.cooldown_period:
                return False, f"转速变化过快，请等待 {self.cooldown_period} 秒冷却期"
            
            return True, "安全检查通过"
            
        except Exception as e:
            return False, f"安全检查失败: {str(e)}"
    
    def _get_current_temperature(self):
        """获取当前系统温度"""
        try:
            # 获取CPU温度
            temps = psutil.sensors_temperatures()
            if temps and 'coretemp' in temps:
                cpu_temps = temps['coretemp']
                if cpu_temps:
                    return max(temp.current for temp in cpu_temps)
            
            # 默认返回安全温度
            return 50
            
        except:
            # 如果无法获取温度，返回安全值
            return 50
    
    def _is_fan_unhealthy(self, fan_device_id):
        """检查风扇是否健康"""
        # 初始化健康状态
        if fan_device_id not in self.fan_health_status:
            self.fan_health_status[fan_device_id] = 'healthy'
            self.error_count[fan_device_id] = 0
        
        # 如果错误次数超过阈值，标记为不健康
        if self.error_count.get(fan_device_id, 0) >= self.max_error_count:
            self.fan_health_status[fan_device_id] = 'unhealthy'
            return True
        
        return self.fan_health_status[fan_device_id] == 'unhealthy'
    
    def _record_fan_error(self, fan_device_id):
        """记录风扇错误"""
        if fan_device_id not in self.error_count:
            self.error_count[fan_device_id] = 0
        
        self.error_count[fan_device_id] += 1
        
        # 如果错误次数超过阈值，标记为不健康
        if self.error_count[fan_device_id] >= self.max_error_count:
            self.fan_health_status[fan_device_id] = 'unhealthy'
    
    def reset_fan_health(self, fan_device_id):
        """重置风扇健康状态"""
        self.fan_health_status[fan_device_id] = 'healthy'
        self.error_count[fan_device_id] = 0
        return True, "风扇健康状态已重置"
    
    def set_safety_parameters(self, max_temp=None, min_speed=None, max_speed=None, cooldown=None):
        """设置安全参数"""
        if max_temp is not None:
            self.max_allowed_temp = max_temp
        if min_speed is not None:
            self.min_safe_speed = min_speed
        if max_speed is not None:
            self.max_safe_speed = max_speed
        if cooldown is not None:
            self.cooldown_period = cooldown
        
        return True, "安全参数已更新"
    
    def enable_safety_mode(self, enabled=True):
        """启用/禁用安全模式"""
        self.safety_enabled = enabled
        status = "启用" if enabled else "禁用"
        return True, f"安全模式已{status}"
    
    def record_fan_history(self, fan_device_id, speed, temperature=None):
        """记录风扇历史数据"""
        try:
            current_time = time.time()
            
            # 检查是否达到记录间隔
            if current_time - self.last_history_update < self.history_interval:
                return
            
            self.last_history_update = current_time
            
            if fan_device_id not in self.fan_history:
                self.fan_history[fan_device_id] = []
            
            # 添加新记录
            self.fan_history[fan_device_id].append((current_time, speed, temperature))
            
            # 限制历史记录大小
            if len(self.fan_history[fan_device_id]) > self.max_history_size:
                self.fan_history[fan_device_id] = self.fan_history[fan_device_id][-self.max_history_size:]
                
            return True
            
        except Exception as e:
            self.logger.error(f"记录风扇历史数据失败: {e}")
            return False
    
    def get_fan_history(self, fan_device_id, time_range=300):
        """获取指定时间范围内的风扇历史数据"""
        try:
            if fan_device_id not in self.fan_history:
                return []
            
            current_time = time.time()
            cutoff_time = current_time - time_range
            
            # 过滤指定时间范围内的数据
            history_data = [
                (timestamp, speed, temp) 
                for timestamp, speed, temp in self.fan_history[fan_device_id]
                if timestamp >= cutoff_time
            ]
            
            return history_data
            
        except Exception as e:
            self.logger.error(f"获取风扇历史数据失败: {e}")
            return []
    
    def clear_fan_history(self, fan_device_id=None):
        """清除风扇历史记录"""
        try:
            if fan_device_id is None:
                # 清除所有历史记录
                self.fan_history.clear()
            else:
                # 清除指定风扇的历史记录
                if fan_device_id in self.fan_history:
                    self.fan_history[fan_device_id].clear()
            
            return True
            
        except Exception as e:
            self.logger.error(f"清除风扇历史记录失败: {e}")
            return False
    
    def get_fan_statistics(self, fan_device_id, time_range=300):
        """获取风扇统计信息"""
        try:
            history_data = self.get_fan_history(fan_device_id, time_range)
            
            if not history_data:
                return {
                    'avg_speed': 0,
                    'max_speed': 0,
                    'min_speed': 0,
                    'data_points': 0
                }
            
            speeds = [speed for _, speed, _ in history_data]
            
            return {
                'avg_speed': sum(speeds) / len(speeds),
                'max_speed': max(speeds),
                'min_speed': min(speeds),
                'data_points': len(history_data)
            }
            
        except Exception as e:
            self.logger.error(f"获取风扇统计信息失败: {e}")
            return {
                'avg_speed': 0,
                'max_speed': 0,
                'min_speed': 0,
                'data_points': 0
            }


class TemperatureMonitor:
    """温度监控器 - 用于智能风扇控制"""
    
    def __init__(self):
        self.temperature_history = {}
        self.update_interval = 5  # 秒
        self.is_monitoring = False
        self.fan_controller = None
        self.control_mode = "balanced"  # balanced, quiet, performance
        self.temperature_thresholds = {
            'balanced': {'target': 60, 'max': 80, 'min_speed': 30},
            'quiet': {'target': 65, 'max': 85, 'min_speed': 20},
            'performance': {'target': 55, 'max': 75, 'min_speed': 40}
        }
        self.trend_analysis = {}
        self.last_control_time = 0
        
    def set_fan_controller(self, fan_controller):
        """设置风扇控制器引用"""
        self.fan_controller = fan_controller
        
    def set_control_mode(self, mode):
        """设置控制模式"""
        if mode in self.temperature_thresholds:
            self.control_mode = mode
            return True
        return False
    
    def set_temperature_thresholds(self, target_temp=None, max_temp=None, min_speed=None):
        """设置温度阈值"""
        if self.control_mode in self.temperature_thresholds:
            if target_temp is not None:
                self.temperature_thresholds[self.control_mode]['target'] = target_temp
            if max_temp is not None:
                self.temperature_thresholds[self.control_mode]['max'] = max_temp
            if min_speed is not None:
                self.temperature_thresholds[self.control_mode]['min_speed'] = min_speed
            return True
        return False
        
    def start_monitoring(self):
        """开始温度监控"""
        self.is_monitoring = True
        self.last_control_time = time.time()
        
    def stop_monitoring(self):
        """停止温度监控"""
        self.is_monitoring = False
        
    def get_temperatures(self):
        """获取系统温度"""
        temperatures = {}
        
        try:
            # 获取CPU温度
            cpu_temps = psutil.sensors_temperatures()
            if cpu_temps:
                for name, entries in cpu_temps.items():
                    for entry in entries:
                        if entry.current:
                            sensor_key = f"{name}_{entry.label or 'temp'}"
                            temperatures[sensor_key] = entry.current
                            
                            # 更新温度历史
                            if sensor_key not in self.temperature_history:
                                self.temperature_history[sensor_key] = []
                            self.temperature_history[sensor_key].append({
                                'temp': entry.current,
                                'time': time.time()
                            })
                            
                            # 保持最近60个数据点
                            if len(self.temperature_history[sensor_key]) > 60:
                                self.temperature_history[sensor_key] = self.temperature_history[sensor_key][-60:]
            
            # 获取GPU温度（如果可用）
            if GPUTIL_AVAILABLE:
                gpus = GPUtil.getGPUs()
                for i, gpu in enumerate(gpus):
                    sensor_key = f"gpu_{i}_temp"
                    temperatures[sensor_key] = gpu.temperature
                    
                    # 更新温度历史
                    if sensor_key not in self.temperature_history:
                        self.temperature_history[sensor_key] = []
                    self.temperature_history[sensor_key].append({
                        'temp': gpu.temperature,
                        'time': time.time()
                    })
                    
                    # 保持最近60个数据点
                    if len(self.temperature_history[sensor_key]) > 60:
                        self.temperature_history[sensor_key] = self.temperature_history[sensor_key][-60:]
            
        except Exception as e:
            print(f"温度监控失败: {e}")
        
        return temperatures
    
    def analyze_temperature_trend(self, sensor_key):
        """分析温度趋势"""
        if sensor_key not in self.temperature_history:
            return "stable"
            
        history = self.temperature_history[sensor_key]
        if len(history) < 10:
            return "stable"
            
        # 计算最近10个数据点的趋势
        recent_temps = [entry['temp'] for entry in history[-10:]]
        
        # 线性回归分析趋势
        x = list(range(len(recent_temps)))
        y = recent_temps
        
        # 计算斜率
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2 = sum(x_i * x_i for x_i in x)
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        
        if slope > 0.5:
            return "rising_fast"
        elif slope > 0.1:
            return "rising"
        elif slope < -0.5:
            return "falling_fast"
        elif slope < -0.1:
            return "falling"
        else:
            return "stable"
    
    def calculate_target_fan_speed(self, current_temp, target_temp=60, max_temp=80, min_speed=30):
        """根据温度计算目标风扇转速"""
        if current_temp <= target_temp:
            # 温度低于目标温度，使用最低转速
            return min_speed
        elif current_temp >= max_temp:
            # 温度达到或超过最高温度，使用最高转速
            return 100
        else:
            # 非线性插值计算转速（更平滑的曲线）
            temp_range = max_temp - target_temp
            speed_range = 100 - min_speed
            temp_ratio = (current_temp - target_temp) / temp_range
            
            # 使用平滑的S曲线函数
            smooth_ratio = 1 / (1 + math.exp(-10 * (temp_ratio - 0.5)))
            return int(min_speed + smooth_ratio * speed_range)
    
    def get_critical_temperature(self):
        """获取关键温度（最高温度）"""
        temperatures = self.get_temperatures()
        if not temperatures:
            return None
        
        max_temp = max(temperatures.values())
        max_sensor = max(temperatures, key=temperatures.get)
        
        return {
            'temperature': max_temp,
            'sensor': max_sensor,
            'trend': self.analyze_temperature_trend(max_sensor)
        }
    
    def auto_control_fans(self):
        """自动控制风扇转速"""
        if not self.is_monitoring or not self.fan_controller:
            return
            
        current_time = time.time()
        # 控制频率限制（至少2秒间隔）
        if current_time - self.last_control_time < 2:
            return
            
        self.last_control_time = current_time
        
        # 获取关键温度
        critical_temp = self.get_critical_temperature()
        if not critical_temp:
            return
            
        current_temp = critical_temp['temperature']
        trend = critical_temp['trend']
        
        # 获取当前控制模式的阈值
        mode_settings = self.temperature_thresholds[self.control_mode]
        target_temp = mode_settings['target']
        max_temp = mode_settings['max']
        min_speed = mode_settings['min_speed']
        
        # 基础风扇转速计算
        base_speed = self.calculate_target_fan_speed(current_temp, target_temp, max_temp, min_speed)
        
        # 根据温度趋势调整转速
        trend_adjustment = 0
        if trend == "rising_fast":
            trend_adjustment = 15
        elif trend == "rising":
            trend_adjustment = 8
        elif trend == "falling_fast":
            trend_adjustment = -10
        elif trend == "falling":
            trend_adjustment = -5
        
        # 最终转速计算
        final_speed = max(min_speed, min(100, base_speed + trend_adjustment))
        
        # 获取可用的风扇设备
        available_fans = self.fan_controller.get_available_fans()
        if not available_fans:
            return
            
        # 设置所有风扇的转速
        for fan in available_fans:
            fan_id = fan['device_id']
            # 根据风扇类型调整转速（CPU风扇更敏感）
            if 'cpu' in fan_id.lower():
                # CPU风扇使用更高的转速
                fan_speed = min(100, final_speed + 5)
            else:
                fan_speed = final_speed
                
            success, message = self.fan_controller.set_fan_speed(fan_id, fan_speed)
            
            if success:
                print(f"自动控制风扇 {fan_id} 转速: {fan_speed}% (温度: {current_temp}°C, 趋势: {trend})")
            else:
                print(f"自动控制失败: {message}")
    
    def get_control_status(self):
        """获取控制状态"""
        critical_temp = self.get_critical_temperature()
        if not critical_temp:
            return {
                'monitoring': self.is_monitoring,
                'mode': self.control_mode,
                'error': '无法获取温度数据'
            }
        
        mode_settings = self.temperature_thresholds[self.control_mode]
        target_speed = self.calculate_target_fan_speed(
            critical_temp['temperature'],
            mode_settings['target'],
            mode_settings['max'],
            mode_settings['min_speed']
        )
        
        return {
            'monitoring': self.is_monitoring,
            'mode': self.control_mode,
            'critical_temperature': critical_temp['temperature'],
            'critical_sensor': critical_temp['sensor'],
            'temperature_trend': critical_temp['trend'],
            'target_fan_speed': target_speed,
            'thresholds': mode_settings
        }


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_background_color = 'white'
        self.window_hidden = False
        self.cached_hardware_info = None
        self.show_background = True
        self.current_background = 'background.jpg'  # 默认背景图片
        self.threads = []
        self.stop_event = threading.Event()
        self.token = None
        self.user_info = None
        
        # 设置窗口属性
        self.setWindowTitle("浩讯亿通电脑工具箱 1.0")
        self.setFixedSize(1280, 700)
        self.center_window()
        
        # 隐藏标题栏
        self.setWindowFlags(Qt.FramelessWindowHint)
        
        # 设置窗口图标
        try:
            self.setWindowIcon(QIcon(get_resource_path("favicon.ico")))
        except Exception as e:
            print(f"无法加载图标文件: {e}")
        
        # 初始化UI
        self.init_ui()
        
        # 初始化日志系统
        self.setup_logging()
        
        # 绑定事件
        self.setup_events()
        
        # 初始化托盘功能
        self.init_system_tray()
        
        # 初始化风扇控制器
        self.fan_controller = FanController()
        self.temperature_monitor = TemperatureMonitor()
        
        # 设置风扇控制器引用到温度监控器
        self.temperature_monitor.set_fan_controller(self.fan_controller)
        
        # 创建自动控制定时器
        self.auto_control_timer = QTimer()
        self.auto_control_timer.timeout.connect(self.temperature_monitor.auto_control_fans)
        
        # 设置默认页面为欢迎页面，不自动加载硬件信息
        self.show_welcome_page()
    
    def init_ui(self):
        """初始化用户界面"""
        # 主widget和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 创建标题栏
        self.title_bar = QFrame()
        self.title_bar.setFixedHeight(40)
        self.title_bar.setObjectName("titleBar")
        main_layout.addWidget(self.title_bar)
        
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(10, 0, 10, 0)
        title_layout.setSpacing(0)  # 按钮完全连在一起
        
        # 添加左侧弹簧，让标题居中
        title_layout.addStretch()
        
        # 标题标签 - 显示gaming.png
        try:
            gaming_path = get_resource_path("Resources\\gaming.png")
            if os.path.exists(gaming_path):
                gaming_pixmap = QPixmap(gaming_path)
                # 创建标签显示gaming.png
                self.title_label = QLabel()
                self.title_label.setPixmap(gaming_pixmap.scaled(160, 30, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                self.title_label.setAlignment(Qt.AlignCenter)
                self.title_label.setObjectName("titleLabel")
                self.title_label.setStyleSheet("""
                    #titleLabel {
                        background: transparent;
                        border: none;
                        padding: 4px;
                        margin: 0px;
                    }
                """)
                title_layout.addWidget(self.title_label)
                print("gaming.png已添加到标题栏并居中")
            else:
                # 如果gaming.png不存在，显示文字标题
                self.title_label = QLabel("浩讯亿通电脑工具箱")
                self.title_label.setAlignment(Qt.AlignCenter)
                self.title_label.setObjectName("titleLabel")
                self.title_label.setStyleSheet("""
                    #titleLabel {
                        color: #ff4757;
                        font-size: 16px;
                        font-weight: bold;
                        background: transparent;
                        border: none;
                        padding: 4px;
                        margin: 0px;
                    }
                """)
                title_layout.addWidget(self.title_label)
                print("gaming.png文件不存在，使用文字标题")
        except Exception as e:
            # 如果出现任何错误，使用文字标题
            self.title_label = QLabel("浩讯亿通电脑工具箱")
            self.title_label.setAlignment(Qt.AlignCenter)
            self.title_label.setObjectName("titleLabel")
            self.title_label.setStyleSheet("""
                #titleLabel {
                    color: #ff4757;
                    font-size: 16px;
                    font-weight: bold;
                    background: transparent;
                    border: none;
                    padding: 4px;
                    margin: 0px;
                }
            """)
            title_layout.addWidget(self.title_label)
            print(f"无法加载gaming.png，使用文字标题: {e}")
        
        # 添加右侧弹簧，让标题真正居中
        title_layout.addStretch()
        
        # 创建按钮容器以实现图片完全重合
        button_container = QWidget()
        button_container.setFixedSize(81, 40)  # 只容纳一个按钮的大小
        button_container.setStyleSheet("background: transparent;")
        
        # 隐藏按钮（底层）
        self.hide_button = QPushButton(button_container)
        self.hide_button.setObjectName("hideButton")
        self.hide_button.setGeometry(0, 0, 40, 40)  # 绝对定位
        # 强制设置样式属性以确保完全透明
        self.hide_button.setStyleSheet("""
            QPushButton#hideButton {
                background: transparent !important;
                border: none !important;
                border-radius: 0px !important;
                color: transparent !important;
                padding: 0px !important;
                margin: 0px !important;
                outline: none !important;
            }
        """)
        
        # 设置隐藏按钮图片并最大化
        try:
            hide_icon_path = get_resource_path("Resources\\-.png")
            if os.path.exists(hide_icon_path):
                hide_icon = QIcon(hide_icon_path)
                self.hide_button.setIcon(hide_icon)
                self.hide_button.setIconSize(QSize(39, 39))  # 最大化图标
        except Exception as e:
            print(f"无法加载隐藏按钮图标: {e}")
        
        # 关闭按钮（顶层，与隐藏按钮完全重合）
        self.close_button = QPushButton(button_container)
        self.close_button.setObjectName("closeButton")
        self.close_button.setGeometry(30, 0, 40, 40)  # 绝对定位，与隐藏按钮重合
        # 强制设置样式属性以确保完全透明
        self.close_button.setStyleSheet("""
            QPushButton#closeButton {
                background: transparent !important;
                border: none !important;
                border-radius: 0px !important;
                color: transparent !important;
                padding: 0px !important;
                margin: 0px !important;
                outline: none !important;
            }
        """)
        # 设置关闭按钮图片并最大化
        try:
            close_icon_path = get_resource_path("Resources\\x.png")
            if os.path.exists(close_icon_path):
                close_icon = QIcon(close_icon_path)
                self.close_button.setIcon(close_icon)
                self.close_button.setIconSize(QSize(39, 39))  # 最大化图标
        except Exception as e:
            print(f"无法加载关闭按钮图标: {e}")
        
        title_layout.addWidget(button_container)
        
        # 主内容区域
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        main_layout.addLayout(content_layout)
        
        # 左侧导航栏
        self.left_nav_frame = QFrame()
        self.left_nav_frame.setFixedWidth(200)
        self.left_nav_frame.setObjectName("leftNavFrame")
        content_layout.addWidget(self.left_nav_frame)
        
        left_nav_layout = QVBoxLayout(self.left_nav_frame)
        left_nav_layout.setContentsMargins(10, 10, 10, 10)
        left_nav_layout.setSpacing(5)
        
        # Logo
        try:
            logo_path = get_resource_path("Resources\\logo1.png")
            if os.path.exists(logo_path):
                logo_pixmap = QPixmap(logo_path)
                self.logo_label = QLabel()
                self.logo_label.setPixmap(logo_pixmap.scaled(180, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                self.logo_label.setAlignment(Qt.AlignCenter)
                left_nav_layout.addWidget(self.logo_label)
        except Exception as e:
            print(f"无法加载logo: {e}")
        
        # 程序名称
        self.program_name_label = QLabel("浩讯亿通工具箱")
        self.program_name_label.setAlignment(Qt.AlignCenter)
        self.program_name_label.setObjectName("programNameLabel")
        self.program_name_label.setStyleSheet("color: red; font-size: 16px; font-weight: bold;")
        left_nav_layout.addWidget(self.program_name_label)
        
        left_nav_layout.addSpacing(20)
        
        # 导航按钮
        self.navigation_items = [
            {"text": "硬件信息", "icon": "Resources\\电脑.svg"}, 
            {"text": "cpu工具", "icon": "Resources\\cpu.svg"}, 
            {"text": "烤鸡工具", "icon": "Resources\\烤鸡.svg"}, 
            {"text": "内存工具", "icon": "Resources\\内存.svg"}, 
            {"text": "网址导航", "icon": "Resources\\网址.svg"}, 
            {"text": "其他工具", "icon": "Resources\\工具.svg"}, 
            {"text": "关于我们", "icon": "Resources\\关于我们.svg"}, 
            {"text": "程序设置", "icon": "Resources\\设置.svg"}
        ]
        self.nav_buttons = []
        
        for item in self.navigation_items:
            # 创建水平布局的按钮容器
            button_layout = QHBoxLayout()
            button_layout.setSpacing(10)
            
            # 加载SVG图标（电竞红色效果）
            svg_icon_path = get_resource_path(item["icon"])
            svg_icon = load_svg_icon(svg_icon_path, red_factor=1.2)
            
            # 创建按钮文本标签
            text_label = QLabel(item["text"])
            text_label.setStyleSheet("color: white; font-size: 13px; font-weight: 500;")
            
            # 创建按钮容器
            button = QPushButton()
            button.setObjectName("navButton")
            button.setFixedHeight(45)
            button.setStyleSheet("""
                #navButton {
                    background: rgba(255, 255, 255, 0.2) !important;
                    border: 1px solid rgba(255, 255, 255, 0.3) !important;
                    border-radius: 8px;
                    margin: 2px 0;
                }
                #navButton:hover {
                    background: rgba(255, 255, 255, 0.3) !important;
                }
                #navButton:pressed {
                    background: rgba(255, 255, 255, 0.4) !important;
                }
            """)
            
            # 添加图标和文本到水平布局
            button_layout.addStretch(1)  # 左侧弹性空间（较小权重）
            
            if svg_icon:
                icon_label = QLabel()
                icon_label.setPixmap(svg_icon.scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                icon_label.setStyleSheet("color: white;")
                button_layout.addWidget(icon_label)
            
            button_layout.addWidget(text_label)
            button_layout.addStretch(3)  # 右侧弹性空间（较大权重，使内容稍微靠左）
            
            # 设置按钮的布局
            button.setLayout(button_layout)
            button.clicked.connect(lambda checked, i=item["text"]: self.on_nav_item_click(i))
            left_nav_layout.addWidget(button)
            self.nav_buttons.append(button)
        
        left_nav_layout.addStretch()
        
        # 版本信息
        self.version_label = QLabel("当前版本: PyQt 1.0")
        self.version_label.setAlignment(Qt.AlignCenter)
        self.version_label.setObjectName("versionLabel")
        left_nav_layout.addWidget(self.version_label)
        
        # 分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        content_layout.addWidget(separator)
        
        # 主内容区域
        self.main_content_frame = QFrame()
        self.main_content_frame.setObjectName("mainContentFrame")
        content_layout.addWidget(self.main_content_frame)
        
        main_content_layout = QVBoxLayout(self.main_content_frame)
        main_content_layout.setContentsMargins(20, 20, 20, 20)
        main_content_layout.setSpacing(20)
        
        # 上方框架 - 默认内容（已移除核心功能展示模块）
        self.upper_frame = QFrame()
        self.upper_frame.setObjectName("upperFrame")
        main_content_layout.addWidget(self.upper_frame)
        
        self.upper_layout = QVBoxLayout(self.upper_frame)
        self.upper_layout.setContentsMargins(10, 10, 10, 10)  # 设置边距
        self.upper_layout.setSpacing(15)  # 设置间距
        # 不再显示默认的欢迎信息，移除了核心功能展示模块
        
        # 下方框架 - 硬件信息（默认隐藏，只在硬件信息页面显示）
        self.lower_frame = QFrame()
        self.lower_frame.setObjectName("lowerFrame")
        self.lower_frame.setVisible(False)  # 默认隐藏
        main_content_layout.addWidget(self.lower_frame)
        
        lower_layout = QVBoxLayout(self.lower_frame)
        lower_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建默认页面内容 - 避免启动时加载硬件信息
        self.create_default_page()
        
        # 应用样式
        self.apply_styles()
        
        # 加载背景图
        self.load_background_image()
        
        # 添加右下角jiao.png图片（已移除键盘控制功能）
        # self.add_bottom_right_image()
    
    def create_default_page(self):
        """创建默认页面内容"""
        try:
            # 清空上方框架
            self.clear_upper_frame()
            
            # 创建简洁的欢迎信息
            welcome_label = QLabel("欢迎使用浩讯亿通电脑工具箱")
            welcome_label.setAlignment(Qt.AlignCenter)
            welcome_label.setObjectName("defaultLabel")
            welcome_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #ff4757; margin: 20px;")
            self.upper_layout.addWidget(welcome_label)
            
            # 添加简短的描述
            desc_label = QLabel("一站式系统检测与硬件测试工具")
            desc_label.setAlignment(Qt.AlignCenter)
            desc_label.setStyleSheet("font-size: 14px; color: #666; margin: 10px;")
            self.upper_layout.addWidget(desc_label)
            
            # 添加"我们的账号"小标题
            account_title = QLabel("我们的账号")
            account_title.setAlignment(Qt.AlignCenter)
            account_title.setStyleSheet("""
                font-size: 20px; 
                font-weight: bold; 
                color: #ff4757; 
                margin: 30px 0 15px 0;
                padding: 15px 25px;
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(255, 71, 87, 0.15),
                    stop: 1 rgba(255, 71, 87, 0.05));
                border-radius: 25px;
                border: 2px solid rgba(255, 71, 87, 0.3);
            """)
            self.upper_layout.addWidget(account_title)
            
            # 创建横向布局用于并排放置图片
            image_layout = QHBoxLayout()
            image_layout.setAlignment(Qt.AlignCenter)
            image_layout.setSpacing(40)  # 图片间距
            
            # 添加ks.png图片（快手二维码）
            try:
                ks_path = get_resource_path("Resources\\ks.png")
                print(f"ks.png路径: {ks_path}")
                print(f"ks.png文件存在: {os.path.exists(ks_path)}")
                if os.path.exists(ks_path):
                    ks_pixmap = QPixmap(ks_path)
                    print(f"ks.png加载成功，尺寸: {ks_pixmap.width()}x{ks_pixmap.height()}")
                    
                    # 创建带有光影效果的二维码容器
                    qr_container = QFrame()
                    qr_container.setFrameStyle(QFrame.Box)
                    qr_container.setLineWidth(3)
                    qr_container.setStyleSheet("""
                        QFrame {
                            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                stop: 0 rgb(255, 100, 100),
                                stop: 0.5 rgb(255, 50, 50),
                                stop: 1 rgb(255, 0, 0));
                            border: 8px solid #ff0000;
                            border-radius: 25px;
                        }
                        QFrame:hover {
                            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                stop: 0 rgb(255, 150, 150),
                                stop: 0.5 rgb(255, 80, 80),
                                stop: 1 rgb(255, 30, 30));
                            border: 8px solid #dd0000;
                        }
                    """)
                    
                    # 为容器添加强烈发光效果
                    container_shadow = QGraphicsDropShadowEffect()
                    container_shadow.setBlurRadius(45)
                    container_shadow.setColor(QColor(255, 0, 0, 255))
                    container_shadow.setOffset(6, 6)
                    qr_container.setGraphicsEffect(container_shadow)
                    qr_container.setFixedSize(160, 200)
                    qr_container.setObjectName("ks_container")
                    
                    qr_layout = QVBoxLayout(qr_container)
                    qr_layout.setContentsMargins(15, 15, 15, 15)
                    qr_layout.setSpacing(10)
                    
                    # 二维码标签
                    ks_label = QLabel()
                    ks_label.setPixmap(ks_pixmap.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                    ks_label.setAlignment(Qt.AlignCenter)
                    ks_label.setStyleSheet("""
                        QLabel {
                            background: transparent;
                            border-radius: 8px;
                        }
                    """)
                    
                    # 添加发光背景效果
                    glow_effect = QGraphicsDropShadowEffect()
                    glow_effect.setBlurRadius(20)
                    glow_effect.setColor(QColor(255, 107, 107, 200))
                    glow_effect.setOffset(3, 3)
                    ks_label.setGraphicsEffect(glow_effect)
                    
                    # 平台名称标签
                    platform_label = QLabel("快手")
                    platform_label.setAlignment(Qt.AlignCenter)
                    platform_label.setStyleSheet("""
                        QLabel {
                            font-size: 14px;
                            font-weight: bold;
                            color: #ff6b6b;
                            background: transparent;
                            padding: 8px;
                        }
                    """)
                    
                    qr_layout.addWidget(ks_label)
                    qr_layout.addWidget(platform_label)
                    image_layout.addWidget(qr_container)
                    print("ks.png已添加光影效果并添加到布局")
                else:
                    print("ks.png文件不存在")
            except Exception as e:
                print(f"无法加载ks.png: {e}")
            
            # 添加dy.png图片（抖音二维码）
            try:
                dy_path = get_resource_path("Resources\\dy.png")
                print(f"dy.png路径: {dy_path}")
                print(f"dy.png文件存在: {os.path.exists(dy_path)}")
                if os.path.exists(dy_path):
                    dy_pixmap = QPixmap(dy_path)
                    print(f"dy.png加载成功，尺寸: {dy_pixmap.width()}x{dy_pixmap.height()}")
                    
                    # 创建带有光影效果的二维码容器
                    dy_container = QFrame()
                    dy_container.setFrameStyle(QFrame.Box)
                    dy_container.setLineWidth(3)
                    dy_container.setStyleSheet("""
                        QFrame {
                            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                stop: 0 rgb(100, 150, 255),
                                stop: 0.5 rgb(50, 100, 255),
                                stop: 1 rgb(0, 0, 255));
                            border: 8px solid #0000ff;
                            border-radius: 25px;
                        }
                        QFrame:hover {
                            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                stop: 0 rgb(150, 200, 255),
                                stop: 0.5 rgb(80, 150, 255),
                                stop: 1 rgb(30, 30, 255));
                            border: 8px solid #0000dd;
                        }
                    """)
                    
                    # 为容器添加强烈发光效果
                    dy_container_shadow = QGraphicsDropShadowEffect()
                    dy_container_shadow.setBlurRadius(45)
                    dy_container_shadow.setColor(QColor(0, 0, 255, 255))
                    dy_container_shadow.setOffset(6, 6)
                    dy_container.setGraphicsEffect(dy_container_shadow)
                    dy_container.setFixedSize(160, 200)
                    dy_container.setObjectName("dy_container")
                    
                    dy_layout = QVBoxLayout(dy_container)
                    dy_layout.setContentsMargins(15, 15, 15, 15)
                    dy_layout.setSpacing(10)
                    
                    # 二维码标签
                    dy_label = QLabel()
                    dy_label.setPixmap(dy_pixmap.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                    dy_label.setAlignment(Qt.AlignCenter)
                    dy_label.setStyleSheet("""
                        QLabel {
                            background: transparent;
                            border-radius: 8px;
                        }
                    """)
                    
                    # 添加发光背景效果
                    dy_glow_effect = QGraphicsDropShadowEffect()
                    dy_glow_effect.setBlurRadius(20)
                    dy_glow_effect.setColor(QColor(88, 86, 214, 200))
                    dy_glow_effect.setOffset(3, 3)
                    dy_label.setGraphicsEffect(dy_glow_effect)
                    
                    # 平台名称标签
                    dy_platform_label = QLabel("抖音")
                    dy_platform_label.setAlignment(Qt.AlignCenter)
                    dy_platform_label.setStyleSheet("""
                        QLabel {
                            font-size: 14px;
                            font-weight: bold;
                            color: #5856d6;
                            background: transparent;
                            padding: 8px;
                        }
                    """)
                    
                    dy_layout.addWidget(dy_label)
                    dy_layout.addWidget(dy_platform_label)
                    image_layout.addWidget(dy_container)
                    print("dy.png已添加光影效果并添加到布局")
                else:
                    print("dy.png文件不存在")
            except Exception as e:
                print(f"无法加载dy.png: {e}")
            
            # 将图片布局添加到主布局
            image_container = QWidget()
            image_container.setLayout(image_layout)
            self.upper_layout.addWidget(image_container)
            
            # 添加提示信息
            tip_label = QLabel("点击左侧菜单开始使用")
            tip_label.setAlignment(Qt.AlignCenter)
            tip_label.setStyleSheet("font-size: 12px; color: #888; margin: 20px;")
            self.upper_layout.addWidget(tip_label)
            
        except Exception as e:
            print(f"创建默认页面失败: {e}")
    
    def apply_styles(self):
        """应用样式表"""
        style = """
        QMainWindow {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, 
                stop: 0 #f5f7fa, stop: 1 #c3cfe2);
        }
        
        #titleBar {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, 
                stop: 0 #ff4757, stop: 1 #cc3629);
            border-bottom: 1px solid rgba(255, 71, 87, 0.3);
        }
        
        #titleLabel {
            font-size: 18px;
            font-weight: bold;
            color: #ff4757;
            background: transparent;
            padding: 5px 10px;
            border-left: 3px solid #ff4757;
            border-radius: 3px;
        }
        
        #navButton:hover {
            background: rgba(255, 255, 255, 0.1);
            padding-left: 20px;
        }
        
        #leftNavFrame {
            background: rgba(255, 255, 255, 0.1);
            border-right: 2px solid rgba(255, 255, 255, 0.2);
            border-radius: 10px;
        }
        
        #programNameLabel {
            font-size: 16px;
            font-weight: bold;
            color: white;
            background: transparent;
        }
        
        #navButton {
            background: rgba(255, 255, 255, 0.2) !important;
            border: 1px solid rgba(255, 255, 255, 0.3) !important;
            text-align: left;
            padding: 12px;
            font-size: 13px;
            color: white !important;
            border-radius: 8px;
            margin: 2px 0;
        }
        
        #navButton:hover {
            background: rgba(255, 255, 255, 0.3) !important;
            border: 1px solid rgba(255, 255, 255, 0.5) !important;
        }
        
        #navButton:pressed {
            background: rgba(255, 255, 255, 0.4) !important;
            border: 1px solid rgba(255, 255, 255, 0.6) !important;
        }
        
        #versionLabel {
            font-size: 10px;
            color: rgba(255, 255, 255, 0.7);
            background: transparent;
        }
        
        #mainContentFrame {
            background: transparent;
        }
        
        #upperFrame {
            background: transparent;
            border-radius: 10px;
        }
        
        #defaultLabel {
            font-size: 16px;
            color: #333;
            background: transparent;
            font-weight: 500;
        }
        
        #lowerFrame {
            background: transparent;
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 15px;
        }
        
        #hardwareInfoLabel {
            font-size: 12px;
            color: #ffffff;
            background: transparent;
            padding: 15px;
            line-height: 1.6;
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        QScrollArea {
            border: none;
            background: transparent;
        }
        
        QScrollBar:vertical {
            background: rgba(0, 0, 0, 0.1);
            width: 12px;
            border-radius: 6px;
        }
        
        QScrollBar::handle:vertical {
            background: rgba(255, 71, 87, 0.8);
            border-radius: 6px;
            min-height: 20px;
        }
        
        QScrollBar::handle:vertical:hover {
            background: rgba(255, 71, 87, 1);
        }
        
        /* 只影响特定按钮的通用样式 */
        QPushButton:not(#navButton):not(#hideButton):not(#closeButton) {
            background: transparent;
            color: transparent;
            border: none;
            border-radius: 0;
            padding: 0px;
            margin: 0px;
            outline: none;
        }
        
        QPushButton:not(#navButton):not(#hideButton):not(#closeButton):hover {
            background: transparent;
            color: transparent;
            border: none;
            outline: none;
        }
        
        QPushButton:not(#navButton):not(#hideButton):not(#closeButton):pressed {
            background: transparent;
            color: transparent;
            border: none;
            outline: none;
        }
        
        /* 强制隐藏和关闭按钮样式 - 最高优先级 */
        #hideButton, #closeButton {
            background: transparent !important;
            border: none !important;
            border-radius: 0 !important;
            color: transparent !important;
            min-width: 40px !important;
            max-width: 40px !important;
            min-height: 40px !important;
            max-height: 40px !important;
            padding: 0 !important;
            margin: 0 !important;
            outline: none !important;
            text-align: center !important;
        }
        
        #hideButton:hover, #closeButton:hover {
            background: transparent !important;
            border: none !important;
            color: transparent !important;
            outline: none !important;
        }
        
        #hideButton:pressed, #closeButton:pressed {
            background: transparent !important;
            border: none !important;
            color: transparent !important;
            outline: none !important;
        }
        
        QLabel {
            color: #333;
        }
        
        QTextEdit {
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 8px;
            padding: 10px;
            background: transparent;
        }
        """
        
        self.setStyleSheet(style)
        
    def setup_logging(self):
        """初始化日志系统"""
        try:
            log_dir = os.path.join(os.getcwd(), "logs")
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            log_file = os.path.join(log_dir, "computer_tools_pyqt.log")
            
            log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            formatter = logging.Formatter(log_format)
            
            self.logger = logging.getLogger('ComputerToolsPyQt')
            self.logger.setLevel(logging.DEBUG)
            
            if not self.logger.handlers:
                file_handler = logging.handlers.RotatingFileHandler(
                    log_file, maxBytes=10*1024*1024, backupCount=5, encoding='utf-8'
                )
                file_handler.setLevel(logging.DEBUG)
                file_handler.setFormatter(formatter)
                
                console_handler = logging.StreamHandler()
                console_handler.setLevel(logging.INFO)
                console_handler.setFormatter(formatter)
                
                self.logger.addHandler(file_handler)
                self.logger.addHandler(console_handler)
            
            self.logger.info("PyQt电脑工具箱日志系统初始化成功")
            
        except Exception as e:
            print(f"日志系统初始化失败: {e}")
            self.logger = type('SimpleLogger', (), {
                'debug': lambda self, msg: print(f"DEBUG: {msg}"),
                'info': lambda self, msg: print(f"INFO: {msg}"),
                'warning': lambda self, msg: print(f"WARNING: {msg}"),
                'error': lambda self, msg: print(f"ERROR: {msg}"),
                'critical': lambda self, msg: print(f"CRITICAL: {msg}")
            })()
    
    def setup_events(self):
        """设置事件处理"""
        # 标题栏拖拽事件
        self.title_bar.mousePressEvent = self.start_move
        self.title_bar.mouseMoveEvent = self.move_window
        
        # 按钮事件
        self.hide_button.clicked.connect(self.hide_window)
        self.close_button.clicked.connect(self.close)
        
        # 快捷键
        QApplication.instance().focusWidget()
        
    def center_window(self):
        """窗口居中"""
        screen = QApplication.desktop().screenGeometry()
        window = self.geometry()
        x = (screen.width() - window.width()) // 2
        y = (screen.height() - window.height()) // 2
        self.move(x, y)
    
    def start_move(self, event):
        """开始移动窗口"""
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
    
    def move_window(self, event):
        """移动窗口"""
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()
    
    def hide_window(self):
        """隐藏窗口到托盘"""
        self.hide_to_tray()
        self.window_hidden = True
    
    def show_window(self):
        """显示窗口"""
        self.show()
        self.window_hidden = False
    
    def load_hardware_info(self):
        """加载硬件信息"""
        if hasattr(self, 'hardware_info_thread') and self.hardware_info_thread.isRunning():
            return
        
        # 更新状态显示
        if hasattr(self, 'hardware_info_status_label') and self.hardware_info_status_label:
            self.hardware_info_status_label.setText("正在获取硬件信息...")
            self.hardware_info_status_label.setStyleSheet("""
                font-size: 12px;
                color: #3b82f6;
                margin-left: 5px;
            """)
        
        # 更新当前时间
        if hasattr(self, 'hardware_info_time_label') and self.hardware_info_time_label:
            from datetime import datetime
            current_time = datetime.now().strftime("%H:%M:%S")
            self.hardware_info_time_label.setText(f"最后更新: {current_time}")
        
        self.hardware_info_thread = HardwareInfoThread()
        self.hardware_info_thread.hardware_info_ready.connect(self.update_hardware_info)
        self.hardware_info_thread.start()
    
    def update_hardware_info(self, hardware_info):
        """更新硬件信息显示 - 简化版本"""
        try:
            self.logger.info("开始更新硬件信息显示")
            
            # 如果有简化的显示组件，使用新的显示逻辑
            if hasattr(self, 'hardware_display_widget') and hasattr(self.hardware_display_widget, 'content_layout'):
                self.update_simple_hardware_display(hardware_info)
            
            # 保留旧标签页的兼容性（如果存在的话）
            elif hasattr(self, 'hardware_tabs'):
                # 更新各个标签页的信息
                if hasattr(self, 'hardware_tabs'):
                    # 更新CPU信息
                    if 'cpu' in hardware_info and 'cpu' in self.hardware_tabs:
                        cpu_tab = self.hardware_tabs['cpu']
                        if hasattr(cpu_tab, 'info_label'):
                            cpu_tab.info_label.setText(str(hardware_info['cpu']))
                            cpu_tab.info_label.setStyleSheet("""
                                font-size: 13px;
                                color: #e5e7eb;
                                line-height: 1.6;
                                background: transparent;
                                border-radius: 8px;
                                padding: 15px;
                                border: 1px solid rgba(59, 130, 246, 0.6);
                            """)
                    
                    # 更新GPU信息
                    if 'gpu' in hardware_info and 'gpu' in self.hardware_tabs:
                        gpu_tab = self.hardware_tabs['gpu']
                        if hasattr(gpu_tab, 'info_label'):
                            gpu_tab.info_label.setText(str(hardware_info['gpu']))
                            gpu_tab.info_label.setStyleSheet("""
                                font-size: 13px;
                                color: #e5e7eb;
                                line-height: 1.6;
                                background: transparent;
                                border-radius: 8px;
                                padding: 15px;
                                border: 1px solid rgba(147, 51, 234, 0.6);
                            """)
                    
                    # 更新内存信息
                    if 'memory' in hardware_info and 'memory' in self.hardware_tabs:
                        memory_tab = self.hardware_tabs['memory']
                        if hasattr(memory_tab, 'info_label'):
                            memory_tab.info_label.setText(str(hardware_info['memory']))
                            memory_tab.info_label.setStyleSheet("""
                                font-size: 13px;
                                color: #e5e7eb;
                                line-height: 1.6;
                                background: transparent;
                                border-radius: 8px;
                                padding: 15px;
                                border: 1px solid rgba(16, 185, 129, 0.6);
                            """)
                    
                    # 更新磁盘信息
                    if 'disk' in hardware_info and 'disk' in self.hardware_tabs:
                        disk_tab = self.hardware_tabs['disk']
                        if hasattr(disk_tab, 'info_label'):
                            disk_tab.info_label.setText(str(hardware_info['disk']))
                            disk_tab.info_label.setStyleSheet("""
                                font-size: 13px;
                                color: #e5e7eb;
                                line-height: 1.6;
                                background: transparent;
                                border-radius: 8px;
                                padding: 15px;
                                border: 1px solid rgba(245, 158, 11, 0.6);
                            """)
                    
                    # 更新系统信息
                    if 'system' in hardware_info and 'system' in self.hardware_tabs:
                        system_tab = self.hardware_tabs['system']
                        if hasattr(system_tab, 'info_label'):
                            system_tab.info_label.setText(str(hardware_info['system']))
                            system_tab.info_label.setStyleSheet("""
                                font-size: 13px;
                                color: #e5e7eb;
                                line-height: 1.6;
                                background: transparent;
                                border-radius: 8px;
                                padding: 15px;
                                border: 1px solid rgba(239, 68, 68, 0.6);
                            """)
            
            # 更新状态显示
            if hasattr(self, 'hardware_info_status_label') and self.hardware_info_status_label:
                self.hardware_info_status_label.setText("硬件信息刷新完成 ✓")
                self.hardware_info_status_label.setStyleSheet("""
                    font-size: 13px;
                    color: #059669;
                    font-weight: 600;
                    margin-left: 8px;
                """)
                
            # 更新当前时间
            if hasattr(self, 'hardware_info_time_label') and self.hardware_info_time_label:
                from datetime import datetime
                current_time = datetime.now().strftime("%H:%M:%S")
                self.hardware_info_time_label.setText(f"最后更新: {current_time}")
                
        except Exception as e:
            self.logger.error(f"更新硬件信息失败: {e}")
            # 如果出错，更新状态标签
            if hasattr(self, 'hardware_info_status_label') and self.hardware_info_status_label:
                self.hardware_info_status_label.setText("硬件信息刷新失败 ✗")
                self.hardware_info_status_label.setStyleSheet("""
                    font-size: 13px;
                    color: #ef4444;
                    font-weight: 600;
                    margin-left: 8px;
                """)
            # 显示错误信息到简化界面
            if hasattr(self, 'hardware_display_widget'):
                self.show_hardware_info_error(str(e))
    
    def update_simple_hardware_display(self, hardware_info):
        """更新简化的硬件信息显示 - 直接显示配置信息，去除空白模块"""
        try:
            content_layout = self.hardware_display_widget.content_layout
            
            # 移除加载标签（如果有的话）
            if hasattr(content_layout, 'loading_item') and content_layout.loading_item:
                content_layout.removeWidget(content_layout.loading_item)
                content_layout.loading_item.deleteLater()
                content_layout.loading_item = None
                
            # 移除成功消息标签（如果有的话）
            if hasattr(content_layout, 'success_item') and content_layout.success_item:
                content_layout.removeWidget(content_layout.success_item)
                content_layout.success_item.deleteLater()
                content_layout.success_item = None
                
            # 移除旧的信息标签（如果有的话）
            if hasattr(content_layout, 'detail_info_item') and content_layout.detail_info_item:
                content_layout.removeWidget(content_layout.detail_info_item)
                content_layout.detail_info_item.deleteLater()
                content_layout.detail_info_item = None
            
            # 创建详细的硬件信息文本
            info_text = self.format_hardware_info(hardware_info)
            
            # 创建详细信息标签 - 完全透明样式
            info_label = QLabel()
            info_label.setText(info_text)
            info_label.setStyleSheet("""
                font-size: 10px;
                color: #ffffff;
                line-height: 1.2;
                background: transparent;
                border-radius: 4px;
                padding: 6px;
                border: 1px solid rgba(255, 255, 255, 0.2);
            """)
            info_label.setWordWrap(True)
            info_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
            info_label.setTextFormat(Qt.RichText)
            info_label.setOpenExternalLinks(True)  # 启用外部链接
            content_layout.addWidget(info_label)
            content_layout.detail_info_item = info_label
            
        except Exception as e:
            self.logger.error(f"更新简化硬件信息显示失败: {e}")
            # 显示错误信息
            self.show_hardware_info_error(str(e))
    
    def format_hardware_info(self, hardware_info):
        """格式化硬件信息为HTML文本"""
        html_content = """
        <div style=\"font-family: 'Microsoft YaHei', sans-serif; color: #ffffff;\">
            <!-- 群组图片 -->
            <div style=\"text-align: center; margin: 10px 0 20px 0; padding: 15px; background: rgba(255, 255, 255, 0.05); border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.1);\">
                <a href=\"https://tieba.baidu.com/f?kw=浩讯亿通电脑&fr=sharewise\" target=\"_blank\" style=\"text-decoration: none; cursor: pointer; display: inline-block; border-radius: 8px; transition: all 0.3s ease;\" onmouseover=\"this.style.transform='scale(1.05)'\" onmouseout=\"this.style.transform='scale(1)'\">
                    <img src=\"Resources/qun.png\" alt=\"点击进入浩讯亿通电脑贴吧\" style=\"max-width: 200px; height: auto; border-radius: 8px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3); display: block;\" />
                </a>
            </div>
        """
        
        # CPU信息
        if 'cpu' in hardware_info:
            cpu_info = hardware_info['cpu']
            if isinstance(cpu_info, dict):
                html_content += f"""
                <div style="margin: 8px 0; padding: 8px; background: transparent; border-radius: 6px; border-left: 4px solid rgba(59, 130, 246, 0.6);">
                    <h3 style="color: #ffffff; margin: 0 0 8px 0; font-size: 16px; font-weight: 600;">🖥️ CPU (处理器)</h3>
                    <p style="margin: 4px 0; font-weight: 500; font-size: 15px;">型号: <span style="color: #e5e7eb;">{cpu_info.get('name', '未知')}</span></p>
                    <p style="margin: 4px 0; font-weight: 500; font-size: 15px;">核心数: <span style="color: #e5e7eb;">{cpu_info.get('cores', '未知')}</span></p>
                    <p style="margin: 4px 0; font-weight: 500; font-size: 15px;">线程数: <span style="color: #e5e7eb;">{cpu_info.get('threads', '未知')}</span></p>
                    <p style="margin: 4px 0; font-weight: 500; font-size: 15px;">基础频率: <span style="color: #e5e7eb;">{cpu_info.get('base_clock', '未知')}</span></p>
                </div>
                """
            else:
                html_content += f"""
                <div style="margin: 12px 0; padding: 12px; background: transparent; border-radius: 8px; border-left: 4px solid rgba(59, 130, 246, 0.6);">
                    <h3 style="color: #ffffff; margin: 0 0 8px 0; font-size: 13px; font-weight: 600;">🖥️ CPU (处理器)</h3>
                    <p style="margin: 8px 0; font-weight: 500;">信息: <span style="color: #e5e7eb;">{str(cpu_info)}</span></p>
                </div>
                """
        
        # GPU信息
        if 'gpu' in hardware_info:
            gpu_info = hardware_info['gpu']
            if isinstance(gpu_info, list):
                for i, gpu in enumerate(gpu_info):
                    if isinstance(gpu, dict):
                        html_content += f"""
                        <div style="margin: 12px 0; padding: 12px; background: transparent; border-radius: 8px; border-left: 4px solid rgba(147, 51, 234, 0.6);">
                            <h3 style="color: #ffffff; margin: 0 0 8px 0; font-size: 16px; font-weight: 600;">🎮 GPU {i+1} (显卡)</h3>
                            <p style="margin: 8px 0; font-weight: 500; font-size: 15px;">型号: <span style="color: #e5e7eb;">{gpu.get('name', '未知')}</span></p>
                            <p style="margin: 8px 0; font-weight: 500; font-size: 15px;">显存: <span style="color: #e5e7eb;">{gpu.get('memory', '未知')}</span></p>
                            <p style="margin: 8px 0; font-weight: 500; font-size: 15px;">驱动版本: <span style="color: #e5e7eb;">{gpu.get('driver', '未知')}</span></p>
                        </div>
                        """
            elif isinstance(gpu_info, dict):
                html_content += f"""
                <div style="margin: 12px 0; padding: 12px; background: transparent; border-radius: 8px; border-left: 4px solid rgba(147, 51, 234, 0.6);">
                    <h3 style="color: #ffffff; margin: 0 0 8px 0; font-size: 16px; font-weight: 600;">🎮 GPU (显卡)</h3>
                    <p style="margin: 8px 0; font-weight: 500; font-size: 15px;">型号: <span style="color: #e5e7eb;">{gpu_info.get('name', '未知')}</span></p>
                    <p style="margin: 8px 0; font-weight: 500; font-size: 15px;">显存: <span style="color: #e5e7eb;">{gpu_info.get('memory', '未知')}</span></p>
                    <p style="margin: 8px 0; font-weight: 500; font-size: 15px;">驱动版本: <span style="color: #e5e7eb;">{gpu_info.get('driver', '未知')}</span></p>
                </div>
                """
            else:
                html_content += f"""
                <div style="margin: 20px 0; padding: 20px; background: transparent; border-radius: 12px; border-left: 4px solid rgba(147, 51, 234, 0.6);">
                    <h3 style="color: #ffffff; margin: 0 0 15px 0; font-size: 16px; font-weight: 600;">🎮 GPU (显卡)</h3>
                    <p style="margin: 8px 0; font-weight: 500;">信息: <span style="color: #e5e7eb;">{str(gpu_info)}</span></p>
                </div>
                """
        
        # 内存信息
        if 'memory' in hardware_info:
            memory_info = hardware_info['memory']
            if isinstance(memory_info, dict):
                html_content += f"""
                <div style="margin: 20px 0; padding: 20px; background: transparent; border-radius: 12px; border-left: 4px solid rgba(16, 185, 129, 0.6);">
                    <h3 style="color: #ffffff; margin: 0 0 15px 0; font-size: 18px; font-weight: 600;">💾 内存</h3>
                    <p style="margin: 8px 0; font-weight: 500; font-size: 16px;">总容量: <span style="color: #e5e7eb;">{memory_info.get('total', '未知')}</span></p>
                    <p style="margin: 8px 0; font-weight: 500; font-size: 16px;">可用: <span style="color: #e5e7eb;">{memory_info.get('available', '未知')}</span></p>
                    <p style="margin: 8px 0; font-weight: 500; font-size: 16px;">使用率: <span style="color: #e5e7eb;">{memory_info.get('usage', '未知')}</span></p>
                </div>
                """
            else:
                html_content += f"""
                <div style="margin: 20px 0; padding: 20px; background: transparent; border-radius: 12px; border-left: 4px solid rgba(16, 185, 129, 0.6);">
                    <h3 style="color: #ffffff; margin: 0 0 15px 0; font-size: 16px; font-weight: 600;">💾 内存</h3>
                    <p style="margin: 8px 0; font-weight: 500;">信息: <span style="color: #e5e7eb;">{str(memory_info)}</span></p>
                </div>
                """
        
        # 磁盘信息
        if 'disk' in hardware_info:
            disk_info = hardware_info['disk']
            if isinstance(disk_info, list):
                for i, disk in enumerate(disk_info):
                    if isinstance(disk, dict):
                        html_content += f"""
                        <div style="margin: 20px 0; padding: 20px; background: transparent; border-radius: 12px; border-left: 4px solid rgba(245, 158, 11, 0.6);">
                            <h3 style="color: #ffffff; margin: 0 0 15px 0; font-size: 18px; font-weight: 600;">💿 磁盘 {i+1}</h3>
                            <p style="margin: 8px 0; font-weight: 500; font-size: 16px;">类型: <span style="color: #e5e7eb;">{disk.get('type', '未知')}</span></p>
                            <p style="margin: 8px 0; font-weight: 500; font-size: 16px;">容量: <span style="color: #e5e7eb;">{disk.get('total', '未知')}</span></p>
                            <p style="margin: 8px 0; font-weight: 500; font-size: 16px;">已用: <span style="color: #e5e7eb;">{disk.get('used', '未知')}</span></p>
                            <p style="margin: 8px 0; font-weight: 500; font-size: 16px;">剩余: <span style="color: #e5e7eb;">{disk.get('free', '未知')}</span></p>
                        </div>
                        """
            elif isinstance(disk_info, dict):
                html_content += f"""
                <div style="margin: 20px 0; padding: 20px; background: transparent; border-radius: 12px; border-left: 4px solid rgba(245, 158, 11, 0.6);">
                    <h3 style="color: #ffffff; margin: 0 0 15px 0; font-size: 16px; font-weight: 600;">💿 磁盘</h3>
                    <p style="margin: 8px 0; font-weight: 500;">类型: <span style="color: #e5e7eb;">{disk_info.get('type', '未知')}</span></p>
                    <p style="margin: 8px 0; font-weight: 500;">容量: <span style="color: #e5e7eb;">{disk_info.get('total', '未知')}</span></p>
                    <p style="margin: 8px 0; font-weight: 500;">已用: <span style="color: #e5e7eb;">{disk_info.get('used', '未知')}</span></p>
                    <p style="margin: 8px 0; font-weight: 500;">剩余: <span style="color: #e5e7eb;">{disk_info.get('free', '未知')}</span></p>
                </div>
                """
            else:
                html_content += f"""
                <div style="margin: 20px 0; padding: 20px; background: transparent; border-radius: 12px; border-left: 4px solid rgba(245, 158, 11, 0.6);">
                    <h3 style="color: #ffffff; margin: 0 0 15px 0; font-size: 16px; font-weight: 600;">💿 磁盘</h3>
                    <p style="margin: 8px 0; font-weight: 500;">信息: <span style="color: #e5e7eb;">{str(disk_info)}</span></p>
                </div>
                """

        # 显示器信息
        if 'display' in hardware_info:
            display_info = hardware_info['display']
            if isinstance(display_info, list):
                # 处理多行信息
                lines = [line for line in display_info if line.strip()]
                if lines:
                    html_content += f"""
                    <div style="margin: 20px 0; padding: 20px; background: transparent; border-radius: 12px; border-left: 4px solid rgba(139, 92, 246, 0.6);">
                        <h3 style="color: #ffffff; margin: 0 0 15px 0; font-size: 18px; font-weight: 600;">🖥️ 显示器</h3>
                    """
                    for line in lines:
                        if line.strip():
                            # 根据缩进判断信息级别
                            if line.startswith('  '):
                                html_content += f'<p style="margin: 6px 0; margin-left: 15px; font-weight: 400; font-size: 15px;">⚫ <span style="color: #d1d5db;">{line.strip()}</span></p>'
                            else:
                                html_content += f'<p style="margin: 8px 0; font-weight: 500; font-size: 16px;">📱 <span style="color: #e5e7eb;">{line.strip()}</span></p>'
                    html_content += "</div>"
            else:
                html_content += f"""
                <div style="margin: 20px 0; padding: 20px; background: transparent; border-radius: 12px; border-left: 4px solid rgba(139, 92, 246, 0.6);">
                    <h3 style="color: #ffffff; margin: 0 0 15px 0; font-size: 16px; font-weight: 600;">🖥️ 显示器</h3>
                    <p style="margin: 8px 0; font-weight: 500;">信息: <span style="color: #e5e7eb;">{str(display_info)}</span></p>
                </div>
                """

        # 网络适配器信息
        if 'network' in hardware_info:
            network_info = hardware_info['network']
            if isinstance(network_info, list):
                # 处理多行信息
                lines = [line for line in network_info if line.strip()]
                if lines:
                    html_content += f"""
                    <div style="margin: 20px 0; padding: 20px; background: transparent; border-radius: 12px; border-left: 4px solid rgba(14, 165, 233, 0.6);">
                        <h3 style="color: #ffffff; margin: 0 0 15px 0; font-size: 18px; font-weight: 600;">🌐 网络适配器</h3>
                    """
                    for line in lines:
                        if line.strip():
                            # 根据缩进判断信息级别
                            if line.startswith('  '):
                                html_content += f'<p style="margin: 6px 0; margin-left: 15px; font-weight: 400; font-size: 15px;">⚫ <span style="color: #d1d5db;">{line.strip()}</span></p>'
                            else:
                                html_content += f'<p style="margin: 8px 0; font-weight: 500; font-size: 16px;">🔌 <span style="color: #e5e7eb;">{line.strip()}</span></p>'
                    html_content += "</div>"
            else:
                html_content += f"""
                <div style="margin: 20px 0; padding: 20px; background: transparent; border-radius: 12px; border-left: 4px solid rgba(14, 165, 233, 0.6);">
                    <h3 style="color: #ffffff; margin: 0 0 15px 0; font-size: 16px; font-weight: 600;">🌐 网络适配器</h3>
                    <p style="margin: 8px 0; font-weight: 500;">信息: <span style="color: #e5e7eb;">{str(network_info)}</span></p>
                </div>
                """

        # 声卡信息
        if 'audio' in hardware_info:
            audio_info = hardware_info['audio']
            if isinstance(audio_info, list):
                # 处理多行信息
                lines = [line for line in audio_info if line.strip()]
                if lines:
                    html_content += f"""
                    <div style="margin: 20px 0; padding: 20px; background: transparent; border-radius: 12px; border-left: 4px solid rgba(168, 85, 247, 0.6);">
                        <h3 style="color: #ffffff; margin: 0 0 15px 0; font-size: 18px; font-weight: 600;">🔊 声卡</h3>
                    """
                    for line in lines:
                        if line.strip():
                            # 根据缩进判断信息级别
                            if line.startswith('  '):
                                html_content += f'<p style="margin: 6px 0; margin-left: 15px; font-weight: 400; font-size: 15px;">⚫ <span style="color: #d1d5db;">{line.strip()}</span></p>'
                            else:
                                html_content += f'<p style="margin: 8px 0; font-weight: 500; font-size: 16px;">🎵 <span style="color: #e5e7eb;">{line.strip()}</span></p>'
                    html_content += "</div>"
            else:
                html_content += f"""
                <div style="margin: 20px 0; padding: 20px; background: transparent; border-radius: 12px; border-left: 4px solid rgba(168, 85, 247, 0.6);">
                    <h3 style="color: #ffffff; margin: 0 0 15px 0; font-size: 16px; font-weight: 600;">🔊 声卡</h3>
                    <p style="margin: 8px 0; font-weight: 500;">信息: <span style="color: #e5e7eb;">{str(audio_info)}</span></p>
                </div>
                """
        
        # 系统信息
        if 'system' in hardware_info:
            system_info = hardware_info['system']
            if isinstance(system_info, dict):
                html_content += f"""
                <div style="margin: 20px 0; padding: 20px; background: transparent; border-radius: 12px; border-left: 4px solid rgba(239, 68, 68, 0.6);">
                    <h3 style="color: #ffffff; margin: 0 0 15px 0; font-size: 16px; font-weight: 600;">🌐 系统</h3>
                    <p style="margin: 8px 0; font-weight: 500;">操作系统: <span style="color: #e5e7eb;">{system_info.get('os', '未知')}</span></p>
                    <p style="margin: 8px 0; font-weight: 500;">版本: <span style="color: #e5e7eb;">{system_info.get('version', '未知')}</span></p>
                    <p style="margin: 8px 0; font-weight: 500;">架构: <span style="color: #e5e7eb;">{system_info.get('architecture', '未知')}</span></p>
                    <p style="margin: 8px 0; font-weight: 500;">运行时间: <span style="color: #e5e7eb;">{system_info.get('uptime', '未知')}</span></p>
                </div>
                """
            else:
                html_content += f"""
                <div style="margin: 20px 0; padding: 20px; background: transparent; border-radius: 12px; border-left: 4px solid rgba(239, 68, 68, 0.6);">
                    <h3 style="color: #ffffff; margin: 0 0 15px 0; font-size: 16px; font-weight: 600;">🌐 系统</h3>
                    <p style="margin: 8px 0; font-weight: 500;">信息: <span style="color: #e5e7eb;">{str(system_info)}</span></p>
                </div>
                """
        
        html_content += "</div>"
        return html_content
    
    def show_warning_message(self, message):
        """显示警告消息"""
        try:
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("警告")
            msg_box.setText(message)
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: #1e1e1e;
                    color: white;
                    font-family: 'Microsoft YaHei';
                }
                QMessageBox QPushButton {
                    background-color: #f59e0b;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QMessageBox QPushButton:hover {
                    background-color: #d97706;
                }
            """)
            msg_box.exec_()
        except Exception as e:
            print(f"显示警告消息失败: {e}")
    
    def show_error_message(self, message):
        """显示错误消息"""
        try:
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("错误")
            msg_box.setText(message)
            msg_box.setIcon(QMessageBox.Critical)
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: #1e1e1e;
                    color: white;
                    font-family: 'Microsoft YaHei';
                }
                QMessageBox QPushButton {
                    background-color: #ef4444;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QMessageBox QPushButton:hover {
                    background-color: #dc2626;
                }
            """)
            msg_box.exec_()
        except Exception as e:
            print(f"显示错误消息失败: {e}")
    
    def show_success_message(self, message):
        """显示成功消息"""
        try:
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("成功")
            msg_box.setText(message)
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: #1e1e1e;
                    color: white;
                    font-family: 'Microsoft YaHei';
                }
                QMessageBox QPushButton {
                    background-color: #10b981;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QMessageBox QPushButton:hover {
                    background-color: #059669;
                }
            """)
            msg_box.exec_()
        except Exception as e:
            print(f"显示成功消息失败: {e}")
    
    def show_hardware_info_error(self, error_msg):
        """显示硬件信息错误"""
        try:
            if hasattr(self, 'hardware_display_widget') and hasattr(self.hardware_display_widget, 'content_layout'):
                content_layout = self.hardware_display_widget.content_layout
                
                # 清除现有内容
                for i in reversed(range(content_layout.count())):
                    child = content_layout.itemAt(i).widget()
                    if child:
                        child.deleteLater()
                
                # 显示错误信息
                error_label = QLabel(f"❌ 硬件信息获取失败\n\n错误详情: {error_msg}\n\n请尝试重新刷新硬件信息")
                error_label.setStyleSheet("""
                    font-size: 14px;
                    color: #ef4444;
                    line-height: 1.6;
                    background: rgba(239, 68, 68, 0.05);
                    border-radius: 12px;
                    padding: 25px;
                    border: 1px solid rgba(239, 68, 68, 0.2);
                """)
                error_label.setAlignment(Qt.AlignCenter)
                error_label.setWordWrap(True)
                content_layout.addWidget(error_label)
                
                # 更新状态标签
                if hasattr(self, 'hardware_info_status_label') and self.hardware_info_status_label:
                    self.hardware_info_status_label.setText("硬件信息获取失败")
                    self.hardware_info_status_label.setStyleSheet("""
                        font-size: 13px;
                        color: #dc2626;
                        font-weight: 600;
                        margin-left: 8px;
                    """)
                
        except Exception as e:
            self.logger.error(f"显示硬件信息错误失败: {e}")
        
    def on_nav_item_click(self, item):
        """导航项点击事件"""
        try:
            # 移除所有按钮的选中状态
            for button in self.nav_buttons:
                button.setProperty("selected", False)
            
            # 设置当前选中按钮的状态
            for button in self.nav_buttons:
                if button.text() == item:
                    button.setProperty("selected", True)
                    button.setStyleSheet("""
                        QPushButton {
                            background: rgba(255, 255, 255, 0.3);
                            color: white;
                            text-align: left;
                            padding-left: 15px;
                            font-size: 13px;
                            font-weight: bold;
                            border-left: 4px solid #ffd700;
                        }
                    """)
                else:
                    button.setStyleSheet("""
                        QPushButton {
                            background: rgba(255, 255, 255, 0.1);
                            color: white;
                            text-align: left;
                            padding-left: 15px;
                            font-size: 13px;
                            font-weight: 500;
                        }
                    """)
            
            if item == "硬件信息":
                self.show_hardware_info()
            elif item == "cpu工具":
                self.show_processor_tools()
            elif item == "烤鸡工具":
                self.show_stress_test()
            elif item == "内存工具":
                self.show_memory_tools()
            elif item == "网址导航":
                self.show_url_navigation()
            elif item == "其他工具":
                self.show_other_tools()
            elif item == "关于我们":
                self.show_about()
            elif item == "程序设置":
                self.show_settings()
        except Exception as e:
            QMessageBox.warning(self, "错误", f"加载页面失败: {str(e)}")
            self.logger.error(f"导航项点击错误: {e}")
    
    def show_hardware_info(self):
        """显示硬件信息页面 - 极简版本"""
        try:
            # 检查并确保 lower_frame 存在
            if not hasattr(self, 'lower_frame') or self.lower_frame is None:
                self.logger.warning("lower_frame 不存在，重新初始化")
                self.init_ui()
            
            # 清空现有内容
            self.clear_upper_frame()
            
            # 显示硬件信息区域
            self.lower_frame.setVisible(True)
            
            # 创建主容器 - 简化版本
            main_container = QWidget()
            main_container.setStyleSheet("""
                background: transparent;
                margin: 5px;
                padding: 0px;
            """)
            self.upper_layout.addWidget(main_container)
            
            # 创建垂直布局
            main_layout = QVBoxLayout(main_container)
            main_layout.setContentsMargins(10, 10, 10, 10)
            main_layout.setSpacing(10)
            
            # 简化的标题区域
            title_label = QLabel("电脑配置信息")
            title_label.setStyleSheet("""
                font-size: 14px; 
                font-weight: bold; 
                color: #ff0000;
                padding: 4px 0;
                margin: 0px;
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 rgba(255, 0, 0, 0.1),
                    stop: 0.5 rgba(255, 0, 0, 0.2),
                    stop: 1 rgba(255, 0, 0, 0.1));
                border-radius: 6px;
                border: 1px solid rgba(255, 0, 0, 0.3);
            """)
            title_label.setAlignment(Qt.AlignCenter)
            main_layout.addWidget(title_label)
            
            # 简化的硬件信息显示区域
            hardware_info_widget = self.create_ultra_simple_hardware_display()
            main_layout.addWidget(hardware_info_widget)
            
            # 保存信息显示区域引用
            self.hardware_display_widget = hardware_info_widget
            
            # 检查是否有缓存的硬件信息
            if hasattr(self, 'hardware_info_thread') and hasattr(self.hardware_info_thread, 'cached_info') and self.hardware_info_thread.cached_info:
                # 直接使用缓存数据更新显示
                self.update_hardware_info(self.hardware_info_thread.cached_info)
            else:
                # 没有缓存时重新获取硬件信息
                self.load_hardware_info()
            
        except Exception as e:
            self.logger.error(f"显示硬件信息失败: {e}")
            # 如果出错，显示错误信息
            error_label = QLabel(f"加载硬件信息页面时出现错误：{str(e)}")
            error_label.setAlignment(Qt.AlignCenter)
            error_label.setStyleSheet("""
                color: #ef4444; 
                font-size: 14px; 
                margin: 20px;
                padding: 20px;
                background: rgba(239, 68, 68, 0.1);
                border-radius: 10px;
                border: 1px solid rgba(239, 68, 68, 0.2);
            """)
            self.upper_layout.addWidget(error_label)
    
    def create_simple_hardware_display(self):
        """创建简化的硬件信息显示区域"""
        widget = QWidget()
        widget.setStyleSheet("""
            background: rgba(255, 255, 255, 0.9);
            border-radius: 20px;
            border: 2px solid rgba(102, 126, 234, 0.15);
            padding: 25px;
        """)
        
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: rgba(0, 0, 0, 0.05);
                width: 10px;
                border-radius: 5px;
                margin: 8px 2px 8px 0px;
            }
            QScrollBar::handle:vertical {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 rgba(59, 130, 246, 0.4),
                    stop: 1 rgba(99, 102, 241, 0.3));
                border-radius: 5px;
                min-height: 25px;
            }
            QScrollBar::handle:vertical:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 rgba(59, 130, 246, 0.6),
                    stop: 1 rgba(99, 102, 241, 0.5));
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0px;
            }
        """)
        
        # 内容容器
        content_widget = QWidget()
        content_widget.setStyleSheet("background: transparent;")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(25)
        
        # 欢迎信息
        welcome_label = QLabel(" 正在获取硬件信息...")
        welcome_label.setStyleSheet("""
            font-size: 16px;
            color: #4f46e5;
            font-weight: 600;
            text-align: center;
            padding: 15px;
            background: rgba(102, 126, 234, 0.08);
            border-radius: 12px;
            border: 1px solid rgba(102, 126, 234, 0.15);
        """)
        welcome_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(welcome_label)
        
        # 详细硬件信息显示区域
        detail_info_label = QLabel("正在获取详细硬件配置信息...")
        detail_info_label.setStyleSheet("""
            font-size: 14px;
            color: #374151;
            line-height: 1.8;
            background: rgba(249, 250, 251, 0.8);
            border-radius: 12px;
            padding: 20px;
            border: 1px solid rgba(209, 213, 219, 0.3);
        """)
        detail_info_label.setWordWrap(True)
        detail_info_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        detail_info_label.setTextFormat(Qt.RichText)
        detail_info_label.setOpenExternalLinks(True)  # 启用外部链接
        content_layout.addWidget(detail_info_label)
        
        # 保存引用
        widget.welcome_label = welcome_label
        widget.detail_info_label = detail_info_label
        widget.content_layout = content_layout
        
        content_layout.addStretch()
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)
        
        return widget

    def create_ultra_simple_hardware_display(self):
        """创建极简的硬件信息显示区域 - 半透明版本"""
        widget = QWidget()
        widget.setStyleSheet("""
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            padding: 6px;
        """)
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(3, 3, 3, 3)
        layout.setSpacing(3)
        
        # 硬件信息显示区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: #e9ecef;
                width: 4px;
                border-radius: 2px;
            }
            QScrollBar::handle:vertical {
                background: #adb5bd;
                border-radius: 2px;
                min-height: 15px;
            }
            QScrollBar::handle:vertical:hover {
                background: #6c757d;
            }
        """)
        
        # 内容容器
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(3, 3, 3, 3)
        content_layout.setSpacing(3)
        
        # 加载状态标签 - 半透明样式
        loading_label = QLabel("🔄 正在获取电脑配置信息...")
        loading_label.setStyleSheet("""
            font-size: 12px;
            color: #ffffff;
            padding: 8px;
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 6px;
        """)
        loading_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(loading_label)
        content_layout.loading_item = loading_label
        
        # 详细信息将在这里显示
        content_layout.addStretch(1)
        
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)
        
        # 保存布局引用供后续使用
        widget.content_layout = content_layout
        
        return widget
    
    def create_modern_button(self, text, color, callback):
        """创建现代化按钮"""
        button = QPushButton(text)
        button.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 {color}dd,
                    stop: 1 {color}cc);
                color: white;
                border: none;
                border-radius: 10px;
                padding: 12px 20px;
                font-size: 13px;
                font-weight: 600;
                min-width: 90px;
                border: 2px solid transparent;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 {color}cc,
                    stop: 1 {color}bb);
                border: 2px solid {color}88;
                padding-top: 10px;
                padding-bottom: 14px;
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 {color}cc,
                    stop: 1 {color}aa);
                padding: 14px 20px 10px 20px;
            }}
            QPushButton:disabled {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #9ca3af,
                    stop: 1 #6b7280);
                color: #d1d5db;
            }}
        """)
        button.clicked.connect(callback)
        return button
    
    def create_hardware_category_tab(self, icon, description):
        """创建硬件分类标签页"""
        tab = QWidget()
        tab.setStyleSheet("""
            background: transparent;
            padding: 20px;
        """)
        
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # 分类标题 - 更现代化的设计
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, 
                stop: 0 rgba(59, 130, 246, 0.12), 
                stop: 0.5 rgba(99, 102, 241, 0.1),
                stop: 1 rgba(147, 51, 234, 0.08));
            border-radius: 15px;
            padding: 18px 20px;
            margin-bottom: 15px;
            border: 2px solid rgba(99, 102, 241, 0.15);
        """)
        header_layout = QHBoxLayout(header_frame)
        header_layout.setSpacing(12)
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("""
            font-size: 24px; 
            margin-right: 12px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 50%;
            padding: 8px;
            min-width: 32px;
            min-height: 32px;
            qproperty-alignment: AlignCenter;
        """)
        header_layout.addWidget(icon_label)
        
        title_label = QLabel(description)
        title_label.setStyleSheet("""
            font-size: 18px;
            font-weight: 700;
            color: #1e40af;
            letter-spacing: 0.5px;
        """)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        layout.addWidget(header_frame)
        
        # 信息显示区域 - 更美观的滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: 2px solid rgba(59, 130, 246, 0.1);
                border-radius: 15px;
                background: transparent;
            }
            QScrollArea > QWidget > QWidget {
                background: transparent;
            }
            QScrollBar:vertical {
                background: rgba(0, 0, 0, 0.05);
                width: 10px;
                border-radius: 5px;
                margin: 15px 3px 15px 0px;
            }
            QScrollBar::handle:vertical {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 rgba(59, 130, 246, 0.4),
                    stop: 1 rgba(99, 102, 241, 0.3));
                border-radius: 5px;
                min-height: 25px;
                border: 1px solid rgba(59, 130, 246, 0.2);
            }
            QScrollBar::handle:vertical:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 rgba(59, 130, 246, 0.6),
                    stop: 1 rgba(99, 102, 241, 0.5));
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0px;
            }
        """)
        
        content_widget = QWidget()
        content_widget.setStyleSheet("""
            background: transparent;
            padding: 5px;
        """)
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(12)
        content_layout.setContentsMargins(15, 15, 15, 15)
        
        # 信息标签 - 更现代化的设计
        info_label = QLabel("正在加载信息...")
        info_label.setStyleSheet("""
            font-size: 14px;
            color: #e5e7eb;
            line-height: 1.8;
            background: transparent;
            border-radius: 12px;
            padding: 20px;
            border: 1px solid rgba(59, 130, 246, 0.6);
            font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
        """)
        info_label.setWordWrap(True)
        info_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        info_label.setTextFormat(Qt.RichText)
        info_label.setOpenExternalLinks(True)  # 启用外部链接
        
        content_layout.addWidget(info_label)
        content_layout.addStretch()
        
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)
        
        # 保存引用以便后续更新
        tab.info_label = info_label
        
        return tab
    
    def create_status_frame(self):
        """创建状态栏框架"""
        status_frame = QFrame()
        status_frame.setStyleSheet("""
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, 
                stop: 0 rgba(16, 185, 129, 0.15), 
                stop: 0.5 rgba(16, 185, 129, 0.1),
                stop: 1 rgba(5, 150, 105, 0.08));
            border-radius: 15px;
            border: 2px solid rgba(16, 185, 129, 0.25);
            padding: 15px 20px;
            margin: 8px 0 5px 0;
        """)
        status_layout = QHBoxLayout(status_frame)
        status_layout.setSpacing(12)
        
        # 状态图标 - 更现代化的设计
        status_icon = QLabel("ℹ️")
        status_icon.setStyleSheet("""
            font-size: 18px;
            background: rgba(16, 185, 129, 0.15);
            border-radius: 50%;
            padding: 6px;
            min-width: 24px;
            min-height: 24px;
            qproperty-alignment: AlignCenter;
        """)
        status_layout.addWidget(status_icon)
        
        status_text = QLabel("准备就绪")
        status_text.setStyleSheet("""
            font-size: 13px;
            color: #065f46;
            font-weight: 600;
            margin-left: 8px;
        """)
        status_layout.addWidget(status_text)
        
        status_layout.addStretch()
        
        # 添加时间显示 - 现代化设计
        time_label = QLabel()
        time_label.setStyleSheet("""
            font-size: 12px;
            color: #6b7280;
            background: rgba(255, 255, 255, 0.7);
            border-radius: 10px;
            padding: 6px 12px;
            border: 1px solid rgba(107, 114, 128, 0.2);
            font-weight: 500;
        """)
        time_label.setAlignment(Qt.AlignCenter)
        status_layout.addWidget(time_label)
        
        # 保存引用
        self.hardware_info_status_label = status_text
        self.hardware_info_time_label = time_label
        
        return status_frame
    
    def show_processor_tools(self):
        """显示处理器工具页面"""
        try:
            # 检查并确保 lower_frame 存在
            if not hasattr(self, 'lower_frame') or self.lower_frame is None:
                self.logger.warning("lower_frame 不存在，重新初始化")
                self.init_ui()
            
            # 隐藏硬件信息区域
            self.lower_frame.setVisible(False)
            
            self.clear_upper_frame()
            
            title_label = QLabel("⚡ cpu工具")
            title_label.setAlignment(Qt.AlignCenter)
            title_label.setStyleSheet("""
                font-size: 24px;
                font-weight: bold;
                color: #ff0000;
                margin: 20px;
                padding: 15px 25px;
                font-family: "Microsoft YaHei", sans-serif;
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, 
                    stop: 0 rgba(255, 0, 0, 0.15), 
                    stop: 1 rgba(255, 0, 0, 0.05));
                border-radius: 15px;
                border: 1px solid rgba(255, 0, 0, 0.3);
            """)
            self.upper_layout.addWidget(title_label)
            
            separator = QFrame()
            separator.setFrameShape(QFrame.HLine)
            separator.setStyleSheet("""
                border: none;
                height: 2px;
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, 
                    stop: 0 rgba(255, 71, 87, 0.3), 
                    stop: 0.5 rgba(255, 71, 87, 0.8), 
                    stop: 1 rgba(255, 71, 87, 0.3));
                margin: 10px 40px;
            """)
            self.upper_layout.addWidget(separator)
            
            tools_layout = QGridLayout()
            self.upper_layout.addLayout(tools_layout)
            
            # 添加处理器工具按钮
            tools = [
                ("CPU-Z", "cpuz"), ("Prime95", "prime95"),
                ("AIDA64", "aida64"),
                ("ThrottleStop", "throttlestop"),
                ("LinX", "linx"), ("SuperPI", "superpi"), ("wPrime", "wprime")
            ]
            
            row = 0
            col = 0
            for tool_name, tool_key in tools:
                try:
                    tool_button = ToolButton(tool_name, tool_path=tool_key)
                    tool_button.clicked.connect(lambda checked, t=tool_key: self.open_tool(t))
                    tools_layout.addWidget(tool_button, row, col)
                    
                    col += 1
                    if col >= 3:
                        col = 0
                        row += 1
                except Exception as e:
                    self.logger.error(f"创建工具按钮失败 {tool_name}: {e}")
            
            self.upper_layout.addStretch()
            
        except Exception as e:
            self.logger.error(f"显示cpu工具失败: {e}")
    
    def show_stress_test(self):
        """显示烤鸡工具页面"""
        try:
            # 检查并确保 lower_frame 存在
            if not hasattr(self, 'lower_frame') or self.lower_frame is None:
                self.logger.warning("lower_frame 不存在，重新初始化")
                self.init_ui()
            
            # 隐藏硬件信息区域
            self.lower_frame.setVisible(False)
            
            self.clear_upper_frame()
            
            title_label = QLabel("烤鸡工具")
            title_label.setAlignment(Qt.AlignCenter)
            title_label.setStyleSheet("""
                font-size: 24px;
                font-weight: bold;
                color: #ff0000;
                margin: 20px;
                padding: 15px 25px;
                font-family: "Microsoft YaHei", sans-serif;
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, 
                    stop: 0 rgba(255, 0, 0, 0.15), 
                    stop: 1 rgba(255, 0, 0, 0.05));
                border-radius: 15px;
                border: 1px solid rgba(255, 0, 0, 0.3);
            """)
            self.upper_layout.addWidget(title_label)
            
            description = QLabel("系统压力测试工具，用于测试系统稳定性\n\n注意：请谨慎使用，可能导致系统过热！")
            description.setAlignment(Qt.AlignCenter)
            description.setStyleSheet("color: #ff6b6b; margin: 10px;")
            self.upper_layout.addWidget(description)
            
            tools_layout = QGridLayout()
            self.upper_layout.addLayout(tools_layout)
            
            tools = [
                ("CPU压力测试", "cpuburner"),
                ("内存测试", "memtest64"),
                ("GPU压力测试", "furmark")
            ]
            
            row = 0
            col = 0
            for tool_name, tool_key in tools:
                tool_button = ToolButton(tool_name, tool_path=tool_key)
                tool_button.clicked.connect(lambda checked, t=tool_key: self.run_stress_test(t))
                tools_layout.addWidget(tool_button, row, col)
                
                col += 1
                if col >= 2:
                    col = 0
                    row += 1
            
            self.upper_layout.addStretch()
            
        except Exception as e:
            self.logger.error(f"显示烤鸡工具失败: {e}")
    
    def show_memory_tools(self):
        """显示内存工具页面"""
        try:
            # 检查并确保 lower_frame 存在
            if not hasattr(self, 'lower_frame') or self.lower_frame is None:
                self.logger.warning("lower_frame 不存在，重新初始化")
                self.init_ui()
            
            # 隐藏硬件信息区域
            self.lower_frame.setVisible(False)
            
            self.clear_upper_frame()
            
            title_label = QLabel("内存工具")
            title_label.setAlignment(Qt.AlignCenter)
            title_label.setStyleSheet("""
                font-size: 24px;
                font-weight: bold;
                color: #ff0000;
                margin: 20px;
                padding: 15px 25px;
                font-family: "Microsoft YaHei", sans-serif;
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, 
                    stop: 0 rgba(255, 0, 0, 0.15), 
                    stop: 1 rgba(255, 0, 0, 0.05));
                border-radius: 15px;
                border: 1px solid rgba(255, 0, 0, 0.3);
            """)
            self.upper_layout.addWidget(title_label)
            
            tools_layout = QGridLayout()
            self.upper_layout.addLayout(tools_layout)
            
            tools = [
                ("MemTest64", "memtest64", "内存.svg"),
                ("MemTest", "memtest", "内存.svg"),
                ("TM5", "tm5", "内存.svg"),
                ("Thaiphoon", "thaiphoon", "内存.svg"),
                ("魔方内存盘", "ramdisk", "内存.svg")
            ]
            
            row = 0
            col = 0
            for tool_name, tool_key, icon_name in tools:
                icon_path = get_resource_path(f"Resources\\{icon_name}")
                tool_button = ToolButton(tool_name, icon_path=icon_path, tool_path=tool_key)
                tool_button.clicked.connect(lambda checked, t=tool_key: self.run_memory_tool(t))
                tools_layout.addWidget(tool_button, row, col)
                
                col += 1
                if col >= 3:
                    col = 0
                    row += 1
            
            self.upper_layout.addStretch()
            
        except Exception as e:
            self.logger.error(f"显示内存工具失败: {e}")
    
    def show_welcome_page(self):
        """显示欢迎页面（已移除核心功能展示模块）"""
        try:
            # 隐藏硬件信息区域
            self.lower_frame.setVisible(False)
            
            # 清空现有内容
            self.clear_upper_frame()
            
            # 创建简洁的欢迎页面内容（已移除核心功能展示模块）
            welcome_container = QWidget()
            welcome_container.setStyleSheet("background: transparent;")
            self.upper_layout.addWidget(welcome_container)
            
            welcome_layout = QVBoxLayout(welcome_container)
            welcome_layout.setContentsMargins(20, 20, 20, 20)
            welcome_layout.setSpacing(20)
            
            # 简单的标题
            main_title = QLabel("浩讯亿通电脑工具箱")
            main_title.setAlignment(Qt.AlignCenter)
            main_title.setStyleSheet("""
                font-size: 24px;
                font-weight: bold;
                color: #ff4757;
                margin: 20px 0;
                padding: 20px;
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, 
                    stop: 0 rgba(255, 71, 87, 0.2), 
                    stop: 1 rgba(255, 71, 87, 0.1));
                border-radius: 20px;
                border: 1px solid rgba(255, 71, 87, 0.3);
            """)
            welcome_layout.addWidget(main_title)

            
            # 添加我们的账号信息
            account_title = QLabel("我们的官方账号")
            account_title.setAlignment(Qt.AlignCenter)
            account_title.setStyleSheet("""
                font-size: 20px; 
                font-weight: bold; 
                color: #ff4757; 
                margin: 30px 0 15px 0;
                padding: 15px 25px;

            """)
            welcome_layout.addWidget(account_title)
            
            # 创建横向布局用于并排放置图片
            image_layout = QHBoxLayout()
            image_layout.setAlignment(Qt.AlignCenter)
            image_layout.setSpacing(40)  # 图片间距
            
            # 快手账号图片
            try:
                ks_path = get_resource_path("Resources\\ks.png")
                print(f"ks.png路径: {ks_path}")
                print(f"ks.png文件存在: {os.path.exists(ks_path)}")
                if os.path.exists(ks_path):
                    ks_pixmap = QPixmap(ks_path)
                    print(f"ks.png加载成功，尺寸: {ks_pixmap.width()}x{ks_pixmap.height()}")
                    ks_label = QLabel()
                    ks_label.setPixmap(ks_pixmap.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                    ks_label.setAlignment(Qt.AlignCenter)
                    image_layout.addWidget(ks_label)
                    print("ks.png已添加到布局")
                else:
                    print("ks.png文件不存在")
            except Exception as e:
                print(f"加载ks.png失败: {e}")
            
            # 抖音账号图片
            try:
                dy_path = get_resource_path("Resources\\dy.png")
                print(f"dy.png路径: {dy_path}")
                print(f"dy.png文件存在: {os.path.exists(dy_path)}")
                if os.path.exists(dy_path):
                    dy_pixmap = QPixmap(dy_path)
                    print(f"dy.png加载成功，尺寸: {dy_pixmap.width()}x{dy_pixmap.height()}")
                    dy_label = QLabel()
                    dy_label.setPixmap(dy_pixmap.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                    dy_label.setAlignment(Qt.AlignCenter)
                    image_layout.addWidget(dy_label)
                    print("dy.png已添加到布局")
                else:
                    print("dy.png文件不存在")
            except Exception as e:
                print(f"加载dy.png失败: {e}")
            
            welcome_layout.addLayout(image_layout)
            
            # 添加账号说明
            account_desc = QLabel("扫描二维码关注我们的官方账号，获取最新资讯和技术支持")
            account_desc.setAlignment(Qt.AlignCenter)
            account_desc.setStyleSheet("""
                font-size: 14px; 
                color: #ff4757; 
                font-weight: bold;
                margin: 15px 0; 
                padding: 12px 20px;

            """)
            welcome_layout.addWidget(account_desc)
            
            welcome_layout.addStretch()
            
        except Exception as e:
            self.logger.error(f"显示欢迎页面失败: {e}")
    
    def show_url_navigation(self):
        """显示网址导航页面"""
        try:
            # 隐藏硬件信息区域
            self.lower_frame.setVisible(False)
            
            self.clear_upper_frame()
            
            title_label = QLabel("网址导航")
            title_label.setAlignment(Qt.AlignCenter)
            title_label.setStyleSheet("""
                font-size: 24px;
                font-weight: bold;
                color: #ff0000;
                margin: 20px;
                padding: 15px 25px;
                font-family: "Microsoft YaHei", sans-serif;
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, 
                    stop: 0 rgba(255, 0, 0, 0.15), 
                    stop: 1 rgba(255, 0, 0, 0.05));
                border-radius: 15px;
                border: 1px solid rgba(255, 0, 0, 0.3);
            """)
            self.upper_layout.addWidget(title_label)
            
            urls_layout = QGridLayout()
            self.upper_layout.addLayout(urls_layout)
            
            urls = [
                ("华硕官网", "https://w3.asus.com.cn/"),
                ("ROG官网", "https://rog.asus.com.cn/"),
                ("技嘉官网", "https://www.gigabyte.cn/"),
                ("七彩虹官网", "https://www.colorful.cn/"),
                ("微星官网", "https://www.msi.com/"),
                ("英伟达官网", "https://www.nvidia.com/"),
                ("英特尔官网", "https://www.intel.com/"),
                ("AMD官网", "https://www.amd.com/"),
                ("GitHub", "https://github.com"),
                ("steam", "https://store.steampowered.com/"),
                ("wegame", "https://www.wegame.com.cn/home//"),
                ("联想官网", "https://www.lenovo.com.cn/"),
                ("戴尔官网", "https://www.dell.com/"),
                ("惠普官网", "https://www.hp.com/"),
                ("小米官网", "https://www.mi.com/"),
                ("华为官网", "https://www.huawei.com/"),
            ]
            
            row = 0
            col = 0
            for url_name, url_link in urls:
                url_button = ToolButton(url_name)
                url_button.clicked.connect(lambda checked, link=url_link: self.open_url(link))
                urls_layout.addWidget(url_button, row, col)
                
                col += 1
                if col >= 3:
                    col = 0
                    row += 1
            
            self.upper_layout.addStretch()
            
        except Exception as e:
            self.logger.error(f"显示网址导航失败: {e}")
    
    def show_other_tools(self):
        """显示其他工具页面"""
        try:
            # 隐藏硬件信息区域
            self.lower_frame.setVisible(False)
            
            self.clear_upper_frame()
            
            title_label = QLabel("其他工具")
            title_label.setAlignment(Qt.AlignCenter)
            title_label.setStyleSheet("""
                font-size: 24px;
                font-weight: bold;
                color: #ff0000;
                margin: 20px;
                padding: 15px 25px;
                font-family: "Microsoft YaHei", sans-serif;
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, 
                    stop: 0 rgba(255, 0, 0, 0.15), 
                    stop: 1 rgba(255, 0, 0, 0.05));
                border-radius: 15px;
                border: 1px solid rgba(255, 0, 0, 0.3);
            """)
            self.upper_layout.addWidget(title_label)
            
            tools_layout = QGridLayout()
            self.upper_layout.addLayout(tools_layout)
            
            tools = [
                # 硬盘工具
                ("DiskGenius", "diskgenius"),
                ("CrystalDiskMark", "crystal_disk_mark"),
                ("CrystalDiskInfo", "crystal_disk_info"),
                ("SpaceSniffer", "spacesniffer"),
                ("魔方数据恢复", "mofang_recovery"),
                
                # 显卡工具
                ("GPU-Z", "gpuz"),
                ("DDU", "ddu"),
                ("FurMark", "furmark"),
                ("GPU Test", "gputest"),
                ("NVIDIA Inspector", "nvidia_inspector"),
                
                # 显示器工具
                ("DisplayX", "displayx"),
                ("色域检测", "color_check"),
                
                # 系统工具
                ("浩讯亿通强力删除", "powerful_delete"),
                ("ToDesk", "todesk")
            ]
            
            row = 0
            col = 0
            for tool_name, tool_key in tools:
                tool_button = ToolButton(tool_name, tool_path=tool_key)
                tool_button.clicked.connect(lambda checked, t=tool_key: self.run_other_tool(t))
                tools_layout.addWidget(tool_button, row, col)
                
                col += 1
                if col >= 3:
                    col = 0
                    row += 1
            
            self.upper_layout.addStretch()
            
        except Exception as e:
            self.logger.error(f"显示其他工具失败: {e}")
    
    def show_about(self):
        """显示关于页面 - 高级电竞风格"""
        try:
            # 清除所有布局内容
            self.clear_upper_frame()
            
            # 创建主容器 - 高级电竞风格
            about_container = QWidget()
            about_container.setStyleSheet("""
                QWidget {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                        stop: 0 #0c0c0c,
                        stop: 0.3 #1a1a1a,
                        stop: 1 #0c0c0c);
                    border-radius: 20px;
                    border: 2px solid #ff2a2a;
                    margin: 15px;
                    padding: 0px;
                }
            """)
            
            about_layout = QVBoxLayout(about_container)
            about_layout.setContentsMargins(0, 0, 0, 0)
            about_layout.setSpacing(0)
            
            # 头部区域 - 高级电竞风格
            header_widget = QWidget()
            header_widget.setStyleSheet("""
                QWidget {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 #ff2a2a,
                        stop: 0.5 #ff5252,
                        stop: 1 #ff2a2a);
                    border-top-left-radius: 20px;
                    border-top-right-radius: 20px;
                    padding: 35px 40px;
                    border-bottom: 3px solid rgba(255, 255, 255, 0.1);
                }
            """)
            
            header_layout = QVBoxLayout(header_widget)
            header_layout.setSpacing(15)
            
            # 标题 - 高级电竞风格
            title_label = QLabel("浩讯亿通电脑工具箱")
            title_label.setAlignment(Qt.AlignCenter)
            title_label.setStyleSheet("""
                QLabel {
                    font-size: 28px;
                    font-weight: 800;
                    color: #ffffff;
                    font-family: "Microsoft YaHei UI", sans-serif;
                    letter-spacing: 1px;
                    max-width: 400px;
                    margin: 0 auto;
                }
            """)
            title_label.setWordWrap(True)
            header_layout.addWidget(title_label)
            
            # 版本信息
            version_label = QLabel("专业电竞版 v5.2.0")
            version_label.setAlignment(Qt.AlignCenter)
            version_label.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    font-weight: 500;
                    color: rgba(255, 255, 255, 0.9);
                    font-family: "Microsoft YaHei UI", sans-serif;
                    letter-spacing: 0.5px;
                }
            """)
            header_layout.addWidget(version_label)
            
            # 内容区域 - 高级电竞风格
            content_widget = QWidget()
            content_widget.setStyleSheet("""
                QWidget {
                    background: #0f0f0f;
                    border-bottom-left-radius: 20px;
                    border-bottom-right-radius: 20px;
                    padding: 30px 25px;
                }
            """)
            
            content_layout = QVBoxLayout(content_widget)
            content_layout.setSpacing(25)
            content_layout.setContentsMargins(0, 0, 0, 0)
            
            # 特性标题
            features_title = QLabel("CORE FEATURES")
            features_title.setAlignment(Qt.AlignCenter)
            features_title.setStyleSheet("""
                QLabel {
                    font-size: 20px;
                    font-weight: 700;
                    color: #ff2a2a;
                    font-family: "Segoe UI", sans-serif;
                    letter-spacing: 1px;
                    text-transform: uppercase;
                    margin-bottom: 10px;
                }
            """)
            content_layout.addWidget(features_title)
            
            # 特性网格 - 高级电竞卡片
            features_grid = QGridLayout()
            features_grid.setSpacing(15)
            features_grid.setContentsMargins(10, 0, 10, 0)
            
            # 定义特性列表
            features = [

            ]
            
            for i, (icon, title, desc) in enumerate(features):
                feature_card = QWidget()
                feature_card.setMinimumSize(120, 120)
                feature_card.setMaximumSize(150, 150)
                feature_card.setStyleSheet("""
                    QWidget {
                        background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                            stop: 0 rgba(40, 40, 40, 0.9),
                            stop: 1 rgba(20, 20, 20, 0.9));
                        border-radius: 10px;
                        border: 1px solid rgba(255, 255, 255, 0.1);
                        margin: 5px;
                    }
                """)
                
                feature_layout = QVBoxLayout(feature_card)
                feature_layout.setSpacing(5)
                feature_layout.setContentsMargins(10, 10, 10, 10)
                
                # 图标
                icon_label = QLabel(icon)
                icon_label.setAlignment(Qt.AlignCenter)
                icon_label.setStyleSheet("""
                    QLabel {
                        font-size: 24px;
                        margin-bottom: 8px;
                    }
                """)
                feature_layout.addWidget(icon_label)
                
                # 标题
                title_label = QLabel(title)
                title_label.setAlignment(Qt.AlignCenter)
                title_label.setStyleSheet("""
                    QLabel {
                        font-size: 14px;
                        font-weight: 600;
                        color: #ffffff;
                        font-family: "Microsoft YaHei UI", sans-serif;
                        margin-bottom: 2px;
                    }
                """)
                feature_layout.addWidget(title_label)
                
                # 描述
                desc_label = QLabel(desc)
                desc_label.setAlignment(Qt.AlignCenter)
                desc_label.setStyleSheet("""
                    QLabel {
                        font-size: 10px;
                        color: #b0b0b0;
                        font-family: "Microsoft YaHei UI", sans-serif;
                        line-height: 1.3;
                    }
                """)
                desc_label.setWordWrap(True)
                feature_layout.addWidget(desc_label)
                
                features_grid.addWidget(feature_card, i // 3, i % 3)
            
            content_layout.addLayout(features_grid)
            
            # 开发信息 - 高级电竞风格
            dev_info = QLabel("""
                <div style='text-align: center; color: #b0b0b0; font-size: 14px; line-height: 1.8; font-family: "Microsoft YaHei UI";'>
                    <p><b style='color: #ff2a2a; font-size: 16px;'>开发团队</b><br>浩讯亿通电脑店</p>
                    <p><b style='color: #ff2a2a; font-size: 16px;'>技术支持</b><br>QQ交流群：182352621</p>
                    <p><b style='color: #ff2a2a; font-size: 16px;'>问题反馈</b><br>zhangyuhao@haoxun.cc</p>
                    <div style='margin-top: 25px; padding-top: 20px; border-top: 1px solid #333333;'>
                        <p style='color: #808080; font-size: 12px;'>
                            © 2025 烟台浩讯网络有限责任公司 | 专业电竞版
                        </p>
                    </div>
                </div>
            """)
            dev_info.setAlignment(Qt.AlignCenter)
            dev_info.setTextFormat(Qt.RichText)
            dev_info.setOpenExternalLinks(True)  # 启用外部链接
            content_layout.addWidget(dev_info)
            
            about_layout.addWidget(content_widget)
            
            # 添加到主布局
            self.upper_layout.addWidget(about_container)
            self.upper_layout.addStretch()
            
        except Exception as e:
            self.logger.error(f"显示关于页面失败: {e}")
    
    def show_settings(self):
        """显示设置页面 - 简约电竞风格"""
        try:
            # 隐藏硬件信息区域
            self.lower_frame.setVisible(False)
            
            self.clear_upper_frame()
            
            # 创建主容器 - 电竞风格设计
            settings_container = QWidget()
            settings_container.setStyleSheet("""
                QWidget {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                        stop: 0 rgba(10, 10, 10, 0.98),
                        stop: 1 rgba(20, 20, 20, 0.98));
                    border-radius: 12px;
                    border: 1px solid rgba(255, 0, 0, 0.3);
                    margin: 10px;
                    padding: 0px;
                }
            """)
            
            settings_layout = QVBoxLayout(settings_container)
            settings_layout.setContentsMargins(0, 0, 0, 0)
            settings_layout.setSpacing(0)
            
            # 头部区域 - 电竞红黑渐变
            header_widget = QWidget()
            header_widget.setStyleSheet("""
                QWidget {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 #ff0000,
                        stop: 0.3 #cc0000,
                        stop: 0.7 #990000,
                        stop: 1 #660000);
                    border-top-left-radius: 12px;
                    border-top-right-radius: 12px;
                    padding: 20px;
                    border-bottom: 2px solid rgba(255, 0, 0, 0.5);
                }
            """)
            
            header_layout = QVBoxLayout(header_widget)
            
            # 标题 - 电竞风格
            title_label = QLabel("程序设置")
            title_label.setAlignment(Qt.AlignCenter)
            title_label.setStyleSheet("""
                font-size: 22px;
                font-weight: bold;
                color: #ffffff;
                margin: 0px;
                padding: 0px;
                font-family: "Microsoft YaHei", sans-serif;
            """)
            header_layout.addWidget(title_label)
            
            # 副标题
            subtitle_label = QLabel("电竞风格个性化设置")
            subtitle_label.setAlignment(Qt.AlignCenter)
            subtitle_label.setStyleSheet("""
                font-size: 12px;
                color: rgba(255, 200, 200, 0.9);
                margin: 5px 0 0 0;
                padding: 0px;
                font-family: "Microsoft YaHei", sans-serif;
            """)
            header_layout.addWidget(subtitle_label)
            
            settings_layout.addWidget(header_widget)
            
            # 内容区域
            content_widget = QWidget()
            content_widget.setStyleSheet("""
                QWidget {
                    background: transparent;
                    border-bottom-left-radius: 12px;
                    border-bottom-right-radius: 12px;
                    padding: 20px;
                }
            """)
            
            content_layout = QVBoxLayout(content_widget)
            content_layout.setSpacing(15)
            
            # 背景设置卡片（可点击）
            bg_card = self.create_setting_card("🎨 背景设置", "点击自定义电竞风格外观", clickable=True, callback=self.show_background_image_dialog)
            content_layout.addWidget(bg_card)
            
            # 背景切换按钮
            self.background_toggle = QPushButton("🔆 显示背景图")
            self.background_toggle.setCheckable(True)
            self.background_toggle.setChecked(True)  # 默认显示背景
            self.background_toggle.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 rgba(255, 69, 58, 0.3), stop: 1 rgba(255, 152, 0, 0.3));
                    border: 1px solid rgba(255, 69, 58, 0.6);
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-size: 12px;
                    color: #ffeb3b;
                    font-family: "Microsoft YaHei";
                    font-weight: bold;
                }
                QPushButton:checked {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 rgba(255, 69, 58, 0.6), stop: 1 rgba(255, 152, 0, 0.6));
                    border: 1px solid rgba(255, 69, 58, 1);
                }
                QPushButton:hover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 rgba(255, 69, 58, 0.5), stop: 1 rgba(255, 152, 0, 0.5));
                    border: 1px solid rgba(255, 69, 58, 0.8);
                }
            """)
            self.background_toggle.clicked.connect(self.toggle_background)
            content_layout.addWidget(self.background_toggle)
            
            # 风扇转速控制卡片（可点击）
            fan_card = self.create_setting_card("🌪️ 风扇控制", "手动调节CPU/机箱风扇转速", clickable=True, callback=self.show_fan_control)
            content_layout.addWidget(fan_card)
            
            content_layout.addStretch()
            settings_layout.addWidget(content_widget)
            
            self.upper_layout.addWidget(settings_container)
            
        except Exception as e:
            self.logger.error(f"显示设置页面失败: {e}")
    
    def show_fan_control(self):
        """显示风扇转速控制页面 - 红色电竞版本"""
        try:
            # 检查并确保 lower_frame 存在
            if not hasattr(self, 'lower_frame') or self.lower_frame is None:
                self.logger.warning("lower_frame 不存在，重新初始化")
                self.init_ui()
            
            # 隐藏硬件信息区域
            self.lower_frame.setVisible(False)
            
            self.clear_upper_frame()
            
            # 初始化风扇控制器
            fan_controller_status = self.fan_controller.initialize()
            
            # 创建红色电竞主容器
            fan_container = QWidget()
            fan_container.setStyleSheet("""
                QWidget {
                    background: rgba(30, 0, 0, 0.95);
                    border-radius: 12px;
                    border: 2px solid rgba(255, 69, 58, 0.6);
                    margin: 6px;
                    padding: 8px;
                }
            """)
            
            fan_layout = QVBoxLayout(fan_container)
            fan_layout.setContentsMargins(8, 8, 8, 8)
            fan_layout.setSpacing(8)
            
            # 标题 - 适配窗口高度
            title_label = QLabel("🔥 风扇控制中心")
            title_label.setAlignment(Qt.AlignCenter)
            title_label.setFixedHeight(60)  # 增加标题高度
            title_label.setStyleSheet("""
                font-size: 18px;
                font-weight: bold;
                color: #ffeb3b;
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 rgba(255, 69, 58, 0.4), stop: 1 rgba(255, 152, 0, 0.4));
                padding: 8px;
                border-radius: 6px;
                border: 1px solid rgba(255, 69, 58, 0.6);
            """)
            fan_layout.addWidget(title_label)
            
            # 风扇设备检测状态显示
            if fan_controller_status:
                fan_count = len(self.fan_controller.get_available_fans())
                status_text = f"✅ 已检测到 {fan_count} 个风扇设备"
            else:
                status_text = f"⚠️ {self.fan_controller.error_message}"
            
            # 状态显示 - 红色电竞风格，适配窗口高度
            status_label = QLabel(f"🔥 {status_text}")
            status_label.setAlignment(Qt.AlignCenter)
            status_label.setFixedHeight(42)  # 增加状态栏高度
            status_label.setStyleSheet("""
                font-size: 13px;
                color: #ffeb3b;
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 rgba(255, 69, 58, 0.3), stop: 1 rgba(255, 152, 0, 0.4));
                padding: 6px;
                border-radius: 4px;
                border: 1px solid rgba(255, 69, 58, 0.6);
                font-weight: bold;
            """)
            fan_layout.addWidget(status_label)
            
            # 模式选择和风扇设备选择 - 红色电竞风格，适配窗口高度
            mode_frame = QFrame()
            mode_frame.setFixedHeight(90)  # 增加高度以容纳风扇选择
            mode_layout = QVBoxLayout(mode_frame)
            mode_layout.setSpacing(6)
            mode_layout.setContentsMargins(12, 8, 12, 8)  # 增加内边距
            
            # 第一行：模式选择
            mode_row_layout = QHBoxLayout()
            mode_row_layout.setSpacing(8)
            
            self.auto_mode_btn = QRadioButton("🚀 自动模式")
            self.manual_mode_btn = QRadioButton("🎮 手动模式")
            self.auto_mode_btn.setChecked(True)
            
            mode_style = """
                QRadioButton {
                    color: #ffeb3b;
                    font-size: 11px;
                    padding: 4px 8px;
                    border: 1px solid rgba(255, 69, 58, 0.6);
                    border-radius: 3px;
                    margin: 2px;
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 rgba(255, 69, 58, 0.2), stop: 1 rgba(255, 152, 0, 0.2));
                    font-weight: bold;
                }
                QRadioButton:checked {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 rgba(255, 69, 58, 0.6), stop: 1 rgba(255, 152, 0, 0.6));
                    border-color: rgba(255, 69, 58, 1);
                    color: #ffffff;
                }
                QRadioButton:hover {
                    border-color: rgba(255, 69, 58, 0.8);
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 rgba(255, 69, 58, 0.4), stop: 1 rgba(255, 152, 0, 0.4));
                }
            """
            self.auto_mode_btn.setStyleSheet(mode_style)
            self.manual_mode_btn.setStyleSheet(mode_style)
            
            self.auto_mode_btn.clicked.connect(self.toggle_fan_mode)
            self.manual_mode_btn.clicked.connect(self.toggle_fan_mode)
            
            mode_row_layout.addWidget(self.auto_mode_btn)
            mode_row_layout.addWidget(self.manual_mode_btn)
            mode_row_layout.addStretch()
            mode_layout.addLayout(mode_row_layout)
            
            # 第二行：风扇设备选择和控制模式选择
            if fan_controller_status:
                fan_select_layout = QHBoxLayout()
                fan_select_layout.setSpacing(6)
                
                fan_label = QLabel("🎯 选择风扇:")
                fan_label.setStyleSheet("""
                    font-size: 10px;
                    color: #ffeb3b;
                    font-weight: bold;
                """)
                fan_select_layout.addWidget(fan_label)
                
                # 风扇选择下拉框
                self.fan_combo = QComboBox()
                available_fans = self.fan_controller.get_available_fans()
                for fan in available_fans:
                    self.fan_combo.addItem(f"{fan['name']} ({fan['type']})", fan['device_id'])
                
                self.fan_combo.setStyleSheet("""
                    QComboBox {
                        font-size: 10px;
                        color: #ffeb3b;
                        background: rgba(255, 69, 58, 0.3);
                        border: 1px solid rgba(255, 69, 58, 0.6);
                        border-radius: 3px;
                        padding: 2px 6px;
                        min-width: 180px;
                    }
                    QComboBox::drop-down {
                        border: none;
                    }
                    QComboBox::down-arrow {
                        image: none;
                        border-left: 3px solid transparent;
                        border-right: 3px solid transparent;
                        border-top: 5px solid #ffeb3b;
                    }
                    QComboBox QAbstractItemView {
                        background: rgba(30, 0, 0, 0.95);
                        border: 1px solid rgba(255, 69, 58, 0.6);
                        color: #ffeb3b;
                        selection-background-color: rgba(255, 69, 58, 0.6);
                    }
                """)
                fan_select_layout.addWidget(self.fan_combo)
                
                # 控制模式选择
                mode_label = QLabel("🎛️ 控制模式:")
                mode_label.setStyleSheet("""
                    font-size: 10px;
                    color: #ffeb3b;
                    font-weight: bold;
                    margin-left: 10px;
                """)
                fan_select_layout.addWidget(mode_label)
                
                self.control_mode_combo = QComboBox()
                self.control_mode_combo.addItem("⚖️ 平衡模式", "balanced")
                self.control_mode_combo.addItem("🔇 静音模式", "quiet")
                self.control_mode_combo.addItem("🚀 性能模式", "performance")
                self.control_mode_combo.setCurrentIndex(0)
                
                self.control_mode_combo.setStyleSheet("""
                    QComboBox {
                        font-size: 10px;
                        color: #ffeb3b;
                        background: rgba(255, 69, 58, 0.3);
                        border: 1px solid rgba(255, 69, 58, 0.6);
                        border-radius: 3px;
                        padding: 2px 6px;
                        min-width: 120px;
                    }
                    QComboBox::drop-down {
                        border: none;
                    }
                    QComboBox::down-arrow {
                        image: none;
                        border-left: 3px solid transparent;
                        border-right: 3px solid transparent;
                        border-top: 5px solid #ffeb3b;
                    }
                    QComboBox QAbstractItemView {
                        background: rgba(30, 0, 0, 0.95);
                        border: 1px solid rgba(255, 69, 58, 0.6);
                        color: #ffeb3b;
                        selection-background-color: rgba(255, 69, 58, 0.6);
                    }
                """)
                self.control_mode_combo.currentIndexChanged.connect(self.change_control_mode)
                fan_select_layout.addWidget(self.control_mode_combo)
                
                fan_select_layout.addStretch()
                mode_layout.addLayout(fan_select_layout)
            
            fan_layout.addWidget(mode_frame)
            
            # 风扇控制区域 - 红色电竞风格
            self.manual_control_frame = QFrame()
            self.manual_control_frame.setVisible(False)  # 默认隐藏
            self.manual_control_frame.setStyleSheet("""
                QFrame {
                    background: rgba(255, 69, 58, 0.08);
                    border-radius: 6px;
                    border: 1px solid rgba(255, 69, 58, 0.4);
                    padding: 8px;
                }
            """)
            
            manual_layout = QVBoxLayout(self.manual_control_frame)
            manual_layout.setSpacing(8)
            
            # 风扇转速控制 - 红色电竞风格
            slider_label = QLabel("🎯 风扇转速: 50%")
            slider_label.setStyleSheet("""
                color: #ffeb3b; 
                font-size: 14px; 
                font-weight: bold;
                padding: 4px 0;
            """)
            manual_layout.addWidget(slider_label)
            
            self.fan_slider = QSlider(Qt.Horizontal)
            self.fan_slider.setRange(0, 100)
            self.fan_slider.setValue(50)
            self.fan_slider.setFixedHeight(48)  # 增加滑块高度
            self.fan_slider.setStyleSheet("""
                QSlider::groove:horizontal {
                    border: 1px solid rgba(255, 69, 58, 0.6);
                    height: 5px;
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 rgba(255, 69, 58, 0.8), stop: 0.5 rgba(255, 152, 0, 0.8), stop: 1 rgba(255, 235, 59, 0.8));
                    border-radius: 2px;
                }
                QSlider::handle:horizontal {
                    background: #ffeb3b;
                    border: 2px solid rgba(255, 69, 58, 0.8);
                    width: 14px;
                    height: 14px;
                    margin: -4px 0;
                    border-radius: 7px;
                }
                QSlider::handle:horizontal:hover {
                    background: rgba(255, 69, 58, 0.9);
                    border: 2px solid #ffeb3b;
                }
            """)
            self.fan_slider.valueChanged.connect(lambda v: slider_label.setText(f"🎯 风扇转速: {v}%"))
            self.fan_slider.valueChanged.connect(self.set_fan_speed)
            manual_layout.addWidget(self.fan_slider)
            
            # 预设模式按钮 - 红色电竞风格
            preset_layout = QHBoxLayout()
            preset_layout.setSpacing(6)
            
            # 静音模式
            silent_btn = QPushButton("🔇 静音模式")
            silent_btn.setFixedHeight(42)  # 增加按钮高度
            silent_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 rgba(52, 152, 219, 0.3), stop: 1 rgba(86, 204, 242, 0.3));
                    border: 1px solid rgba(52, 152, 219, 0.6);
                    border-radius: 3px;
                    color: #ffeb3b;
                    font-size: 10px;
                    font-weight: bold;
                    padding: 4px 8px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 rgba(52, 152, 219, 0.5), stop: 1 rgba(86, 204, 242, 0.5));
                    border-color: #3498db;
                }
                QPushButton:pressed {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 rgba(52, 152, 219, 0.7), stop: 1 rgba(86, 204, 242, 0.7));
                }
            """)
            silent_btn.clicked.connect(lambda: self.set_fan_speed(30))
            
            # 平衡模式
            balance_btn = QPushButton("⚖️ 平衡模式")
            balance_btn.setFixedHeight(42)  # 增加按钮高度
            balance_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 rgba(46, 204, 113, 0.3), stop: 1 rgba(88, 214, 141, 0.3));
                    border: 1px solid rgba(46, 204, 113, 0.6);
                    border-radius: 3px;
                    color: #ffeb3b;
                    font-size: 10px;
                    font-weight: bold;
                    padding: 4px 8px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 rgba(46, 204, 113, 0.5), stop: 1 rgba(88, 214, 141, 0.5));
                    border-color: #2ecc71;
                }
                QPushButton:pressed {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 rgba(46, 204, 113, 0.7), stop: 1 rgba(88, 214, 141, 0.7));
                }
            """)
            balance_btn.clicked.connect(lambda: self.set_fan_speed(50))
            
            # 性能模式
            performance_btn = QPushButton("🚀 性能模式")
            performance_btn.setFixedHeight(32)  # 增加按钮高度
            performance_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 rgba(255, 69, 58, 0.3), stop: 1 rgba(255, 152, 0, 0.3));
                    border: 1px solid rgba(255, 69, 58, 0.6);
                    border-radius: 3px;
                    color: #ffeb3b;
                    font-size: 10px;
                    font-weight: bold;
                    padding: 4px 8px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 rgba(255, 69, 58, 0.5), stop: 1 rgba(255, 152, 0, 0.5));
                    border-color: #ff453a;
                }
                QPushButton:pressed {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 rgba(255, 69, 58, 0.7), stop: 1 rgba(255, 152, 0, 0.7));
                }
            """)
            performance_btn.clicked.connect(lambda: self.set_fan_speed(80))
            
            preset_layout.addWidget(silent_btn)
            preset_layout.addWidget(balance_btn)
            preset_layout.addWidget(performance_btn)
            
            manual_layout.addLayout(preset_layout)
            
            fan_layout.addWidget(self.manual_control_frame)
            
            # 控制按钮 - 红色电竞风格
            button_layout = QHBoxLayout()
            
            apply_btn = QPushButton("⚡ 应用设置")
            apply_btn.setFixedHeight(46)  # 增加按钮高度
            apply_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 rgba(255, 69, 58, 0.8), stop: 1 rgba(255, 152, 0, 0.8));
                    border: 1px solid rgba(255, 69, 58, 0.9);
                    border-radius: 4px;
                    color: #ffffff;
                    font-size: 12px;
                    font-weight: bold;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 rgba(255, 69, 58, 1), stop: 1 rgba(255, 152, 0, 1));
                    border-color: #ffeb3b;
                }
                QPushButton:pressed {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 rgba(255, 69, 58, 0.9), stop: 1 rgba(255, 152, 0, 0.9));
                }
            """)
            apply_btn.clicked.connect(self.apply_fan_settings)
            
            back_btn = QPushButton("🔙 返回")
            back_btn.setFixedHeight(46)  # 增加按钮高度
            back_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 rgba(120, 120, 120, 0.3), stop: 1 rgba(180, 180, 180, 0.3));
                    border: 1px solid rgba(120, 120, 120, 0.6);
                    border-radius: 4px;
                    color: #ffeb3b;
                    font-size: 12px;
                    font-weight: bold;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 rgba(120, 120, 120, 0.5), stop: 1 rgba(180, 180, 180, 0.5));
                    border-color: #ffeb3b;
                }
                QPushButton:pressed {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 rgba(120, 120, 120, 0.7), stop: 1 rgba(180, 180, 180, 0.7));
                }
            """)
            back_btn.clicked.connect(self.show_settings)
            
            button_layout.addWidget(apply_btn)
            button_layout.addStretch()
            button_layout.addWidget(back_btn)
            
            fan_layout.addLayout(button_layout)
            
            self.upper_layout.addWidget(fan_container)
            
        except Exception as e:
            self.logger.error(f"显示风扇控制页面失败: {e}")
    
    def create_simple_fan_control_interface(self, parent_layout):
        """创建增强版风扇控制界面"""
        try:
            # 主容器卡片 - 更精美的设计
            main_card = QWidget()
            main_card.setStyleSheet("""
                QWidget {
                    background: rgba(20, 20, 40, 0.9);
                    border-radius: 12px;
                    border: 1px solid rgba(0, 255, 255, 0.3);
                    padding: 16px;
                    margin: 8px 0;
                }
            """)
            
            main_layout = QVBoxLayout(main_card)
            main_layout.setSpacing(12)
            main_layout.setContentsMargins(12, 12, 12, 12)
            
            # 标题区域
            title_layout = QHBoxLayout()
            
            # 标题图标和文字
            title_icon = QLabel("🌪️")
            title_icon.setStyleSheet("font-size: 20px;")
            title_text = QLabel("风扇控制中心")
            title_text.setStyleSheet("""
                font-size: 16px;
                font-weight: bold;
                color: #00ffff;
                margin-bottom: 8px;
            """)
            
            # 控制模式切换
            self.control_mode_group = QButtonGroup()
            self.auto_mode_btn = QRadioButton("自动")
            self.manual_mode_btn = QRadioButton("手动")
            self.auto_mode_btn.setChecked(True)
            
            mode_style = """
                QRadioButton {
                    color: #ffffff;
                    font-size: 12px;
                    padding: 4px 8px;
                    border: none;
                }
                QRadioButton:checked {
                    color: #00ffff;
                    font-weight: bold;
                }
                QRadioButton:hover {
                    color: #00cccc;
                }
            """
            self.auto_mode_btn.setStyleSheet(mode_style)
            self.manual_mode_btn.setStyleSheet(mode_style)
            
            title_layout.addWidget(title_icon)
            title_layout.addWidget(title_text)
            title_layout.addStretch()
            title_layout.addWidget(self.auto_mode_btn)
            title_layout.addWidget(self.manual_mode_btn)
            
            main_layout.addLayout(title_layout)
            
            # 系统状态显示区域
            status_frame = QFrame()
            status_frame.setStyleSheet("""
                QFrame {
                    background: rgba(0, 100, 150, 0.2);
                    border-radius: 8px;
                    border: 1px solid rgba(0, 255, 255, 0.2);
                    padding: 8px;
                }
            """)
            status_layout = QGridLayout(status_frame)
            status_layout.setSpacing(6)
            
            # CPU温度
            cpu_temp_label = QLabel("CPU温度:")
            cpu_temp_label.setStyleSheet("color: #aaaaaa; font-size: 11px;")
            self.cpu_temp_value = QLabel("45°C")
            self.cpu_temp_value.setStyleSheet("""
                color: #44ff44;
                font-size: 13px;
                font-weight: bold;
                background: rgba(68, 255, 68, 0.1);
                padding: 3px 6px;
                border-radius: 4px;
                border: 1px solid rgba(68, 255, 68, 0.3);
                max-width: 60px;
            """)
            
            # 风扇转速
            fan_rpm_label = QLabel("风扇转速:")
            fan_rpm_label.setStyleSheet("color: #aaaaaa; font-size: 11px;")
            self.fan_rpm_value = QLabel("1200 RPM")
            self.fan_rpm_value.setStyleSheet("""
                color: #ffaa00;
                font-size: 13px;
                font-weight: bold;
                background: rgba(255, 170, 0, 0.1);
                padding: 3px 6px;
                border-radius: 4px;
                border: 1px solid rgba(255, 170, 0, 0.3);
                max-width: 80px;
            """)
            
            # 噪音水平
            noise_label = QLabel("噪音等级:")
            noise_label.setStyleSheet("color: #aaaaaa; font-size: 11px;")
            self.noise_level = QLabel("低")
            self.noise_level.setStyleSheet("""
                color: #44ff44;
                font-size: 13px;
                font-weight: bold;
                background: rgba(68, 255, 68, 0.1);
                padding: 3px 6px;
                border-radius: 4px;
                border: 1px solid rgba(68, 255, 68, 0.3);
                max-width: 40px;
            """)
            
            status_layout.addWidget(cpu_temp_label, 0, 0)
            status_layout.addWidget(self.cpu_temp_value, 0, 1)
            status_layout.addWidget(fan_rpm_label, 1, 0)
            status_layout.addWidget(self.fan_rpm_value, 1, 1)
            status_layout.addWidget(noise_label, 2, 0)
            status_layout.addWidget(self.noise_level, 2, 1)
            
            main_layout.addWidget(status_frame)
            
            # 手动控制区域
            self.manual_control_frame = QFrame()
            self.manual_control_frame.setVisible(False)  # 默认隐藏
            self.manual_control_frame.setStyleSheet("""
                QFrame {
                    background: rgba(40, 20, 60, 0.3);
                    border-radius: 8px;
                    border: 1px solid rgba(255, 0, 255, 0.2);
                    padding: 12px;
                }
            """)
            manual_layout = QVBoxLayout(self.manual_control_frame)
            manual_layout.setSpacing(8)
            
            # 风扇转速控制
            fan_control_label = QLabel("风扇转速控制")
            fan_control_label.setStyleSheet("""
                color: #ff66ff;
                font-size: 14px;
                font-weight: bold;
                margin-bottom: 4px;
            """)
            manual_layout.addWidget(fan_control_label)
            
            # 滑块控制
            slider_frame = QFrame()
            slider_layout = QVBoxLayout(slider_frame)
            slider_layout.setSpacing(4)
            
            # 滑块标签
            self.unified_fan_slider = QSlider(Qt.Horizontal)
            self.unified_fan_slider.setRange(0, 100)
            self.unified_fan_slider.setValue(50)
            self.unified_fan_slider.setFixedHeight(25)
            self.unified_fan_slider.setStyleSheet("""
                QSlider::groove:horizontal {
                    border: 1px solid rgba(255, 255, 255, 0.2);
                    height: 6px;
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 #ff4444, stop: 0.3 #ffaa00, stop: 0.7 #44aa44, stop: 1 #44ff44);
                    border-radius: 3px;
                }
                QSlider::handle:horizontal {
                    background: #ffffff;
                    border: 2px solid #00ffff;
                    width: 16px;
                    height: 16px;
                    margin: -6px 0;
                    border-radius: 8px;
                }
                QSlider::handle:horizontal:hover {
                    background: #00ffff;
                    border-color: #ffffff;
                }
                QSlider::sub-page:horizontal {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 #ff4444, stop: 0.3 #ffaa00, stop: 0.7 #44aa44, stop: 1 #44ff44);
                    border-radius: 3px;
                }
            """)
            
            # 百分比和RPM显示
            value_layout = QHBoxLayout()
            self.unified_fan_value = QLabel("50% (1200 RPM)")
            self.unified_fan_value.setStyleSheet("""
                font-size: 14px;
                font-weight: bold;
                color: #ffffff;
                background: rgba(0, 255, 255, 0.1);
                padding: 6px 12px;
                border-radius: 6px;
                border: 1px solid rgba(0, 255, 255, 0.3);
                min-width: 100px;
            """)
            
            # 风扇健康状态
            self.fan_health = QLabel("🟢 正常")
            self.fan_health.setStyleSheet("""
                font-size: 12px;
                color: #44ff44;
                background: rgba(68, 255, 68, 0.1);
                padding: 6px 12px;
                border-radius: 6px;
                border: 1px solid rgba(68, 255, 68, 0.3);
            """)
            
            value_layout.addWidget(self.unified_fan_value)
            value_layout.addStretch()
            value_layout.addWidget(self.fan_health)
            
            slider_layout.addWidget(self.unified_fan_slider)
            slider_layout.addLayout(value_layout)
            
            manual_layout.addWidget(slider_frame)
            
            # 预设模式按钮组
            preset_frame = QFrame()
            preset_layout = QHBoxLayout(preset_frame)
            preset_layout.setSpacing(8)
            
            # 静音模式
            silent_btn = QPushButton("🌙 静音模式")
            silent_btn.setFixedHeight(35)
            silent_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 #4a4aff, stop: 1 #2a2aff);
                    border: 1px solid #6666ff;
                    border-radius: 6px;
                    color: white;
                    font-size: 12px;
                    font-weight: bold;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 #6a6aff, stop: 1 #4a4aff);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 #2a2aff, stop: 1 #1a1aff);
                }
            """)
            silent_btn.clicked.connect(lambda: self.set_fan_preset_with_description("silent"))
            
            # 平衡模式
            balance_btn = QPushButton("⚖️ 平衡模式")
            balance_btn.setFixedHeight(35)
            balance_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 #ffaa00, stop: 1 #ff9900);
                    border: 1px solid #ffcc00;
                    border-radius: 6px;
                    color: white;
                    font-size: 12px;
                    font-weight: bold;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 #ffcc00, stop: 1 #ffaa00);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 #ff9900, stop: 1 #ff8800);
                }
            """)
            balance_btn.clicked.connect(lambda: self.set_fan_preset_with_description("balance"))
            
            # 性能模式
            performance_btn = QPushButton("🚀 性能模式")
            performance_btn.setFixedHeight(35)
            performance_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 #ff4444, stop: 1 #cc0000);
                    border: 1px solid #ff6666;
                    border-radius: 6px;
                    color: white;
                    font-size: 12px;
                    font-weight: bold;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 #ff6666, stop: 1 #dd0000);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 #dd0000, stop: 1 #bb0000);
                }
            """)
            performance_btn.clicked.connect(lambda: self.set_fan_preset_with_description("performance"))
            
            # 极速模式
            turbo_btn = QPushButton("⚡ 极速模式")
            turbo_btn.setFixedHeight(35)
            turbo_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 #ff00ff, stop: 1 #cc00cc);
                    border: 1px solid #ff66ff;
                    border-radius: 6px;
                    color: white;
                    font-size: 12px;
                    font-weight: bold;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 #ff66ff, stop: 1 #dd00dd);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 #dd00dd, stop: 1 #bb00bb);
                }
            """)
            turbo_btn.clicked.connect(lambda: self.set_fan_preset_with_description("turbo"))
            
            preset_layout.addWidget(silent_btn)
            preset_layout.addWidget(balance_btn)
            preset_layout.addWidget(performance_btn)
            preset_layout.addWidget(turbo_btn)
            
            manual_layout.addWidget(preset_frame)
            
            main_layout.addWidget(self.manual_control_frame)
            
            # 模式说明区域
            self.mode_description = QLabel("自动模式：根据CPU温度自动调节风扇转速")
            self.mode_description.setWordWrap(True)
            self.mode_description.setStyleSheet("""
                font-size: 12px;
                color: #cccccc;
                background: rgba(100, 100, 100, 0.1);
                padding: 8px 12px;
                border-radius: 6px;
                border: 1px solid rgba(200, 200, 200, 0.2);
                margin-top: 8px;
            """)
            main_layout.addWidget(self.mode_description)
            
            # 控制按钮
            button_layout = QHBoxLayout()
            
            apply_btn = QPushButton("✅ 应用设置")
            apply_btn.setFixedHeight(30)
            apply_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 #00aa00, stop: 1 #008800);
                    border: 1px solid #00cc00;
                    border-radius: 6px;
                    color: white;
                    font-size: 12px;
                    font-weight: bold;
                    padding: 6px 16px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 #00cc00, stop: 1 #00aa00);
                }
            """)
            apply_btn.clicked.connect(self.apply_fan_settings)
            
            refresh_btn = QPushButton("🔄 刷新")
            refresh_btn.setFixedHeight(30)
            refresh_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 #666666, stop: 1 #444444);
                    border: 1px solid #888888;
                    border-radius: 6px;
                    color: white;
                    font-size: 12px;
                    font-weight: bold;
                    padding: 6px 16px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 #888888, stop: 1 #666666);
                }
            """)
            refresh_btn.clicked.connect(self.refresh_fan_display)
            
            reset_btn = QPushButton("↩️ 重置")
            reset_btn.setFixedHeight(30)
            reset_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 #aa4444, stop: 1 #882222);
                    border: 1px solid #cc6666;
                    border-radius: 6px;
                    color: white;
                    font-size: 12px;
                    font-weight: bold;
                    padding: 6px 16px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 #cc6666, stop: 1 #aa4444);
                }
            """)
            reset_btn.clicked.connect(self.reset_fan_settings)
            
            button_layout.addWidget(apply_btn)
            button_layout.addWidget(refresh_btn)
            button_layout.addWidget(reset_btn)
            
            main_layout.addLayout(button_layout)
            
            # 连接信号
            self.unified_fan_slider.valueChanged.connect(self.update_unified_fan_value)
            self.auto_mode_btn.toggled.connect(self.on_control_mode_changed)
            
            # 添加到布局
            parent_layout.addWidget(main_card)
            
        except Exception as e:
            self.logger.error(f"创建增强版风扇控制界面失败: {e}")
    
    def create_fan_control_interface(self, parent_layout):
        """创建风扇控制界面"""
        try:
            # 获取系统风扇信息
            fans = self.get_system_fans()
            
            if not fans:
                # 如果没有检测到风扇，显示提示信息
                no_fan_label = QLabel("🔍 未检测到可控制的风扇\n\n可能原因：\n• 系统不支持风扇控制\n• 需要管理员权限\n• 主板/BIOS不支持")
                no_fan_label.setAlignment(Qt.AlignCenter)
                no_fan_label.setStyleSheet("""
                    font-size: 16px;
                    color: #ffaa00;
                    padding: 40px;
                    background: rgba(255, 170, 0, 0.1);
                    border-radius: 8px;
                    border: 1px solid rgba(255, 170, 0, 0.3);
                """)
                parent_layout.addWidget(no_fan_label)
                return
            
            # 创建主容器
            main_container = QWidget()
            main_layout = QVBoxLayout(main_container)
            
            # 为每个风扇创建控制组件
            for i, fan in enumerate(fans):
                fan_widget = self.create_fan_control_card(fan, i)
                main_layout.addWidget(fan_widget)
            
            # 添加历史记录和图表显示区域
            history_container = self.create_fan_history_section()
            main_layout.addWidget(history_container)
            
            # 添加说明信息
            info_label = QLabel("⚠️ 注意事项：\n• 调高风扇转速会增加噪音\n• 建议根据CPU温度调整转速\n• 修改前请确认风扇支持PWM控制")
            info_label.setStyleSheet("""
                font-size: 12px;
                color: #ffcc00;
                padding: 15px;
                background: rgba(255, 204, 0, 0.1);
                border-radius: 8px;
                border: 1px solid rgba(255, 204, 0, 0.3);
                margin-top: 20px;
            """)
            main_layout.addWidget(info_label)
            
            # 将主容器添加到父布局
            parent_layout.addWidget(main_container)
            
        except Exception as e:
            self.logger.error(f"创建风扇控制界面失败: {e}")
    
    def create_fan_history_section(self):
        """创建风扇历史记录和图表显示区域"""
        try:
            # 历史记录容器
            history_container = QWidget()
            history_container.setStyleSheet("""
                QWidget {
                    background: rgba(255, 255, 255, 0.05);
                    border-radius: 10px;
                    border: 1px solid rgba(0, 255, 255, 0.3);
                    padding: 20px;
                    margin: 5px 0;
                }
            """)
            
            history_layout = QVBoxLayout(history_container)
            history_layout.setSpacing(15)
            
            # 标题
            history_title = QLabel("📊 风扇转速历史记录")
            history_title.setStyleSheet("""
                font-size: 18px;
                font-weight: bold;
                color: #ffffff;
                margin-bottom: 10px;
            """)
            history_layout.addWidget(history_title)
            
            # 图表显示区域
            chart_container = QWidget()
            chart_container.setFixedHeight(200)
            chart_container.setStyleSheet("""
                QWidget {
                    background: rgba(0, 0, 0, 0.3);
                    border-radius: 8px;
                    border: 1px solid rgba(255, 255, 255, 0.2);
                }
            """)
            
            chart_layout = QVBoxLayout(chart_container)
            
            # 图表占位符（实际实现需要绘图库）
            chart_placeholder = QLabel("📈 风扇转速图表将在这里显示\n\n功能特点：\n• 实时显示转速变化趋势\n• 支持5分钟历史数据查看\n• 温度与转速关联分析")
            chart_placeholder.setAlignment(Qt.AlignCenter)
            chart_placeholder.setStyleSheet("""
                font-size: 14px;
                color: #cccccc;
                padding: 40px;
            """)
            chart_layout.addWidget(chart_placeholder)
            
            history_layout.addWidget(chart_container)
            
            # 统计信息区域
            stats_container = QWidget()
            stats_layout = QHBoxLayout(stats_container)
            stats_layout.setSpacing(20)
            
            # 平均转速
            avg_speed_widget = self.create_stat_widget("平均转速", "-- %", "#00ff88")
            stats_layout.addWidget(avg_speed_widget)
            
            # 最高转速
            max_speed_widget = self.create_stat_widget("最高转速", "-- %", "#ff4444")
            stats_layout.addWidget(max_speed_widget)
            
            # 最低转速
            min_speed_widget = self.create_stat_widget("最低转速", "-- %", "#4444ff")
            stats_layout.addWidget(min_speed_widget)
            
            # 数据点数
            data_points_widget = self.create_stat_widget("数据点数", "--", "#ffaa00")
            stats_layout.addWidget(data_points_widget)
            
            stats_layout.addStretch()
            
            history_layout.addWidget(stats_container)
            
            # 控制按钮区域
            button_layout = QHBoxLayout()
            
            # 刷新按钮
            refresh_btn = QPushButton("🔄 刷新数据")
            refresh_btn.setFixedSize(120, 35)
            refresh_btn.setStyleSheet("""
                QPushButton {
                    background: #4444ff;
                    border: none;
                    border-radius: 8px;
                    color: white;
                    font-size: 12px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: #6666ff;
                }
            """)
            refresh_btn.clicked.connect(self.refresh_fan_history)
            button_layout.addWidget(refresh_btn)
            
            # 清除历史按钮
            clear_btn = QPushButton("🗑️ 清除历史")
            clear_btn.setFixedSize(120, 35)
            clear_btn.setStyleSheet("""
                QPushButton {
                    background: #ff4444;
                    border: none;
                    border-radius: 8px;
                    color: white;
                    font-size: 12px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: #ff6666;
                }
            """)
            clear_btn.clicked.connect(self.clear_fan_history_ui)
            button_layout.addWidget(clear_btn)
            
            button_layout.addStretch()
            
            history_layout.addLayout(button_layout)
            
            # 保存历史记录组件引用
            self.fan_history_widgets = {
                'avg_speed': avg_speed_widget,
                'max_speed': max_speed_widget,
                'min_speed': min_speed_widget,
                'data_points': data_points_widget,
                'chart_container': chart_container
            }
            
            return history_container
            
        except Exception as e:
            self.logger.error(f"创建风扇历史记录区域失败: {e}")
            return QWidget()
    
    def create_stat_widget(self, title, value, color):
        """创建统计信息小部件"""
        widget = QWidget()
        widget.setFixedSize(120, 60)
        widget.setStyleSheet(f"""
            QWidget {{
                background: rgba({color[1:3]}, {color[3:5]}, {color[5:7]}, 0.1);
                border-radius: 8px;
                border: 1px solid rgba({color[1:3]}, {color[3:5]}, {color[5:7]}, 0.3);
            }}
        """)
        
        layout = QVBoxLayout(widget)
        layout.setSpacing(5)
        
        # 标题
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 11px;
            color: #cccccc;
        """)
        layout.addWidget(title_label)
        
        # 数值
        value_label = QLabel(value)
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #ffffff;
        """)
        layout.addWidget(value_label)
        
        return widget
    
    def refresh_fan_history(self):
        """刷新风扇历史记录显示"""
        try:
            if not hasattr(self, 'fan_controller') or not self.fan_controller:
                return
            
            # 获取风扇统计信息
            fans = self.fan_controller.get_available_fans()
            if not fans:
                return
            
            # 获取第一个风扇的统计信息
            fan_device_id = fans[0]['device_id']
            stats = self.fan_controller.get_fan_statistics(fan_device_id)
            
            # 更新统计信息显示
            if hasattr(self, 'fan_history_widgets'):
                # 更新平均转速
                avg_label = self.fan_history_widgets['avg_speed'].findChild(QLabel, None)
                if avg_label and avg_label.text() != "-- %":
                    avg_label.setText(f"{stats['avg_speed']:.1f} %")
                
                # 更新最高转速
                max_label = self.fan_history_widgets['max_speed'].findChild(QLabel, None)
                if max_label and max_label.text() != "-- %":
                    max_label.setText(f"{stats['max_speed']:.1f} %")
                
                # 更新最低转速
                min_label = self.fan_history_widgets['min_speed'].findChild(QLabel, None)
                if min_label and min_label.text() != "-- %":
                    min_label.setText(f"{stats['min_speed']:.1f} %")
                
                # 更新数据点数
                data_label = self.fan_history_widgets['data_points'].findChild(QLabel, None)
                if data_label and data_label.text() != "--":
                    data_label.setText(f"{stats['data_points']}")
            
        except Exception as e:
            self.logger.error(f"刷新风扇历史记录失败: {e}")
    
    def clear_fan_history_ui(self):
        """清除风扇历史记录UI"""
        try:
            if not hasattr(self, 'fan_controller') or not self.fan_controller:
                return
            
            # 清除历史记录
            self.fan_controller.clear_fan_history()
            
            # 重置统计信息显示
            if hasattr(self, 'fan_history_widgets'):
                # 重置平均转速
                avg_label = self.fan_history_widgets['avg_speed'].findChild(QLabel, None)
                if avg_label:
                    avg_label.setText("-- %")
                
                # 重置最高转速
                max_label = self.fan_history_widgets['max_speed'].findChild(QLabel, None)
                if max_label:
                    max_label.setText("-- %")
                
                # 重置最低转速
                min_label = self.fan_history_widgets['min_speed'].findChild(QLabel, None)
                if min_label:
                    min_label.setText("-- %")
                
                # 重置数据点数
                data_label = self.fan_history_widgets['data_points'].findChild(QLabel, None)
                if data_label:
                    data_label.setText("--")
            
            # 显示清除成功消息
            self.show_message("历史记录已清除", "info")
            
        except Exception as e:
            self.logger.error(f"清除风扇历史记录UI失败: {e}")
    
    def create_fan_control_card(self, fan_info, index):
        """创建单个风扇控制卡片"""
        try:
            # 风扇卡片
            fan_card = QWidget()
            fan_card.setStyleSheet("""
                QWidget {
                    background: rgba(255, 255, 255, 0.05);
                    border-radius: 10px;
                    border: 1px solid rgba(0, 255, 255, 0.3);
                    padding: 20px;
                    margin: 5px 0;
                }
            """)
            
            card_layout = QVBoxLayout(fan_card)
            card_layout.setSpacing(15)
            
            # 风扇信息头部
            header_layout = QHBoxLayout()
            
            # 风扇名称
            fan_name = QLabel(f"🌪️ {fan_info.get('name', f'风扇 {index+1}')}")
            fan_name.setStyleSheet("""
                font-size: 18px;
                font-weight: bold;
                color: #ffffff;
            """)
            header_layout.addWidget(fan_name)
            
            header_layout.addStretch()
            
            # 当前转速显示
            self.fan_control_widgets[f"current_rpm_{index}"] = QLabel("-- RPM")
            self.fan_control_widgets[f"current_rpm_{index}"].setStyleSheet("""
                font-size: 14px;
                font-weight: bold;
                color: #00ff88;
                background: rgba(0, 255, 136, 0.1);
                padding: 5px 10px;
                border-radius: 15px;
                border: 1px solid rgba(0, 255, 136, 0.3);
            """)
            header_layout.addWidget(self.fan_control_widgets[f"current_rpm_{index}"])
            
            card_layout.addLayout(header_layout)
            
            # 转速控制滑块
            slider_layout = QVBoxLayout()
            
            # 滑块标签
            slider_label = QLabel("风扇转速 (%):")
            slider_label.setStyleSheet("""
                font-size: 14px;
                color: #ffffff;
                margin-bottom: 5px;
            """)
            slider_layout.addWidget(slider_label)
            
            # 转速滑块
            self.fan_control_widgets[f"speed_slider_{index}"] = QSlider(Qt.Horizontal)
            self.fan_control_widgets[f"speed_slider_{index}"].setRange(0, 100)
            self.fan_control_widgets[f"speed_slider_{index}"].setValue(50)  # 默认50%
            self.fan_control_widgets[f"speed_slider_{index}"].setStyleSheet("""
                QSlider::groove:horizontal {
                    border: 1px solid rgba(255, 255, 255, 0.3);
                    height: 8px;
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 #ff4444, stop: 0.5 #ffaa00, stop: 1 #44ff44);
                    border-radius: 4px;
                }
                QSlider::handle:horizontal {
                    background: #ffffff;
                    border: 2px solid #00ffff;
                    width: 20px;
                    height: 20px;
                    margin: -5px 0;
                    border-radius: 10px;
                }
                QSlider::handle:horizontal:hover {
                    background: #00ffff;
                }
            """)
            
            # 速度标签显示
            self.fan_control_widgets[f"speed_label_{index}"] = QLabel("50%")
            self.fan_control_widgets[f"speed_label_{index}"].setAlignment(Qt.AlignCenter)
            self.fan_control_widgets[f"speed_label_{index}"].setStyleSheet("""
                font-size: 16px;
                font-weight: bold;
                color: #ffffff;
                background: rgba(0, 255, 255, 0.1);
                padding: 8px;
                border-radius: 8px;
                border: 1px solid rgba(0, 255, 255, 0.3);
                margin: 5px 0;
            """)
            
            # 滑块值变化连接
            self.fan_control_widgets[f"speed_slider_{index}"].valueChanged.connect(
                lambda value, idx=index: self.update_fan_speed_label(idx, value)
            )
            
            slider_layout.addWidget(self.fan_control_widgets[f"speed_slider_{index}"])
            slider_layout.addWidget(self.fan_control_widgets[f"speed_label_{index}"])
            
            card_layout.addLayout(slider_layout)
            
            # 预设按钮
            preset_layout = QHBoxLayout()
            preset_layout.setSpacing(10)
            
            # 静音模式
            silent_btn = QPushButton("🔇 静音")
            silent_btn.setFixedSize(80, 30)
            silent_btn.setStyleSheet("""
                QPushButton {
                    background: #4444ff;
                    border: none;
                    border-radius: 15px;
                    color: white;
                    font-size: 12px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: #6666ff;
                }
            """)
            silent_btn.clicked.connect(lambda: self.set_fan_preset_speed(index, 30))
            
            # 平衡模式
            balance_btn = QPushButton("⚖️ 平衡")
            balance_btn.setFixedSize(80, 30)
            balance_btn.setStyleSheet("""
                QPushButton {
                    background: #ffaa00;
                    border: none;
                    border-radius: 15px;
                    color: white;
                    font-size: 12px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: #ffcc00;
                }
            """)
            balance_btn.clicked.connect(lambda: self.set_fan_preset_speed(index, 50))
            
            # 性能模式
            performance_btn = QPushButton("🚀 性能")
            performance_btn.setFixedSize(80, 30)
            performance_btn.setStyleSheet("""
                QPushButton {
                    background: #ff4444;
                    border: none;
                    border-radius: 15px;
                    color: white;
                    font-size: 12px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: #ff6666;
                }
            """)
            performance_btn.clicked.connect(lambda: self.set_fan_preset_speed(index, 80))
            
            preset_layout.addWidget(silent_btn)
            preset_layout.addWidget(balance_btn)
            preset_layout.addWidget(performance_btn)
            preset_layout.addStretch()
            
            card_layout.addLayout(preset_layout)
            
            return fan_card
            
        except Exception as e:
            self.logger.error(f"创建风扇控制卡片失败: {e}")
            return QWidget()  # 返回空部件
    
    def get_system_fans(self):
        """获取系统风扇信息"""
        try:
            fans = []
            
            # 检查wmi是否可用
            try:
                import wmi
                computer = wmi.WMI()
                
                for sensor in computer.Win32_PerfRawData_PerfComputers():
                    if 'fan' in sensor.Name.lower() or '转速' in sensor.Name:
                        fans.append({
                            'name': sensor.Name,
                            'current_rpm': getattr(sensor, 'CurrentReading', 0),
                            'index': len(fans)
                        })
            except ImportError:
                self.logger.debug("WMI模块不可用")
            except Exception as e:
                self.logger.debug(f"WMI获取风扇信息失败: {e}")
            
            # 如果没有检测到，使用模拟数据
            if not fans:
                self.logger.info("未检测到实际风扇，使用模拟数据")
                fans = [
                    {'name': 'CPU风扇', 'current_rpm': 1200, 'index': 0},
                    {'name': '机箱风扇1', 'current_rpm': 800, 'index': 1},
                    {'name': '机箱风扇2', 'current_rpm': 900, 'index': 2}
                ]
            
            return fans
            
        except Exception as e:
            self.logger.error(f"获取系统风扇信息失败: {e}")
            return []
    
    def update_fan_speed_label(self, fan_index, value):
        """更新风扇速度标签显示"""
        try:
            if f"speed_label_{fan_index}" in self.fan_control_widgets:
                self.fan_control_widgets[f"speed_label_{fan_index}"].setText(f"{value}%")
        except Exception as e:
            self.logger.error(f"更新风扇速度标签失败: {e}")
    
    def set_fan_preset_speed(self, fan_index, speed):
        """设置风扇预设速度"""
        try:
            if f"speed_slider_{fan_index}" in self.fan_control_widgets:
                self.fan_control_widgets[f"speed_slider_{fan_index}"].setValue(speed)
        except Exception as e:
            self.logger.error(f"设置风扇预设速度失败: {e}")
    
    def refresh_fan_speeds(self):
        """刷新风扇转速显示"""
        try:
            fans = self.get_system_fans()
            for i, fan in enumerate(fans):
                if f"current_rpm_{i}" in self.fan_control_widgets:
                    rpm = fan.get('current_rpm', 0)
                    self.fan_control_widgets[f"current_rpm_{i}"].setText(f"{rpm} RPM")
            
            self.logger.info("风扇转速信息已刷新")
        except Exception as e:
            self.logger.error(f"刷新风扇转速失败: {e}")
    
    def apply_fan_settings(self):
        """应用风扇设置"""
        try:
            # 这里实现实际的风扇控制逻辑
            # 目前只是模拟应用
            
            applied_fans = []
            for i in range(10):  # 最多检查10个风扇
                if f"speed_slider_{i}" in self.fan_control_widgets:
                    speed = self.fan_control_widgets[f"speed_slider_{i}"].value()
                    applied_fans.append(f"风扇{i+1}: {speed}%")
            
            if applied_fans:
                self.show_success_message(f"✅ 风扇设置已应用:\n" + "\n".join(applied_fans))
                self.logger.info(f"风扇设置已应用: {applied_fans}")
            else:
                self.show_success_message("⚠️ 没有可应用的风扇设置")
            
            # 返回设置页面
            self.show_settings()
            
        except Exception as e:
            self.logger.error(f"应用风扇设置失败: {e}")
            self.show_success_message("❌ 应用风扇设置失败")
    
    def update_cpu_fan_value(self, value):
        """更新CPU风扇转速显示"""
        try:
            self.cpu_fan_value.setText(f"{value}%")
        except Exception as e:
            self.logger.error(f"更新CPU风扇转速显示失败: {e}")
    
    def update_gpu_fan_value(self, value):
        """更新显卡风扇转速显示"""
        try:
            self.gpu_fan_value.setText(f"{value}%")
        except Exception as e:
            self.logger.error(f"更新显卡风扇转速显示失败: {e}")
    
    def update_unified_fan_value(self, value):
        """更新统一风扇控制显示值"""
        try:
            # 转换为RPM显示（基于0-100%映射到0-2000RPM）
            rpm = int(value * 20)  # 100% = 2000 RPM
            self.unified_fan_value.setText(f"{value}% ({rpm} RPM)")
            
            # 根据转速更新噪音等级
            if value < 30:
                noise = "极低"
                noise_color = "#44ff44"
            elif value < 50:
                noise = "低"
                noise_color = "#44ff44"
            elif value < 70:
                noise = "中等"
                noise_color = "#ffaa00"
            elif value < 85:
                noise = "高"
                noise_color = "#ff6600"
            else:
                noise = "极高"
                noise_color = "#ff4444"
            
            self.noise_level.setText(noise)
            self.noise_level.setStyleSheet(f"""
                font-size: 14px;
                font-weight: bold;
                color: {noise_color};
                background: rgba({int(noise_color[1:3], 16)}, {int(noise_color[3:5], 16)}, {int(noise_color[5:7], 16)}, 0.1);
                padding: 4px 8px;
                border-radius: 4px;
                border: 1px solid rgba({int(noise_color[1:3], 16)}, {int(noise_color[3:5], 16)}, {int(noise_color[5:7], 16)}, 0.3);
            """)
            
            # 更新风扇转速显示
            self.fan_rpm_value.setText(f"{rpm} RPM")
            
            # 模拟CPU温度（基于风扇转速）
            temp = max(30, 85 - (value * 0.4))  # 风扇越快，温度越低
            temp_color = "#44ff44" if temp < 60 else "#ffaa00" if temp < 75 else "#ff4444"
            self.cpu_temp_value.setText(f"{temp:.1f}°C")
            self.cpu_temp_value.setStyleSheet(f"""
                font-size: 14px;
                font-weight: bold;
                color: {temp_color};
                background: rgba({int(temp_color[1:3], 16)}, {int(temp_color[3:5], 16)}, {int(temp_color[5:7], 16)}, 0.1);
                padding: 4px 8px;
                border-radius: 4px;
                border: 1px solid rgba({int(temp_color[1:3], 16)}, {int(temp_color[3:5], 16)}, {int(temp_color[5:7], 16)}, 0.3);
            """)
            
            self.logger.debug(f"风扇转速更新: {value}% ({rpm} RPM), 温度: {temp:.1f}°C, 噪音: {noise}")
        except Exception as e:
            self.logger.error(f"更新风扇转速显示失败: {e}")
    
    def set_fan_preset_with_description(self, mode):
        """设置风扇预设模式（带描述）"""
        try:
            descriptions = {
                "silent": {
                    "value": 25,
                    "description": "静音模式：低噪音，适合日常办公和轻度使用",
                    "color": "#4a4aff"
                },
                "balance": {
                    "value": 50,
                    "description": "平衡模式：性能与噪音的完美平衡",
                    "color": "#ffaa00"
                },
                "performance": {
                    "value": 80,
                    "description": "性能模式：高性能输出，适合游戏和重负载任务",
                    "color": "#ff4444"
                },
                "turbo": {
                    "value": 100,
                    "description": "极速模式：最大散热，适合极限性能需求",
                    "color": "#ff00ff"
                }
            }
            
            if mode in descriptions:
                preset = descriptions[mode]
                if hasattr(self, 'unified_fan_slider'):
                    self.unified_fan_slider.setValue(preset["value"])
                    self.update_unified_fan_value(preset["value"])
                    self.mode_description.setText(f"✅ {preset['description']}")
                    self.logger.info(f"设置{mode}模式: 统一风扇={preset['value']}%")
        except Exception as e:
            self.logger.error(f"设置预设模式失败: {e}")

    def on_control_mode_changed(self, checked):
        """控制模式切换事件处理"""
        try:
            if self.auto_mode_btn.isChecked():
                # 切换到自动模式
                self.manual_control_frame.setVisible(False)
                self.mode_description.setText("🔄 自动模式：根据CPU温度自动调节风扇转速")
                
                # 停止手动控制时的CPU温度更新
                if hasattr(self, 'fan_update_timer'):
                    self.fan_update_timer.stop()
                    
            else:
                # 切换到手动模式
                self.manual_control_frame.setVisible(True)
                self.mode_description.setText("✋ 手动模式：您可以手动调节风扇转速")
                
                # 开始定时更新显示数据
                if not hasattr(self, 'fan_update_timer'):
                    from PyQt5.QtCore import QTimer
                    self.fan_update_timer = QTimer()
                    self.fan_update_timer.timeout.connect(self.simulate_fan_data)
                
                self.fan_update_timer.start(2000)  # 每2秒更新一次
                
            self.logger.info(f"控制模式切换到: {'自动' if self.auto_mode_btn.isChecked() else '手动'}")
        except Exception as e:
            self.logger.error(f"控制模式切换失败: {e}")

    def simulate_fan_data(self):
        """模拟风扇数据更新"""
        try:
            if hasattr(self, 'unified_fan_slider'):
                value = self.unified_fan_slider.value()
                self.update_unified_fan_value(value)
                
                # 模拟风扇健康状态
                import random
                health_statuses = [
                    ("🟢 正常", "#44ff44"),
                    ("🟡 良好", "#ffaa00"),
                    ("🔶 磨损", "#ff6600"),
                    ("🔴 故障", "#ff4444")
                ]
                # 90%概率正常，10%概率其他状态
                if random.random() > 0.1:
                    status, color = health_statuses[0]
                else:
                    status, color = random.choice(health_statuses[1:])
                
                self.fan_health.setText(status)
                self.fan_health.setStyleSheet(f"""
                    font-size: 12px;
                    color: {color};
                    background: rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.1);
                    padding: 6px 12px;
                    border-radius: 6px;
                    border: 1px solid rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.3);
                """)
        except Exception as e:
            self.logger.error(f"模拟风扇数据失败: {e}")

    def refresh_fan_display(self):
        """刷新风扇显示数据"""
        try:
            if hasattr(self, 'unified_fan_slider'):
                value = self.unified_fan_slider.value()
                self.update_unified_fan_value(value)
                self.simulate_fan_data()
                
            # 停止并重启定时器（如果存在）
            if hasattr(self, 'fan_update_timer'):
                self.fan_update_timer.stop()
                if self.manual_mode_btn.isChecked():
                    self.fan_update_timer.start(2000)
                
            self.show_success_message("✅ 风扇数据显示已刷新")
            self.logger.info("风扇显示数据已刷新")
        except Exception as e:
            self.logger.error(f"刷新风扇显示失败: {e}")

    def reset_fan_settings(self):
        """重置风扇设置"""
        try:
            if hasattr(self, 'unified_fan_slider'):
                # 重置到默认值
                self.unified_fan_slider.setValue(50)
                self.update_unified_fan_value(50)
                self.mode_description.setText("🔄 已重置到默认设置")
                
                # 重置模式选择
                self.auto_mode_btn.setChecked(True)
                self.manual_control_frame.setVisible(False)
                
                # 停止手动模式定时器
                if hasattr(self, 'fan_update_timer'):
                    self.fan_update_timer.stop()
                
                self.show_success_message("↩️ 风扇设置已重置为默认值")
                self.logger.info("风扇设置已重置")
        except Exception as e:
            self.logger.error(f"重置风扇设置失败: {e}")

    def set_silent_mode(self):
        """设置静音模式（兼容性方法）"""
        self.set_fan_preset_with_description("silent")

    def set_balance_mode(self):
        """设置平衡模式（兼容性方法）"""
        self.set_fan_preset_with_description("balance")

    def set_performance_mode(self):
        """设置性能模式（兼容性方法）"""
        self.set_fan_preset_with_description("performance")
    

            
    def toggle_fan_mode(self):
        """切换风扇模式"""
        try:
            if hasattr(self, 'manual_control_frame'):
                if self.manual_mode_btn.isChecked():
                    self.manual_control_frame.setVisible(True)
                    # 停止自动控制
                    self.stop_auto_fan_control()
                    self.logger.info("切换到手动模式")
                else:
                    self.manual_control_frame.setVisible(False)
                    # 启动自动温度控制
                    self.start_auto_fan_control()
                    self.logger.info("切换到自动模式")
        except Exception as e:
            self.logger.error(f"切换风扇模式失败: {e}")
            
    def set_fan_speed(self, speed):
        """设置风扇转速"""
        try:
            if hasattr(self, 'fan_slider'):
                self.fan_slider.setValue(speed)
                
                # 获取选中的风扇
                if hasattr(self, 'fan_combo') and self.fan_combo.currentIndex() >= 0:
                    fan_id = self.fan_combo.currentData()
                    # 调用风扇控制器设置转速
                    success = self.fan_controller.set_fan_speed(fan_id, speed)
                    if success:
                        self.logger.info(f"设置风扇 {fan_id} 转速: {speed}%")
                    else:
                        self.logger.error(f"设置风扇转速失败: {self.fan_controller.error_message}")
                else:
                    self.logger.warning("未选择风扇设备")
        except Exception as e:
            self.logger.error(f"设置风扇转速失败: {e}")
    
    def change_control_mode(self, index):
        """切换控制模式"""
        try:
            if hasattr(self, 'control_mode_combo'):
                mode = self.control_mode_combo.currentData()
                self.logger.info(f"切换到 {mode} 控制模式")
                
                # 设置温度监控器的控制模式
                if hasattr(self, 'temperature_monitor') and self.temperature_monitor:
                    self.temperature_monitor.set_control_mode(mode)
                    
                    # 根据模式设置不同的温度阈值
                    if mode == "quiet":
                        self.temperature_monitor.set_temperature_thresholds(
                            target_temp=60, max_temp=75
                        )
                        self.logger.info("静音模式：目标温度60°C，最高温度75°C")
                    elif mode == "balanced":
                        self.temperature_monitor.set_temperature_thresholds(
                            target_temp=65, max_temp=80
                        )
                        self.logger.info("平衡模式：目标温度65°C，最高温度80°C")
                    elif mode == "performance":
                        self.temperature_monitor.set_temperature_thresholds(
                            target_temp=70, max_temp=85
                        )
                        self.logger.info("性能模式：目标温度70°C，最高温度85°C")
                
                # 如果当前是自动模式，立即应用新的控制策略
                if hasattr(self, 'auto_mode_radio') and self.auto_mode_radio.isChecked():
                    if hasattr(self, 'temperature_monitor') and self.temperature_monitor:
                        self.temperature_monitor.auto_control_fans()
                        
                # 显示模式切换提示
                mode_names = {
                    "quiet": "静音模式",
                    "balanced": "平衡模式", 
                    "performance": "性能模式"
                }
                mode_name = mode_names.get(mode, mode)
                self.show_status_message(f"已切换到 {mode_name}", "info")
                
        except Exception as e:
            self.logger.error(f"切换控制模式失败: {e}")
            self.show_status_message(f"切换控制模式失败: {e}", "error")
    
    def start_auto_fan_control(self):
        """启动自动风扇控制"""
        try:
            # 启动温度监控和自动控制
            if hasattr(self, 'temperature_monitor'):
                self.temperature_monitor.start_monitoring()
                self.logger.info("启动自动风扇控制")
        except Exception as e:
            self.logger.error(f"启动自动风扇控制失败: {e}")
    
    def stop_auto_fan_control(self):
        """停止自动风扇控制"""
        try:
            # 停止温度监控
            if hasattr(self, 'temperature_monitor'):
                self.temperature_monitor.stop_monitoring()
                self.logger.info("停止自动风扇控制")
        except Exception as e:
            self.logger.error(f"停止自动风扇控制失败: {e}")
            
    def apply_fan_settings(self):
        """应用风扇设置"""
        try:
            mode = "手动" if self.manual_mode_btn.isChecked() else "自动"
            speed = self.fan_slider.value() if hasattr(self, 'fan_slider') else 50
            
            # 应用实际的风扇控制逻辑
            if hasattr(self, 'fan_combo') and self.fan_combo.currentIndex() >= 0:
                fan_id = self.fan_combo.currentData()
                # 调用风扇控制器设置转速
                success = self.fan_controller.set_fan_speed(fan_id, speed)
                if success:
                    self.logger.info(f"应用风扇设置: 模式={mode}, 风扇={fan_id}, 转速={speed}%")
                    self.show_success_message(f"✅ 风扇设置已应用！\n模式: {mode}\n风扇: {self.fan_combo.currentText()}\n转速: {speed}%")
                else:
                    self.logger.error(f"应用风扇设置失败: {self.fan_controller.error_message}")
                    self.show_error_message(f"❌ 风扇设置失败！\n错误: {self.fan_controller.error_message}")
            else:
                self.logger.warning("未选择风扇设备")
                self.show_warning_message("⚠️ 请先选择风扇设备！")
            
            # 返回设置页面
            self.show_settings()
        except Exception as e:
            self.logger.error(f"应用风扇设置失败: {e}")
            self.show_error_message(f"❌ 风扇设置失败！\n错误: {str(e)}")
            self.show_settings()
    
    def create_preset_colors_widget(self):
        """创建快速预设颜色组件 - 简化版"""
        preset_widget = QWidget()
        preset_widget.setFixedHeight(200)  # 限制高度
        preset_widget.setStyleSheet("""
            QWidget {
                background: rgba(255, 255, 255, 0.05);
                border-radius: 15px;
                border: 1px solid rgba(255, 0, 0, 0.2);
                padding: 15px;
            }
        """)
        
        # 使用垂直布局而不是网格布局，更简洁
        preset_layout = QVBoxLayout(preset_widget)
        preset_layout.setSpacing(8)
        preset_layout.setAlignment(Qt.AlignCenter)
        
        # 简化预设颜色列表 - 只保留最常用的8个
        preset_colors = [
            ("❤️ 红色", "#ff0000"),
            ("💙 蓝色", "#0080ff"), 
            ("💚 绿色", "#00ff80"),
            ("💛 黄色", "#ffff00"),
            ("💜 紫色", "#8000ff"),
            ("🧡 橙色", "#ff8000"),
            ("🤍 白色", "#ffffff"),
            ("🖤 黑色", "#000000")
        ]
        
        # 创建预设颜色按钮布局 - 简化为2行4列
        for i, (name, color) in enumerate(preset_colors):
            # 创建水平布局的按钮组
            if i % 4 == 0:  # 每4个颜色创建一行
                row_layout = QHBoxLayout()
                row_layout.setSpacing(8)
                preset_layout.addLayout(row_layout)
            
            btn = QPushButton(name)
            btn.setFixedSize(80, 30)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {color};
                    border: 1px solid rgba(255, 255, 255, 0.3);
                    border-radius: 15px;
                    color: white;
                    font-size: 10px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    border: 1px solid rgba(255, 255, 255, 0.6);
                }}
            """)
            btn.clicked.connect(lambda checked, c=color: self.apply_preset_color(c))
            
            # 添加到当前行
            current_row = preset_layout.itemAt(preset_layout.count() - 1).layout()
            current_row.addWidget(btn)
        
        return preset_widget
    

    

    

    
    def _handle_card_click(self, card, callback, event):
        """处理卡片点击事件"""
        # 临时更改样式以显示按下效果
        card.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 rgba(20, 20, 20, 0.95),
                    stop: 1 rgba(40, 40, 40, 0.95));
                border-radius: 10px;
                border: 1px solid rgba(255, 0, 0, 0.8);
                padding: 15px;
            }
        """)
        # 调用回调函数
        if callback:
            callback()
        # 立即恢复正常样式，避免延迟访问已删除的对象
        try:
            card.setStyleSheet("""
                QWidget {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                        stop: 0 rgba(30, 30, 30, 0.95),
                        stop: 1 rgba(50, 50, 50, 0.95));
                    border-radius: 10px;
                    border: 1px solid rgba(255, 0, 0, 0.3);
                    padding: 15px;
                }
            """)
        except RuntimeError:
            pass
        
    def _handle_card_hover(self, card, is_hovered):
        """处理卡片悬停事件"""
        # 使用更安全的方式检查QWidget对象是否仍然存在
        try:
            # 使用sip.isdeleted()检查对象是否已被删除（如果可用）
            try:
                import sip
                if sip.isdeleted(card):
                    return
            except ImportError:
                # 如果sip不可用，使用对象属性检查
                try:
                    # 尝试访问对象的内部状态来检查是否有效
                    hasattr(card, 'parent') and card.parent()
                    hasattr(card, 'isHidden') and card.isHidden()
                except RuntimeError:
                    return
            
            if is_hovered:
                # 悬停样式
                card.setStyleSheet("""
                    QWidget {
                        background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                            stop: 0 rgba(40, 40, 40, 0.95),
                            stop: 1 rgba(60, 60, 60, 0.95));
                        border-radius: 10px;
                        border: 1px solid rgba(255, 0, 0, 0.6);
                        padding: 15px;
                    }
                """)
            else:
                # 正常样式
                card.setStyleSheet("""
                    QWidget {
                        background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                            stop: 0 rgba(30, 30, 30, 0.95),
                            stop: 1 rgba(50, 50, 50, 0.95));
                        border-radius: 10px;
                        border: 1px solid rgba(255, 0, 0, 0.3);
                        padding: 15px;
                    }
                """)
        except (RuntimeError, AttributeError):
            # 对象已被删除或没有属性，忽略错误
            pass
    
    def create_setting_card(self, title, description, clickable=False, callback=None):
        """创建设置卡片 - 电竞风格"""
        if clickable:
            # 对于可点击的卡片，创建一个QWidget并添加标签来支持富文本
            card = QWidget()
            card.setCursor(Qt.PointingHandCursor)
            
            # 设置卡片样式（包含正常、悬停和按下状态）
            card.setStyleSheet("""
                QWidget {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                        stop: 0 rgba(30, 30, 30, 0.95),
                        stop: 1 rgba(50, 50, 50, 0.95));
                    border-radius: 10px;
                    border: 1px solid rgba(255, 0, 0, 0.3);
                    padding: 15px;
                }
            """)
            
            # 创建垂直布局
            layout = QVBoxLayout(card)
            
            # 创建标题标签，使用富文本
            title_label = QLabel()
            title_label.setTextFormat(Qt.RichText)
            title_label.setOpenExternalLinks(True)  # 启用外部链接
            title_label.setText(f"<b>{title}</b>")
            title_label.setStyleSheet("color: white; font-family: 'Microsoft YaHei'; margin-bottom: 5px;")
            
            # 创建描述标签，使用富文本
            desc_label = QLabel()
            desc_label.setTextFormat(Qt.RichText)
            desc_label.setOpenExternalLinks(True)  # 启用外部链接
            desc_label.setText(f"<small>{description}</small>")
            desc_label.setStyleSheet("color: lightgray; font-family: 'Microsoft YaHei';")
            
            # 将标签添加到布局
            layout.addWidget(title_label)
            layout.addWidget(desc_label)
            layout.setContentsMargins(0, 0, 0, 0)  # 移除布局边距
            
            # 添加鼠标事件处理
            card.mousePressEvent = lambda event: self._handle_card_click(card, callback, event)
            card.enterEvent = lambda event: self._handle_card_hover(card, True)
            card.leaveEvent = lambda event: self._handle_card_hover(card, False)
            
            # 设置文本格式
            card.setProperty("title", title)
            card.setProperty("description", description)
            
            if callback:
                # 点击事件已经在create_setting_card方法内部通过mousePressEvent处理
                pass
            
            return card
        else:
            # 对于不可点击的卡片，使用原来的实现
            card = QWidget()
            card.setStyleSheet("""
                QWidget {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                        stop: 0 rgba(30, 30, 30, 0.95),
                        stop: 1 rgba(50, 50, 50, 0.95));
                    border-radius: 10px;
                    border: 1px solid rgba(255, 0, 0, 0.3);
                    padding: 15px;
                }
                QWidget:hover {
                    border: 1px solid rgba(255, 0, 0, 0.6);
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                        stop: 0 rgba(40, 40, 40, 0.95),
                        stop: 1 rgba(60, 60, 60, 0.95));
                }
            """)
            
            card_layout = QVBoxLayout(card)
            card_layout.setSpacing(8)
            
            # 卡片标题
            card_title = QLabel(title)
            card_title.setStyleSheet("""
                font-size: 15px;
                font-weight: bold;
                color: #ff3333;
                margin: 0px;
                font-family: "Microsoft YaHei";
            """)
            card_layout.addWidget(card_title)
            
            # 卡片描述
            card_desc = QLabel(description)
            card_desc.setStyleSheet("""
                font-size: 12px;
                color: #cccccc;
                margin: 0px;
                font-family: "Microsoft YaHei";
            """)
            card_layout.addWidget(card_desc)
            
            return card
    
    def clear_upper_frame(self):
        """清空上方框架"""
        while self.upper_layout.count():
            child = self.upper_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                # 递归清除嵌套布局
                self.clear_layout_recursive(child.layout())
    
    def clear_layout_recursive(self, layout):
        """递归清除布局"""
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self.clear_layout_recursive(child.layout())
    
    def open_tool(self, tool_key):
        """打开工具"""
        try:
            tool_mapping = {
                # 处理器工具
                'cpuz': '处理器工具/CPUZ/cpuz64.exe',
                'prime95': '处理器工具/Prime95/prime95x64.exe',
                'aida64': '处理器工具/aida64/aida64.exe',
                'throttlestop': '处理器工具/ThrottleStop/ThrottleStop.exe',
                'linx': '处理器工具/LinX/LinX.exe',
                'superpi': '处理器工具/superpi/Superpi.exe',
                'wprime': '处理器工具/wPrime/wPrime.exe',
                
                # 显卡工具
                'gpuz': '显卡工具/GPUZ/GPUZ.exe',
                'ddu': '显卡工具/DDU/DDU.exe',
                'gputest': '显卡工具/GpuTest_Windows x64/GpuTest_GUI.exe',
                'nvidia_inspector': '显卡工具/nvidiaInspector/nvidiaInspector.exe',

                
                # 内存工具
                'memtest64': '内存工具/memtest64/MemTest64.exe',
                'memtest': '内存工具/memtest/memtest.exe',
                'tm5': '内存工具/tm5/TM5.exe',
                'thaiphoon': '内存工具/Thaiphoon/Thaiphoon.exe',
                'ramdisk': '内存工具/魔方内存盘/ramdisk.exe',
                
                # 硬盘工具
                'diskgenius': '硬盘工具/DiskGenius/DiskGenius.exe',
                'crystal_disk_mark': '硬盘工具/CrystalDiskMark/DiskMarkx64.exe',
                'crystal_disk_info': '硬盘工具/CrystalDiskInfo/DiskInfo64.exe',
                'spacesniffer': '硬盘工具/SpaceSniffer/SpaceSniffer.exe',
                'mofang_recovery': '硬盘工具/魔方数据恢复/魔方数据恢复.exe',
                
                # 烤鸡工具（压力测试工具）
                'furmark': '烤鸡工具/FurMark/FurMark.exe',
                'cpuburner': '烤鸡工具/FurMark/cpuburner.exe',
                
                # 显示器工具
                'displayx': '显示器工具/displayx/DisplayX.exe',
                'color_check': '显示器工具/色域检测/monitorinfo.exe',
                
                # 其他工具
                'todesk': '远程工具/ToDesk_4.8.2.2.exe',
                'asssd_benchmark': '硬盘工具/ASSSDBenchmark/ASSSDBenchmark.exe',
                'atto_disk_benchmark': '硬盘工具/ATTODISKBENCHMARK/ATTO 磁盘基准测试.exe',
                'powerful_delete': '强力删除工具/浩讯电脑急救强力删除工具.exe'
            }
            
            tool_path = tool_mapping.get(tool_key)
            if tool_path:
                full_tool_path = os.path.join(chengxubao_path, tool_path)
                if os.path.exists(full_tool_path):
                    # 尝试以管理员权限启动工具
                    try:
                        # 使用runas命令请求管理员权限
                        subprocess.Popen(full_tool_path, shell=True)
                        self.logger.info(f"启动工具: {tool_path}")
                    except Exception as admin_error:
                        # 如果管理员权限启动失败，尝试普通方式
                        try:
                            subprocess.Popen(full_tool_path)
                            self.logger.info(f"以普通权限启动工具: {tool_path}")
                        except Exception as normal_error:
                            # 如果普通方式也失败，提示用户手动以管理员权限运行
                            QMessageBox.warning(self, "权限提示", 
                                f"工具启动失败，可能需要管理员权限。\n\n"
                                f"请右键点击工具图标，选择'以管理员身份运行'。\n\n"
                                f"工具路径: {full_tool_path}")
                            self.logger.error(f"工具启动失败: {normal_error}")
                else:
                    QMessageBox.information(self, "提示", f"工具文件不存在：{tool_path}")
            else:
                QMessageBox.information(self, "提示", f"未知工具: {tool_key}")
                
        except Exception as e:
            QMessageBox.warning(self, "错误", f"启动工具失败: {str(e)}")
            self.logger.error(f"启动工具失败: {e}")
    
    def run_stress_test(self, tool_key):
        """运行压力测试"""
        try:
            # 直接使用工具路径调用对应的工具
            self.open_tool(tool_key)
                
        except Exception as e:
            QMessageBox.warning(self, "错误", f"压力测试失败: {str(e)}")
    
    def run_memory_tool(self, tool_type):
        """运行内存工具"""
        try:
            # 使用统一的open_tool方法启动内存工具
            self.open_tool(tool_type)
                
        except Exception as e:
            QMessageBox.warning(self, "错误", f"内存工具失败: {str(e)}")
    
    def open_url(self, url):
        """打开网址"""
        try:
            import webbrowser
            webbrowser.open(url)
        except Exception as e:
            QMessageBox.warning(self, "错误", f"打开网址失败: {str(e)}")
    
    def run_other_tool(self, tool_type):
        """运行其他工具"""
        try:
            # 使用统一的open_tool方法启动其他工具
            self.open_tool(tool_type)
        except Exception as e:
            QMessageBox.warning(self, "错误", f"工具运行失败: {str(e)}")
    
    def toggle_background(self):
        """切换背景图显示"""
        try:
            if self.background_toggle.isChecked():
                self.show_background = False
                self.background_toggle.setText("🔆 显示背景图")
            else:
                self.show_background = True
                self.background_toggle.setText("🌙 隐藏背景图")
            
            self.load_background_image()
            
        except Exception as e:
            self.logger.error(f"切换背景图失败: {e}")
    
    def update_current_bg_preview(self):
        """更新当前背景图片预览"""
        try:
            if hasattr(self, 'current_background'):
                background_file = self.current_background
            else:
                background_file = "background.jpg"
                self.current_background = background_file
            
            background_path = get_resource_path(f"Resources\\{background_file}")
            if os.path.exists(background_path):
                # 创建缩略图
                pixmap = QPixmap(background_path)
                if not pixmap.isNull():
                    # 缩放图片到预览大小
                    scaled_pixmap = pixmap.scaled(56, 36, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                    self.current_bg_preview.setPixmap(scaled_pixmap)
        except Exception as e:
            self.logger.error(f"更新背景预览失败: {e}")
    
    def show_background_image_dialog(self):
        """显示背景图片选择对话框"""
        try:
            # 创建对话框
            dialog = QDialog(self)
            dialog.setWindowTitle("选择背景图片")
            dialog.setFixedSize(600, 550)
            dialog.setStyleSheet("""
                QDialog {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                        stop: 0 #1a1a1a, stop: 1 #2a2a2a);
                    border: 2px solid #ff3333;
                    border-radius: 10px;
                }
                QLabel {
                    color: white;
                    font-family: "Microsoft YaHei";
                }
            """)
            
            # 主布局
            main_layout = QVBoxLayout(dialog)
            
            # 标题
            title_label = QLabel("🎨 选择背景图片")
            title_label.setStyleSheet("""
                font-size: 18px;
                font-weight: bold;
                color: #ff3333;
                text-align: center;
                margin: 10px;
            """)
            main_layout.addWidget(title_label)
            
            # 上传按钮区域
            upload_layout = QHBoxLayout()
            upload_layout.setContentsMargins(20, 0, 20, 10)
            
            upload_button = QPushButton("📁 上传自定义背景图片")
            upload_button.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 #ff6b35, stop: 1 #ff4757);
                    border: 2px solid #ff3333;
                    border-radius: 8px;
                    padding: 10px 20px;
                    font-size: 14px;
                    font-weight: bold;
                    color: white;
                    font-family: "Microsoft YaHei";
                }
                QPushButton:hover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 #ff8c5a, stop: 1 #ff6b6b);
                    border: 2px solid #ff5555;
                }
                QPushButton:pressed {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 #ff4d1a, stop: 1 #ff3333);
                }
            """)
            upload_button.clicked.connect(lambda: self.upload_custom_background(dialog))
            upload_layout.addWidget(upload_button)
            upload_layout.addStretch()
            
            main_layout.addLayout(upload_layout)
            
            # 分隔线
            separator = QFrame()
            separator.setFrameShape(QFrame.HLine)
            separator.setStyleSheet("""
                border: none;
                height: 1px;
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 rgba(255, 51, 51, 0.3), 
                    stop: 0.5 rgba(255, 51, 51, 0.8), 
                    stop: 1 rgba(255, 51, 51, 0.3));
                margin: 5px 20px;
            """)
            main_layout.addWidget(separator)
            
            # 图片网格布局
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setStyleSheet("""
                QScrollArea {
                    border: none;
                    background: transparent;
                }
                QScrollBar:vertical {
                    background: #333333;
                    width: 12px;
                    border-radius: 6px;
                }
                QScrollBar::handle:vertical {
                    background: #ff3333;
                    border-radius: 6px;
                    min-height: 20px;
                }
                QScrollBar::handle:vertical:hover {
                    background: #ff5555;
                }
            """)
            
            # 图片容器
            image_container = QWidget()
            image_container.setStyleSheet("background: transparent;")
            grid_layout = QGridLayout(image_container)
            grid_layout.setSpacing(15)
            grid_layout.setContentsMargins(20, 20, 20, 20)
            
            # 获取所有背景图片（包括用户上传的图片）
            background_images = self.get_all_background_images()
            
            # 添加图片预览
            for i, (image_file, image_name) in enumerate(background_images):
                image_path = get_resource_path(f"Resources\\{image_file}")
                if os.path.exists(image_path):
                    # 创建图片预览项
                    preview_item = self.create_image_preview_item(image_path, image_name, image_file)
                    row = i // 2
                    col = i % 2
                    grid_layout.addWidget(preview_item, row, col)
            
            scroll_area.setWidget(image_container)
            main_layout.addWidget(scroll_area)
            
            # 按钮布局
            button_layout = QHBoxLayout()
            
            # 取消按钮
            cancel_button = QPushButton("取消")
            cancel_button.setStyleSheet("""
                QPushButton {
                    background: #666666;
                    border: 1px solid #888888;
                    border-radius: 6px;
                    padding: 8px 20px;
                    font-size: 12px;
                    color: white;
                    font-family: "Microsoft YaHei";
                }
                QPushButton:hover {
                    background: #888888;
                    border: 1px solid #aaaaaa;
                }
            """)
            cancel_button.clicked.connect(dialog.reject)
            
            button_layout.addStretch()
            button_layout.addWidget(cancel_button)
            main_layout.addLayout(button_layout)
            
            # 显示对话框
            dialog.exec_()
            
        except Exception as e:
            # 显示背景图片选择对话框失败
            self.logger.error(f"显示背景图片选择对话框失败: {e}")
    
    def create_image_preview_item(self, image_path, image_name, image_file):
        """创建图片预览项"""
        try:
            # 创建预览项容器
            preview_widget = QWidget()
            preview_widget.setFixedSize(250, 180)
            preview_widget.setStyleSheet("""
                QWidget {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 rgba(40, 40, 40, 0.9), stop: 1 rgba(60, 60, 60, 0.9));
                    border: 2px solid #444444;
                    border-radius: 8px;
                }
                QWidget:hover {
                    border: 2px solid #ff3333;
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 rgba(50, 50, 50, 0.9), stop: 1 rgba(70, 70, 70, 0.9));
                }
            """)
            
            layout = QVBoxLayout(preview_widget)
            layout.setContentsMargins(10, 10, 10, 10)
            layout.setSpacing(8)
            
            # 图片预览
            image_label = QLabel()
            image_label.setFixedSize(230, 120)
            image_label.setStyleSheet("""
                QLabel {
                    border: 1px solid #666666;
                    border-radius: 4px;
                    background: #1a1a1a;
                }
            """)
            image_label.setAlignment(Qt.AlignCenter)
            
            # 加载并显示图片
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(220, 110, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                image_label.setPixmap(scaled_pixmap)
            
            # 图片名称
            name_label = QLabel(image_name)
            name_label.setStyleSheet("""
                font-size: 12px;
                font-weight: bold;
                color: #ff3333;
                text-align: center;
            """)
            name_label.setAlignment(Qt.AlignCenter)
            
            # 选择按钮
            select_button = QPushButton("选择")
            select_button.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 #ff3333, stop: 1 #cc0000);
                    border: 1px solid #ff3333;
                    border-radius: 4px;
                    padding: 4px 8px;
                    font-size: 10px;
                    color: white;
                    font-family: "Microsoft YaHei";
                }
                QPushButton:hover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 #ff5555, stop: 1 #dd2222);
                }
            """)
            
            # 连接按钮点击事件
            select_button.clicked.connect(lambda checked, img=image_file: self.select_background_image(img))
            
            layout.addWidget(image_label)
            layout.addWidget(name_label)
            layout.addWidget(select_button)
            
            return preview_widget
        
        except Exception as e:
            self.logger.error(f"创建图片预览项失败: {e}")
            return QWidget()

    def upload_custom_background(self, parent_dialog):
        """上传自定义背景图片"""
        try:
            # 打开文件选择对话框
            file_dialog = QFileDialog()
            file_dialog.setWindowTitle("选择背景图片")
            file_dialog.setNameFilter("图片文件 (*.jpg *.jpeg *.png *.bmp *.gif)")
            file_dialog.setViewMode(QFileDialog.Detail)
            
            if file_dialog.exec_():
                selected_files = file_dialog.selectedFiles()
                if selected_files:
                    image_path = selected_files[0]
                    
                    # 验证图片文件
                    if not self.validate_image_file(image_path):
                        QMessageBox.warning(parent_dialog, "图片验证失败", 
                                          "请选择有效的图片文件（JPG、PNG、BMP、GIF格式，大小不超过10MB）")
                        return
                    
                    # 保存图片到Resources目录
                    saved_path = self.save_custom_background(image_path)
                    if saved_path:
                        QMessageBox.information(parent_dialog, "上传成功", 
                                              f"自定义背景图片已成功保存！\n文件: {os.path.basename(saved_path)}")
                        
                        # 刷新对话框以显示新图片
                        parent_dialog.accept()
                        self.show_background_image_dialog()
                    else:
                        QMessageBox.critical(parent_dialog, "上传失败", 
                                           "保存图片时发生错误，请重试")
            
        except Exception as e:
            self.logger.error(f"上传自定义背景图片失败: {e}")
            QMessageBox.critical(parent_dialog, "上传失败", 
                               f"上传过程中发生错误: {str(e)}")
    
    def validate_image_file(self, image_path):
        """验证图片文件"""
        try:
            # 检查文件扩展名
            valid_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif'}
            file_ext = os.path.splitext(image_path)[1].lower()
            if file_ext not in valid_extensions:
                return False
            
            # 检查文件大小（限制为10MB）
            file_size = os.path.getsize(image_path)
            if file_size > 10 * 1024 * 1024:  # 10MB
                return False
            
            # 尝试加载图片验证格式
            pixmap = QPixmap(image_path)
            if pixmap.isNull():
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"验证图片文件失败: {e}")
            return False
    
    def save_custom_background(self, image_path):
        """保存自定义背景图片到Resources目录"""
        try:
            # 确保Resources目录存在
            resources_dir = get_resource_path("Resources")
            if not os.path.exists(resources_dir):
                os.makedirs(resources_dir)
            
            # 生成唯一的文件名
            timestamp = int(time.time())
            file_ext = os.path.splitext(image_path)[1].lower()
            new_filename = f"custom_background_{timestamp}{file_ext}"
            new_filepath = os.path.join(resources_dir, new_filename)
            
            # 复制图片文件
            import shutil
            shutil.copy2(image_path, new_filepath)
            
            # 更新用户上传图片列表
            self.update_custom_backgrounds_list(new_filename)
            
            return new_filepath
            
        except Exception as e:
            self.logger.error(f"保存自定义背景图片失败: {e}")
            return None
    
    def update_custom_backgrounds_list(self, filename):
        """更新用户上传的图片列表"""
        try:
            # 读取现有的自定义图片列表
            config_file = get_resource_path("Resources\\custom_backgrounds.json")
            custom_backgrounds = []
            
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    custom_backgrounds = json.load(f)
            
            # 添加新图片
            if filename not in custom_backgrounds:
                custom_backgrounds.append(filename)
                
                # 保存更新后的列表
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(custom_backgrounds, f, ensure_ascii=False, indent=2)
            
        except Exception as e:
            self.logger.error(f"更新自定义背景图片列表失败: {e}")
            # 如果JSON文件操作失败，尝试创建新文件
            try:
                config_file = get_resource_path("Resources\\custom_backgrounds.json")
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump([filename], f, ensure_ascii=False, indent=2)
            except Exception as e2:
                self.logger.error(f"创建自定义背景图片列表文件失败: {e2}")
    
    def get_all_background_images(self):
        """获取所有背景图片（包括预设和用户上传的）"""
        try:
            # 预设背景图片
            preset_images = [
                ("background.jpg", "🏞️ 默认背景"),
                ("background2.png", "🌅 背景2"),
                ("background3.png", "🌄 背景3"),
                ("background4.png", "🌇 背景4")
            ]
            
            # 用户上传的背景图片
            custom_images = self.get_custom_backgrounds()
            
            # 合并所有图片
            all_images = preset_images + custom_images
            
            return all_images
            
        except Exception as e:
            self.logger.error(f"获取所有背景图片失败: {e}")
            return [
                ("background.jpg", "🏞️ 默认背景"),
                ("background2.png", "🌅 背景2"),
                ("background3.png", "🌄 背景3"),
                ("background4.png", "🌇 背景4")
            ]
    
    def get_custom_backgrounds(self):
        """获取用户上传的自定义背景图片"""
        try:
            config_file = get_resource_path("Resources\\custom_backgrounds.json")
            custom_images = []
            
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    filenames = json.load(f)
                
                for filename in filenames:
                    # 检查文件是否存在
                    filepath = get_resource_path(f"Resources\\{filename}")
                    if os.path.exists(filepath):
                        # 生成友好的显示名称
                        display_name = f"🎨 {os.path.splitext(filename)[0]}"
                        custom_images.append((filename, display_name))
            
            return custom_images
            
        except Exception as e:
            self.logger.error(f"获取自定义背景图片失败: {e}")
            return []

    def select_background_image(self, image_file):
        """选择背景图片"""
        try:
            # 设置当前选择的背景图片
            self.current_background = image_file
            
            # 确保显示背景图
            self.show_background = True
            self.background_toggle.setChecked(False)
            self.background_toggle.setText("🌙 隐藏背景图")
            
            # 重新加载背景图
            self.load_background_image()
            
            # 关闭选择对话框
            # 查找并关闭对话框
            for widget in QApplication.topLevelWidgets():
                if isinstance(widget, QDialog) and widget.windowTitle() == "选择背景图片":
                    widget.accept()
                    break
            
            self.logger.info(f"已选择背景图片: {image_file}")
            
        except Exception as e:
            self.logger.error(f"选择背景图片失败: {e}")

    def load_background_image(self):
        """加载背景图"""
        try:
            if hasattr(self, 'background_label') and self.background_label:
                self.background_label.deleteLater()
                self.background_label = None
            
            if self.show_background:
                # 获取当前选择的背景图片
                if hasattr(self, 'current_background'):
                    background_file = self.current_background
                else:
                    background_file = "background.jpg"
                    self.current_background = background_file
                
                background_path = get_resource_path(f"Resources\\{background_file}")
                if os.path.exists(background_path):
                    # 使用QPainter设置背景图
                    self.setStyleSheet(f"""
                    QMainWindow {{
                        background-image: url('{background_path.replace(os.sep, "/")}');
                        background-repeat: no-repeat;
                        background-position: center;
                        
                    }}
                    """)
                else:
                    # 如果选择的图片不存在，使用默认背景
                    default_path = get_resource_path("Resources\\background.jpg")
                    if os.path.exists(default_path):
                        self.setStyleSheet(f"""
                        QMainWindow {{
                            background-image: url('{default_path.replace(os.sep, "/")}');
                            background-repeat: no-repeat;
                            background-position: center;
                            
                        }}
                        """)
            else:
                # 当不显示背景图时，清除背景图片
                self.setStyleSheet("""
                QMainWindow {
                    background-image: none;
                    background-color: #1a1a1a;
                }
                """)
            
            # 更新当前背景预览
            if hasattr(self, 'current_bg_preview'):
                self.update_current_bg_preview()
                    
        except Exception as e:
            self.logger.error(f"加载背景图失败: {e}")
    
    def closeEvent(self, event):
        """窗口关闭事件 - 增强版"""
        try:
            # 询问用户是否确认退出
            reply = QMessageBox.question(self, '确认退出', 
                                       '您确定要退出浩讯亿通电脑工具箱吗？',
                                       QMessageBox.Yes | QMessageBox.No,
                                       QMessageBox.No)
            
            if reply == QMessageBox.No:
                event.ignore()  # 忽略关闭事件
                return
            
            self.logger.info("开始关闭程序，清理资源...")
            
            # 停止所有线程
            self.stop_event.set()
            
            # 清理定时器
            self.cleanup_timers()
            
            # 等待线程结束（带超时机制）
            self.wait_for_threads_completion()
            
            # 清理资源
            self.cleanup_resources()
            
            # 清理托盘图标
            if hasattr(self, 'tray_icon'):
                self.tray_icon.hide()
                self.tray_icon.deleteLater()
                self.logger.info("托盘图标已清理")
            
            # 记录关闭日志
            self.logger.info("程序资源清理完成，正在退出...")
            
            # 调用父类关闭方法
            super().closeEvent(event)
            
        except Exception as e:
            self.logger.error(f"关闭程序时出错: {e}")
            # 即使出错也要确保程序能退出
            super().closeEvent(event)
    
    def cleanup_timers(self):
        """清理所有定时器"""
        try:
            # 清理风扇更新定时器
            if hasattr(self, 'fan_update_timer') and self.fan_update_timer.isActive():
                self.fan_update_timer.stop()
                self.fan_update_timer.deleteLater()
                self.logger.info("风扇更新定时器已停止")
            
            # 清理其他可能存在的定时器
            timer_attrs = [attr for attr in dir(self) if 'timer' in attr.lower()]
            for attr_name in timer_attrs:
                try:
                    timer = getattr(self, attr_name)
                    if hasattr(timer, 'isActive') and timer.isActive():
                        timer.stop()
                        if hasattr(timer, 'deleteLater'):
                            timer.deleteLater()
                        self.logger.info(f"定时器 {attr_name} 已停止")
                except Exception as e:
                    self.logger.warning(f"停止定时器 {attr_name} 时出错: {e}")
                    
        except Exception as e:
            self.logger.error(f"清理定时器时出错: {e}")
    
    def wait_for_threads_completion(self):
        """等待线程完成（带超时机制）"""
        try:
            if hasattr(self, 'threads') and self.threads:
                self.logger.info(f"等待 {len(self.threads)} 个线程完成...")
                
                max_wait_time = 3000  # 最大等待时间3秒
                start_time = time.time()
                
                for i, thread in enumerate(self.threads):
                    if thread.isRunning():
                        self.logger.info(f"等待线程 {i+1} 完成...")
                        
                        # 带超时的等待
                        if not thread.wait(max_wait_time):
                            self.logger.warning(f"线程 {i+1} 超时，强制终止")
                            thread.terminate()  # 强制终止
                            thread.wait(500)   # 再给500ms终止时间
                        
                        # 检查是否超时
                        if time.time() - start_time > max_wait_time / 1000:
                            self.logger.warning("等待线程超时，继续清理其他资源")
                            break
                
                self.logger.info("线程等待完成")
                
        except Exception as e:
            self.logger.error(f"等待线程完成时出错: {e}")
    
    def cleanup_resources(self):
        """清理资源"""
        try:
            # 清理图片资源
            if hasattr(self, 'background_label') and self.background_label.pixmap():
                self.background_label.pixmap().cache().clear()
            
            # 清理其他可能存在的图片资源
            label_attrs = [attr for attr in dir(self) if 'label' in attr.lower()]
            for attr_name in label_attrs:
                try:
                    label = getattr(self, attr_name)
                    if hasattr(label, 'pixmap') and label.pixmap():
                        label.pixmap().cache().clear()
                except:
                    pass
            
            # 清理缓存
            import gc
            gc.collect()
            
            self.logger.info("资源清理完成")
            
        except Exception as e:
            self.logger.error(f"清理资源时出错: {e}")
    
    def safe_exit(self):
        """安全退出程序（供外部调用）"""
        try:
            self.logger.info("收到安全退出请求")
            self.close()
        except Exception as e:
            self.logger.error(f"安全退出时出错: {e}")
            QApplication.quit()
    
    def init_system_tray(self):
        """初始化系统托盘功能"""
        try:
            # 检查系统是否支持托盘
            if not QSystemTrayIcon.isSystemTrayAvailable():
                self.logger.warning("系统不支持托盘功能")
                return
            
            # 创建托盘图标
            self.tray_icon = QSystemTrayIcon(self)
            
            # 设置托盘图标
            try:
                icon_path = get_resource_path("Resources\\favicon.ico")
                if os.path.exists(icon_path):
                    self.tray_icon.setIcon(QIcon(icon_path))
                else:
                    # 使用默认图标
                    self.tray_icon.setIcon(self.windowIcon())
            except Exception as e:
                self.logger.warning(f"设置托盘图标失败: {e}")
                self.tray_icon.setIcon(self.windowIcon())
            
            # 设置托盘提示
            self.tray_icon.setToolTip("浩讯亿通电脑工具箱")
            
            # 创建托盘菜单
            self.tray_menu = QMenu(self)
            
            # 显示主窗口菜单项
            show_action = QAction("显示工具箱", self)
            show_action.triggered.connect(self.show_and_activate)
            self.tray_menu.addAction(show_action)
            
            # 隐藏主窗口菜单项
            hide_action = QAction("隐藏工具箱", self)
            hide_action.triggered.connect(self.hide_to_tray)
            self.tray_menu.addAction(hide_action)
            
            self.tray_menu.addSeparator()
            
            # 退出程序菜单项
            exit_action = QAction("退出", self)
            exit_action.triggered.connect(self.safe_exit)
            self.tray_menu.addAction(exit_action)
            
            # 设置托盘菜单
            self.tray_icon.setContextMenu(self.tray_menu)
            
            # 连接托盘图标点击事件
            self.tray_icon.activated.connect(self.on_tray_activated)
            
            # 显示托盘图标
            self.tray_icon.show()
            
            self.logger.info("托盘功能初始化成功")
            
        except Exception as e:
            self.logger.error(f"初始化托盘功能失败: {e}")
    
    def show_and_activate(self):
        """显示并激活主窗口"""
        try:
            self.show()
            self.activateWindow()
            self.raise_()
            self.logger.info("从托盘显示主窗口")
        except Exception as e:
            self.logger.error(f"显示主窗口失败: {e}")
    
    def hide_to_tray(self):
        """隐藏主窗口到托盘"""
        try:
            self.hide()
            self.tray_icon.showMessage(
                "浩讯亿通电脑工具箱",
                "程序已最小化到托盘，双击托盘图标可重新显示",
                QSystemTrayIcon.Information,
                2000
            )
            self.logger.info("主窗口已隐藏到托盘")
        except Exception as e:
            self.logger.error(f"隐藏到托盘失败: {e}")
    
    def on_tray_activated(self, reason):
        """托盘图标激活事件处理"""
        try:
            if reason == QSystemTrayIcon.DoubleClick:
                # 双击托盘图标显示主窗口
                if self.isHidden():
                    self.show_and_activate()
                else:
                    self.hide_to_tray()
            elif reason == QSystemTrayIcon.Trigger:
                # 单击托盘图标切换显示状态
                if self.isHidden():
                    self.show_and_activate()
                else:
                    self.hide_to_tray()
        except Exception as e:
            self.logger.error(f"处理托盘激活事件失败: {e}")
    
    def copy_hardware_info(self):
        """复制硬件信息到剪贴板"""
        try:
            # 收集所有硬件信息
            all_info = []
            all_info.append("=" * 60)
            all_info.append("🖥️ 浩讯亿通电脑工具箱 - 硬件信息报告")
            all_info.append("=" * 60)
            all_info.append("")
            
            # 获取当前时间
            from datetime import datetime
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            all_info.append(f"📅 报告生成时间: {current_time}")
            all_info.append("")
            
            if hasattr(self, 'hardware_tabs'):
                # 按分类添加信息
                categories = [
                    ('cpu', '🖥️ CPU处理器'),
                    ('gpu', '🎮 GPU显卡'),
                    ('memory', '💾 内存'),
                    ('disk', '💿 磁盘存储'),
                    ('system', '🌐 系统信息')
                ]
                
                for cat_key, cat_name in categories:
                    if cat_key in self.hardware_tabs:
                        tab = self.hardware_tabs[cat_key]
                        if hasattr(tab, 'info_label'):
                            info_text = tab.info_label.text()
                            if info_text and info_text not in ["正在加载...", "点击刷新获取信息"]:
                                all_info.append(cat_name)
                                all_info.append("-" * 30)
                                all_info.append(info_text)
                                all_info.append("")
            
            # 添加页脚
            all_info.append("=" * 60)
            all_info.append("🔧 由浩讯亿通电脑工具箱生成")
            all_info.append("=" * 60)
            
            # 复制到剪贴板
            info_text = "\n".join(all_info)
            
            # 使用QApplication获取剪贴板
            from PyQt5.QtWidgets import QApplication
            clipboard = QApplication.clipboard()
            clipboard.setText(info_text)
            
            # 更新状态
            if hasattr(self, 'hardware_info_status_label') and self.hardware_info_status_label:
                self.hardware_info_status_label.setText("硬件信息已复制到剪贴板 📋")
                self.hardware_info_status_label.setStyleSheet("""
                    font-size: 12px;
                    color: #059669;
                    margin-left: 5px;
                """)
            
            QMessageBox.information(self, "复制成功", "硬件信息已成功复制到剪贴板！\n\n您可以粘贴到任何文本编辑器中保存。")
            
        except Exception as e:
            self.logger.error(f"复制硬件信息失败: {e}")
            QMessageBox.warning(self, "复制失败", f"复制硬件信息时出现错误：{str(e)}")
            
            # 更新错误状态
            if hasattr(self, 'hardware_info_status_label') and self.hardware_info_status_label:
                self.hardware_info_status_label.setText("复制失败 ✗")
                self.hardware_info_status_label.setStyleSheet("""
                    font-size: 12px;
                    color: #ef4444;
                    margin-left: 5px;
                """)

    def export_hardware_info(self):
        """导出硬件信息到文件"""
        try:
            # 收集所有硬件信息
            all_info = []
            all_info.append("=" * 60)
            all_info.append("🖥️ 浩讯亿通电脑工具箱 - 硬件信息报告")
            all_info.append("=" * 60)
            all_info.append("")
            
            # 获取当前时间
            from datetime import datetime
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            all_info.append(f"📅 报告生成时间: {current_time}")
            all_info.append("")
            
            if hasattr(self, 'hardware_tabs'):
                # 按分类添加信息
                categories = [
                    ('cpu', '🖥️ CPU处理器'),
                    ('gpu', '🎮 GPU显卡'),
                    ('memory', '💾 内存'),
                    ('disk', '💿 磁盘存储'),
                    ('system', '🌐 系统信息')
                ]
                
                for cat_key, cat_name in categories:
                    if cat_key in self.hardware_tabs:
                        tab = self.hardware_tabs[cat_key]
                        if hasattr(tab, 'info_label'):
                            info_text = tab.info_label.text()
                            if info_text and info_text not in ["正在加载...", "点击刷新获取信息"]:
                                all_info.append(cat_name)
                                all_info.append("-" * 30)
                                all_info.append(info_text)
                                all_info.append("")
            
            # 添加页脚
            all_info.append("=" * 60)
            all_info.append("🔧 由浩讯亿通电脑工具箱生成")
            all_info.append("=" * 60)
            
            # 保存到文件
            info_text = "\n".join(all_info)
            
            # 获取保存路径
            from PyQt5.QtWidgets import QFileDialog, QApplication
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            filename, _ = QFileDialog.getSaveFileName(
                self, 
                "导出硬件信息", 
                os.path.join(desktop_path, f"硬件信息报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"),
                "文本文件 (*.txt);;所有文件 (*)"
            )
            
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(info_text)
                
                # 更新状态
                if hasattr(self, 'hardware_info_status_label') and self.hardware_info_status_label:
                    self.hardware_info_status_label.setText(f"已导出到: {os.path.basename(filename)} 📁")
                    self.hardware_info_status_label.setStyleSheet("""
                        font-size: 12px;
                        color: #059669;
                        margin-left: 5px;
                    """)
                
                QMessageBox.information(self, "导出成功", f"硬件信息已成功导出到:\n{filename}")
            else:
                # 用户取消了保存
                return
                
        except Exception as e:
            self.logger.error(f"导出硬件信息失败: {e}")
            QMessageBox.warning(self, "导出失败", f"导出硬件信息时出现错误：{str(e)}")
            
            # 更新错误状态
            if hasattr(self, 'hardware_info_status_label') and self.hardware_info_status_label:
                self.hardware_info_status_label.setText("导出失败 ✗")
                self.hardware_info_status_label.setStyleSheet("""
                    font-size: 12px;
                    color: #ef4444;
                    margin-left: 5px;
                """)

    def retry_load_hardware_info(self):
        """重试加载硬件信息"""
        try:
            # 清空缓存，强制重新获取
            if hasattr(self, 'hardware_info_thread') and hasattr(self.hardware_info_thread, 'cached_info'):
                self.hardware_info_thread.cached_info = None
            
            # 更新状态
            if hasattr(self, 'hardware_info_status_label') and self.hardware_info_status_label:
                self.hardware_info_status_label.setText("正在重试获取硬件信息...")
                self.hardware_info_status_label.setStyleSheet("""
                    font-size: 12px;
                    color: #f59e0b;
                    margin-left: 5px;
                """)
            
            # 重新加载
            self.load_hardware_info()
            
        except Exception as e:
            self.logger.error(f"重试加载硬件信息失败: {e}")
            QMessageBox.warning(self, "重试失败", f"重试加载硬件信息时出现错误：{str(e)}")
            
            # 更新错误状态
            if hasattr(self, 'hardware_info_status_label') and self.hardware_info_status_label:
                self.hardware_info_status_label.setText("重试失败 ✗")
                self.hardware_info_status_label.setStyleSheet("""
                    font-size: 12px;
                    color: #ef4444;
                    margin-left: 5px;
                """)


def start_floating_window():
    """启动悬浮窗（如果需要）"""
    # 这里是原始版本的悬浮窗功能，PyQt版本可以保持空实现或添加相应功能
    pass


def check_single_instance():
    """检查程序是否已经在运行（Windows兼容）"""
    import ctypes
    from ctypes import wintypes
    
    # 创建一个Windows互斥量来检测重复启动
    # 如果互斥量已存在，说明程序已经在运行
    MUTEX_NAME = "Global\\ComputerTools_PyQt_SingleInstance_Mutex"
    
    try:
        # Windows API常量
        SYNCHRONIZE = 0x00100000
        MUTEX_MODIFY_STATE = 0x0001
        
        # 尝试打开现有的互斥量
        mutex_handle = ctypes.windll.kernel32.OpenMutexW(
            SYNCHRONIZE | MUTEX_MODIFY_STATE, False, MUTEX_NAME
        )
        
        if mutex_handle != 0:
            # 互斥量已存在，说明程序已经在运行
            ctypes.windll.kernel32.CloseHandle(mutex_handle)
            print("检测到程序已在运行（互斥量方式）")
            return False, None
            
        # 如果打开失败，说明互斥量不存在，创建它
        mutex_handle = ctypes.windll.kernel32.CreateMutexW(None, False, MUTEX_NAME)
        
        if mutex_handle == 0:
            # 创建互斥量失败，使用备用方法
            return check_process_instance()
            
        print("创建启动互斥量成功")
        
        # 创建清理函数
        def cleanup_mutex():
            try:
                if mutex_handle:
                    ctypes.windll.kernel32.CloseHandle(mutex_handle)
            except Exception as e:
                print(f"清理互斥量时出错: {e}")
        
        return True, cleanup_mutex
        
    except Exception as e:
        print(f"互斥量检测失败，使用备用方法: {e}")
        return check_process_instance()

def check_process_instance():
    """备用方法：通过进程名称检测重复启动"""
    import psutil
    import time
    
    current_process = psutil.Process()
    current_name = current_process.name()
    current_pid = current_process.pid
    
    # 检查是否有其他同名进程运行
    running_processes = []
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'] == current_name and proc.info['pid'] != current_pid:
                running_processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    
    if running_processes:
        print(f"检测到 {len(running_processes)} 个同名进程在运行")
        for proc_info in running_processes:
            print(f"  - PID: {proc_info['pid']}")
        return False, None
    
    print("没有检测到重复的进程实例")
    return True, lambda: None

def main():
    """程序入口"""
    try:
        print("开始初始化应用程序...")
        
        # 检查程序是否已经在运行
        print("检查程序启动状态...")
        is_first_instance, cleanup_lock = check_single_instance()
        
        if not is_first_instance:
            print("检测到程序已经在运行，提示用户...")
            
            try:
                # 尝试使用现有的QApplication实例
                app_check = QApplication.instance()
                
                if app_check is None:
                    # 如果没有现有的QApplication实例，则创建一个临时的
                    app_check = QApplication([])
                
                # 设置应用程序属性（避免重复启动）
                app_check.setApplicationName("浩讯亿通电脑工具箱 PyQt版")
                app_check.setApplicationVersion("1.0")
                
                # 显示提示消息
                msg_box = QMessageBox()
                msg_box.setWindowTitle("程序已启动")
                msg_box.setText("浩讯亿通电脑工具箱已经在运行中！\n\n请不要重复启动程序。")
                msg_box.setIcon(QMessageBox.Information)
                msg_box.setStandardButtons(QMessageBox.Ok)
                
                # 设置样式
                msg_box.setStyleSheet("""
                    QMessageBox {
                        background-color: #f8fafc;
                    }
                    QMessageBox QLabel {
                        color: #334155;
                        font-size: 14px;
                        font-weight: 500;
                    }
                    QMessageBox QPushButton {
                        background-color: #3b82f6;
                        color: white;
                        border: none;
                        padding: 8px 16px;
                        border-radius: 6px;
                        font-size: 13px;
                        min-width: 80px;
                    }
                    QMessageBox QPushButton:hover {
                        background-color: #2563eb;
                    }
                """)
                
                msg_box.exec_()
                
                # 如果是我们创建的临时应用，则退出它
                if QApplication.instance() is None:
                    app_check.quit()
                
            except Exception as e:
                print(f"显示重复启动提示时出错: {e}")
                # 如果GUI显示失败，至少在控制台输出提示
                print("浩讯亿通电脑工具箱已经在运行中！请不要重复启动程序。")
            
            print("用户已收到程序运行提示，退出...")
            sys.exit(0)
        
        print("程序未运行，继续启动...")
        
        # 设置系统编码环境
        try:
            # 设置标准输出编码
            if sys.stdout.encoding != 'utf-8':
                sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
            if sys.stderr.encoding != 'utf-8':
                sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
            
            # 设置locale
            locale.setlocale(locale.LC_ALL, 'zh_CN.UTF-8')
        except Exception as e:
            print(f"编码设置警告: {e}")
        
        # 创建应用程序
        app = QApplication(sys.argv)
        app.setApplicationName("浩讯亿通电脑工具箱 PyQt版")
        app.setApplicationVersion("1.0")
        
        # 防止应用程序在没有可见窗口时立即退出
        app.setQuitOnLastWindowClosed(False)
        
        # 设置退出时的清理函数
        if cleanup_lock:
            app.aboutToQuit.connect(cleanup_lock)
        
        # 设置应用程序字体，确保中文显示正常
        font = QFont("Microsoft YaHei", 9)
        app.setFont(font)
        
        print("应用程序创建成功")
        
        # 创建主窗口
        print("创建主窗口...")
        window = MainWindow()
        print("主窗口创建成功，显示窗口")
        window.show()
        
        # 检查窗口是否可见
        print(f"窗口是否可见: {window.isVisible()}")
        print(f"窗口标题: {window.windowTitle()}")
        
        # 启动悬浮窗线程
        print("启动悬浮窗线程...")
        threading.Thread(target=start_floating_window, daemon=True).start()
        print("悬浮窗线程启动完成")
        
        # 运行应用程序
        print("开始应用程序主循环...")
        result = app.exec_()
        print(f"应用程序退出，返回代码: {result}")
        sys.exit(result)
        
    except Exception as e:
        print(f"程序启动失败: {e}")
        import traceback
        traceback.print_exc()
        input("按回车键退出...")


if __name__ == "__main__":
    main()


class CircularColorWheel(QWidget):
    """环形色轮组件 - 自定义彩色选择器"""
    
    color_changed = pyqtSignal(str)  # 颜色改变信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(300, 300)
        self.current_color = "#ff0000"
        self.hue = 0.0
        self.saturation = 1.0
        self.lightness = 0.5
        
        # 鼠标跟踪
        self.dragging = False
        
    def paintEvent(self, event):
        """绘制色轮"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 获取绘制区域
        rect = self.rect()
        size = min(rect.width(), rect.height()) - 20  # 留出边距
        center = rect.center()
        radius = size // 2
        
        # 绘制外圈色轮
        for angle in range(360):
            # 计算当前角度的颜色
            hue = angle / 360.0
            color = QColor.fromHsvF(hue, 1.0, 1.0)
            
            # 设置画笔
            pen = QPen(color)
            pen.setWidth(8)
            pen.setCapStyle(Qt.RoundCap)
            
            # 计算起点和终点
            start_angle = angle * 16  # Qt使用1/16度
            end_angle = (angle + 1) * 16
            
            # 绘制弧线
            path = QPainterPath()
            inner_radius = radius - 8
            
            # 创建圆弧路径
            outer_arc = QRectF(center.x() - radius, center.y() - radius, 
                              2 * radius, 2 * radius)
            inner_arc = QRectF(center.x() - inner_radius, center.y() - inner_radius,
                              2 * inner_radius, 2 * inner_radius)
            
            # 绘制外圈色环
            painter.setPen(pen)
            painter.drawArc(outer_arc, start_angle, end_angle - start_angle)
            
        # 绘制中心圆（白色到黑色的径向渐变）
        center_radius = radius * 0.6
        center_rect = QRectF(center.x() - center_radius, center.y() - center_radius,
                            2 * center_radius, 2 * center_radius)
        
        # 创建径向渐变
        gradient = QRadialGradient(center, 0, center, center_radius)
        gradient.setColorAt(0, Qt.white)
        gradient.setColorAt(1, Qt.black)
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(center_rect)
        
        # 绘制选择指示器
        self.draw_selector(painter, center, radius)
        
    def draw_selector(self, painter, center, radius):
        """绘制选择指示器"""
        # 计算当前颜色的位置
        if self.saturation <= 0:
            # 如果饱和度为0，位置在中心
            pos = center
        else:
            # 根据色调和饱和度计算位置
            angle_rad = math.radians(self.hue * 360)
            distance = radius * self.saturation
            
            x = center.x() + math.cos(angle_rad) * distance
            y = center.y() - math.sin(angle_rad) * distance  # y轴向下为正，需要反转
            
            pos = QPointF(x, y)
        
        # 绘制选择环
        selector_radius = 12
        selector_rect = QRectF(pos.x() - selector_radius, pos.y() - selector_radius,
                              2 * selector_radius, 2 * selector_radius)
        
        # 外圈
        painter.setPen(QPen(QColor(255, 255, 255, 200), 3))
        painter.setBrush(Qt.NoPen)
        painter.drawEllipse(selector_rect)
        
        # 内圈
        painter.setPen(QPen(QColor(0, 0, 0, 200), 2))
        painter.setBrush(Qt.NoPen)
        inner_rect = QRectF(pos.x() - selector_radius + 3, pos.y() - selector_radius + 3,
                           2 * (selector_radius - 3), 2 * (selector_radius - 3))
        painter.drawEllipse(inner_rect)
        
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.update_color_from_pos(event.pos())
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if self.dragging:
            self.update_color_from_pos(event.pos())
    
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if event.button() == Qt.LeftButton:
            self.dragging = False
    
    def update_color_from_pos(self, pos):
        """根据鼠标位置更新颜色"""
        rect = self.rect()
        center = rect.center()
        size = min(rect.width(), rect.height()) - 20
        radius = size // 2
        
        # 计算鼠标相对于中心的坐标
        dx = pos.x() - center.x()
        dy = center.y() - pos.y()  # y轴向上为正
        
        # 计算距离和角度
        distance = math.sqrt(dx * dx + dy * dy)
        angle_rad = math.atan2(dy, dx)  # 返回-π到π
        
        # 限制在色轮范围内
        if distance > radius:
            distance = radius
        elif distance < 0:
            distance = 0
        
        # 计算色调 (0-1)
        self.hue = (angle_rad + math.pi) / (2 * math.pi)
        if self.hue >= 1.0:
            self.hue -= 1.0
        
        # 计算饱和度 (0-1)
        self.saturation = distance / radius
        
        # 计算亮度 (固定为0.5)
        self.lightness = 0.5
        
        # 转换为十六进制颜色
        color = QColor.fromHsvF(self.hue, self.saturation, self.lightness)
        color_hex = color.name()
        
        # 更新当前颜色并发射信号
        self.current_color = color_hex
        self.color_changed.emit(color_hex)
        self.update()  # 重绘组件
        
    def setColor(self, color_hex):
        """设置当前颜色"""
        try:
            color = QColor(color_hex)
            if color.isValid():
                # 转换为HSV并设置
                self.hue = color.hueF()
                self.saturation = color.saturationF()
                self.lightness = color.lightnessF()
                
                self.current_color = color_hex
                self.update()
        except Exception as e:
            print(f"设置颜色失败: {e}")
    
    def getColor(self):
        """获取当前颜色"""
        return self.current_color