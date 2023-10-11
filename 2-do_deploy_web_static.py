#!/usr/bin/python3
from fabric.api import env, run
from fabric.operations import put
from datetime import datetime
import os

env.hosts = ['54.237.14.8', '100.26.232.63']
env.user = 'ubuntu'
env.key_filename = '~/.ssh/id_rsa'

def do_pack():
    """Create a compressed archive of the web_static folder."""
    try:
        current_time = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        archive_path = f"versions/web_static_{current_time}.tgz"
        local("mkdir -p versions")
        local("tar -czvf {} web_static".format(archive_path))
        return archive_path
    except:
        return None

def do_deploy(archive_path):
    """Distribute an archive to the web servers."""
    if not os.path.exists(archive_path):
        return False

    try:
        # Upload the archive
        put(archive_path, "/tmp/")
        file_name = os.path.basename(archive_path)
        file_name_without_extension = file_name.split('.')[0]
        remote_path = "/data/web_static/releases/{}/".format(file_name_without_extension)

        # Create necessary directories
        run("sudo mkdir -p {}".format(remote_path))

        # Unpack the archive
        run("sudo tar -xzf /tmp/{} -C {}".format(file_name, remote_path))

        # Delete the uploaded archive
        run("sudo rm /tmp/{}".format(file_name))

        # Move contents to the appropriate location
        run("sudo mv {}web_static/* {}".format(remote_path, remote_path))

        # Remove the symbolic link if it exists
        run("sudo rm -rf /data/web_static/current")

        # Create a new symbolic link
        run("sudo ln -s {} /data/web_static/current".format(remote_path))

        return True
    except:
        return False

def deploy():
    archive_path = do_pack()
    if archive_path is None:
        return False
    return do_deploy(archive_path)

if __name__ == "__main__":
    deploy()

