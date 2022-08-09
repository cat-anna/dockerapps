echo "
USER_UID=$(id -u git)
USER_GID=$(id -g git)
USER_HOME=$(getent passwd git | cut -d: -f6)
"
