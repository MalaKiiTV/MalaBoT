with open('cogs/moderation.py', 'r') as f:
    lines = f.readlines()

# Fix the problematic lines around 689-694
for i, line in enumerate(lines):
    if i == 688:  # line 689 (0-indexed)
        lines[i] = '                   try:\n'
    elif i == 689:  # line 690
        lines[i] = '                       if user and hasattr(user, "send"):\n'
    elif i == 690:  # line 691
        lines[i] = '                           await user.send(\n'
    elif i == 691:  # line 692
        lines[i] = '                               f"You have been unmuted in {interaction.guild and interaction.guild and interaction.guild.name}"\n'
    elif i == 692:  # line 693
        lines[i] = '                           )\n'
    elif i == 693:  # line 694
        lines[i] = '                   except:\n'

with open('cogs/moderation.py', 'w') as f:
    f.writelines(lines)
