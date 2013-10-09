# 
#  PyInstaller Build Script for OS X
#  CINEMA 4D Plugin Wizard
#  
#  Created by André Berg on 2013-08-23.
#  Copyright 2013 Berg Media. All rights reserved.
# 


author_name="André Berg"
app_name="CINEMA 4D Plugin Wizard"
app_icon="c4dapp.icns"
bundle_identifier="com.seramediavfx.C4DPluginWizard"
version="0.1"
cr_year=`date +%Y`
base="$HOME/Documents/Eclipse/Workspaces/Python/C4D Plugin Wizard"
pyinstdir="$HOME/source/pyinstaller-2.0"
distdir="$base/dist/osx"
appdir="$distdir/$app_name.app"
contentsdir="$appdir/Contents"
resdir="$contentsdir/Resources"
bindir="$contentsdir/MacOS"
python="/usr/local/bin/python"  # make sure to use Python from python.org not the System one

rm -rf "$distdir"

# for future reference the command line that was used to create the initial Spec file
#"$python" pyinstaller.py --onefile --icon="$base/source/res/$app_icon" --name="$app_name" --paths="$base/source/gui.py" --paths="$base/source/c4dplugwiz.py" --additional-hooks-dir="$base/support/pyinstaller/hooks" --noconfirm "$base/source/gui.py"

"$python" "$pyinstdir/pyinstaller.py" "$base/scripts/C4D Plugin Wizard.spec"

# create dirs

echo "\n-------------- creating appdir ---------------\n"
mkdir -p "$appdir"

if [[ ! -d "$appdir" ]]; then
	echo -e "couldn't create app dir '$appdir'. Exiting..."
	exit 1
fi

echo "\n------------- Create Bindir ---------------\n"
mkdir -p "$bindir"

echo "\n-------------- Create Resdir ---------------\n"
mkdir -p "$resdir"

# copy over resources

echo "\n-------------- Copy Binary ---------------\n"
cp -v "$distdir/$app_name" "$bindir"

echo "\n-------------- Copy Icon ---------------\n"
cp -v "$base/source/res/$app_icon" "$resdir"


# copying images and data is handled by Python code inside the Spec file

# echo "\n-------------- copying images ---------------\n"
# cp -Rv "$base/source/images" "$resdir"

# echo -e "\n-------------- copying data ---------------\n"
# cp -Rv "$base/source/c4dplugwiz_data" "$resdir"


echo "\n-------------- Create Info.plist ---------------\n"

cat > "$contentsdir/Info.plist" <<NFO
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>CFBundleDevelopmentRegion</key>
	<string>English</string>
	<key>CFBundleDisplayName</key>
	<string>$app_name</string>
	<key>CFBundleExecutable</key>
	<string>$app_name</string>
	<key>CFBundleGetInfoString</key>
	<string>$app_name v$version, Copyright $author_name $cr_year. All rights reserved.</string>
	<key>CFBundleIconFile</key>
	<string>c4dapp.icns</string>
	<key>CFBundleIdentifier</key>
	<string>$bundle_identifier</string>
	<key>CFBundleInfoDictionaryVersion</key>
	<string>6.0</string>
	<key>CFBundleName</key>
	<string>$app_name</string>
	<key>CFBundlePackageType</key>
	<string>APPL</string>
	<key>CFBundleShortVersionString</key>
	<string>$version</string>
	<key>CFBundleSignature</key>
	<string>????</string>
	<key>CFBundleVersion</key>
	<string>0.0.0</string>
	<key>LSHasLocalizedDisplayName</key>
	<false/>
	<key>NSAppleScriptEnabled</key>
	<false/>
	<key>NSHumanReadableCopyright</key>
	<string>© $author_name, $cr_year</string>
	<key>NSMainNibFile</key>
	<string>MainMenu</string>
	<key>NSPrincipalClass</key>
	<string>NSApplication</string>
</dict>
</plist>
NFO

echo "\n--------------- Clean Up ---------------\n"

rm "$resdir/icon-windowed.icns"

echo "\n--------------- Make Zip ---------------\n"

cd "$distdir"
zip -r  -Z=deflate -9 "$app_name (OSX).zip" "c4dplugwiz_data/" "images/" "$app_name.app/"
cd -

echo "\n--------------- Done ---------------\n"
open -a "Finder" "$distdir"
