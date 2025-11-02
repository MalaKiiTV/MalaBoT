            CREATE TABLE IF NOT EXISTS appeals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                guild_id INTEGER NOT NULL,
                appeal_text TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reviewed_by INTEGER DEFAULT NULL,
                reviewed_at TIMESTAMP DEFAULT NULL,
                review_notes TEXT DEFAULT NULL
            )
            
            CREATE TABLE IF NOT EXISTS level_roles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER NOT NULL,
                level INTEGER NOT NULL,
                role_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(guild_id, level)
            )
        """)
        
        await conn.commit()
        
        # Initialize roast_xp if not exists
        await self._initialize_roast_xp()
