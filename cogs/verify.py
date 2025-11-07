# --- SNIP --- (other code unchanged, starting at PlatformSelect)

class PlatformSelect(Select):
    def __init__(
        self,
        activision_id: str,
        screenshot_url: str,
        user_id: int,
        screenshot_bytes=None,
        screenshot_filename=None,
    ):
        super().__init__(
            placeholder="Select your gaming platform...",
            min_values=1,
            max_values=1,
            options=PLATFORM_OPTIONS,
        )
        self.activision_id = activision_id
        self.screenshot_url = screenshot_url
        self.user_id = user_id
        self.screenshot_bytes = screenshot_bytes
        self.screenshot_filename = screenshot_filename

    async def callback(self, interaction: discord.Interaction):
        platform = self.values[0]

        try:
            bot = interaction.client
            db = bot.db_manager
            conn = await db.get_connection()

            # Verify database schema first
            cursor = await conn.execute('PRAGMA table_info(verifications)')
            columns = await cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            if 'discord_id' not in column_names:
                log_system('ERROR: discord_id column missing from verifications table!', level='error')
                await interaction.response.send_message(
                    embed=create_embed(
                        'Database Error',
                        'The verification system is not properly configured. Please contact an administrator.',
                        COLORS['error'],
                    ),
                    ephemeral=True,
                )
                return
            
            await conn.execute(
                "INSERT INTO verifications (discord_id, activision_id, platform, screenshot_url) VALUES (?, ?, ?, ?)",
                (self.user_id, self.activision_id, platform, self.screenshot_url),
            )
            await conn.commit()

            # Delete the platform selection message to clean up the channel
            try:
                await interaction.message.delete()
            except:
                pass

            # Send a brief public confirmation that auto-deletes
            confirmation_msg = await interaction.channel.send(
                embed=create_embed(
                    "✅ Verification Submitted",
                    f"<@{self.user_id}>'s verification has been submitted for review!",
                    COLORS["success"],
                )
            )

            # Also send ephemeral confirmation to user
            await interaction.response.send_message(
                embed=create_embed(
                    "Verification Submitted ✅",
                    "Your verification has been sent for mod review. You'll be notified once it's approved or rejected.",
                    COLORS["success"],
                ),
                ephemeral=True,
            )

            # Delete the confirmation message after 5 seconds
            import asyncio
            await asyncio.sleep(5)
            try:
                await confirmation_msg.delete()
            except:
                pass

            log_system(
                f"[VERIFY] User {self.user_id} submitted verification for {self.activision_id} on {platform}"
            )

            guild_id = interaction.guild.id if interaction.guild else None
            review_channel_id = await db.get_setting("verify_channel", guild_id)
            review_channel = (
                bot.get_channel(int(review_channel_id)) if review_channel_id else None
            )

            if review_channel:
                # Debug logging
                log_system(
                    f"[VERIFY_DEBUG] Has screenshot bytes: {self.screenshot_bytes is not None}"
                )

                embed = discord.Embed(
                    title="📸 New Verification Submission",
                    description=(
                        f"**User:** <@{self.user_id}>\n"
                        f"**Activision ID:** `{self.activision_id}`\n"
                        f"**Platform:** `{platform}`\n"
                        f"**Submitted:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    ),
                    color=COLORS["info"],
                )

                embed.set_footer(text=f"User ID: {self.user_id}")

                # Send with screenshot file attachment if available
                if self.screenshot_bytes and self.screenshot_filename:
                    import io

                    file = discord.File(
                        io.BytesIO(self.screenshot_bytes),
                        filename=self.screenshot_filename,
                    )
                    embed.set_image(url=f"attachment://{self.screenshot_filename}")
                    await review_channel.send(embed=embed, file=file)
                else:
                    log_system(
                        f"[VERIFY_WARNING] No screenshot data for user {self.user_id}",
                        level="warning",
                    )
                    await review_channel.send(embed=embed)

            await db.log_event(
                category="VERIFY",
                action="SUBMIT",
                user_id=self.user_id,
                details=f"{self.activision_id} ({platform})",
            )

            # Clean up pending verification
            if self.user_id in bot.pending_verifications:
                del bot.pending_verifications[self.user_id]

        except Exception as e:
            log_system(f"Platform selection callback error: {e}", level="error")
            await interaction.response.send_message(
                embed=create_embed(
                    "Error",
                    "Something went wrong processing your selection. Please try again.",
                    COLORS["error"],
                ),
                ephemeral=True,
            )

# --- END OF CORRECTION ---

# Everything else unchanged.