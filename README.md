# Dependency Translator
Translates a list of packages into a list of another packages from a different Linux distro. This is targeted especially to translate list of dependencies.


## Example 
```bash
$ ./dependency_translator.py ubuntu "libyaml-dev make libssl-dev libcapstone-dev"
====== Command for ARCHLINUX ======

 # pacman -S libyaml make openssl capstone
```



## Future Ideas
- [ ] Allow arbitrary delimiters.
- [ ] Show installation commands based on installed programs, e.g., `yay` only if `yay` is installed on the system.
