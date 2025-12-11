from quart import Blueprint, render_template, session, redirect, url_for, request, jsonify
import aiohttp
import os

dashboard_bp = Blueprint('dashboard', __name__)

DISCORD_API_BASE = "https://discord.com/api/v10"
CLIENT_ID = os.getenv('DISCORD_CLIENT_ID')
CLIENT_SECRET = os.getenv('DISCORD_CLIENT_SECRET')
REDIRECT_URI = os.getenv('DISCORD_REDIRECT_URI', 'http://165.232.156.230:8080/callback')

# Bot will be set by app.py after initialization
bot = None

@dashboard_bp.route('/')
async def index():
    """Landing page"""
    return await render_template('index.html')

@dashboard_bp.route('/login')
async def login():
    """Redirect to Discord OAuth"""
    oauth_url = (
        f"https://discord.com/api/oauth2/authorize"
        f"?client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&response_type=code"
        f"&scope=identify%20guilds"
    )
    return redirect(oauth_url)

@dashboard_bp.route('/callback')
async def callback():
    """Handle OAuth callback"""
    code = request.args.get('code')
    if not code:
        return "No code provided", 400

    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI
    }

    async with aiohttp.ClientSession() as http_session:
        async with http_session.post(f'{DISCORD_API_BASE}/oauth2/token', data=data) as resp:
            if resp.status != 200:
                return "Failed to get token", 400
            token_data = await resp.json()

        access_token = token_data['access_token']

        headers = {'Authorization': f'Bearer {access_token}'}
        async with http_session.get(f'{DISCORD_API_BASE}/users/@me', headers=headers) as resp:
            user_data = await resp.json()

        async with http_session.get(f'{DISCORD_API_BASE}/users/@me/guilds', headers=headers) as resp:
            guilds_data = await resp.json()

    session['user'] = user_data
    session['access_token'] = access_token
    session['guilds'] = guilds_data

    return redirect(url_for('dashboard.dashboard_home'))

@dashboard_bp.route('/dashboard')
async def dashboard_home():
    """Main dashboard"""
    if 'user' not in session:
        return redirect(url_for('dashboard.login'))

    user = session['user']
    guilds = session.get('guilds', [])
    manageable_guilds = [g for g in guilds if int(g.get('permissions', 0)) & 0x20]

    return await render_template('dashboard.html', user=user, guilds=manageable_guilds)

@dashboard_bp.route('/dashboard/<int:guild_id>')
async def guild_settings(guild_id):
    """Guild settings page"""
    if 'user' not in session:
        return redirect(url_for('dashboard.login'))

    guilds = session.get('guilds', [])
    guild = next((g for g in guilds if int(g['id']) == guild_id), None)

    if not guild or not (int(guild.get('permissions', 0)) & 0x20):
        return "Access denied", 403

    settings = {}
    if bot and bot.db:
        async with bot.db.execute(
            'SELECT setting_key, setting_value FROM guild_settings WHERE guild_id = ?',
            (guild_id,)
        ) as cursor:
            rows = await cursor.fetchall()
            settings = {row[0]: row[1] for row in rows}

    return await render_template(
        'guild_settings_complete.html',
        guild=guild,
        guild_id=guild_id,
        settings=settings
    )

@dashboard_bp.route('/api/guild/<int:guild_id>/data')
async def get_guild_data(guild_id):
    """Get guild channels and roles"""
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    if not bot:
        return jsonify({'error': 'Bot not ready'}), 503

    guild = bot.get_guild(guild_id)
    if not guild:
        return jsonify({'error': 'Guild not found'}), 404

    channels = [{'id': str(c.id), 'name': c.name, 'type': c.type.value} for c in guild.channels]
    roles = [{'id': str(r.id), 'name': r.name, 'color': r.color.value} for r in guild.roles]

    return jsonify({'channels': channels, 'roles': roles})

@dashboard_bp.route('/api/guild/<int:guild_id>/settings/<setting_type>', methods=['POST'])
async def update_settings(guild_id, setting_type):
    """Update guild settings"""
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    if not bot or not bot.db:
        return jsonify({'error': 'Bot not ready'}), 503

    data = await request.get_json()

    for key, value in data.items():
        await bot.db.execute(
            '''INSERT INTO guild_settings (guild_id, setting_key, setting_value)
               VALUES (?, ?, ?)
               ON CONFLICT(guild_id, setting_key)
               DO UPDATE SET setting_value = excluded.setting_value''',
            (guild_id, key, str(value))
        )

    await bot.db.commit()

    return jsonify({'success': True})

@dashboard_bp.route('/logout')
async def logout():
    """Logout user"""
    session.clear()
    return redirect(url_for('dashboard.index'))
