import sys
import random
from datetime import datetime
import os
from subprocess import Popen, PIPE, STDOUT


def main(argv):
    random.seed(datetime.now())

    gen_image()



def list_sum(l):
    sum = 0
    for i in l:
        sum += i
    return sum



BUILD_PATH = "/root/"
IMAGE_NAME = "hdd.img"

PARTITIONS = ["ntfs", "fat", "ext3"]
SECTOR_START = 2048
SECTOR_END = 799999

# Generate the image and its partitions
def gen_image():
    global PARTITIONS

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

    print(p_sz, PARTITIONS)

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
    print(repr(fdisk_str))

    # Create partitions via fdisk
    p = Popen(["fdisk", image_path], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
    fdisk_stdout = p.communicate(input=fdisk_str.encode('latin-1'))

    for i in range(len(PARTITIONS)):
        # Set up partition as loop device to change fs type
        # p = Popen(["losetup", "--offset", str(512 * p_info[i][0]), str(512 * p_info[i][1]), "--show", "--find", image_path])
        # print(p.communicate())
        r = os.system("losetup --offset $((512*{})) --sizelimit $((512*{})) --show --find {}".format(p_info[i][0], p_info[i][1], image_path))
        assert(r == 0)

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
        r = os.system("mkdir -p /mnt/hddp")
        assert(r == 0)
        r = os.system("mount /dev/loop0 /mnt/hddp")
        assert(r == 0)

        # ===== Do stuff to fs of partition @ /mnt/hddp =====
        os.system("cp {} {}".format("/forensics/corgis/corgi1.png", "/mnt/hddp/"))
        os.system("cp {} {}".format("/forensics/corgis/corgi2.jpg", "/mnt/hddp/"))
        os.system("cp {} {}".format("/forensics/corgis/corgi3.jpg", "/mnt/hddp/"))
        os.system("rm -f {}".format("/mnt/hddp/corgi2.jpg"))

        # Unmount partition & loop device
        r = os.system("umount /mnt/hddp")
        assert(r == 0)
        r = os.system("losetup -d /dev/loop0")
        assert(r == 0)

        

        






if __name__ == "__main__":
    main(sys.argv[1:])