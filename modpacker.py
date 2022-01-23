import os
from typing import List, Set
from zipfile import ZipFile
import sys
from shutil import copy
import json


class ModProject(object):
    def __init__(self, root: str):
        self.root_dir = root
        self.plugin_dir = os.path.join(root, "plugin")
        self.patcher_dir = os.path.join(root, "patcher")
        self.meta_dir = os.path.join(root, "meta")
        self.release_dir = os.path.join(root, "release")
        self.manifest_file = os.path.join(self.meta_dir, "manifest.json")
        if not os.path.isfile(self.manifest_file):
            self.manifest_file = os.path.join(self.root_dir, "manifest.json")
        self.readme_file = os.path.join(self.meta_dir, "README.md")
        if not os.path.isfile(self.readme_file):
            self.readme_file = os.path.join(self.root_dir, "README.md")
        self.icon_file = os.path.join(self.meta_dir, "icon.png")
        if not os.path.isfile(self.icon_file):
            self.icon_file = os.path.join(self.root_dir, "icon.png")
        self.manifest = None

    def load_manifest(self):
        with open(self.manifest_file) as mf:
            self.manifest = json.load(mf)

    def has_plugin(self) -> bool:
        return os.path.isdir(self.plugin_dir)

    def has_patcher(self) -> bool:
        return os.path.isdir(self.patcher_dir)

    def _get_project_name(self, base_dir) -> str:
        proj_files = [file for file in os.listdir(base_dir) if file.endswith('.csproj')]
        if len(proj_files) == 0:
            sys.exit("No csproj file in '{}'".format(base_dir))
        if len(proj_files) > 1:
            sys.exit("Multiple csproj files in '{}'".format(base_dir))
        return os.path.splitext(proj_files[0])[0]

    def _get_artifacts(self, base_dir, artifact_type) -> Set[str]:
        if not os.path.isdir(base_dir):
            return set()
        bin_dir = os.path.join(base_dir, "bin")
        artifacts = {os.path.join(bin_dir, self._get_project_name(base_dir) + ".dll")}
        if "artifacts" in self.manifest and artifact_type in self.manifest["artifacts"]:
            for artifact in self.manifest["artifacts"][artifact_type]:
                artifacts.add(os.path.join(bin_dir, artifact))
        return artifacts

    def get_plugin_artifacts(self) -> Set[str]:
        return self._get_artifacts(self.plugin_dir, "plugin")

    def get_patcher_artifacts(self) -> Set[str]:
        return self._get_artifacts(self.patcher_dir, "patcher")

    def get_name(self) -> str:
        return self.manifest["name"]

    def get_author(self) -> str:
        return self.manifest["author"]

    def get_version_number(self) -> str:
        return self.manifest["version_number"]

    def get_website_url(self) -> str:
        return self.manifest["website_url"]

    def get_description(self) -> str:
        return self.manifest["description"]

    def get_dependencies(self) -> List[str]:
        return self.manifest["dependencies"]

    def is_valid(self):
        return os.path.isdir(self.root_dir) \
               and (os.path.isdir(self.plugin_dir) or os.path.isdir(self.patcher_dir)) \
               and os.path.isfile(self.manifest_file)


def find_mod_project() -> ModProject:
    mod_root = os.getcwd()
    mod_project = ModProject(mod_root)
    while not mod_project.is_valid():
        mod_root = os.path.dirname(mod_root)
        if mod_project.root_dir == mod_root:
            break
        mod_project = ModProject(mod_root)
    return mod_project


def find_bepinex_dir():
    profiles_dir = os.path.expandvars(r'%APPDATA%\r2modmanPlus-local\Outward\profiles')  # Only r2modmanPlus is supported (for now)
    if not os.path.isdir(profiles_dir):
        profiles_dir = os.path.expandvars(r'%LOCALAPPDATA%\r2modmanPlus-local\Outward\profiles')
    if not os.path.isdir(profiles_dir):
        return None
    profile_dir = os.path.join(profiles_dir, "Default")  # Only Default profile is supported (for now)
    if not os.path.isdir(profile_dir):
        return None
    return os.path.join(profile_dir, "BepInEx")


def copy_artifacts(artifacts, target_dir, artifact_type):
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    print("Copying {0} to: {1}".format(artifact_type, target_dir))
    for artifact in artifacts:
        print("Copying file {0}".format(artifact))
        copy(artifact, target_dir)


mod = find_mod_project()
if not mod.is_valid():
    sys.exit("ERROR: Failed to find a mod project at '{}' or any of its parent folders".format(os.getcwd()))

mod.load_manifest()

actions = sys.argv[1:] if len(sys.argv) > 1 else ["local", "thunderstore"]
print("Executing actions: {0}".format(", ".join(actions)))

if "local" in actions:
    print("Copying the mod to BepInEx folder")
    bepinex_dir = find_bepinex_dir()
    if bepinex_dir is None:
        sys.exit("ERROR: Failed to find the BepInEx folder")
    plugins_dir = os.path.join(bepinex_dir, "plugins")
    patchers_dir = os.path.join(bepinex_dir, "patchers")
    if mod.has_plugin():
        plugin_dir = os.path.join(plugins_dir, mod.get_author()+"-"+mod.get_name())
        copy_artifacts(mod.get_plugin_artifacts(), plugin_dir, "plugin")
    if mod.has_patcher():
        patcher_dir = os.path.join(patchers_dir, mod.get_author()+"-"+mod.get_name())
        copy_artifacts(mod.get_patcher_artifacts(), patcher_dir, "patcher")
    print("Finished copying the mod to BepInEx folder")

if "thunderstore" in actions:
    package_dir = os.path.join(mod.release_dir, "Thunderstore")
    if not os.path.isdir(package_dir):
        os.makedirs(package_dir)
    package_file = os.path.join(package_dir, mod.get_name()+".zip")
    if os.path.exists(package_file):
        os.remove(package_file)
    thunderstore_manifest = {"name": mod.get_name(),
                             "version_number": mod.get_version_number(),
                             "website_url": mod.get_website_url(),
                             "description": mod.get_description(),
                             "dependencies": mod.get_dependencies()}
    print("Creating Thunderstore package: {0}".format(package_file))
    with ZipFile(package_file, "w") as myzip:
        myzip.writestr("manifest.json", json.dumps(thunderstore_manifest, indent=4))
        myzip.write(mod.readme_file, "README.md")
        myzip.write(mod.icon_file, "icon.png")
        for plugin_file in mod.get_plugin_artifacts():
            myzip.write(plugin_file, "plugins/"+os.path.basename(plugin_file))
        for patcher_file in mod.get_patcher_artifacts():
            myzip.write(patcher_file, "patchers/"+os.path.basename(patcher_file))

print("Done!")
