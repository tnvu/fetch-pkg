# fetch-pkg
Fetches PS4/PS5 packages

My implementation of a PS4/PS5 patch file fetcher and merger.

This is different from https://github.com/ps5-payload-dev/fetchpkg
in that it will keep the completed parts so it doesn't have to re-download
them again.

This is also different from https://github.com/Tustin/pkg-merge because
it uses the JSON file to create the patch package ensuring the filenames
and offsets are placed in the correct location. You do not need to rename
 the *_sc.pkg file because it's location is already defined in the JSON.

 I've used all built-in implmentations so you only need Python on your system.

 If you're using https://prosperopatches.com/ you can just copy the link to
 the '.crc' file and it will automatically find the .json file.

 Usage:
 
        python fetch-pkg.py <url-to-json-file> ...

Example:
        # Download update to Assassin's Creed Mirage (US)
        
        python fetch-pkg.py https://sgst.prod.dl.playstation.net/sgst/prod/00/PPSA07230_00/app/info/48/f_16539a36460b1784b8bc4b6771a9dbc6d68e7f15dfff7c7391f3af44b5024942/UP0001-PPSA07230_00-GAME000000000000.json
