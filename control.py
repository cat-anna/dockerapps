#!/usr/bin/env -S python3 -u

# import yaml
import sys
import os
import subprocess
import re
import grp
import pwd

def stripComments(line):
    r = re.sub(r"#.+$", "", str(line)).strip()
    return r


def anydup(thelist):
    seen = set()
    for x in thelist:
        if x in seen:
            return True
        seen.add(x)
    return False


def exec_docker(args, cwd):
    subprocess.check_call(args=["docker"] + args, cwd=cwd)


def exec_docker_compose(args, cwd):
    env_script = os.path.join(cwd, "env.sh")
    env_file = os.path.join(cwd, ".env")
    env_generated = False
    try:
        if os.path.isfile(env_script):
            env_generated = True
            with open(env_file, "w") as outfile:
                subprocess.check_call(args=["/usr/bin/bash", "-c", env_script], cwd=cwd, stdout=outfile)

        subprocess.check_call(args=["docker-compose"] + args, cwd=cwd)
    finally:
        if env_generated:
            os.remove(env_file)


def get_app_dir(opts, app):
    return app["compose_dir"]


def action_template_forward(opts, action, apps, args):
    for app in apps:
        root = get_app_dir(opts=opts, app=app)
        exec_docker_compose(args=args, cwd=root)


def action_template_reverse(opts, action, apps, args):
    return action_template_forward(opts, action, apps[::-1], args)


def action_build(opts, action, apps):
    for app in apps:
        root = get_app_dir(opts=opts, app=app)
        exec_docker_compose(args=["pull"], cwd=root)
        exec_docker_compose(args=["build", "--no-cache"], cwd=root)


ACTIONS = {
    "build": action_build,
    "recreate": ["build", "up"],
    "restart": ["stop", "start"],  # needed to maitain order of containers
    "up": lambda a, b, c: action_template_forward(a, b, c, ["up", "-d"]),
    "down": lambda a, b, c: action_template_forward(a, b, c, ["down"]),
    "stop": lambda a, b, c: action_template_reverse(a, b, c, ["stop"]),
    "start": lambda a, b, c: action_template_forward(a, b, c, ["start"]),
}


def get_action_list(action):
    l = []
    if type(action) == str:
        a = ACTIONS.get(action)
        if not a:
            print(f"Unknown action '{action}' - TODO")
            return None

        if type(a) == list:
            for item in a:
                l.extend(get_action_list(item))
        elif type(a) == str:
            l.extend(get_action_list(a))
        else:
            l.append((action, a))

    return l


def process_app_list(opts, lst):
    apps = []
    for item in lst:
        apps.extend(process_app_arg(opts, item))
    return apps


def process_app_arg(opts, value):
    if os.path.isfile(value):
        filename, file_extension = os.path.splitext(value)
        if file_extension == ".yaml":
            print(f"Yaml list type is not yet supported: {value} - TODO")
            return []
        elif file_extension == ".txt":
            with open(value) as f:
                # remove comments
                l = [stripComments(x) for x in f.read().splitlines()]
                # remove too short
                l = [x for x in l if len(x) >= 3]
                return process_app_list(opts, l)
        else:
            print(f"Unkown app list type: {value} - TODO")
            return []

    search_paths = [
        os.path.join(opts["startup_dir"], "apps", value),
        os.path.join(opts["startup_dir"], value),
        os.path.join(opts["script_dir"], "apps", value),
    ]

    for option in search_paths:
        compose_files = [
            os.path.join(option, "docker-compose.yaml"),
            os.path.join(option, "docker-compose.yml"),
        ]

        for compose_file in compose_files:
            if os.path.isfile(compose_file):
                return [{"compose_dir": option}]

    print(f"Failed to find app {value} - TODO")
    return None


def setup_env_variables():
    if "HOSTNAME" not in os.environ:
        os.environ["HOSTNAME"] = os.uname()[1]
    if "DOCKER_GID" not in os.environ:
        os.environ["DOCKER_GID"] = f"{grp.getgrnam('docker').gr_gid}"


def main(argv):
    if len(argv) < 3:
        print("USAGE: APP [APP...] action")
        return 1

    opts = {
        "script_dir": os.path.dirname(os.path.realpath(__file__)),
        "startup_dir": os.path.abspath(os.curdir),
    }

    app_list = process_app_list(opts, argv[1:-1])

    if anydup(x["compose_dir"] for x in app_list):
        print("Resolved app list has duplicates. Refusing to process.")
        return 1

    action_list = get_action_list(action=argv[-1])

    setup_env_variables()

    for i in range(len(action_list)):
        name, func = action_list[i]
        print(f"Invoking action {i+1}/{len(action_list)}: {name}")
        func(opts, name, app_list)

    print("Completed")
    return 0


sys.exit(main(sys.argv))
