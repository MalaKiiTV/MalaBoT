def fix_setup_methods():
    """Fix indentation of setup methods to be inside Setup class."""
    with open('cogs/setup.py', 'r') as f:
        lines = f.readlines()
    
    # Find the start and end of each setup method and fix indentation
    in_setup_method = False
    method_start_patterns = [
        'async def setup_verification(',
        'async def setup_welcome(',
        'async def setup_birthday(',
        'async def setup_xp(',
        'async def setup_general(',
        'async def setup_role_connections(',
        'async def view_config('
    ]
    
    new_lines = []
    for line in lines:
        # Check if this line starts a setup method
        if any(pattern in line for pattern in method_start_patterns):
            # This should be indented as part of Setup class
            if line.strip().startswith('async def'):
                new_lines.append('    ' + line.lstrip())
                in_setup_method = True
            else:
                new_lines.append(line)
        elif in_setup_method:
            # We're inside a setup method, fix indentation
            if line.strip() == '':
                new_lines.append(line)
            elif line.strip().startswith('class ') or line.strip().startswith('async def setup(bot:'):
                # We've reached the end of setup methods
                new_lines.append(line)
                in_setup_method = False
            else:
                # Add proper indentation for method content
                current_indent = len(line) - len(line.lstrip())
                if current_indent == 0:
                    new_lines.append('        ' + line.lstrip())
                else:
                    # Adjust existing indentation
                    new_lines.append('    ' + line)
        else:
            new_lines.append(line)
    
    with open('cogs/setup.py', 'w') as f:
        f.writelines(new_lines)
    
    print("Fixed setup methods indentation")

if __name__ == "__main__":
    fix_setup_methods()