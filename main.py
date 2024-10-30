import subprocess
package_name = 'grype'
install_command = f'apk add {package_name}'
try:
    subprocess.run(install_command, shell=True, check=True)
    print(f"{package_name} has been successfully installed.")
except subprocess.CalledProcessError as e:
    print(f"Failed to install {package_name}: {e}")

with open('/mnt/reports/input.txt', 'r') as file:
    # Read each line in the file
    for line in file:
        # Print each line
        print(line.strip())