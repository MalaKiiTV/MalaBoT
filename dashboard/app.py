from flask import Flask, render_template, redirect, url_for, session, request, jsonify
from flask_discord import DiscordOAuth2Session, requires_authorization, Unauthorized
import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
import requests
import traceback

# Load environment variables
load_dotenv()

# IMPORTANT: Allow OAuth over HTTP (for development/non-HTTPS servers)
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-here')
app.config['DISCORD_CLIENT_ID'] = os.getenv('DISCORD_CLIENT_ID')
app.config['DISCORD_CLIENT_SECRET'] = os.getenv('DISCORD_CLIENT_SECRET')
app.config['DISCORD_REDIRECT_URI'] = 'http://165.232.156.230:8080/callback'
app.config['DISCORD_BOT_TOKEN'] = os.getenv('DISCORD_TOKEN')

discord_oauth = DiscordOAuth2Session(app)

def get_db_connection():
    """Create database connection"""
    return psycopg2.connect(os.getenv('DATABASE_URL'))

def get_bot_guilds():
    """Fetch guilds the bot is in using Discord REST API"""
    headers = {
        'Authorization': f'Bot {app.config["DISCORD_BOT_TOKEN"]}'
    }
    response = requests.get('https://discord.com/api/v10/users/@me/guilds', headers=headers)
    if response.status_code == 200:
        return response.json()
    return []

def map_settings_for_template(db_settings):
    """Map database settings to template field names"""
    mapped = {}
    
    # Direct mappings
    for key, value in db_settings.items():
        mapped[key] = value
    
    # Handle channel_id variants - use the _id version if it exists
    if 'welcome_channel_id' in db_settings:
        mapped['welcome_channel'] = db_settings['welcome_channel_id']
    if 'goodbye_channel_id' in db_settings:
        mapped['goodbye_channel'] = db_settings['goodbye_channel_id']
    if 'xp_channel_id' in db_settings:
        mapped['xp_levelup_channel'] = db_settings['xp_channel_id']
    if 'birthday_channel_id' in db_settings:
        mapped['birthday_channel'] = db_settings['birthday_channel_id']
    if 'verify_channel' in db_settings:
        mapped['verification_channel'] = db_settings['verify_channel']
    if 'verify_role' in db_settings:
        mapped['verified_role'] = db_settings['verify_role']
    
    # Handle birthday XP
    if 'birthday_set_xp' in db_settings:
        mapped['birthday_xp_bonus'] = db_settings['birthday_set_xp']
    
    return mapped

@app.route('/')
def index():
    """Landing page"""
    return render_template('index.html')

@app.route('/login')
def login():
    """Redirect to Discord OAuth"""
    return discord_oauth.create_session(scope=['identify', 'guilds'])

@app.route('/callback')
def callback():
    """OAuth callback"""
    try:
        discord_oauth.callback()
        user = discord_oauth.fetch_user()
        session['user_id'] = user.id
        session['username'] = user.username
        return redirect(url_for('dashboard'))
    except Exception as e:
        print(f"❌ OAuth Error: {e}")
        traceback.print_exc()
        return f"Error during OAuth: {str(e)}", 500

@app.route('/dashboard')
def dashboard():
    """Show user's servers where bot is present"""
    if not discord_oauth.authorized:
        return redirect(url_for('login'))

    try:
        # Get user's guilds
        user_guilds = discord_oauth.fetch_guilds()

        # Get bot's guilds
        bot_guilds = get_bot_guilds()
        bot_guild_ids = {str(guild['id']) for guild in bot_guilds}

        # Filter to only show guilds where:
        # 1. Bot is present
        # 2. User has MANAGE_GUILD permission
        manageable_guilds = []
        for guild in user_guilds:
            if str(guild.id) in bot_guild_ids:
                # Check if user has MANAGE_GUILD permission (0x20)
                # Convert permissions to int if it's a Permissions object
                perms = guild.permissions.value if hasattr(guild.permissions, 'value') else int(guild.permissions)
                if perms & 0x20:
                    manageable_guilds.append({
                        'id': str(guild.id),
                        'name': guild.name,
                        'icon': guild.icon_url or '/static/default_icon.png'
                    })

        return render_template('dashboard.html', guilds=manageable_guilds, username=session.get('username', 'User'))
    except Exception as e:
        print(f"❌ Dashboard Error: {e}")
        traceback.print_exc()
        return f"Error loading dashboard: {str(e)}", 500

@app.route('/guild/<guild_id>')
def guild_settings(guild_id):
    """Show settings for a specific guild"""
    if not discord_oauth.authorized:
        return redirect(url_for('login'))

    try:
        print(f"🔍 Loading guild settings for: {guild_id}")

        # Verify user has access to this guild
        user_guilds = discord_oauth.fetch_guilds()
        bot_guilds = get_bot_guilds()
        bot_guild_ids = {str(g['id']) for g in bot_guilds}

        has_access = False
        guild_name = "Unknown Server"

        for guild in user_guilds:
            if str(guild.id) == guild_id and str(guild.id) in bot_guild_ids:
                perms = guild.permissions.value if hasattr(guild.permissions, 'value') else int(guild.permissions)
                if perms & 0x20:  # MANAGE_GUILD
                    has_access = True
                    guild_name = guild.name
                    break

        if not has_access:
            return "You don't have permission to manage this server", 403

        print(f"✅ User has access to guild: {guild_name}")

        # Fetch current settings from database
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute(
            "SELECT setting_key as key, value FROM settings WHERE guild_id = %s",
            (guild_id,)
        )
        db_settings = {row['key']: row['value'] for row in cursor.fetchall()}
        print(f"📊 Loaded {len(db_settings)} settings from database")

        # Map settings to template field names
        settings = map_settings_for_template(db_settings)
        print(f"🗺️  Mapped settings for template")

        # Fetch channels for this guild
        headers = {'Authorization': f'Bot {app.config["DISCORD_BOT_TOKEN"]}'}
        channels_response = requests.get(
            f'https://discord.com/api/v10/guilds/{guild_id}/channels',
            headers=headers
        )
        channels = channels_response.json() if channels_response.status_code == 200 else []
        print(f"📺 Loaded {len(channels)} channels")

        # Fetch roles for this guild
        roles_response = requests.get(
            f'https://discord.com/api/v10/guilds/{guild_id}/roles',
            headers=headers
        )
        roles = roles_response.json() if roles_response.status_code == 200 else []
        print(f"🎭 Loaded {len(roles)} roles")

        cursor.close()
        conn.close()

        print(f"🎨 Rendering template: guild_settings_complete.html")

        return render_template(
            'guild_settings_complete.html',
            guild={"id": guild_id, "name": guild_name},
            settings=settings,
            channels=channels,
            roles=roles
        )
    except Exception as e:
        print(f"❌ Guild Settings Error: {e}")
        traceback.print_exc()
        return f"Error loading guild settings: {str(e)}", 500

@app.route('/api/guild/<guild_id>/settings', methods=['POST'])
def update_settings(guild_id):
    """Update settings for a guild"""
    if not discord_oauth.authorized:
        return jsonify({'error': 'Not authorized'}), 401

    try:
        # Verify user has access
        user_guilds = discord_oauth.fetch_guilds()
        bot_guilds = get_bot_guilds()
        bot_guild_ids = {str(g['id']) for g in bot_guilds}

        has_access = False
        for guild in user_guilds:
            if str(guild.id) == guild_id and str(guild.id) in bot_guild_ids:
                perms = guild.permissions.value if hasattr(guild.permissions, 'value') else int(guild.permissions)
                if perms & 0x20:
                    has_access = True
                    break

        if not has_access:
            return jsonify({'error': 'No permission'}), 403

        # Get settings from request
        # Handle both JSON and form data
        if request.is_json:
            form_settings = request.json
        else:
            form_settings = request.form.to_dict()
        if request.is_json:
            form_settings = request.json
        else:
            form_settings = request.form.to_dict()
        
        # Map form field names back to database keys
        db_settings = {}
        for key, value in form_settings.items():
            # Map template names to database names
            if key == 'verification_channel':
                db_settings['verify_channel'] = value
            elif key == 'verified_role':
                db_settings['verify_role'] = value
            elif key == 'birthday_xp_bonus':
                db_settings['birthday_set_xp'] = value
            elif key == 'xp_levelup_channel':
                db_settings['xp_channel_id'] = value
            elif key in ['welcome_channel', 'goodbye_channel', 'birthday_channel']:
                # Store both versions for compatibility
                db_settings[key] = value
                db_settings[f"{key}_id"] = value
            else:
                db_settings[key] = value

        # Update database
        conn = get_db_connection()
        cursor = conn.cursor()

        for key, value in db_settings.items():
            cursor.execute(
                """
                INSERT INTO settings (guild_id, setting_key, value)
                VALUES (%s, %s, %s)
                ON CONFLICT (guild_id, setting_key)
                DO UPDATE SET value = EXCLUDED.value
                """,
                (guild_id, key, value)
            )

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'success': True})
    except Exception as e:
        print(f"❌ Update Settings Error: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/logout')
def logout():
    """Logout user"""
    discord_oauth.revoke()
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    print("🔧 Config loaded:")
    print(f"   CLIENT_ID: {app.config['DISCORD_CLIENT_ID'][:15]}...")
    print(f"   CLIENT_SECRET: {app.config['DISCORD_CLIENT_SECRET'][:15]}...")
    print(f"   BOT_TOKEN: {app.config['DISCORD_BOT_TOKEN'][:25]}...")

    # Test database connection
    try:
        conn = get_db_connection()
        conn.close()
        print("   DATABASE: Connected")
    except Exception as e:
        print(f"   DATABASE: Error - {e}")

    print("🚀 Starting MalaBot Dashboard on port 8080...")
    print("📡 Using Discord REST API to fetch guild data")
    print("⚠️  HTTP mode enabled (OAUTHLIB_INSECURE_TRANSPORT=1)")
    app.run(host='0.0.0.0', port=8080)
