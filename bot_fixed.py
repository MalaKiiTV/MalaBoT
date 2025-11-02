import sys
with open('bot.py', 'r') as f:
    content = f.read()

# Remove the problematic copy_global_to line completely
content = content.replace('                           self.tree.copy_global_to(guild=guild)', '')

with open('bot.py', 'w') as f:
    f.write(content)

print('Removed problematic line')
