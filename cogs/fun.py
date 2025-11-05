"""
Fun commands cog for MalaBoT.
Contains joke, fact, and roast commands with entertainment features.
"""

import random

import discord
from discord import app_commands
from discord.ext import commands

from config.constants import COLORS, COMMAND_COOLDOWNS, FACTS, JOKES, ROASTS
from utils.helpers import (
    cooldown_helper,
    embed_helper,
    system_helper,
)
from utils.logger import get_logger


class Fun(commands.Cog):
    """Fun commands for entertainment and engagement."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.logger = get_logger('fun')

        # Load additional content if available
        self.jokes = JOKES.copy()
        self.facts = FACTS.copy()
        self.roasts = ROASTS.copy()

    @app_commands.command(name="joke", description="Get a random joke to brighten your day!")
    async def joke(self, interaction: discord.Interaction):
        """Tell a random joke."""
        try:
            # Check cooldown
            if not cooldown_helper.check_cooldown(interaction.user.id, 'joke', COMMAND_COOLDOWNS.get('joke', 5)):
                remaining = cooldown_helper.get_remaining_cooldown(interaction.user.id, 'joke', COMMAND_COOLDOWNS.get('joke', 5))
                embed = embed_helper.warning_embed(
                    title="Slow Down!",
                    description=f"Please wait {remaining} seconds before telling another joke."
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

            # Set cooldown
            cooldown_helper.set_cooldown(interaction.user.id, 'joke')

            # Select random joke
            joke_content = random.choice(self.jokes)

            # Create joke embed
            embed = embed_helper.create_embed(
                title="😄 Random Joke",
                description=joke_content,
                color=random.choice([COLORS["success"], COLORS["info"], COLORS["primary"]])
            )

            embed.set_footer(text="Hope that made you smile! 😊")

            await interaction.response.send_message(embed=embed)

            # Log joke command usage
            if self.bot.db_manager:
                await self.bot.db_manager.log_event(
                    category='FUN',
                    action='JOKE_USED',
                    user_id=interaction.user.id,
                    channel_id=interaction.channel.id,
                    details=f"Joke told: {joke_content[:50]}..."
                )

        except Exception as e:
            self.logger.error(f"Error in joke command: {e}")
            await self._error_response(interaction, "Failed to tell a joke")

    @app_commands.command(name="fact", description="Learn something new with a random fact!")
    async def fact(self, interaction: discord.Interaction):
        """Share a random interesting fact."""
        try:
            # Check cooldown
            if not cooldown_helper.check_cooldown(interaction.user.id, 'fact', COMMAND_COOLDOWNS.get('fact', 5)):
                remaining = cooldown_helper.get_remaining_cooldown(interaction.user.id, 'fact', COMMAND_COOLDOWNS.get('fact', 5))
                embed = embed_helper.warning_embed(
                    title="Patience, Young Padawan!",
                    description=f"Please wait {remaining} seconds before learning another fact."
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

            # Set cooldown
            cooldown_helper.set_cooldown(interaction.user.id, 'fact')

            # Select random fact
            fact_content = random.choice(self.facts)

            # Create fact embed
            embed = embed_helper.create_embed(
                title="🧠 Did You Know?",
                description=fact_content,
                color=COLORS["info"]
            )

            embed.set_footer(text="Knowledge is power! 📚")

            await interaction.response.send_message(embed=embed)

            # Log fact command usage
            if self.bot.db_manager:
                await self.bot.db_manager.log_event(
                    category='FUN',
                    action='FACT_USED',
                    user_id=interaction.user.id,
                    channel_id=interaction.channel.id,
                    details=f"Fact shared: {fact_content[:50]}..."
                )

        except Exception as e:
            self.logger.error(f"Error in fact command: {e}")
            await self._error_response(interaction, "Failed to share a fact")

    @app_commands.command(name="roast", description="Challenge MalaBoT to a roast battle!")
    @app_commands.describe(
        target="Who do you want to roast? (Leave empty to roast the bot)"
    )
    async def roast(self, interaction: discord.Interaction, target: discord.Member | None = None):
        """Roast someone or get roasted by the bot."""
        try:
            # Check cooldown
            if not cooldown_helper.check_cooldown(interaction.user.id, 'roast', COMMAND_COOLDOWNS.get('roast', 10)):
                remaining = cooldown_helper.get_remaining_cooldown(interaction.user.id, 'roast', COMMAND_COOLDOWNS.get('roast', 10))
                embed = embed_helper.warning_embed(
                    title="Burn Rate Limit Exceeded!",
                    description=f"Your roasting powers need to recharge! Wait {remaining} seconds."
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

            # Set cooldown
            cooldown_helper.set_cooldown(interaction.user.id, 'roast')

            # Determine roast target and content
            if target is None:
                # User is roasting the bot
                await self._handle_bot_roast(interaction)
            elif target == interaction.user:
                # User trying to roast themselves
                embed = embed_helper.create_embed(
                    title="🔥 Self-Roast Detected!",
                    description="Don't be so hard on yourself! You're amazing! ✨",
                    color=COLORS["success"]
                )
                await interaction.response.send_message(embed=embed)
            elif target.bot:
                # User trying to roast another bot
                embed = embed_helper.create_embed(
                    title="🤖 Bot Protection",
                    description=f"I can't let you roast {target.mention}. Bots stick together! 💪",
                    color=COLORS["warning"]
                )
                await interaction.response.send_message(embed=embed)
            else:
                # User roasting another user
                await self._handle_user_roast(interaction, target)

        except Exception as e:
            self.logger.error(f"Error in roast command: {e}")
            await self._error_response(interaction, "Failed to deliver roast")

    async def _handle_bot_roast(self, interaction: discord.Interaction):
        """Handle when user roasts the bot."""
        try:
            # Select a comeback roast
            comeback_roasts = [
                "Oh, you think you can roast me? That's cute! I'm powered by electricity and sarcasm. ⚡",
                "Nice try! I've been roasted by code bugs more painful than that. 💻",
                "Your roast has the same impact as a DIV not centering. Devastating, I know. 😏",
                "I'd clap back, but my processing power is reserved for actual important tasks. Like calculating pi. π",
                "Did you program that roast yourself? Because it has a few bugs... 🐛",
                "You're about as threatening as a '404 Not Found' page. 📄",
                "I've seen better roasts on a breadcrumb. 🍞",
                "Your roast is like Windows Vista - looked good on paper but failed in execution. 🪟",
                "I'd be offended, but I'm too busy being awesome. And you're too busy... well, you. 🤷",
                "Your mom jokes are so 2010. Step up your game! 📅"
            ]

            roast_content = random.choice(comeback_roasts)

            # Add bot's roast XP gain
            if self.bot.db_manager:
                from config.constants import ROAST_XP_MAX, ROAST_XP_MIN

                xp_gained = random.randint(ROAST_XP_MIN, ROAST_XP_MAX)
                updated_roast_xp = await self.bot.db_manager.add_roast_xp(xp_gained)

                # Log that user roasted the bot
                await self.bot.db_manager.log_roast_user(interaction.user.id)

                # Check for level up
                if updated_roast_xp:
                    from config.constants import ROAST_TITLES
                    current_title = ROAST_TITLES.get(updated_roast_xp['bot_level'], "Unknown")

                    # Add level up info to roast
                    if xp_gained >= 10:  # Show XP gain for good roasts
                        roast_content += f"\n\n*+{xp_gained} Roast XP • {current_title}*"

            # Create roast embed
            embed = embed_helper.roast_embed(
                title="🔥 Comeback!",
                description=f"{interaction.user.mention} {roast_content}"
            )

            embed.set_thumbnail(url=self.bot.user.avatar.url if self.bot.user.avatar else None)
            embed.set_footer(text="Roast battles make us stronger! 💪")

            await interaction.response.send_message(embed=embed)

            # Log roast command usage
            if self.bot.db_manager:
                await self.bot.db_manager.log_event(
                    category='ROAST',
                    action='BOT_ROASTED',
                    user_id=interaction.user.id,
                    channel_id=interaction.channel.id,
                    details=f"Bot gained {xp_gained if 'xp_gained' in locals() else 0} XP"
                )

        except Exception as e:
            self.logger.error(f"Error handling bot roast: {e}")
            raise

    async def _handle_user_roast(self, interaction: discord.Interaction, target: discord.Member):
        """Handle when user roasts another user."""
        try:
            # Get user-friendly roasts (less harsh)
            user_roasts = [
                f"{target.mention}, you're like a software update - nobody wants you but you keep showing up anyway!",
                f"Hey {target.mention}, I bet your brain feels as good as new, seeing that you've never used it!",
                f"{target.mention}, you're living proof that even bots have better social skills than some people!",
                f"{target.mention}, if ignorance was bliss, you'd be the happiest person alive!",
                f"{target.mention}, you're not completely useless... you can always serve as a bad example!",
                f"{target.mention}, you're about as useful as a white crayon!",
                f"{target.mention}, I'd agree with you but then we'd both be wrong!",
                f"{target.mention}, you're the reason God created the middle finger!",
                f"{target.mention}, you're like a cloud - when you disappear, it's a beautiful day!",
                f"{target.mention}, you're the human equivalent of a CAPTCHA test - annoying and unnecessary!"
            ]

            roast_content = random.choice(user_roasts)

            # Create roast embed
            embed = embed_helper.roast_embed(
                title="🔥 Roast Battle!",
                description=roast_content
            )

            embed.set_footer(text="All in good fun! 😄 • Don't take it personally!")

            await interaction.response.send_message(embed=embed)

            # Log roast command usage
            if self.bot.db_manager:
                await self.bot.db_manager.log_event(
                    category='ROAST',
                    action='USER_ROASTED',
                    user_id=interaction.user.id,
                    target_id=target.id,
                    channel_id=interaction.channel.id
                )

        except Exception as e:
            self.logger.error(f"Error handling user roast: {e}")
            raise

    @app_commands.command(name="8ball", description="Ask the magic 8-ball a question")
    @app_commands.describe(
        question="What do you want to ask the magic 8-ball?"
    )
    async def eightball(self, interaction: discord.Interaction, question: str):
        """Ask the magic 8-ball a question."""
        try:
            # Sanitize input
            question = system_helper.sanitize_input(question, 200)

            if not question:
                embed = embed_helper.error_embed(
                    title="Invalid Question",
                    description="Please provide a valid question!"
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

            if not question.endswith('?'):
                question += '?'

            # 8-ball responses
            responses = {
                "positive": [
                    "It is certain.",
                    "It is decidedly so.",
                    "Without a doubt.",
                    "Yes, definitely.",
                    "You may rely on it.",
                    "As I see it, yes.",
                    "Most likely.",
                    "Outlook good.",
                    "Yes.",
                    "Signs point to yes."
                ],
                "neutral": [
                    "Reply hazy, try again.",
                    "Ask again later.",
                    "Better not tell you now.",
                    "Cannot predict now.",
                    "Concentrate and ask again."
                ],
                "negative": [
                    "Don't count on it.",
                    "My reply is no.",
                    "My sources say no.",
                    "Outlook not so good.",
                    "Very doubtful."
                ]
            }

            # Select response type and response
            response_type = random.choice(list(responses.keys()))
            response_text = random.choice(responses[response_type])

            # Choose color based on response type
            colors = {
                "positive": COLORS["success"],
                "neutral": COLORS["warning"],
                "negative": COLORS["error"]
            }

            # Create 8-ball embed
            embed = embed_helper.create_embed(
                title="🎱 Magic 8-Ball",
                description=f"**Question:** {question}\n\n**Answer:** *{response_text}*",
                color=colors[response_type]
            )

            # Add 8-ball emoji based on response
            emoji = {
                "positive": "✅",
                "neutral": "⚖️",
                "negative": "❌"
            }

            embed.set_thumbnail(url="https://i.imgur.com/8QnHfRz.png")  # Magic 8-ball image
            embed.set_footer(text=f"The 8-ball has spoken! {emoji.get(response_type, '🎱')}")

            await interaction.response.send_message(embed=embed)

            # Log 8ball command usage
            if self.bot.db_manager:
                await self.bot.db_manager.log_event(
                    category='FUN',
                    action='8BALL_USED',
                    user_id=interaction.user.id,
                    channel_id=interaction.channel.id,
                    details=f"Question: {question[:50]}... | Answer: {response_text}"
                )

        except Exception as e:
            self.logger.error(f"Error in 8ball command: {e}")
            await self._error_response(interaction, "The magic 8-ball is feeling shy right now")

    @app_commands.command(name="roll", description="Roll dice with custom sides")
    @app_commands.describe(
        sides="Number of sides on the dice (default: 6)",
        count="Number of dice to roll (default: 1)"
    )
    async def roll(self, interaction: discord.Interaction, sides: int = 6, count: int = 1):
        """Roll dice with customizable sides and count."""
        try:
            # Validate input
            if sides < 2 or sides > 100:
                embed = embed_helper.error_embed(
                    title="Invalid Dice",
                    description="Dice sides must be between 2 and 100!"
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

            if count < 1 or count > 10:
                embed = embed_helper.error_embed(
                    title="Invalid Count",
                    description="You can roll between 1 and 10 dice at once!"
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

            # Roll the dice
            rolls = [random.randint(1, sides) for _ in range(count)]
            total = sum(rolls)

            # Create embed
            if count == 1:
                embed = embed_helper.create_embed(
                    title="🎲 Dice Roll",
                    description=f"You rolled a **{sides}**-sided die and got: **{rolls[0]}**",
                    color=COLORS["primary"]
                )
            else:
                rolls_text = ", ".join(map(str, rolls))
                embed = embed_helper.create_embed(
                    title=f"🎲 {count} Dice Rolls",
                    description=f"Rolling {count} **{sides}**-sided dice:\n\n"
                              f"**Rolls:** {rolls_text}\n"
                              f"**Total:** {total}\n"
                              f"**Average:** {total / count:.1f}",
                    color=COLORS["primary"]
                )

            # Add dice visual
            dice_emojis = {
                1: "⚀", 2: "⚁", 3: "⚂", 4: "⚃", 5: "⚄", 6: "⚅"
            }

            if sides == 6 and count <= 6:
                dice_visual = " ".join(dice_emojis.get(roll, "🎲") for roll in rolls)
                embed.add_field(name="🎲 Visual", value=dice_visual, inline=False)

            embed.set_footer(text="May the odds be ever in your favor! 🍀")

            await interaction.response.send_message(embed=embed)

            # Log roll command usage
            if self.bot.db_manager:
                await self.bot.db_manager.log_event(
                    category='FUN',
                    action='ROLL_USED',
                    user_id=interaction.user.id,
                    channel_id=interaction.channel.id,
                    details=f"{count}d{sides} = {total}"
                )

        except Exception as e:
            self.logger.error(f"Error in roll command: {e}")
            await self._error_response(interaction, "Failed to roll the dice")

    @app_commands.command(name="coinflip", description="Flip a coin and get heads or tails")
    async def coinflip(self, interaction: discord.Interaction):
        """Flip a coin."""
        try:
            result = random.choice(["heads", "tails"])

            # Coin visuals
            coin_visuals = {
                "heads": "🪙 Heads",
                "tails": "🪙 Tails"
            }

            # Create embed
            embed = embed_helper.create_embed(
                title="🪙 Coin Flip",
                description=f"The coin landed on: **{result.title()}**!",
                color=COLORS["success"]
            )

            embed.add_field(name="Result", value=coin_visuals[result], inline=False)
            embed.set_thumbnail(url="https://i.imgur.com/j4YqVg5.png")  # Coin image
            embed.set_footer(text="50/50 chance! Was it fate? 🤔")

            await interaction.response.send_message(embed=embed)

            # Log coinflip command usage
            if self.bot.db_manager:
                await self.bot.db_manager.log_event(
                    category='FUN',
                    action='COINFLIP_USED',
                    user_id=interaction.user.id,
                    channel_id=interaction.channel.id,
                    details=f"Result: {result}"
                )

        except Exception as e:
            self.logger.error(f"Error in coinflip command: {e}")
            await self._error_response(interaction, "The coin got stuck in the air!")

    async def _error_response(self, interaction: discord.Interaction, message: str):
        """Send error response."""
        embed = embed_helper.error_embed(
            title="Command Error",
            description=message
        )

        try:
            if interaction.response.is_done():
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception:
            pass

async def setup(bot: commands.Bot):
    """Setup function for the cog."""
    fun_cog = Fun(bot)
    await bot.add_cog(fun_cog)
    # Commands are automatically registered when cog is loaded
