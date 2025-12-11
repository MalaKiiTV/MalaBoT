from flask import Flask, render_template, session, redirect, request, jsonify
import os
import sqlite3
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')

DB_PATH = '../data/malabot.db'

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>MalaBot Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
            h1 { color: #5865F2; }
            a { color: #5865F2; text-decoration: none; padding: 10px 20px; background: #f0f0f0; border-radius: 5px; display: inline-block; margin: 10px 0; }
            a:hover { background: #e0e0e0; }
        </style>
    </head>
    <body>
        <h1>MalaBot Dashboard</h1>
        <p>This is a simple dashboard that reads from your bot's database.</p>
        <a href="/guilds">View Guilds</a>
    </body>
    </html>
    """

@app.route('/guilds')
def guilds():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT guild_id FROM settings")
        guilds = cursor.fetchall()
        conn.close()
        
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Guilds - MalaBot Dashboard</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
                h1 { color: #5865F2; }
                ul { list-style: none; padding: 0; }
                li { margin: 10px 0; }
                a { color: #5865F2; text-decoration: none; padding: 10px 20px; background: #f0f0f0; border-radius: 5px; display: inline-block; }
                a:hover { background: #e0e0e0; }
                .back { background: #ccc; }
            </style>
        </head>
        <body>
            <h1>Guilds in Database</h1>
            <ul>
        """
        
        if guilds:
            for guild in guilds:
                html += f'<li><a href="/guild/{guild[0]}">Guild ID: {guild[0]}</a></li>'
        else:
            html += '<li>No guilds found in database yet.</li>'
        
        html += """
            </ul>
            <a href="/" class="back">Back to Home</a>
        </body>
        </html>
        """
        return html
    except Exception as e:
        return f"<h1>Error</h1><p>{str(e)}</p><p>Make sure your bot has run at least once to create the database.</p>"

@app.route('/guild/<guild_id>')
def guild_settings(guild_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT setting_key, setting_value FROM settings WHERE guild_id = ?", (guild_id,))
        settings = cursor.fetchall()
        conn.close()
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Guild {guild_id} - MalaBot Dashboard</title>
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }}
                h1 {{ color: #5865F2; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background-color: #5865F2; color: white; }}
                tr:hover {{ background-color: #f5f5f5; }}
                a {{ color: #5865F2; text-decoration: none; padding: 10px 20px; background: #f0f0f0; border-radius: 5px; display: inline-block; margin: 10px 0; }}
                a:hover {{ background: #e0e0e0; }}
            </style>
        </head>
        <body>
            <h1>Settings for Guild {guild_id}</h1>
        """
        
        if settings:
            html += """
            <table>
                <tr>
                    <th>Setting Key</th>
                    <th>Setting Value</th>
                </tr>
            """
            for setting in settings:
                html += f"<tr><td>{setting[0]}</td><td>{setting[1]}</td></tr>"
            html += "</table>"
        else:
            html += "<p>No settings found for this guild yet.</p>"
        
        html += """
            <a href="/guilds">Back to Guilds</a>
        </body>
        </html>
        """
        return html
    except Exception as e:
        return f"<h1>Error</h1><p>{str(e)}</p>"

if __name__ == '__main__':
    print("Starting MalaBot Dashboard...")
    print("Open your browser to: http://localhost:5000")
    app.run(debug=True, port=5000, host='127.0.0.1')
