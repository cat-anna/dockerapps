
local path = require "pl.path"
local dir = require "pl.dir"
local tablex = require "pl.tablex"
local lfs = require "lfs"
local posix = require "posix"

local hostname = require("socket").dns.gethostname()

local cwd_stack = { }
local function pushd(path)
    table.insert(cwd_stack, lfs.currentdir())
    -- print("pushd", path)
    lfs.chdir(path)
end

local function popd()
    local path = table.remove(cwd_stack, #cwd_stack)
    -- print("popd", path)
    lfs.chdir(path)
end

local function exec(line)
    print("exec", line)
    os.execute(line)
end

local function RunService(action, service)
    pushd(lfs.currentdir() .. "/" .. service)
    if lfs.attributes("env.sh") ~= nil then
        exec("./env.sh > .env")
    end
    local actions = {
        up = "docker-compose up --build --detach",
        down = "docker-compose down --remove-orphans",
    }
    exec(actions[action])
    popd()
end

local function RunServices(action, list)
    print("Action", action, table.concat(list, ","))
    if action == "down" then
        for i = #list, 1, -1 do
            RunService(action, list[i])
        end
    else
        for _,v in ipairs(list) do
            RunService(action, v)
        end
    end
end

local Services = {
    shared = {
        -- "shared/network",
        -- "shared/whoami",
        -- "test/py",
    },
}

local srv_list = { }

tablex.icopy(srv_list, Services.shared, #srv_list+1)
tablex.icopy(srv_list, Services[hostname] or { }, #srv_list+1)

posix.setenv("HOSTNAME", hostname)

local Actions = {
    restart = function (action, list)
        RunServices("down", list)
        RunServices("up", list)
    end
}

local action = arg[1] or "up"
if Actions[action] then
    Actions[action](action, srv_list)
else
    RunServices(action, srv_list)
end