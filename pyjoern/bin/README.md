# Joern Binaries
The Joern backend is not installed here. It lives outside the package, in `~/.pyjoern/joern-cli` by
default, because Joern's native frontends resolve their helper binaries relative to their own install
path and mis-resolve it under a directory named `lib` (which every `site-packages` path contains).
Set `$PYJOERN_JOERN_DIR` to install it somewhere else.
