with open('bot.py', 'r') as f:
    lines = f.readlines()

# Fix the problematic section by finding and replacing it exactly
for i, line in enumerate(lines):
    if 'self.tree.copy_global_to(guild=guild)' in line:
        # Replace with proper indentation (27 spaces to match the surrounding context)
        lines[i] = '                           self.tree.copy_global_to(guild=guild)\n'
        break

# Also clean up any stray debug lines that are misaligned
for i, line in enumerate(lines):
    if '# Copy global commands to guild for debug mode' in line and i > 0:
        if not line.startswith('                           '):
            lines[i] = '                           # Copy global commands to guild for debug mode\n'

with open('bot.py', 'w') as f:
    f.writelines(lines)

print('Fixed final indentation issues')
