from flask import Flask, request, redirect, url_for, render_template_string
import os
import subprocess
import sqlite3
from datetime import datetime

app = Flask(__name__)

# データベース初期化
def init_db():
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS data (
            id INTEGER PRIMARY KEY,
            content TEXT,
            created_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def home():
    user_agent = request.headers.get('User-Agent', '').lower()
    is_mobile = 'iphone' in user_agent or 'android' in user_agent
    if is_mobile:
        return '''
        <!DOCTYPE html>
        <html lang="ja">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>サーバー管理 (モバイル)</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 10px; }
                a, button { display: block; margin: 10px 0; text-align: center; padding: 10px; text-decoration: none; border: 1px solid #007BFF; border-radius: 5px; background-color: #007BFF; color: white; }
                button:hover, a:hover { background-color: #0056b3; }
            </style>
        </head>
        <body>
            <h1>サーバー管理ページ (モバイル版)</h1>
            <a href="/view-data">データビュー画面</a>
            <a href="/edit-source">ソースコードを編集</a>
            <form action="/restart-server" method="POST">
                <button type="submit">サーバーを再起動</button>
            </form>
        </body>
        </html>
        '''
    else:
        return '''
        <!DOCTYPE html>
        <html lang="ja">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>サーバー管理 (PC)</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                a, button { display: inline-block; margin: 10px; padding: 10px; text-decoration: none; border: 1px solid #007BFF; border-radius: 5px; background-color: #007BFF; color: white; }
                button:hover, a:hover { background-color: #0056b3; }
            </style>
        </head>
        <body>
            <h1>サーバー管理ページ (PC版)</h1>
            <a href="/view-data">データビュー画面</a>
            <a href="/edit-source">ソースコードを編集</a>
            <form action="/restart-server" method="POST">
                <button type="submit">サーバーを再起動</button>
            </form>
        </body>
        </html>
        '''

@app.route('/edit-source', methods=['GET', 'POST'])
def edit_source():
    base_path = os.path.dirname(__file__)
    files = {
        "Python (app.py)": os.path.join(base_path, "app.py"),
        "HTML (send_form.html)": os.path.join(base_path, "send_form.html")
    }

    if request.method == 'POST':
        file_to_edit = request.form.get('file_to_edit')
        new_code = request.form.get('source_code', '')

        if not file_to_edit or file_to_edit not in files:
            return "選択されたファイルが無効です。", 400

        try:
            with open(files[file_to_edit], 'w', encoding='utf-8') as f:
                f.write(new_code)
            return redirect(url_for('edit_source', file=file_to_edit))
        except Exception as e:
            return f"ファイルの保存中にエラーが発生しました: {e}", 500

    selected_file = request.args.get('file')
    current_code = ""

    if selected_file and selected_file in files:
        try:
            with open(files[selected_file], 'r', encoding='utf-8') as f:
                current_code = f.read()
        except FileNotFoundError:
            return "指定されたファイルが見つかりませんでした。", 404

    file_options = ''.join(
        f'<option value="{key}" {"selected" if key == selected_file else ""}>{key}</option>'
        for key in files.keys()
    )

    return f'''
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ソースコード編集</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            textarea {{ width: 100%; height: 300px; }}
            button {{ padding: 10px 20px; background-color: #007BFF; color: white; border: none; border-radius: 5px; cursor: pointer; }}
            button:hover {{ background-color: #0056b3; }}
            select {{ margin-bottom: 10px; }}
        </style>
    </head>
    <body>
        <h1>ソースコードを編集</h1>
        <form action="/edit-source" method="GET">
            <label for="file">編集するファイルを選択:</label>
            <select name="file" id="file" onchange="this.form.submit()">
                {file_options}
            </select>
        </form>
        <form action="/edit-source" method="POST">
            <label for="source_code">ソースコード:</label><br>
            <textarea name="source_code" id="source_code">{current_code}</textarea>
            <input type="hidden" name="file_to_edit" value="{selected_file}">
            <br>
            <button type="submit">保存</button>
        </form>
        <a href="/">戻る</a>
    </body>
    </html>
    '''

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
