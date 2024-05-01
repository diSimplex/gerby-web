# Local testing of this Podman container

The (simple bash) scripts contained in this directory can be used to:

- `build` builds a test image

- `run`  starts a test container

- `enter` (re)enters an already running test container. This allows you to
          look at the container's files from the "inside"

- `cleanupContainer`  removes the test container

- `cleanupImage` removes the test image

All of these scripts *should* be run in the main directory of this
repository (the directory which contains the `Dockerfile`)

## Requirements

- (linux) Bash

- Podman (the rootless container system (like Docker but runs with the
  same privileges as the user))
