---
layout: default
---

# Getting Started: Training & Tutorial

We aren't so cruel as to throw you into the deep end with no life ring. 
This section will teach you how to navigate and solve challenges starting from the beginning,
giving you exposure to four of the main filesystems and types of problems you may see.


### Tutorial Structure: 

We provide you with a single image containing several challenges within, with an additional memory image. 
The idea is to make a small multi-step environment that students can learn from, building upon previous knowledge.

## Image 1: NTFS, Ext3, FAT

(Unfamiliar with these terms? Here is a good resource link to get brushed up!)

| Topic (NTFS, mostly)          |  Description                                                       |
| ------------                  |-----------------                                                   |
| Part 1: Basic information     | (ext3) Md5sum, File System Type, Block Size, Inode Size?           |
| Part 2: Deleted File Recovery | (NTFS) Can you find the flag in the deleted file?                  |
| Part 3: Strings               | (ext3) By a Thread: It's in there somewhere!                       |
| Part 4: Grep                  | (NTFS) It's in there somewhere pt 2 (regex on a file? impossibru!) |
| Part 5: Broken header         | (NTFS) Images have Heads too! This image is broken somehow: how?   |
| Part 6: File Carving          | (NTFS) What is the file containing this keyword? (TBD)             |

### Solutions:

Part 1

```
md5sum [file]
tune2fs -l /dev/[ext3]
Ext3 block + inode size:
| grep -i 'block size'
| grep -i ‘inode size'
```

Part 2

```
-Use tsk_recover, autopsy, or other file recovery tool
-View file
```

Part 3

`
$ strings [file/partition]
`

Part 4

`
$ grep -i [file/partition] “picoCTF“
`

Part 5

```
View jpg image, see it’s broken
View in hex editor
Research jpg headers, compare and find the missing part of the header
Use bless or other hex editor to re-insert missing piece
```

Part 6

`
TBD
`


| Topic (FAT, mostly)           |  Description                                                       |
| ------------                  |-----------------                                                   |
| Part 1: Broken PDF            | (FAT)Another broken file problem. But this time it's a PDF!        |
| Part 2: Deleted File Recovery | (FAT)                                                              |
| Part 5: Metadata              | (FAT) BUT IS IT META???                                            |


### Solutions:

Part 1

```
Attempt to open pdf, see it’s broken
View in hex editor
Research pdf headers, find the missing part of the header or file content
Use bless or other hex editor to re-insert missing piece
```

Part 2

`
TBD
`

Part 3

`
TBD
`

## Image 2: Android Memory

| Topic (Mobile)                |  Description                                                       |
| ------------                  |-----------------                                                   |
| Part 1: Basic information     | Md5sum, Profile, what are the processes for X,Y,Z pids?     |
| Part 2: MFTParser             | What does the $DATA section contain at MFT entry @ offset 0x1f8c6000? |
| Part 3: Extract File          | What is the md5sum of the file containing “[data in MFT entry @ offset]”|
| Part 4: Clipboard             | The flag is the user's last copypasta. Don't copypasta passwords kids!|
| Part 4.5: Combo99             | What is the file associated with the data in clipboard history?   |
| Part 5: Combo 100: IEhist, MFT| What are the contents of the file recently last accessed at 15:11:40?|

### Solutions:

Part 1

```
$ md5sum memtutorial.mem
$ volatility -f memtutorial.mem imageinfo
$ volatility -f memtutorial.mem --profile=Win7SP1x86 pslist
```

Part 2

```
Get MFT entry at given offset
$ volatility -f memtutorial.mem --profile=Win7SP1x86 mftparser -o 0x1f8c6000
```

Part 3

```
$ volatility -f memtutorial.mem --profile=Win7SP1x86 mftparser -o 0x1f8c6000 -D outdir 
$ file.0x1f8c6000.data0.dmp
```

Part 4

`
$ volatility -f memtutorial.mem --profile=Win7SP1x86 clipboard
`

Part 5

```
$ volatility -f memtutorial.mem --profile=Win7SP1x86 mftparser | grep -C 20 OP-DATOU
OR
$ volatility -f memtutorial.mem --profile=Win7SP1x86 mftparser > mftdump
$ cat mftdump | grep -C 20 OP-DATOU
Answer: omaewashindeiru.txt
```

Part 6

```
$ volatility -f memtutorial.mem --profile=Win7SP1x86 iehistory
=>
$ volatility -f memtutorial.mem --profile=Win7SP1x86 mftparser | grep -C 20 hoho.txt
OR
$ volatility -f memtutorial.mem --profile=Win7SP1x86 mftparser > mftdump
$ cat mftdump | grep -C 20 hoho.txt
```
