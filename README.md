# BepInEx ModPacker

This script manages a BepInEx mod project's artifacts.

## Main features
- Installs the artifacts in a local r2modman/BepInEx folder
- Creates a Thunderstore package

## Project structure
The script assumes that the project is organized in the following structure:
 
```
Project
│
└─meta
│  │ icon.png
│  │ manifest.json
│  │ README.md
│
└─plugin
│  │ YourPluginProject.csproj
│  │
│  └─bin
│     │ YourPluginProject.dll
│     │ OtherPluginArtifact.dll
│   
└─patcher
│  │ YourPatcherProject.csproj
│  │
│  └─bin
│     │ YourPatcherProject.dll
│     │ OtherPatcherArtifact.dll
│   
```
The contents of the `meta` folder can be in the project root, but the `meta` folder takes priority 
(for example if you have `README.md` in both folders, the one in `meta` goes into the package).

## manifest.json
The `manifest.json` file is similar to the standard Thunderstore manifest with a few added fields:
```Json
{
    "name": "The mod's name",
    "author": "Your name in Thunderstore",
    "version_number": "1.0.0",
    "website_url": "The mod's website url",
    "description": "The mod's short description",
    "dependencies": [
      "The mod's dependencies, for example:",
      "BepInEx-BepInExPack_Outward-5.4.8"
    ],
    "artifacts": {
        "plugin": [
          "Extra plugin artifacts that should be included in the mod package",
          "OtherPluginArtifact.dll",
          "These artifacts need to exist in the bin folder"
        ],
        "patcher": [
          "Extra patcher artifacts that should be included in the mod package",
          "OtherPatcherArtifact.dll",
          "These artifacts need to exist in the bin folder"
        ]
    }
}
```

## Usage
The script needs to be run from the project root or any subfolder (it automatically finds the project root).  
*It's strongly recommended to add the script to PATH and/or run it as a post-build step.*  
The script executes various tasks specified by command line arguments.  
If it's ran without any command line arguments, then **all tasks are executed**.  

### Local install
The `local` command line argument installs the project artifacts to r2modman/BepInEx folder.

### Thunderstore
The `thunderstore` command line argument creates a Thunderstore package in the `release/Thunderstore` folder.

## Notes
- Right now the mod only supports a `r2modmanPlus-local` installation for `Outward` with `Default` profile 
(more BepInEx locations, profiles and generic game support coming soon). 
For now, it's fairly straightforward to edit the paths in the script
- The script is not guaranteed bug-free, **always check your package before publishing**, I am not responsible for broken packages
- I will probably implement a more flexible project setup support later
- Feel free to contact me on the `Outward modding discord` if you have suggestions or ideas
