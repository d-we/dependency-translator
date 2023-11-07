#! /usr/bin/env python3

import argparse
import json
import os

VERBOSE = False

SCRIPT_PATH = os.path.dirname(__file__)
TRANSLATION_FNAME = SCRIPT_PATH + "/translations.json"

INSTALLATION_COMMANDS = {
    "archlinux": "pacman -S",
    "aur": "yay -S",
    "ubuntu": "apt install",
    "nix": "niv-env -i",
}

class Translation:
    name = ""
    aur = False
    repo = ""

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    VERBOSE = '\033[96m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def log_error(message):
    print(f"{bcolors.FAIL}[x] {message}{bcolors.ENDC}")

def log_warning(message):
    print(f"{bcolors.WARNING}[-] {message}{bcolors.ENDC}")

def log_success(message):
    print(f"{bcolors.OKGREEN}[+] {message}{bcolors.ENDC}")

def log_info(message):
    print(f"{bcolors.OKBLUE}[+] {message}{bcolors.ENDC}")

def log_debug(message):
    if VERBOSE:
        print(f"{bcolors.VERBOSE}[*] {message}{bcolors.ENDC}")


def parse_arguments() -> dict:
    parser = argparse.ArgumentParser()
    parser.add_argument(type=str,  # cast argument to this type
                        metavar="<ubuntu|archlinux|nix>", # the value used for help messages
                        dest="pkgtype-src",
                        action="store",  # just store the value
                        help="Type of packages, e.g., 'ubuntu' for an input originating from an ubuntu package list")
    parser.add_argument(type=str,  # cast argument to this type
                        metavar="<package-list>",  # the value used for help messages, e.g., "--number-prints <n>"
                        dest="pkglist",
                        action="store",  # just store the value
                        help="List of packages, e.g., make build-essentials libyaml-dev")
    parser.add_argument('-v', '--verbose',
                        dest="verbose",
                        action="store_true",  # just store that the value was set
                        help="Enable verbose messages",
                        required=False)
    return vars(parser.parse_args())


def build_translation_index(packagetype_src):
    log_debug(f"Building translation index from {TRANSLATION_FNAME}...")
    try:
        translations_json =  json.load(open(TRANSLATION_FNAME))
    except json.decoder.JSONDecodeError as e:
        log_error(f'Invalid JSON in "{TRANSLATION_FNAME}"!')
        log_error(e)
        return 1

    translation_index = dict()
    for entry in translations_json:
        key = entry[packagetype_src]["name"]
        translation_index[key] = entry
            
    log_debug(f"Translation index built.")
    return translation_index
    

def remove_duplicates(package_list):
    existing = list()
    new_package_list = list()
    for entry in package_list:
        if entry.name not in existing:
            new_package_list.append(entry)
            existing.append(entry.name)

    return new_package_list


def translate_package_list(package_list, packagetype_src, translation_index):
    translated_packages = dict()
    
    for package_src in package_list.split():
        log_debug(f"Translating {package_src}")

        if not package_src in translation_index:
            log_warning(f"No known translation for package '{package_src}'. Skipping.")
            continue
            
        translation_entry = translation_index[package_src]
        for distro in translation_entry:
            if distro == packagetype_src:
                # we do not need to translate to the original
                continue

            if distro not in translated_packages:
                translated_packages[distro] = list()
            
            translation = Translation()
            translation.name = translation_entry[distro]["name"]
            translation.repo = translation_entry[distro]["repo"]
            if distro == "archlinux":
                translation.aur = translation_entry["archlinux"]["AUR"]

            translated_packages[distro].append(translation)
            
    return translated_packages

        
def print_installation_commands(packagelists):
    for distro, packagelist in packagelists.items():
        cmd = INSTALLATION_COMMANDS[distro]
        packagelist = remove_duplicates(packagelist)

        if distro == "archlinux":
            cmd_aur = INSTALLATION_COMMANDS["aur"]

        aur_packages_required = False
        for translation in packagelist:
            if distro == "archlinux" and translation.aur:
                cmd_aur += " "
                cmd_aur += translation.name
                aur_packages_required = True
            else:
                cmd += " "
                cmd += translation.name

        print(f"====== Command for {distro.upper()} ======\n")
        print(f"{bcolors.OKBLUE} # {cmd}{bcolors.ENDC}")
        if distro == "archlinux" and aur_packages_required:
            print(f"{bcolors.OKBLUE} # {cmd_aur}{bcolors.ENDC}")
        print("")
            
    
def main():
    arg_dict = parse_arguments()

    if arg_dict["verbose"]:
        global VERBOSE
        VERBOSE = True

    packagetype_src = arg_dict["pkgtype-src"]
    package_list_src = arg_dict["pkglist"]
        
    translation_index = build_translation_index(packagetype_src)

    #print(json.dumps(translation_index, indent=2))
    resulting_packagelists = translate_package_list(package_list_src, 
                                                    packagetype_src, 
                                                    translation_index)

    print_installation_commands(resulting_packagelists)
    



if __name__ == "__main__":
    main()
