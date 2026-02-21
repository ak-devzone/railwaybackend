import os

file_path = r"d:\html\Digital Library SYSTEM\frontend\src\contexts\AuthContext.jsx"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

target = "try {\n            const response"
replacement = """try {
            // Sync user to Backend immediately
            try {
                const syncResponse = await fetch(`${API_URL}/users/sync/`, {
                    method: 'POST',
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                if (syncResponse.ok) console.log("User synced to MySQL");
            } catch (e) {
                console.error("Sync failed", e);
            }

            const response"""

if target in content:
    new_content = content.replace(target, replacement)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Successfully patched AuthContext.jsx")
else:
    print("Target not found in AuthContext.jsx")
    print("First 200 chars of try block context:")
    start_idx = content.find("try {")
    if start_idx != -1:
        print(content[start_idx:start_idx+200])
