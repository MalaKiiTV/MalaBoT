with open('src/cogs/setup.py', 'r', encoding='utf-8') as f: 
    lines = f.readlines() 
 
output = [] 
i = 0 
while i < len(lines): 
    line = lines[i] 
    output.append(line) 
    if 'if protected:' in line and i+1 < len(lines) and 'role_list = []' in lines[i+1]: 
        output.append(lines[i+1]) 
        output.append('            deleted_roles = []\n') 
        i += 2 
        while i < len(lines) and 'embed.add_field' not in lines[i]: 
            if 'if role:' in lines[i]: 
                output.append(lines[i]) 
                i += 1 
                output.append(lines[i]) 
                output.append('                else:\n') 
                output.append('                    deleted_roles.append(role_id)\n') 
                output.append('            \n') 
                output.append('            # Clean up deleted roles\n') 
                output.append('            if deleted_roles:\n') 
                output.append('                for role_id in deleted_roles:\n') 
                output.append('                    protected.remove(role_id)\n') 
                output.append('                self.manager.protected_roles_cache[self.guild.id] = protected\n') 
                output.append('                await self.manager.save_protected_roles(self.guild.id)\n') 
                i += 1 
                break 
            else: 
                output.append(lines[i]) 
                i += 1 
        continue 
    i += 1 
 
with open('src/cogs/setup.py', 'w', encoding='utf-8') as f: 
    f.writelines(output) 
 
print("Fixed!") 
