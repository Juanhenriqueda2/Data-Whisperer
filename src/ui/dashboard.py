import threading
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import traceback

import panel as pn
import param

from src.query.query_processor import QueryProcessor
from src.visualization.viz_engine import VisualizationEngine
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

APPLE_DARK_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;700&display=swap');

    :root {
        --bg-0: #04070d;
        --bg-1: #09111c;
        --bg-2: #101827;
        --panel-0: rgba(12, 18, 31, 0.88);
        --panel-1: rgba(18, 25, 42, 0.72);
        --panel-border: rgba(255, 255, 255, 0.08);
        --text-0: #f4f7fb;
        --text-1: rgba(228, 234, 246, 0.72);
        --text-2: rgba(228, 234, 246, 0.48);
        --accent: #68d5ff;
        --accent-2: #7a5cff;
        --accent-3: #1cc8a0;
        --shadow-lg: 0 30px 80px rgba(0, 0, 0, 0.38);
        --shadow-md: 0 18px 50px rgba(0, 0, 0, 0.28);
    }

    * {
        box-sizing: border-box;
        font-family: 'Manrope', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }

    h1, h2, h3, h4, .display-font {
        font-family: 'Space Grotesk', 'Manrope', sans-serif;
    }

    html, body {
        min-height: 100%;
        margin: 0;
        background-color: var(--bg-0) !important;
    }

    body {
        background:
            radial-gradient(circle at 12% 10%, rgba(104, 213, 255, 0.14), transparent 28%),
            radial-gradient(circle at 86% 8%, rgba(122, 92, 255, 0.16), transparent 24%),
            radial-gradient(circle at 55% 100%, rgba(28, 200, 160, 0.10), transparent 30%),
            linear-gradient(180deg, var(--bg-0) 0%, var(--bg-1) 45%, #050912 100%);
        color: var(--text-0);
        background-attachment: fixed;
    }

    .glass {
        background: linear-gradient(180deg, rgba(18, 25, 42, 0.94) 0%, rgba(10, 14, 24, 0.90) 100%);
        backdrop-filter: blur(22px) saturate(140%);
        -webkit-backdrop-filter: blur(22px) saturate(140%);
        border: 1px solid var(--panel-border);
        box-shadow: var(--shadow-md);
    }

    .smooth-transition {
        transition: transform 0.35s ease, box-shadow 0.35s ease, border-color 0.35s ease, background 0.35s ease;
    }

    .hover-lift:hover {
        transform: translateY(-6px);
        box-shadow: 0 26px 60px rgba(0, 0, 0, 0.34);
        border-color: rgba(104, 213, 255, 0.16);
    }

    .eyebrow {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 8px 12px;
        border-radius: 999px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        background: rgba(255, 255, 255, 0.04);
        color: var(--text-1);
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
    }

    .eyebrow::before {
        content: "";
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: linear-gradient(135deg, var(--accent) 0%, var(--accent-2) 100%);
        box-shadow: 0 0 14px rgba(104, 213, 255, 0.55);
    }

    body .bk,
    body .bk-root,
    body .bk-Column,
    body .bk-Row,
    body .bk-panel-models-layout-Column,
    body .bk-panel-models-layout-Row {
        color: var(--text-0) !important;
    }

    body .bk-root {
        min-height: 100vh;
        background:
            radial-gradient(circle at 12% 10%, rgba(104, 213, 255, 0.12), transparent 28%),
            radial-gradient(circle at 86% 8%, rgba(122, 92, 255, 0.14), transparent 24%),
            radial-gradient(circle at 55% 100%, rgba(28, 200, 160, 0.08), transparent 30%),
            linear-gradient(180deg, var(--bg-0) 0%, var(--bg-1) 45%, #050912 100%) !important;
    }

    .bk-root,
    .bk-Column,
    .bk-Row,
    .bk-panel-models-layout-Column,
    .bk-panel-models-layout-Row {
        background: transparent !important;
    }

    .bk-Column .bk-Column,
    .bk-Column .bk-Row,
    .bk-Row .bk-Column,
    .bk-Row .bk-Row {
        background: transparent !important;
    }

    .tabulator {
        background: rgba(11, 16, 27, 0.82) !important;
        color: var(--text-0) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important;
        overflow: hidden;
    }

    .tabulator .tabulator-header {
        background: rgba(255, 255, 255, 0.03) !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.06) !important;
        color: var(--text-1) !important;
    }

    .tabulator .tabulator-col,
    .tabulator .tabulator-cell {
        border-right-color: rgba(255, 255, 255, 0.04) !important;
    }

    .tabulator-row {
        background: transparent !important;
        color: var(--text-0) !important;
        border-top-color: rgba(255, 255, 255, 0.04) !important;
    }

    .tabulator-row:nth-child(even) {
        background: rgba(255, 255, 255, 0.02) !important;
    }

    .tabulator-row:hover {
        background: rgba(104, 213, 255, 0.06) !important;
    }

    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.05);
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.2);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(255, 255, 255, 0.3);
    }
    
    textarea, input, select {
        color: var(--text-0) !important;
    }

    textarea::placeholder, input::placeholder {
        color: var(--text-2) !important;
    }

    .bk-input,
    .bk-btn,
    .bk-panel-models-widgets-TextAreaInput textarea,
    .bk-panel-models-widgets-FileInput input {
        color: var(--text-0) !important;
    }
</style>
"""


class DataWhispererDashboard(param.Parameterized):
    
    data_loaded = param.Boolean(default=False)
    processing = param.Boolean(default=False)
    
    def __init__(self, config, **params):
        super().__init__(**params)
        self.config = config
        
        self.query_processor = QueryProcessor(config)
        self.viz_engine = VisualizationEngine(config)
        
        self.file_input = None
        self.query_input = None
        self.submit_button = None
        self.clear_button = None
        self.status_indicator = None
        self.schema_display = None
        self.results_grid = None
        self.stats_row = None
        
        self.query_history = []
        self.result_cards = []
        
        logger.info("dashboard initialized")
    
    def _create_header(self):
        
        header_html = """
        <div style="
            background:
                radial-gradient(circle at top left, rgba(104, 213, 255, 0.18), transparent 34%),
                radial-gradient(circle at right center, rgba(122, 92, 255, 0.18), transparent 26%),
                linear-gradient(145deg, rgba(15, 24, 42, 0.96) 0%, rgba(8, 12, 22, 0.94) 100%);
            padding: 38px 42px;
            border-radius: 30px;
            border: 1px solid rgba(255, 255, 255, 0.10);
            box-shadow: 0 28px 90px rgba(0, 0, 0, 0.34);
            backdrop-filter: blur(24px);
            margin-bottom: 30px;
            position: relative;
            overflow: hidden;
        ">
            <div style="
                position: absolute;
                inset: 0;
                background:
                    linear-gradient(120deg, rgba(255, 255, 255, 0.05), transparent 42%),
                    radial-gradient(circle at 15% 20%, rgba(104, 213, 255, 0.16), transparent 24%);
                animation: pulse 8s ease-in-out infinite;
            "></div>
            
            <div style="position: relative; z-index: 1; display: flex; flex-wrap: wrap; align-items: stretch; justify-content: space-between; gap: 24px;">
                <div style="flex: 1 1 620px; min-width: 280px;">
                    <div class="eyebrow" style="margin-bottom: 18px;">Natural Language Analytics</div>
                    <div style="display: flex; align-items: center; gap: 18px;">
                        <div style="
                            width: 68px;
                            height: 68px;
                            background: linear-gradient(135deg, #68d5ff 0%, #7a5cff 100%);
                            border-radius: 22px;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            box-shadow: 0 20px 48px rgba(67, 143, 255, 0.34);
                            border: 1px solid rgba(255, 255, 255, 0.16);
                        ">
                            <svg width="34" height="34" viewBox="0 0 24 24" fill="white">
                                <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/>
                            </svg>
                        </div>
                        <div>
                            <h1 style="
                                color: #f4f7fb;
                                margin: 0;
                                font-size: clamp(36px, 5vw, 54px);
                                font-weight: 700;
                                letter-spacing: -0.05em;
                                line-height: 0.98;
                            ">DataWhisperer</h1>
                            <p style="
                                color: rgba(228, 234, 246, 0.76);
                                margin: 8px 0 0 0;
                                font-size: 17px;
                                line-height: 1.6;
                                max-width: 700px;
                            ">Upload a dataset, ask plain-English questions, and watch the dashboard assemble itself into a clean modern workspace for exploration.</p>
                        </div>
                    </div>
                    <div style="display: flex; flex-wrap: wrap; gap: 10px; margin-top: 22px;">
                        <span style="padding: 9px 14px; border-radius: 999px; background: rgba(255,255,255,0.06); color: rgba(228,234,246,0.86); font-size: 13px; border: 1px solid rgba(255,255,255,0.08);">Dark workspace</span>
                        <span style="padding: 9px 14px; border-radius: 999px; background: rgba(255,255,255,0.06); color: rgba(228,234,246,0.86); font-size: 13px; border: 1px solid rgba(255,255,255,0.08);">Multi-question dashboards</span>
                        <span style="padding: 9px 14px; border-radius: 999px; background: rgba(255,255,255,0.06); color: rgba(228,234,246,0.86); font-size: 13px; border: 1px solid rgba(255,255,255,0.08);">Spark-backed insights</span>
                    </div>
                </div>

                <div class="glass" style="
                    flex: 0 1 360px;
                    min-width: 280px;
                    border-radius: 24px;
                    padding: 18px;
                    background: linear-gradient(180deg, rgba(20, 30, 50, 0.72) 0%, rgba(10, 14, 24, 0.74) 100%);
                ">
                    <div style="color: rgba(228, 234, 246, 0.56); font-size: 12px; text-transform: uppercase; letter-spacing: 0.16em; margin-bottom: 14px;">Flow</div>
                    <div style="display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px;">
                        <div style="padding: 16px; border-radius: 18px; background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(255,255,255,0.06);">
                            <div style="font-size: 13px; color: rgba(228,234,246,0.52); margin-bottom: 8px;">Step 01</div>
                            <div style="font-size: 17px; color: #f4f7fb; font-weight: 700;">Upload</div>
                        </div>
                        <div style="padding: 16px; border-radius: 18px; background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(255,255,255,0.06);">
                            <div style="font-size: 13px; color: rgba(228,234,246,0.52); margin-bottom: 8px;">Step 02</div>
                            <div style="font-size: 17px; color: #f4f7fb; font-weight: 700;">Ask</div>
                        </div>
                        <div style="padding: 16px; border-radius: 18px; background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(255,255,255,0.06);">
                            <div style="font-size: 13px; color: rgba(228,234,246,0.52); margin-bottom: 8px;">Step 03</div>
                            <div style="font-size: 17px; color: #f4f7fb; font-weight: 700;">Analyze</div>
                        </div>
                        <div style="padding: 16px; border-radius: 18px; background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(255,255,255,0.06);">
                            <div style="font-size: 13px; color: rgba(228,234,246,0.52); margin-bottom: 8px;">Step 04</div>
                            <div style="font-size: 17px; color: #f4f7fb; font-weight: 700;">Explore</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <style>
            @keyframes pulse {
                0%, 100% { transform: translate(0, 0) scale(1); }
                50% { transform: translate(10%, 10%) scale(1.1); }
            }
        </style>
        """
        
        return pn.pane.HTML(header_html, sizing_mode='stretch_width')
    
    def _create_stats_row(self):
        """Create minimal stats cards"""
        
        self.stats_row = pn.Row(
            visible=False,
            sizing_mode='stretch_width',
            margin=(0, 0, 25, 0)
        )
        
        return self.stats_row
    
    def _update_stats(self):
        """Update statistics with glassmorphism cards"""
        
        if not self.query_processor.table_name:
            self.stats_row.visible = False
            return
        
        stats_html = f"""
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 16px; margin-bottom: 28px;">
            <div class="glass smooth-transition hover-lift" style="padding: 22px; border-radius: 22px; text-align: left; position: relative; overflow: hidden; background: linear-gradient(180deg, rgba(18, 25, 42, 0.94) 0%, rgba(10, 14, 24, 0.90) 100%);">
                <div style="position: absolute; top: 0; left: 0; width: 100%; height: 3px; background: linear-gradient(90deg, #68d5ff 0%, transparent 100%);"></div>
                <div style="font-size: 12px; color: rgba(228,234,246,0.72); font-weight: 700; text-transform: uppercase; letter-spacing: 0.14em; margin-bottom: 14px;">Dataset</div>
                <div style="font-size: 26px; font-weight: 700; color: #f4f7fb; letter-spacing: -0.04em; margin-bottom: 8px;">{self.query_processor.table_name}</div>
                <div style="font-size: 13px; color: rgba(228,234,246,0.76);">Active analysis source</div>
            </div>
            
            <div class="glass smooth-transition hover-lift" style="padding: 22px; border-radius: 22px; text-align: left; position: relative; overflow: hidden; background: linear-gradient(180deg, rgba(18, 25, 42, 0.94) 0%, rgba(10, 14, 24, 0.90) 100%);">
                <div style="position: absolute; top: 0; left: 0; width: 100%; height: 3px; background: linear-gradient(90deg, #1cc8a0 0%, transparent 100%);"></div>
                <div style="font-size: 12px; color: rgba(228,234,246,0.72); font-weight: 700; text-transform: uppercase; letter-spacing: 0.14em; margin-bottom: 14px;">Rows</div>
                <div style="font-size: 26px; font-weight: 700; color: #f4f7fb; letter-spacing: -0.04em; margin-bottom: 8px;">{self.query_processor.row_count:,}</div>
                <div style="font-size: 13px; color: rgba(228,234,246,0.76);">Records ready for querying</div>
            </div>
            
            <div class="glass smooth-transition hover-lift" style="padding: 22px; border-radius: 22px; text-align: left; position: relative; overflow: hidden; background: linear-gradient(180deg, rgba(18, 25, 42, 0.94) 0%, rgba(10, 14, 24, 0.90) 100%);">
                <div style="position: absolute; top: 0; left: 0; width: 100%; height: 3px; background: linear-gradient(90deg, #ffb44a 0%, transparent 100%);"></div>
                <div style="font-size: 12px; color: rgba(228,234,246,0.72); font-weight: 700; text-transform: uppercase; letter-spacing: 0.14em; margin-bottom: 14px;">Columns</div>
                <div style="font-size: 26px; font-weight: 700; color: #f4f7fb; letter-spacing: -0.04em; margin-bottom: 8px;">{len(self.query_processor.schema_details)}</div>
                <div style="font-size: 13px; color: rgba(228,234,246,0.76);">Fields mapped into the model</div>
            </div>
            
            <div class="glass smooth-transition hover-lift" style="padding: 22px; border-radius: 22px; text-align: left; position: relative; overflow: hidden; background: linear-gradient(180deg, rgba(18, 25, 42, 0.94) 0%, rgba(10, 14, 24, 0.90) 100%);">
                <div style="position: absolute; top: 0; left: 0; width: 100%; height: 3px; background: linear-gradient(90deg, #7a5cff 0%, transparent 100%);"></div>
                <div style="font-size: 12px; color: rgba(228,234,246,0.72); font-weight: 700; text-transform: uppercase; letter-spacing: 0.14em; margin-bottom: 14px;">Insights</div>
                <div style="font-size: 26px; font-weight: 700; color: #f4f7fb; letter-spacing: -0.04em; margin-bottom: 8px;">{len(self.query_history)}</div>
                <div style="font-size: 13px; color: rgba(228,234,246,0.76);">Dashboard cards currently shown</div>
            </div>
        </div>
        """
        
        self.stats_row.clear()
        self.stats_row.append(pn.pane.HTML(stats_html, sizing_mode='stretch_width'))
        self.stats_row.visible = True
    
    def _create_upload_section(self):
        """Create minimal upload interface"""
        
        self.file_input = pn.widgets.FileInput(
            accept=','.join(self.config.supported_file_types),
            sizing_mode='stretch_width',
            height=54,
            styles={
                'background': 'linear-gradient(180deg, rgba(14, 20, 34, 0.92) 0%, rgba(10, 14, 24, 0.88) 100%)',
                'border': '1px solid rgba(255, 255, 255, 0.08)',
                'border-radius': '16px',
                'color': '#f4f7fb',
                'box-shadow': '0 16px 40px rgba(0, 0, 0, 0.20)',
                'padding': '8px 10px'
            }
        )
        self.file_input.param.watch(self._on_file_upload, 'value')
        
        upload_html = """
        <div class="glass smooth-transition" style="
            border-radius: 28px;
            padding: 36px;
            text-align: center;
            cursor: pointer;
            border: 1px solid rgba(255, 255, 255, 0.10);
            background:
                radial-gradient(circle at 15% 10%, rgba(104, 213, 255, 0.12), transparent 30%),
                linear-gradient(180deg, rgba(17, 25, 40, 0.86) 0%, rgba(10, 14, 24, 0.86) 100%);
        " onmouseover="this.style.borderColor='rgba(104, 213, 255, 0.28)'; this.style.transform='translateY(-2px)';" 
           onmouseout="this.style.borderColor='rgba(255, 255, 255, 0.10)'; this.style.transform='translateY(0px)';">
            <div class="eyebrow" style="margin-bottom: 18px;">Data Intake</div>
            <div style="
                width: 78px;
                height: 78px;
                margin: 0 auto 22px;
                background: linear-gradient(135deg, #68d5ff 0%, #7a5cff 100%);
                border-radius: 24px;
                display: flex;
                align-items: center;
                justify-content: center;
                box-shadow: 0 18px 36px rgba(80, 123, 255, 0.26);
                border: 1px solid rgba(255,255,255,0.14);
            ">
                <svg width="36" height="36" viewBox="0 0 24 24" fill="white">
                    <path d="M9 16v-6h-4l5-5 5 5h-4v6h-2zm-4 2h14v2h-14z"/>
                </svg>
            </div>
            <h3 style="color: #f4f7fb; margin: 0 0 10px 0; font-weight: 700; font-size: 24px; letter-spacing: -0.04em;">
                Bring a dataset into the workspace
            </h3>
            <p style="color: rgba(228, 234, 246, 0.64); margin: 0 0 20px 0; font-size: 15px; line-height: 1.6; max-width: 560px; margin-left: auto; margin-right: auto;">
                Drag a file in, or use the picker just below. The workflow stays the same, but the surface now feels more like a modern analytics studio.
            </p>
            <div style="display: inline-flex; gap: 8px; flex-wrap: wrap; justify-content: center;">
                <span style="background: rgba(255, 255, 255, 0.06); padding: 7px 13px; border-radius: 999px; font-size: 13px; color: rgba(228, 234, 246, 0.76); border: 1px solid rgba(255,255,255,0.08);">CSV</span>
                <span style="background: rgba(255, 255, 255, 0.06); padding: 7px 13px; border-radius: 999px; font-size: 13px; color: rgba(228, 234, 246, 0.76); border: 1px solid rgba(255,255,255,0.08);">Excel</span>
                <span style="background: rgba(255, 255, 255, 0.06); padding: 7px 13px; border-radius: 999px; font-size: 13px; color: rgba(228, 234, 246, 0.76); border: 1px solid rgba(255,255,255,0.08);">JSON</span>
                <span style="background: rgba(255, 255, 255, 0.06); padding: 7px 13px; border-radius: 999px; font-size: 13px; color: rgba(228, 234, 246, 0.76); border: 1px solid rgba(255,255,255,0.08);">Parquet</span>
            </div>
        </div>
        """
        
        return pn.Column(
            pn.pane.HTML(upload_html, sizing_mode='stretch_width'),
            self.file_input,
            sizing_mode='stretch_width',
            margin=(0, 0, 25, 0)
        )
    
    def _create_query_section(self):
        """Create minimal query interface with proper text visibility"""
        
        self.query_input = pn.widgets.TextAreaInput(
            placeholder='Ask multiple questions (one per line):\nWhat is the total revenue?\nShow top 10 products by sales\nRevenue trend over time',
            height=140,
            disabled=True,
            sizing_mode='stretch_width',
            auto_grow=True,
            max_height=400,
            styles={
                'font-size': '16px',
                'background': 'transparent',
                'border': 'none',
                'border-radius': '0',
                'padding': '0',
                'color': '#f4f7fb',
                'backdrop-filter': 'none',
                'box-shadow': 'none',
                'resize': 'vertical'
            },
            stylesheets=["""
                :host {
                    --design-background-color: transparent;
                    display: block;
                }
                textarea {
                    color: #f4f7fb !important;
                    background: linear-gradient(180deg, rgba(15, 21, 36, 0.94) 0%, rgba(10, 14, 24, 0.90) 100%) !important;
                    resize: vertical !important;
                    min-height: 140px !important;
                    border: 1px solid rgba(255, 255, 255, 0.10) !important;
                    border-radius: 22px !important;
                    padding: 18px !important;
                    font-family: 'Manrope', sans-serif !important;
                    line-height: 1.7 !important;
                    letter-spacing: -0.01em !important;
                    box-shadow: 0 20px 48px rgba(0, 0, 0, 0.22) !important;
                    outline: none !important;
                }
                textarea:focus {
                    border-color: rgba(104, 213, 255, 0.42) !important;
                    box-shadow:
                        0 0 0 1px rgba(104, 213, 255, 0.18) inset,
                        0 20px 48px rgba(0, 0, 0, 0.22) !important;
                }
                textarea::placeholder {
                    color: rgba(228, 234, 246, 0.56) !important;
                }
            """]
        )
        
        self.submit_button = pn.widgets.Button(
            name='✨ Analyze All',
            button_type='primary',
            width=160,
            height=52,
            disabled=True,
            styles={
                'background': 'linear-gradient(135deg, #68d5ff 0%, #7a5cff 100%)',
                'border': 'none',
                'font-size': '16px',
                'font-weight': '700',
                'border-radius': '16px',
                'box-shadow': '0 16px 32px rgba(86, 128, 255, 0.32)',
                'color': 'white'
            }
        )
        self.submit_button.on_click(self._on_submit_query)
        
        self.clear_button = pn.widgets.Button(
            name='Clear Dashboard',
            button_type='light',
            width=140,
            height=52,
            disabled=True,
            styles={
                'background': 'rgba(255, 255, 255, 0.05)',
                'border': '1px solid rgba(255, 255, 255, 0.10)',
                'border-radius': '16px',
                'font-size': '15px',
                'font-weight': '600',
                'color': '#f4f7fb',
                'box-shadow': '0 14px 30px rgba(0, 0, 0, 0.18)'
            }
        )
        self.clear_button.on_click(self._on_clear_results)
        
        self.status_indicator = pn.indicators.LoadingSpinner(
            value=False,
            size=32,
            color='primary',
            visible=False
        )
        
        button_row = pn.Row(
            pn.layout.HSpacer(),
            self.submit_button,
            self.clear_button,
            self.status_indicator,
            pn.layout.HSpacer(),
            align='center',
            margin=(15, 0, 0, 0)
        )
        
        query_intro = """
        <div style="margin: 4px 0 16px 0;">
            <div class="eyebrow" style="margin-bottom: 16px;">Query Studio</div>
            <h3 style="color: #f4f7fb; margin: 0 0 10px 0; font-size: 26px; font-weight: 700; letter-spacing: -0.04em;">Ask multiple questions</h3>
            <p style="color: rgba(228, 234, 246, 0.76); margin: 0; font-size: 15px; line-height: 1.6; max-width: 760px;">Enter one prompt per line and build the dashboard card by card without changing the underlying layout.</p>
        </div>
        """
        
        return pn.Column(
            pn.pane.HTML(query_intro, sizing_mode='stretch_width'),
            self.query_input,
            button_row,
            sizing_mode='stretch_width'
        )
    
    def _create_results_section(self):
        """Create dashboard-style results container (like Power BI/Tableau)"""
        
        empty_state_html = """
        <div style="
            text-align: center;
            padding: 86px 28px;
            background:
                radial-gradient(circle at top left, rgba(104, 213, 255, 0.10), transparent 28%),
                linear-gradient(180deg, rgba(16, 23, 38, 0.72) 0%, rgba(9, 13, 22, 0.72) 100%);
            border-radius: 28px;
            border: 1px solid rgba(255, 255, 255, 0.08);
            box-shadow: 0 20px 50px rgba(0,0,0,0.20);
        ">
            <div style="
                width: 88px;
                height: 88px;
                margin: 0 auto 26px;
                background: linear-gradient(135deg, rgba(104, 213, 255, 0.22) 0%, rgba(122, 92, 255, 0.24) 100%);
                border-radius: 26px;
                display: flex;
                align-items: center;
                justify-content: center;
                border: 1px solid rgba(255,255,255,0.08);
            ">
                <svg width="40" height="40" viewBox="0 0 24 24" fill="rgba(244, 247, 251, 0.48)">
                    <path d="M3 3h7v7h-7v-7zm11 0h7v7h-7v-7zm-11 11h7v7h-7v-7zm11 0h7v7h-7v-7z"/>
                </svg>
            </div>
            <h3 style="color: rgba(244, 247, 251, 0.92); margin: 0 0 12px 0; font-weight: 700; font-size: 24px; letter-spacing: -0.04em;">
                Ready for Insights
            </h3>
            <p style="color: rgba(228, 234, 246, 0.56); margin: 0 auto; font-size: 16px; max-width: 560px; line-height: 1.7;">
                Upload your data and ask multiple questions at once.<br/>Each insight will appear here in a dashboard layout.
            </p>
        </div>
        """
        
        # Use GridBox for true dashboard-style layout
        self.results_grid = pn.GridBox(
            pn.pane.HTML(empty_state_html, sizing_mode='stretch_width'),
            ncols=2,  # 2 columns by default (Power BI style)
            sizing_mode='stretch_width'
        )
        
        return pn.Column(
            pn.pane.HTML("""
                <div style="margin: 4px 0 18px 0;">
                    <div class="eyebrow" style="margin-bottom: 14px;">Dashboard Canvas</div>
                    <h3 style="
                        color: #f4f7fb;
                        margin: 0 0 8px 0;
                        font-size: 28px;
                        font-weight: 700;
                        letter-spacing: -0.05em;
                    ">Dashboard</h3>
                    <p style="color: rgba(228, 234, 246, 0.76); margin: 0; font-size: 15px; line-height: 1.6;">
                        Cards still render in the same dashboard layout. The visual treatment is just cleaner, sharper, and more contemporary.
                    </p>
                </div>
            """),
            self.results_grid,
            sizing_mode='stretch_width'
        )
    
    def _on_file_upload(self, event):
        """Handle file upload"""
        
        if event.new is None:
            return
        
        try:
            self.status_indicator.visible = True
            self.status_indicator.value = True
            
            self.file_input.disabled = True
            self.query_input.disabled = True
            self.submit_button.disabled = True
            
            file_name = self.file_input.filename
            file_size_mb = len(event.new) / (1024 * 1024)
            
            if file_size_mb > self.config.max_file_size_mb:
                pn.state.notifications.error(
                    f"File too large ({file_size_mb:.1f}MB). Max: {self.config.max_file_size_mb}MB",
                    duration=5000
                )
                self.file_input.value = None
                return
            
            file_extension = Path(file_name).suffix.lower()
            if file_extension not in self.config.supported_file_types:
                pn.state.notifications.error(
                    f"Unsupported file type: {file_extension}",
                    duration=5000
                )
                self.file_input.value = None
                return
            
            pn.state.notifications.info(
                f"📂 Processing {file_name}...",
                duration=3000
            )
            
            def process_file():
                try:
                    success, message = self.query_processor.load_dataset(event.new, file_name)
                    
                    if not success:
                        raise ValueError(message)
                    
                    pn.state.execute(lambda: self._update_ui_after_upload(file_name))
                    
                    pn.state.execute(
                        lambda: pn.state.notifications.success(
                            f"✅ {file_name} loaded successfully!",
                            duration=4000
                        )
                    )
                    
                except Exception as e:
                    error_msg = f"Error: {str(e)}"
                    logger.error(error_msg, exc_info=True)
                    pn.state.execute(
                        lambda: pn.state.notifications.error(error_msg, duration=6000)
                    )
                    pn.state.execute(lambda: setattr(self.file_input, 'value', None))
                    
                finally:
                    pn.state.execute(lambda: setattr(self.status_indicator, 'visible', False))
                    pn.state.execute(lambda: setattr(self.status_indicator, 'value', False))
                    pn.state.execute(lambda: setattr(self.file_input, 'disabled', False))
                    pn.state.execute(lambda: setattr(self.query_input, 'disabled', False))
            
            thread = threading.Thread(target=process_file, daemon=True)
            thread.start()
            
        except Exception as e:
            logger.error("Upload error: %s", str(e), exc_info=True)
            pn.state.notifications.error(f"Upload failed: {str(e)}", duration=6000)
            
            self.status_indicator.visible = False
            self.status_indicator.value = False
            self.file_input.disabled = False
            self.query_input.disabled = False
            self.file_input.value = None
    
    def _update_ui_after_upload(self, file_name: str):
        """Update UI after successful upload"""
        
        self.data_loaded = True
        self.query_input.disabled = False
        self.submit_button.disabled = False
        self._update_stats()
        
        logger.info("✅ UI updated for dataset: %s", file_name)
    
    def _on_submit_query(self, event):
        """Handle query submission with multi-query support and dashboard layout"""
        
        if self.processing or not self.query_input.value:
            return
        
        self.processing = True
        self.submit_button.disabled = True
        self.query_input.disabled = True
        self.status_indicator.visible = True
        self.status_indicator.value = True
        
        query_text = self.query_input.value.strip()
        
        logger.info("🔍 Processing queries: %s", query_text[:100])
        pn.state.notifications.info(f"🤖 Analyzing queries...", duration=2000)
        
        def run_queries():
            try:
                # process_query now returns a LIST of results
                results = self.query_processor.process_queries(query_text)
                
                # Validate results
                if not isinstance(results, list):
                    raise TypeError(f"Expected list of results, got {type(results)}")
                
                if not results:
                    raise ValueError("No results returned from query processor")
                
                # Process each result
                successful_results = []
                failed_results = []
                
                for idx, result in enumerate(results):
                    try:
                        # Validate result structure
                        if not isinstance(result, dict):
                            logger.error(f"Result {idx} is not a dict: {type(result)}")
                            failed_results.append({
                                'query': f'Query {idx+1}',
                                'error': f'Invalid result type: {type(result)}'
                            })
                            continue
                        
                        if not result.get('success', False):
                            error_msg = result.get('error', 'Unknown error')
                            logger.warning(f"Query {idx} failed: {error_msg}")
                            failed_results.append({
                                'query': result.get('query', f'Query {idx+1}'),
                                'error': error_msg
                            })
                            continue
                        
                        # Validate required fields
                        required_fields = ['query', 'data', 'viz_config']
                        missing_fields = [f for f in required_fields if f not in result]
                        if missing_fields:
                            logger.error(f"Result {idx} missing fields: {missing_fields}")
                            failed_results.append({
                                'query': result.get('query', f'Query {idx+1}'),
                                'error': f'Missing fields: {missing_fields}'
                            })
                            continue
                        
                        # Extract data safely
                        query = result.get('query', f'Query {idx+1}')
                        sql = result.get('sql', '')
                        data = result.get('data')
                        viz_config = result.get('viz_config', {})
                        
                        # Validate data
                        if data is None or (hasattr(data, 'empty') and data.empty):
                            logger.warning(f"Query {idx} returned empty data")
                            failed_results.append({
                                'query': query,
                                'error': 'Query returned no data'
                            })
                            continue
                        
                        # Create visualization
                        try:
                            viz = self.viz_engine.create_visualization(data, viz_config, query)
                            
                            successful_results.append({
                                'query': query,
                                'sql': sql,
                                'viz': viz,
                                'viz_config': viz_config,
                                'data': data
                            })
                            
                        except Exception as viz_error:
                            logger.error(f"Viz creation failed for query {idx}: {viz_error}", exc_info=True)
                            failed_results.append({
                                'query': query,
                                'error': f'Visualization error: {str(viz_error)}'
                            })
                    
                    except Exception as result_error:
                        logger.error(f"Error processing result {idx}: {result_error}", exc_info=True)
                        failed_results.append({
                            'query': f'Query {idx+1}',
                            'error': str(result_error)
                        })
                
                # Update UI on main thread
                def apply_results():
                    try:
                        # Show error notifications for failed queries
                        for failed in failed_results:
                            pn.state.notifications.warning(
                                f"⚠️ {failed['query']}: {failed['error'][:100]}",
                                duration=5000
                            )
                        
                        # Add successful visualizations to dashboard
                        if successful_results:
                            self._rebuild_dashboard_grid(successful_results)
                            
                            # Update query history
                            for result in successful_results:
                                self.query_history.append({
                                    'query': result['query'],
                                    'sql': result['sql'],
                                    'timestamp': datetime.now().isoformat(),
                                    'viz_type': result['viz_config'].get('visualization_type', 'unknown')
                                })
                            
                            self.clear_button.disabled = False
                            self.query_input.value = ""
                            self._update_stats()
                            
                            success_msg = f"✅ Added {len(successful_results)} insight(s) to dashboard!"
                            if failed_results:
                                success_msg += f" ({len(failed_results)} failed)"
                            pn.state.notifications.success(success_msg, duration=4000)
                        else:
                            fatal_error = next(
                                (
                                    failed['error']
                                    for failed in failed_results
                                    if 'api key is invalid or expired' in failed['error'].lower()
                                ),
                                None,
                            )
                            pn.state.notifications.error(
                                fatal_error or "❌ All queries failed. Please check your questions and try again.",
                                duration=6000
                            )
                    
                    except Exception as ui_error:
                        logger.error(f"Error updating UI: {ui_error}", exc_info=True)
                        pn.state.notifications.error(f"UI Error: {str(ui_error)}", duration=6000)
                
                pn.state.execute(apply_results)
                
            except Exception as exc:
                error_text = str(exc)
                error_trace = traceback.format_exc()
                logger.error(f"Query processing error: {error_text}\n{error_trace}")
                
                def apply_error():
                    pn.state.notifications.error(f"❌ {error_text[:150]}", duration=6000)
                
                pn.state.execute(apply_error)
                
            finally:
                def reset_ui():
                    self.processing = False
                    self.submit_button.disabled = False
                    self.query_input.disabled = False
                    self.status_indicator.visible = False
                    self.status_indicator.value = False
                
                pn.state.execute(reset_ui)
        
        thread = threading.Thread(target=run_queries, daemon=True)
        thread.start()
    
    def _rebuild_dashboard_grid(self, new_results: List[Dict[str, Any]]):
        """Rebuild the entire dashboard grid with all visualizations (Power BI style)"""
        
        try:
            # Add new results to existing cards
            for result in new_results:
                card = self._create_result_card(
                    result['query'],
                    result['sql'],
                    result['viz'],
                    result['viz_config']
                )
                self.result_cards.append(card)
            
            # Clear the grid
            self.results_grid.clear()
            
            # Determine optimal layout based on number of cards
            n_cards = len(self.result_cards)
            
            if n_cards == 0:
                # Show empty state
                self._show_empty_dashboard()
                return
            
            # Smart grid layout (like Power BI)
            # - 1 card: Full width
            # - 2-4 cards: 2 columns
            # - 5+ cards: 2-3 columns based on viz types
            
            if n_cards == 1:
                ncols = 1
            elif n_cards <= 4:
                ncols = 2
            else:
                # For 5+ cards, use 2 columns (cleaner look)
                ncols = 2
            
            # Rebuild grid with new layout
            self.results_grid.ncols = ncols
            
            # Add all cards to grid
            for card in self.result_cards:
                self.results_grid.append(card)
            
            logger.info(f"✅ Dashboard rebuilt: {n_cards} cards in {ncols} columns")
            
        except Exception as e:
            logger.error(f"Error rebuilding dashboard: {e}", exc_info=True)
            pn.state.notifications.error(f"Dashboard layout error: {str(e)}", duration=5000)
    
    def _show_empty_dashboard(self):
        """Show empty state in dashboard"""
        empty_html = """
        <div style="
            text-align: center;
            padding: 86px 28px;
            background:
                radial-gradient(circle at top left, rgba(104, 213, 255, 0.10), transparent 28%),
                linear-gradient(180deg, rgba(16, 23, 38, 0.72) 0%, rgba(9, 13, 22, 0.72) 100%);
            border-radius: 28px;
            border: 1px solid rgba(255, 255, 255, 0.08);
            box-shadow: 0 20px 50px rgba(0,0,0,0.20);
        ">
            <div style="
                width: 88px;
                height: 88px;
                margin: 0 auto 26px;
                background: linear-gradient(135deg, rgba(104, 213, 255, 0.22) 0%, rgba(122, 92, 255, 0.24) 100%);
                border-radius: 26px;
                display: flex;
                align-items: center;
                justify-content: center;
                border: 1px solid rgba(255,255,255,0.08);
            ">
                <svg width="40" height="40" viewBox="0 0 24 24" fill="rgba(244, 247, 251, 0.48)">
                    <path d="M3 3h7v7h-7v-7zm11 0h7v7h-7v-7zm-11 11h7v7h-7v-7zm11 0h7v7h-7v-7z"/>
                </svg>
            </div>
            <h3 style="color: rgba(244, 247, 251, 0.92); margin: 0 0 12px 0; font-weight: 700; font-size: 24px; letter-spacing: -0.04em;">
                Ready for Insights
            </h3>
            <p style="color: rgba(228, 234, 246, 0.56); margin: 0; font-size: 16px; line-height: 1.7;">
                Ask multiple questions to populate your dashboard.
            </p>
        </div>
        """
        self.results_grid.append(pn.pane.HTML(empty_html, sizing_mode='stretch_both'))
    
    def _create_result_card(self, query, sql, viz, viz_config):
        """Create minimal Apple-style result card for dashboard"""
        
        try:
            timestamp = datetime.now().strftime("%H:%M")
            viz_type = viz_config.get('visualization_type', 'chart')
            title = viz_config.get('title', 'Results')
            description = viz_config.get('description', '')
            
            # Determine card size based on viz type
            # KPIs and numbers: compact
            # Charts: standard
            # Tables: larger
            if viz_type in ['number', 'kpi', 'metric']:
                min_height = 200
            elif viz_type == 'table':
                min_height = 400
            else:
                min_height = 350
            
            # Create card with glassmorphism
            card_content = pn.Column(
                # Header
                pn.pane.HTML(f"""
                    <div style="
                        padding: 22px 22px 16px 22px;
                        border-bottom: 1px solid rgba(255, 255, 255, 0.06);
                        background:
                            linear-gradient(180deg, rgba(255,255,255,0.03) 0%, rgba(255,255,255,0.00) 100%);
                    ">
                        <div style="font-size: 12px; color: rgba(228,234,246,0.58); margin-bottom: 10px; text-transform: uppercase; letter-spacing: 0.12em; font-weight: 700;">
                            {timestamp} • {viz_type.replace('_', ' ').title()}
                        </div>
                        <div style="font-size: 18px; font-weight: 700; color: #f4f7fb; line-height: 1.5; letter-spacing: -0.02em;">
                            {query}
                        </div>
                    </div>
                """, sizing_mode='stretch_width'),
                
                # Insight badge (if exists)
                pn.pane.HTML(f"""
                    <div style="
                        padding: 16px 18px;
                        background: linear-gradient(135deg, rgba(104, 213, 255, 0.08) 0%, rgba(122, 92, 255, 0.08) 100%);
                        border: 1px solid rgba(255,255,255,0.08);
                        margin: 16px 20px 6px 20px;
                        border-radius: 16px;
                    ">
                        <div style="font-size: 12px; color: rgba(228,234,246,0.56); margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.12em; font-weight: 700;">
                            💡 Insight
                        </div>
                        <div style="font-size: 14px; color: #f4f7fb; line-height: 1.6;">
                            {description}
                        </div>
                    </div>
                """, sizing_mode='stretch_width') if description else pn.Spacer(height=0),
                
                # Visualization container
                pn.pane.HTML('<div style="padding: 0 20px 20px 20px;">', sizing_mode='stretch_width'),
                viz,
                pn.pane.HTML('</div>', sizing_mode='stretch_width'),
                
                sizing_mode='stretch_both',
                min_height=min_height,
                styles={
                    'background': 'linear-gradient(180deg, rgba(18, 25, 42, 0.78) 0%, rgba(10, 14, 24, 0.82) 100%)',
                    'border': '1px solid rgba(255, 255, 255, 0.08)',
                    'border-radius': '24px',
                    'backdrop-filter': 'blur(24px)',
                    'overflow': 'hidden',
                    'box-shadow': '0 24px 56px rgba(0, 0, 0, 0.28)'
                }
            )
            
            return card_content
            
        except Exception as e:
            logger.error(f"Error creating result card: {e}", exc_info=True)
            # Return error card
            return pn.pane.HTML(f"""
                <div style="
                    background: rgba(255, 0, 0, 0.1);
                    border: 1px solid rgba(255, 0, 0, 0.3);
                    border-radius: 24px;
                    padding: 30px;
                    text-align: center;
                    color: #ff6b6b;
                ">
                    <h4>⚠️ Card Creation Error</h4>
                    <p>{str(e)}</p>
                </div>
            """, sizing_mode='stretch_both', height=200)
    
    def _on_clear_results(self, event):
        """Clear all results from dashboard"""
        
        try:
            self.result_cards.clear()
            self.query_history.clear()
            
            self.results_grid.clear()
            self._show_empty_dashboard()
            
            self.clear_button.disabled = True
            self._update_stats()
            
            pn.state.notifications.info("🧹 Dashboard cleared", duration=2000)
            logger.info("Dashboard cleared")
            
        except Exception as e:
            logger.error(f"Error clearing dashboard: {e}", exc_info=True)
            pn.state.notifications.error(f"Clear error: {str(e)}", duration=4000)
    
    def create_app(self):
        """Create the complete Apple-inspired dark theme application"""
        
        content = pn.Column(
            pn.pane.HTML(APPLE_DARK_CSS),
            self._create_header(),
            self._create_stats_row(),
            self._create_upload_section(),
            self._create_query_section(),
            self._create_results_section(),
            sizing_mode='stretch_width',
            styles={
                'background': 'transparent',
                'padding': '34px clamp(18px, 3vw, 42px) 56px clamp(18px, 3vw, 42px)',
                'max-width': '1560px',
                'margin': '0 auto',
                'min-height': '100vh'
            }
        )
        
        return pn.Column(
            content,
            sizing_mode='stretch_width',
            styles={
                'background': 'radial-gradient(circle at 12% 10%, rgba(104, 213, 255, 0.12), transparent 28%), radial-gradient(circle at 86% 8%, rgba(122, 92, 255, 0.14), transparent 24%), radial-gradient(circle at 55% 100%, rgba(28, 200, 160, 0.08), transparent 30%), linear-gradient(180deg, #04070d 0%, #09111c 45%, #050912 100%)',
                'min-height': '100vh'
            }
        )
