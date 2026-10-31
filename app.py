import os
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Text & Language Toolbox</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #4f46e5;
            --primary-hover: #4338ca;
            --bg: #f8fafc;
            --card-bg: #ffffff;
            --text-main: #0f172a;
            --text-muted: #64748b;
            --border: #e2e8f0;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background-color: var(--bg);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 40px 20px;
        }
        .container {
            max-width: 800px;
            width: 100%;
            background: var(--card-bg);
            border-radius: 16px;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.01);
            border: 1px solid var(--border);
            padding: 32px;
        }
        .header {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 24px;
        }
        .logo-badge {
            width: 44px;
            height: 44px;
            background: linear-gradient(135deg, #4f46e5, #06b6d4);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 22px;
            color: white;
        }
        h1 { font-size: 22px; font-weight: 700; color: var(--text-main); }
        p.subtitle { font-size: 14px; color: var(--text-muted); margin-top: 2px; }
        textarea {
            width: 100%;
            height: 220px;
            padding: 16px;
            border-radius: 12px;
            border: 1.5px solid var(--border);
            font-family: inherit;
            font-size: 15px;
            color: var(--text-main);
            outline: none;
            resize: vertical;
            transition: border-color 0.2s, box-shadow 0.2s;
        }
        textarea:focus {
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
            gap: 16px;
            margin-top: 24px;
        }
        .stat-card {
            background: #f1f5f9;
            padding: 16px;
            border-radius: 12px;
            text-align: center;
            border: 1px solid #e2e8f0;
        }
        .stat-value {
            font-size: 24px;
            font-weight: 700;
            color: var(--primary);
        }
        .stat-label {
            font-size: 12px;
            color: var(--text-muted);
            text-transform: uppercase;
            font-weight: 600;
            margin-top: 4px;
        }
        .actions {
            margin-top: 24px;
            display: flex;
            gap: 12px;
        }
        .btn {
            background: var(--primary);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.2s;
        }
        .btn:hover { background: var(--primary-hover); }
        .btn-secondary {
            background: #e2e8f0;
            color: #334155;
        }
        .btn-secondary:hover { background: #cbd5e1; }
        .status-dot {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #10b981;
            margin-right: 6px;
        }
        .footer {
            margin-top: 24px;
            font-size: 13px;
            color: var(--text-muted);
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo-badge">⚡</div>
            <div>
                <h1>AI 文本智能分析与语言工具箱</h1>
                <p class="subtitle">轻量级自然语言处理、字符统计与可读性评估套件</p>
            </div>
        </div>

        <textarea id="textInput" placeholder="在这里输入或粘贴要分析的文本..."></textarea>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value" id="charCount">0</div>
                <div class="stat-label">总字符数</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="wordCount">0</div>
                <div class="stat-label">词数 / 汉字</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="lineCount">0</div>
                <div class="stat-label">段落行数</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="readingTime">0 分钟</div>
                <div class="stat-label">预估阅读时间</div>
            </div>
        </div>

        <div class="actions">
            <button class="btn btn-secondary" onclick="clearText()">清空内容</button>
            <button class="btn btn-secondary" onclick="formatText()">修剪多余空行</button>
        </div>

        <div class="footer">
            <div><span class="status-dot"></span>服务就绪 (Cloud Linux Container)</div>
            <div>v1.0.0 · Web Toolbox</div>
        </div>
    </div>

    <script>
        const input = document.getElementById('textInput');
        const charCount = document.getElementById('charCount');
        const wordCount = document.getElementById('wordCount');
        const lineCount = document.getElementById('lineCount');
        const readingTime = document.getElementById('readingTime');

        function updateStats() {
            const val = input.value;
            charCount.textContent = val.length;
            
            // 简单分词与字符匹配
            const words = val.trim() ? val.trim().split(/\\s+/).length : 0;
            const cjk = (val.match(/[\\u4e00-\\u9fa5]/g) || []).length;
            wordCount.textContent = words + cjk;

            const lines = val.trim() ? val.split('\\n').filter(l => l.trim().length > 0).length : 0;
            lineCount.textContent = lines;

            const readMin = Math.ceil((val.length || 0) / 400);
            readingTime.textContent = (val.length ? readMin : 0) + ' 分钟';
        }

        input.addEventListener('input', updateStats);

        function clearText() {
            input.value = '';
            updateStats();
        }

        function formatText() {
            input.value = input.value.split('\\n').map(l => l.trim()).filter(l => l.length > 0).join('\\n\\n');
            updateStats();
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "service": "text-toolbox"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 7860))
    app.run(host='0.0.0.0', port=port)
