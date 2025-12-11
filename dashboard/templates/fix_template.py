import re 
 
with open('guild_settings_complete.html', 'r', encoding='utf-8') as f: 
    content = f.read() 
 
# Find and replace the setTimeout block 
                                submitBtn.textContent = 'No Changes'; 
                                submitBtn.classList.remove('btn-success'); 
                                submitBtn.classList.add('btn-primary'); 
                                submitBtn.disabled = true; 
                                submitBtn.style.opacity = '0.5'; 
                                submitBtn.style.cursor = 'not-allowed'; 
 
                                // Update original values after save 
                                const inputs = form.querySelectorAll('input, select, textarea'); 
                                const originalValues = new Map(); 
                                inputs.forEach(input => { 
                                    if (input.type === 'checkbox') { 
                                        originalValues.set(input.name, input.checked); 
                                    } else { 
                                        originalValues.set(input.name, input.value); 
                                    } 
                                }); 
 
                                submitBtn.textContent = 'No Changes'; 
                                submitBtn.classList.remove('btn-success'); 
                                submitBtn.classList.add('btn-primary'); 
                                submitBtn.disabled = true; 
                                submitBtn.style.opacity = '0.5'; 
                                submitBtn.style.cursor = 'not-allowed'; 
 
content = content.replace(old_code, new_code) 
 
with open('guild_settings_complete.html', 'w', encoding='utf-8') as f: 
    f.write(content) 
 
print("Fixed!") 
