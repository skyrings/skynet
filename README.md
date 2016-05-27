# skynet: Node eventing agent for skyring
skynet is the node eventing agent for Skyring. Each storage node managed by Skyring will have this agent running on them. It is a daemon which listens to dbus signals, filters it, processes it and pushes the filtered signals to Skyring using saltstack's eventing framework. Currently this daemon has capability to send basic storage related, few node process related events.

# Installation
This project has a installer script that you can run to install skynet on storage nodes. Just download the install_skynet.sh file and execute it by running './install_skyring.sh'. Alternatively run the below command to execute the installer script - curl -L https://github.com/skyrings/skynet/raw/master/misc/install_skynet.sh | bash -s

# Configuration
The events that has to be sent to SkyRing from a particular node is configurable. To configure the interested events you can use the config file /etc/skynet/skynet.conf.

# Documentation
Please visit the [WIKI](https://github.com/skyrings/skynet/wiki) for project documentation.

# Development
SkyNet development happens in [gerrithub.io](https://review.gerrithub.io/#/admin/projects/skyrings/skynet).  Please submit your patches to gerrithub than pull request.

# Licensing
SkyNet is licensed under the Apache License, Version 2.0.  See [LICENSE](https://github.com/skyrings/skynet/blob/master/LICENSE) for the full license text.

# Releasing
1. Check out the master branch, and pull the latest changes to be sure
   your local master branch is up to date.

```
git checkout master
git pull
```

2. Bump the version number in `src/skynetd/__init__.py` and commit your
   changes with the standard commit message.

```
python setup.py bump
```

3. Tag and push directly to the `origin` Git remote.

```
python setup.py release
```
