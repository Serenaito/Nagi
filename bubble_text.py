from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QPainter, QColor, QFont


class BubbleText:
    """气泡文字类，存储气泡的显示信息"""
    def __init__(self, text, x, y, duration=2000, bg_color=QColor(255, 255, 255, 200), 
                 text_color=QColor(0, 0, 0), font_size=12, typing_speed=50, max_width=200):
        self.original_text = text  # 原始文字
        self.text = text  # 可能会被换行处理后的文字
        self.x = x  # 相对于 widget 的 x 坐标
        self.y = y  # 相对于 widget 的 y 坐标
        self.duration = duration  # 显示时长 (毫秒)，从文字全部显示完后开始计算
        self.elapsed = 0  # 已经过的时间
        self.bg_color = bg_color
        self.text_color = text_color
        self.font_size = font_size
        self.padding = 8  # 文字内边距
        self.max_width = max_width  # 气泡最大宽度（不含 padding）
        
        # 打字机效果相关
        self.typing_speed = typing_speed  # 每个字符出现的间隔时间 (毫秒)
        self.typing_elapsed = 0  # 打字效果已经过的时间
        self.visible_chars = 0  # 当前可见的字符数
        self.typing_complete = False  # 打字效果是否完成
        
        # 换行后的文字行列表（在绑定字体后计算）
        self.lines = []
        self.wrapped = False  # 是否已完成换行处理
    
    @property
    def visible_text(self):
        """获取当前应该显示的文字（原始文字的前 N 个字符）"""
        return self.original_text[:self.visible_chars]
    
    @property
    def total_typing_time(self):
        """获取打字效果的总时间"""
        return len(self.original_text) * self.typing_speed
    
    def wrap_text(self, font_metrics):
        """根据字体度量和最大宽度对文字进行换行处理"""
        if self.wrapped:
            return
        
        self.lines = []
        current_line = ""
        
        for char in self.original_text:
            # 处理原有换行符
            if char == '\n':
                self.lines.append(current_line)
                current_line = ""
                continue
            
            test_line = current_line + char
            line_width = font_metrics.horizontalAdvance(test_line)
            
            if line_width > self.max_width and current_line:
                # 当前行已满，换行
                self.lines.append(current_line)
                current_line = char
            else:
                current_line = test_line
        
        # 添加最后一行
        if current_line:
            self.lines.append(current_line)
        
        # 生成换行后的完整文字
        self.text = '\n'.join(self.lines)
        self.wrapped = True
    
    def get_visible_lines(self):
        """获取当前应该显示的行（基于可见字符数）"""
        if not self.lines:
            return [self.visible_text]
        
        result_lines = []
        char_count = 0
        
        for line in self.lines:
            line_len = len(line)
            if char_count + line_len <= self.visible_chars:
                # 整行可见
                result_lines.append(line)
                char_count += line_len
            elif char_count < self.visible_chars:
                # 部分可见
                visible_in_line = self.visible_chars - char_count
                result_lines.append(line[:visible_in_line])
                break
            else:
                break
        
        return result_lines


class BubbleManager:
    """气泡管理器，负责气泡的创建、更新和绘制"""
    
    def __init__(self, widget):
        """
        初始化气泡管理器
        
        Args:
            widget: 父 widget，用于获取尺寸信息
        """
        self.widget = widget
        self.bubbles = []  # 存储当前显示的气泡文字
    
    def show_bubble(self, text, x=None, y=None, duration=2000, typing_speed=50, max_width=200, **kwargs):
        """
        显示气泡文字（带打字机效果，支持自动换行）
        
        Args:
            text: 要显示的文字内容
            x: 气泡的 x 坐标，如果为 None 则居中显示
            y: 气泡的 y 坐标，如果为 None 则显示在顶部
            duration: 文字全部显示完后的持续时长 (毫秒)
            typing_speed: 打字机效果的速度，每个字符出现的间隔时间 (毫秒)
            max_width: 气泡最大宽度 (像素)，超过此宽度自动换行，默认 200
            **kwargs: 其他参数传递给 BubbleText (bg_color, text_color, font_size)
        """
        if x is None:
            x = self.widget.width() // 2
        if y is None:
            y = 50
        bubble = BubbleText(text, x, y, duration, typing_speed=typing_speed, max_width=max_width, **kwargs)
        self.bubbles.append(bubble)
    
    def update(self, delta=33):
        """
        更新气泡状态，移除已过期的气泡
        
        Args:
            delta: 时间增量 (毫秒)，默认 33ms（约 30fps）
        """
        for bubble in self.bubbles[:]:
            # 更新打字机效果
            if not bubble.typing_complete:
                bubble.typing_elapsed += delta
                # 计算应该显示的字符数（基于原始文字长度）
                new_visible_chars = min(
                    len(bubble.original_text),
                    int(bubble.typing_elapsed / bubble.typing_speed)
                )
                bubble.visible_chars = new_visible_chars
                
                # 检查打字效果是否完成
                if bubble.visible_chars >= len(bubble.original_text):
                    bubble.typing_complete = True
            else:
                # 打字完成后开始计算显示时长
                bubble.elapsed += delta
                if bubble.elapsed >= bubble.duration:
                    self.bubbles.remove(bubble)
    
    def draw(self, painter=None):
        """
        绘制所有气泡文字
        
        Args:
            painter: QPainter 对象，如果为 None 则创建新的
        """
        if not self.bubbles:
            return
        
        own_painter = False
        if painter is None:
            painter = QPainter(self.widget)
            own_painter = True
        
        painter.setRenderHint(QPainter.Antialiasing)
        
        for bubble in self.bubbles:
            self._draw_bubble(painter, bubble)
        
        if own_painter:
            painter.end()
    
    def _draw_bubble(self, painter, bubble):
        """绘制单个气泡"""
        # 计算淡出效果（仅在打字完成后生效）
        alpha_ratio = 1.0
        if bubble.typing_complete:
            remaining = bubble.duration - bubble.elapsed
            if remaining < 500:
                alpha_ratio = remaining / 500
        
        # 准备字体
        font = QFont("Microsoft YaHei", bubble.font_size)
        painter.setFont(font)
        font_metrics = painter.fontMetrics()
        
        # 进行换行处理（仅第一次）
        bubble.wrap_text(font_metrics)
        
        # 获取当前应该显示的行
        visible_lines = bubble.get_visible_lines()
        if not visible_lines or not visible_lines[0]:
            return
        
        # 计算气泡尺寸（基于固定最大宽度和完整文字行数）
        line_height = font_metrics.height()
        total_lines = len(bubble.lines) if bubble.lines else 1
        
        # 气泡宽度为固定的 max_width + padding
        rect_width = bubble.max_width + bubble.padding * 2
        rect_height = line_height * total_lines + bubble.padding * 2
        
        # 计算初始位置（居中于 bubble.x）
        rect_x = bubble.x - rect_width // 2
        rect_y = bubble.y - rect_height
        
        # 获取 widget 尺寸
        widget_width = self.widget.width()
        widget_height = self.widget.height()
        margin = 5  # 边缘留白
        
        # 水平方向边界检查和调整
        if rect_x < margin:
            rect_x = margin
        elif rect_x + rect_width > widget_width - margin:
            rect_x = widget_width - margin - rect_width
        
        # 垂直方向边界检查和调整
        if rect_y < margin:
            # 如果上方空间不足，将气泡移到 y 坐标下方显示
            rect_y = bubble.y + margin
        if rect_y + rect_height > widget_height - margin:
            rect_y = widget_height - margin - rect_height
        
        # 绘制气泡背景 (圆角矩形)
        bg_color = QColor(bubble.bg_color)
        bg_color.setAlpha(int(bg_color.alpha() * alpha_ratio))
        painter.setBrush(bg_color)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(QRectF(rect_x, rect_y, rect_width, rect_height), 10, 10)
        
        # 绘制文字（逐行绘制，左对齐以实现打字机效果）
        text_color = QColor(bubble.text_color)
        text_color.setAlpha(int(text_color.alpha() * alpha_ratio))
        painter.setPen(text_color)
        
        # 逐行绘制文字
        text_start_x = rect_x + bubble.padding
        text_start_y = rect_y + bubble.padding
        
        for i, line in enumerate(visible_lines):
            line_rect = QRectF(
                text_start_x,
                text_start_y + i * line_height,
                bubble.max_width,
                line_height
            )
            painter.drawText(line_rect, Qt.AlignLeft | Qt.AlignVCenter, line)
    
    def clear(self):
        """清除所有气泡"""
        self.bubbles.clear()
    
    def has_bubbles(self):
        """检查是否有气泡正在显示"""
        return len(self.bubbles) > 0
