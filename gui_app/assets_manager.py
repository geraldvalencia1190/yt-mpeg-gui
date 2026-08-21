import os
import sys
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QPen, QBrush, QPainterPath, QPolygonF
from PySide6.QtCore import Qt, QPointF, QRectF, QSize

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
LOGO_PNG = os.path.join(ASSETS_DIR, "logo.png")
LOGO_ICO = os.path.join(ASSETS_DIR, "app.ico")

def get_app_icon() -> QIcon:
    """Return the application icon."""
    if os.path.isfile(LOGO_PNG):
        return QIcon(LOGO_PNG)
    if os.path.isfile(LOGO_ICO):
        return QIcon(LOGO_ICO)
    return QIcon()

def get_logo_pixmap(width: int = 48, height: int = 48) -> QPixmap:
    """Return scaled logo pixmap."""
    if os.path.isfile(LOGO_PNG):
        pm = QPixmap(LOGO_PNG)
        if not pm.isNull():
            return pm.scaled(width, height, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
    pm = QPixmap(width, height)
    pm.fill(Qt.GlobalColor.transparent)
    return pm

def get_icon(name: str, color_hex: str = "#e2e8f0", size: int = 24) -> QIcon:
    """
    Generate crisp vector-rendered QIcon for standard application controls.
    """
    pixmap = QPixmap(size * 2, size * 2)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)

    pen = QPen(QColor(color_hex))
    pen.setWidthF(size * 0.1)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)

    s = size * 2.0
    p = s * 0.15  # Padding

    if name == "download":
        # Down arrow with tray
        # Tray
        tray = QPainterPath()
        tray.moveTo(p, s * 0.65)
        tray.lineTo(p, s - p)
        tray.lineTo(s - p, s - p)
        tray.lineTo(s - p, s * 0.65)
        painter.drawPath(tray)
        # Arrow
        painter.drawLine(QPointF(s * 0.5, p), QPointF(s * 0.5, s * 0.65))
        arrow = QPainterPath()
        arrow.moveTo(s * 0.3, s * 0.45)
        arrow.lineTo(s * 0.5, s * 0.65)
        arrow.lineTo(s * 0.7, s * 0.45)
        painter.drawPath(arrow)

    elif name == "pause":
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(color_hex))
        w = s * 0.18
        h = s * 0.6
        painter.drawRoundedRect(QRectF(s * 0.28, s * 0.2, w, h), 2, 2)
        painter.drawRoundedRect(QRectF(s * 0.54, s * 0.2, w, h), 2, 2)

    elif name in ("play", "resume"):
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(color_hex))
        poly = QPolygonF([
            QPointF(s * 0.3, s * 0.2),
            QPointF(s * 0.78, s * 0.5),
            QPointF(s * 0.3, s * 0.8)
        ])
        painter.drawPolygon(poly)

    elif name == "queue":
        # Bullet list / playlist
        for y_factor in (0.3, 0.5, 0.7):
            painter.drawLine(QPointF(s * 0.4, s * y_factor), QPointF(s * 0.85, s * y_factor))
            painter.drawPoint(QPointF(s * 0.22, s * y_factor))

    elif name == "history":
        # Clock circle
        r = (s - 2 * p) / 2.0
        center = QPointF(s * 0.5, s * 0.5)
        painter.drawEllipse(center, r, r)
        # Clock hands
        painter.drawLine(center, QPointF(s * 0.5, s * 0.3))
        painter.drawLine(center, QPointF(s * 0.68, s * 0.58))

    elif name == "settings":
        # Gear icon
        center = QPointF(s * 0.5, s * 0.5)
        painter.drawEllipse(center, s * 0.22, s * 0.22)
        painter.drawEllipse(center, s * 0.36, s * 0.36)

    elif name == "logs":
        # Terminal prompt >_
        prompt = QPainterPath()
        prompt.moveTo(s * 0.25, s * 0.25)
        prompt.lineTo(s * 0.5, s * 0.5)
        prompt.lineTo(s * 0.25, s * 0.75)
        painter.drawPath(prompt)
        painter.drawLine(QPointF(s * 0.58, s * 0.75), QPointF(s * 0.82, s * 0.75))

    elif name in ("search", "analyze"):
        # Magnifying glass
        r = s * 0.25
        c = QPointF(s * 0.42, s * 0.42)
        painter.drawEllipse(c, r, r)
        painter.drawLine(QPointF(s * 0.6, s * 0.6), QPointF(s * 0.82, s * 0.82))

    elif name == "folder":
        # Folder shape
        path = QPainterPath()
        path.moveTo(p, s * 0.35)
        path.lineTo(p, s - p)
        path.lineTo(s - p, s - p)
        path.lineTo(s - p, s * 0.35)
        path.lineTo(s * 0.55, s * 0.35)
        path.lineTo(s * 0.45, s * 0.22)
        path.lineTo(p, s * 0.22)
        path.closeSubpath()
        painter.drawPath(path)

    elif name in ("refresh", "update"):
        # Circular reload arrows
        arc_rect = QRectF(p, p, s - 2 * p, s - 2 * p)
        painter.drawArc(arc_rect, 45 * 16, 270 * 16)
        # Arrowhead
        arrow = QPainterPath()
        arrow.moveTo(s * 0.75, s * 0.15)
        arrow.lineTo(s * 0.88, s * 0.32)
        arrow.lineTo(s * 0.68, s * 0.38)
        painter.drawPath(arrow)

    elif name in ("cancel", "close", "stop"):
        # Cross X
        painter.drawLine(QPointF(p * 1.2, p * 1.2), QPointF(s - p * 1.2, s - p * 1.2))
        painter.drawLine(QPointF(s - p * 1.2, p * 1.2), QPointF(p * 1.2, s - p * 1.2))

    elif name in ("trash", "clear"):
        # Trash bin
        painter.drawLine(QPointF(p, s * 0.3), QPointF(s - p, s * 0.3))
        painter.drawLine(QPointF(s * 0.38, s * 0.2), QPointF(s * 0.62, s * 0.2))
        bin_path = QPainterPath()
        bin_path.moveTo(s * 0.25, s * 0.3)
        bin_path.lineTo(s * 0.3, s - p)
        bin_path.lineTo(s * 0.7, s - p)
        bin_path.lineTo(s * 0.75, s * 0.3)
        painter.drawPath(bin_path)

    elif name == "video":
        # Video camera
        cam = QPainterPath()
        cam.addRoundedRect(QRectF(p, s * 0.28, s * 0.52, s * 0.44), 3, 3)
        painter.drawPath(cam)
        # Lens triangle
        poly = QPolygonF([
            QPointF(s * 0.65, s * 0.4),
            QPointF(s * 0.85, s * 0.28),
            QPointF(s * 0.85, s * 0.72),
            QPointF(s * 0.65, s * 0.6)
        ])
        painter.setBrush(QColor(color_hex))
        painter.drawPolygon(poly)

    elif name == "audio":
        # Headphones
        headband = QPainterPath()
        headband.arcMoveTo(QRectF(p, p, s - 2 * p, s - 2 * p), 0)
        headband.arcTo(QRectF(p, p, s - 2 * p, s - 2 * p), 0, 180)
        painter.drawPath(headband)
        # Ear cups
        painter.setBrush(QColor(color_hex))
        painter.drawRoundedRect(QRectF(p - s * 0.04, s * 0.5, s * 0.16, s * 0.28), 2, 2)
        painter.drawRoundedRect(QRectF(s - p - s * 0.12, s * 0.5, s * 0.16, s * 0.28), 2, 2)

    elif name == "check":
        # Checkmark
        chk = QPainterPath()
        chk.moveTo(s * 0.2, s * 0.5)
        chk.lineTo(s * 0.45, s * 0.75)
        chk.lineTo(s * 0.82, s * 0.28)
        painter.drawPath(chk)

    elif name == "plus":
        painter.drawLine(QPointF(s * 0.5, p), QPointF(s * 0.5, s - p))
        painter.drawLine(QPointF(p, s * 0.5), QPointF(s - p, s * 0.5))

    painter.end()
    return QIcon(pixmap)
