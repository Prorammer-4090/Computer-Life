"""
Style Utilities
Helper functions for consistent styling across the application.
"""

def get_button_style(color_scheme='primary'):
    """Get button style based on color scheme."""
    schemes = {
        'primary': {
            'normal': '#007acc',
            'hover': '#005a9e', 
            'pressed': '#004080'
        },
        'success': {
            'normal': '#4CAF50',
            'hover': '#45a049',
            'pressed': '#3d8b40'
        },
        'warning': {
            'normal': '#FF9800',
            'hover': '#F57C00',
            'pressed': '#E68900'
        },
        'danger': {
            'normal': '#f44336',
            'hover': '#d32f2f',
            'pressed': '#b71c1c'
        }
    }
    
    colors = schemes.get(color_scheme, schemes['primary'])
    
    return f"""
        QPushButton {{
            background-color: {colors['normal']};
            color: white;
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
            font-size: 14px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: {colors['hover']};
        }}
        QPushButton:pressed {{
            background-color: {colors['pressed']};
        }}
    """


def get_gradient_button_style(color_scheme='success'):
    """Get gradient button style for more visual appeal."""
    schemes = {
        'success': {
            'start': '#4CAF50', 'end': '#45a049',
            'hover_start': '#5CBF60', 'hover_end': '#55b059',
            'pressed_start': '#3CAF40', 'pressed_end': '#359039'
        },
        'warning': {
            'start': '#FF9800', 'end': '#F57C00',
            'hover_start': '#FFA820', 'hover_end': '#F68C00',
            'pressed_start': '#E68900', 'pressed_end': '#D67C00'
        },
        'danger': {
            'start': '#ff4444', 'end': '#cc3333',
            'hover_start': '#ff5555', 'hover_end': '#dd4444',
            'pressed_start': '#ee3333', 'pressed_end': '#bb2222'
        }
    }
    
    colors = schemes.get(color_scheme, schemes['success'])
    
    return f"""
        QPushButton {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {colors['start']}, stop:1 {colors['end']});
            border: none;
            border-radius: 16px;
            color: white;
            font-size: 12px;
            font-weight: bold;
            padding: 8px;
            min-width: 30px;
            min-height: 30px;
        }}
        QPushButton:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {colors['hover_start']}, stop:1 {colors['hover_end']});
        }}
        QPushButton:pressed {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {colors['pressed_start']}, stop:1 {colors['pressed_end']});
        }}
    """


def get_frame_style():
    """Get standard frame styling."""
    return """
        QFrame {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #2a2a2a, stop:1 #1a1a1a);
            border: 2px solid #404040;
            border-radius: 12px;
        }
    """


def get_scroll_area_style():
    """Get standard scroll area styling."""
    return """
        QScrollArea {
            border: none;
            background-color: transparent;
        }
        QScrollBar:vertical {
            background-color: #2a2a2a;
            width: 8px;
            border-radius: 4px;
        }
        QScrollBar::handle:vertical {
            background-color: #555;
            border-radius: 4px;
            min-height: 20px;
        }
        QScrollBar::handle:vertical:hover {
            background-color: #666;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            border: none;
            background: none;
        }
    """


def get_menu_style():
    """Get standard menu styling."""
    return """
        QMenu {
            background-color: #2b2b2b;
            border: 2px solid #4a4a4a;
            border-radius: 8px;
            padding: 4px;
            color: white;
            font-size: 14px;
        }
        QMenu::item {
            background-color: transparent;
            padding: 8px 16px;
            border-radius: 4px;
            margin: 2px;
        }
        QMenu::item:selected {
            background-color: #007acc;
        }
        QMenu::item:pressed {
            background-color: #005a9e;
        }
        QMenu::separator {
            height: 1px;
            background-color: #555;
            margin: 4px 8px;
        }
    """
