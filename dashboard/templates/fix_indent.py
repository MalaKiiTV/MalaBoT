with open('guild_settings_complete.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Delete the broken function (lines 762-776, which is index 761-775)
del lines[761:776]

# Insert the correctly formatted function
correct_function = """
                // Function to update original values
                function updateOriginalValues() {
                    originalValues.clear();
                    inputs.forEach(input => {
                        if (input.type === 'checkbox') {
                            originalValues.set(input.name, input.checked);
                        } else {
                            originalValues.set(input.name, input.value);
                        }
                    });
                }

                // Initialize original values
                updateOriginalValues();
"""

lines.insert(761, correct_function)

with open('guild_settings_complete.html', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("✅ Fixed indentation!")
