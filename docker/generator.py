import sys
import random
from datetime import datetime
import os
from subprocess import Popen, PIPE, STDOUT, call
from string import digits, ascii_letters
import randomfiletree
from PIL import Image, ImageFont, ImageDraw
import lorem
from fpdf import FPDF
import hivex
import shutil



BUILD_PATH = "/root/"
IMAGE_NAME = "hdd.img"
MOUNT_PATH = "/mnt/hddp"
SHARED_DIR = "/forensics"
CONTENT_PATH = os.path.join(SHARED_DIR, "content")

PARTITIONS = ["ntfs", "fat", "ext3"]
SECTOR_START = 2048
SECTOR_END = 799999



random.seed(datetime.now())



def main(argv):
    gen_image()


def list_sum(l):
    sum = 0
    for i in l:
        sum += i
    return sum


def create_random_tree(path):
    return randomfiletree.create_random_tree(path, nfiles=2.0, nfolders=0.6, maxdepth=5, repeat=4)


def gen_flag():
    return "flag{" + ''.join(random.choice(digits + 'abcdef') for i in range(32)) + "}"

def gen_filename():
    return ''.join(random.choice(ascii_letters) for i in range(random.randint(5,10)))

def pick_content(type="image", ext=None):
    global CONTENT_PATH
    if ext != None:
        choice_fn = ""
        while choice_fn.split('.')[-1] != ext:
            choice_fn = random.choice(os.listdir(os.path.join(CONTENT_PATH,type)))
        return choice_fn
    return random.choice(os.listdir(os.path.join(CONTENT_PATH,type)))


def add_flag_to_image(path_in, path_out, flag):
    global CONTENT_PATH
    img = Image.open(path_in)
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(os.path.join(CONTENT_PATH, "font", "microsoft-sans-serif.ttf"), 20)
    draw.text((0, 0),flag,(0,0,0),font=font) # this will draw text with Blackcolor and 16 size
    img.save(path_out)


# Generate the image and its partitions
def gen_image():
    global PARTITIONS, MOUNT_PATH, CONTENT_PATH

    # SETUP
    # Create image path
    image_path = os.path.join(BUILD_PATH, IMAGE_NAME)

    # Generate partition sizes
    p_sz = []
    for i in range(len(PARTITIONS)):
        if i == len(PARTITIONS) - 1:
            p_sz.append(min((SECTOR_END-SECTOR_START-(list_sum(p_sz)*2048))/2048,random.randint(80, 100)))
        else:
            p_sz.append(random.randint(80, 100))
    random.shuffle(p_sz)
    random.shuffle(PARTITIONS)

    # print(p_sz, PARTITIONS)

    # Create new blank image
    r = os.system("dd if=/dev/zero of={} bs=4k count=100000".format(image_path))  
    assert(r == 0)

    # Generate string to give to fdisk to create new partitions
    p_info = []
    fdisk_str = ""
    sz_count = 2048
    for i in range(len(p_sz)):
        fdisk_str += "n\np\n{}\n{}\n{}\n".format(i+1, sz_count, "+{}M".format(p_sz[i]))
        p_info.append((sz_count, p_sz[i]*2048))
        sz_count += p_sz[i]*2048
    fdisk_str += "w\n"
    # print(repr(fdisk_str))

    # Create partitions via fdisk
    p = Popen(["fdisk", image_path], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
    fdisk_stdout = p.communicate(input=fdisk_str.encode('latin-1'))

    challenges = {}
    for i in range(len(PARTITIONS)):
        # Set up partition as loop device to change fs type
        # p = Popen(["losetup", "--offset", str(512 * p_info[i][0]), str(512 * p_info[i][1]), "--show", "--find", image_path])
        # print(p.communicate())
        r = os.system("losetup --offset $((512*{})) --sizelimit $((512*{})) --show --find {}".format(p_info[i][0], p_info[i][1], image_path))
        assert(r == 0)

        slack_begin = sz_count + 1
        slack_end = SECTOR_END

        # Change fs type
        if PARTITIONS[i] == "ntfs":
            r = os.system("mkfs.ntfs /dev/loop0")
            assert(r == 0)
        elif PARTITIONS[i] == "fat":
            r = os.system("mkfs.fat /dev/loop0")
            assert(r == 0)
        elif PARTITIONS[i] == "ext3":
            r = os.system("mkfs.ext3 /dev/loop0")
            assert(r == 0)
        else:
            print("Unsupported FS")
            exit()


        # Mount partition
        r = os.system("mkdir -p {}".format(MOUNT_PATH))
        assert(r == 0)
        r = os.system("mount /dev/loop0 {}".format(MOUNT_PATH))
        assert(r == 0)

        # ===== Do stuff to fs of partition @ /mnt/hddp =====

        if PARTITIONS[i] == "ntfs":
            tree_dirs = []
            while tree_dirs == []:
                (tree_dirs, tree_files) = create_random_tree(MOUNT_PATH)
            
            # NTFS partition Challenges

            challenges["ntfs_file_recovery"] = {}
            challenges["ntfs_file_recovery"]["flag"] = gen_flag()
            challenge_file = pick_content()
            challenges["ntfs_file_recovery"]["path_out"] = os.path.join(str(random.choice(tree_dirs)),challenge_file)
            ntfs_file_recovery(challenges["ntfs_file_recovery"]["flag"], os.path.join(CONTENT_PATH,"image",challenge_file), challenges["ntfs_file_recovery"]["path_out"])

            challenges["ntfs_strings"] = {}
            challenges["ntfs_strings"]["flag"] = gen_flag()
            challenges["ntfs_strings"]["path_out"] = os.path.join(str(random.choice(tree_dirs)), gen_filename())
            ntfs_strings(challenges["ntfs_strings"]["flag"], challenges["ntfs_strings"]["path_out"])

            challenges["ntfs_grep"] = {}
            challenges["ntfs_grep"]["flag"] = gen_flag()
            challenges["ntfs_grep"]["path_out"] = os.path.join(str(random.choice(tree_dirs)), gen_filename())
            ntfs_grep(challenges["ntfs_grep"]["flag"], challenges["ntfs_grep"]["path_out"])

            challenges["ntfs_broken_img_hdr"] = {}
            challenges["ntfs_broken_img_hdr"]["flag"] = gen_flag()
            challenge_file = pick_content(ext="jpg")
            challenges["ntfs_broken_img_hdr"]["path_out"] = os.path.join(str(random.choice(tree_dirs)),challenge_file)
            ntfs_broken_img_hdr(challenges["ntfs_broken_img_hdr"]["flag"], os.path.join(CONTENT_PATH,"image",challenge_file), challenges["ntfs_broken_img_hdr"]["path_out"])
            
        elif PARTITIONS[i] == "fat":
            tree_dirs = []
            while tree_dirs == []:
                (tree_dirs, tree_files) = create_random_tree(MOUNT_PATH)

            # FAT partition challenges
            
            challenges["fat_broken_pdf_hdr"] = {}
            challenges["fat_broken_pdf_hdr"]["flag"] = gen_flag()
            challenges["fat_broken_pdf_hdr"]["path_out"] = os.path.join(str(random.choice(tree_dirs)),gen_filename())
            fat_broken_pdf_hdr(challenges["fat_broken_pdf_hdr"]["flag"], challenges["fat_broken_pdf_hdr"]["path_out"])

            challenges["fat_registry_hive"] = {}
            challenges["fat_registry_hive"]["flag"] = gen_flag()
            challenge_file = pick_content(type="registry")
            challenges["fat_registry_hive"]["path_out"] = os.path.join(str(random.choice(tree_dirs)), challenge_file)
            fat_registry_hive(challenges["fat_registry_hive"]["flag"], os.path.join(CONTENT_PATH, "registry", challenge_file), challenges["fat_registry_hive"]["path_out"])

        elif PARTITIONS[i] == "ext3":
            tree_dirs = []
            while tree_dirs == []:
                (tree_dirs, tree_files) = create_random_tree(MOUNT_PATH)

            # ext3 partition challenges

            challenges["ext3_img_metadata"] = {}
            challenges["ext3_img_metadata"]["flag"] = gen_flag()
            challenge_file = pick_content(type="image", ext="jpg")
            challenges["ext3_img_metadata"]["path_out"] = os.path.join(str(random.choice(tree_dirs)), challenge_file)
            ext3_img_metadata(challenges["ext3_img_metadata"]["flag"], os.path.join(CONTENT_PATH, "image", challenge_file), challenges["ext3_img_metadata"]["path_out"])

        else:
            print("Unsupported partition type")
            exit()

        # Unmount partition & loop device
        r = os.system("umount /mnt/hddp")
        assert(r == 0)
        r = os.system("losetup -d /dev/loop0")
        assert(r == 0)


        # Slack space challenges
        # challenge_flags["slack_file_carve"] = gen_flag()
        # challenge_file = pick_content(type="doc")
        # slack_file_carve(challenge_flags["slack_file_carve"], os.path.join(CONTENT_PATH, "doc", challenge_file), slack_begin, slack_end)

    print("")
    print("*****************************************")
    print("**    CHALLENGE CREATION SUCCESSFUL    **")
    print("*****************************************")

    with open("flags.txt", "w+") as f:
        for k,v in challenges.items():
            f.write("{}\n".format(k))
            f.write("Flag: {}\n".format(v["flag"]))
            if "path_out" in v:
                new_path_out = "[{}]{}".format(k.split("_")[0].upper(), v["path_out"][9:])
                f.write("File location: {}\n".format(new_path_out))
            f.write("\n")

    print("Challenge flags output to flags.txt")
    print("Moving challenge file to shared folder")

    shutil.move(os.path.join(BUILD_PATH, IMAGE_NAME), os.path.join(SHARED_DIR, IMAGE_NAME))

    print("Challenge file moved to shared folder as {}".format(IMAGE_NAME))
    print("")



def ntfs_file_recovery(flag, path_in, path_out):
    add_flag_to_image(path_in, path_out, flag)
    # os.system("cp {} {}".format(path_in, path_out))
    os.system("rm -f {}".format(path_out))


def ntfs_strings(flag, path_out): 
    # Read data from rnd, save as file
    with open("/dev/random", "rb") as f:
        bin_data = f.read(random.randint(6000,10000))

    with open(path_out, "wb+") as f:
        f.write(bin_data)
        f.seek(0,2)
        size = f.tell()	
        random_loc = random.randrange(0, size-len(flag))
        f.seek(random_loc, 0)
        f.write(flag.encode('latin-1'))


def ntfs_grep(flag, path_out): 
    # Gen data via lorem, save as file
    with open(path_out, "w+") as f:
        for i in range(random.randint(50,60)):
            f.write(lorem.text())
        f.seek(0,2)
        size = f.tell()	
        random_loc = random.randrange(0, size-len(flag))
        f.seek(random_loc, 0)
        f.write(flag)


def ntfs_broken_img_hdr(flag, path_in, path_out):    
    add_flag_to_image(path_in, path_out, flag)
    with open(path_out, 'r+b') as f:
        f.write(b'\x00\x00\x00\x00')


def fat_broken_pdf_hdr(flag, path_out):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Courier', '', 16)
    pdf.cell(40, 10, flag)
    pdf.output(path_out, 'F')

    with open(path_out, 'r+b') as f:
        f.seek(17)
        f.write(b'~~')


def fat_registry_hive(flag, path_in, path_out):
    keys = []
    h = hivex.Hivex(path_in, write=True)

    def rec(key, depth=0):
        keys.append(key)
        for subkey in h.node_children(key):
            rec(subkey, depth + 1)
    rec(h.root())

    selected_key = random.choice(keys)
    h.node_set_value(selected_key, {"key":"flag", "t":3, "value":flag.encode('latin-1')})
    h.commit(path_out)


def ext3_img_metadata(flag, path_in, path_out):
    shutil.copy(path_in, path_out)
    call(["exiftool","-overwrite_original_in_place","-comment=\"" + flag + "\"", path_out])


def slack_file_carve(flag, path_in, slack_begin, slack_end):
    global BUILD_PATH, IMAGE_NAME

    with open(path_in, "r+b") as f:
        s = f.read()
        idx = s.find(b"aaaaaaaaaaaa", 0)

    with open(os.path.join(BUILD_PATH, IMAGE_NAME), "wb") as f:
        begin_write = random.randint((slack_end - len(s)*5)*512, (slack_end - len(s))*512)
        print("Writing to %d" % begin_write)
        f.seek(begin_write)
        f.write(s)
        f.seek(begin_write + idx, 0)
        f.write(flag.encode('latin-1'))


if __name__ == "__main__":
    main(sys.argv[1:])