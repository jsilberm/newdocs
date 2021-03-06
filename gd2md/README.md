# Instructions
------------
1. Copy following files in one location:
    credentials.json
    parse_gdoc.py
    readgdoc.py
    token.pickle
2. Copy the _.gdocs file into your home directory
3. rename _.gdocs to .gdocs
4. cd to the location where you just coped the 4 files
5. If needed, modify first line in readdoc.py file to point to your python3 binary (Default: /usr/bin/python3)
6. execute:
./readgdoc --help
and
./readgdoc headless --help

EXAMPLES:

Example 1:
Read the doc <ID> hedless and store all bitmat images in /home/roger/final/images and store the md file in /home/roger/final 

```
./readgdoc headless -i <Document ID> -b "/home/roger/final/images" -d "/home/roger/final"
```

Example 2:
If the readgdoc.py scrip need to write images to a mounted path that is different than the md file will read the imnages, use relative path 
(Lets assume that /my_mount_2_dest is mounted to: /home/roger/final, when readgdoc.py executes)
Read the doc <ID> hedless and store all bitmat images in /my_mount_2_dest/images and store the md file in /my_mount_2_dest, with the md file references the images by relative path "./images"

```
./readgdoc headless -i <Document ID> -b "/my_mount_2_dest/images" -d "/my_mount_2_dest" -r "./images"
```

Example 3:
To scan the doc and get report only:

```
./readgdoc scan -i <Document ID>
```

# Running as Container

Make sure `.gdocs` is in `$PWD` and contains the password for the `release` user.

To build : ` docker build -t gd2md:latest .`

To run container as daemon (Ex:): 
```
DOCNAME="PSM_User_Guide"
DOCDIR=/home/jeff/docs/content/psm/v1.8.0-E/$DOCNAME
IMGDIR=/home/jeff/docs/static/images/PSM/$DOCNAME
mkdir -p $DOCDIR $IMGDIR
docker run -u `id -u`:`id -g` -v `pwd`:/home/release -v $DOCDIR:/tmp/docs -v $IMGDIR:/tmp/bitmaps gd2md headless -i 1MUYMOptgsOCg_2h8Rnv4GGsrDeOugmYAq9wbuGedGVQ -d /tmp/docs -b /tmp/bitmaps -r /images/PSM/PSM_User_Guide -v
```
