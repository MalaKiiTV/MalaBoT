def fix_indentation():
    """Fix indentation of moved setup methods."""
    with open('cogs/setup.py', 'r') as f:
        lines = f.readlines()
    
    new_lines = []
    in_setup_class = False
    in_setup_method = False
    
    for line in lines:
        if 'class Setup(commands.Cog):' in line:
            in_setup_class = True
            new_lines.append(line)
        elif in_setup_class and 'async def setup(' in line and 'bot: commands.Bot' in line:
            # End of Setup class
            in_setup_class = False
            new_lines.append(line)
        elif in_setup_class and line.strip().startswith('async def setup_'):
            # Start of a setup method - needs 4 spaces indentation
            new_lines.append('    ' + line.lstrip())
            in_setup_method = True
        elif in_setup_class and in_setup_method:
            # Content of setup method - needs 8 spaces indentation
            if line.strip() == '':
                new_lines.append(line)
            else:
                new_lines.append('        ' + line.lstrip())
        elif in_setup_class and line.strip().startswith('def ') and not line.strip().startswith('async def setup_'):
            # Other methods in Setup class
            new_lines.append('    ' + line.lstrip())
            in_setup_method = False
        else:
            new_lines.append(line)
    
    with open('cogs/setup.py', 'w') as f:
        f.writelines(new_lines)
    
    print("Fixed indentation")

if __name__ == "__main__":
    fix_indentation()