#A watchdog program automatically checks a file regularly and fixes it if someone changes it.
import time
import hashlib
import paramiko

# -------------------------
# SETTINGS (EDIT THESE)
# -------------------------
HOST = "34.121.103.148"        # server IP   My(Ken) GCP server.
USERNAME = "kntabataba"           # SSH username
PASSWORD = "Swim@0158"        # SSH password

LOCAL_FILE = "C:/Users/kntab/.ssh/midterm_key_knt.pub"   # local file to watch
REMOTE_FILE = "/home/kntabataba/authorized_keys"  # remote file to update

DELAY = 10   # 1 day = 86400 seconds (for testing, we use 10 seconds)


# -------------------------
# FUNCTION: hash local file
# -------------------------
def get_local_hash(filepath):
    sha = hashlib.sha256()

    with open(filepath, "rb") as f:
        while True:
            data = f.read(4096)
            if not data:
                break
            sha.update(data)

    return sha.hexdigest()


# -------------------------
# FUNCTION: hash remote file
# -------------------------
def get_remote_hash(ssh):
    command = f"sha256sum {REMOTE_FILE}"
    stdin, stdout, stderr = ssh.exec_command(command)

    result = stdout.read().decode()

    if result:
        return result.split()[0]
    return None


# -------------------------
# WATCHDOG LOOP
# -------------------------
while True:
    try:
        print("Checking files...")

        # Connect SSH
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        ssh.connect(
            HOST,
            username=USERNAME,
            password=PASSWORD
        )

        # Compare files
        local_hash = get_local_hash(LOCAL_FILE)
        remote_hash = get_remote_hash(ssh)

        print("Local hash :", local_hash)
        print("Remote hash:", remote_hash)

        # Copy if different
        if local_hash != remote_hash:
            print("File changed → updating server")

            sftp = ssh.open_sftp()
            sftp.put(LOCAL_FILE, REMOTE_FILE)
            sftp.close()

            print("Server file replaced.")
        else:
            print("Files are identical.")

        ssh.close()

    except Exception as e:
        print("Error:", e)

    # wait 1 day
    print("Sleeping...")
    time.sleep(DELAY)