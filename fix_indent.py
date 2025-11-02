with open('bot.py', 'r') as f:
    lines = f.readlines()

# Find the problematic line and fix indentation
for i, line in enumerate(lines):
    if 'self.tree.copy_global_to(guild=guild)' in line:
        # Fix this line to have proper indentation (27 spaces to match surrounding code)
        lines[i] = '                           self.tree.copy_global_to(guild=guild)\n'
        break

with open('bot.py', 'w') as f:
    f.writelines(lines)

print('Fixed indentation')
