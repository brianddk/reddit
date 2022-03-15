#!/bin/bash
# [rights]  Copyright 2022 brianddk at github https://github.com/brianddk
# [license] Apache 2.0 License https://www.apache.org/licenses/LICENSE-2.0
# [repo]    github.com/brianddk/reddit/blob/master/shell/fixgrub.sh
# [btc]     BTC-b32: bc1qwc2203uym96u0nmq04pcgqfs9ldqz9l3mz8fpj
# [tipjar]  github.com/brianddk/reddit/blob/master/tipjar/tipjar.txt
# [ref]     https://www.reddit.com/r/Ubuntu/comments/tc32p8/

# Few convince variables
esp="/dev/sda1"
bootimg="/esp/efi/boot.img"
grubtostyle="GRUB_TIMEOUT_STYLE="
grubtoamt="GRUB_TIMEOUT="

# make the mount points, backup and move the mount
mkdir -p /esp/{loop,efi}
cp -a /boot /boot.bk
umount /boot/efi
mount "$esp" /esp/efi

# move boot
mv /boot /boot.old

# make a loopback boot image
dd if=/dev/zero of=$bootimg bs=1MiB count=250
losetup -f $bootimg
ldev=$( losetup -j $bootimg | cut -f 1 -d : )
mkfs.ext4 -L "Ubuntu boot.img" $ldev
mount $ldev /esp/loop
mv /boot.old/grub /esp/efi/grub
rmdir /boot.old/efi
mv /boot.old /esp/loop/boot
ln -s /esp/loop/boot /boot
ln -s /esp/efi/grub /boot/grub
ln -s /esp/efi /boot/efi

# modify our fstab
cp /etc/fstab /etc/fstab.old
sed -i 's#\(\s\)/boot/efi#\1/esp/efi#' /etc/fstab
echo "$bootimg /esp/loop ext4 loop 0 2" >> /etc/fstab
mount -a # (to test fstab)

# unhide our grub menu
cp /etc/default/grub /etc/default/grub.old
sed -i "s/^$grubtostyle/#$grubtostyle/" /etc/default/grub
sed -i "s/^$grubtoamt/#$grubtoamt/" /etc/default/grub

# rebuild grub / initrd since we are now "special
grub-install --efi-directory /boot/efi --recheck --uefi-secure-boot $esp
update-initramfs -c -k all # (takes forever)
update-grub

# make grub mount our loopback boot.img in EFI
mv /boot/efi/EFI/ubuntu/grub.cfg /boot/efi/EFI/ubuntu/grub.cfg.old
head -n 1 /boot/efi/EFI/ubuntu/grub.cfg.old | sed 's/root/esp/' > /boot/efi/EFI/ubuntu/grub.cfg
cat << "HEREDOC" >> /boot/efi/EFI/ubuntu/grub.cfg
loopback loop0 ($esp)'/boot.img'
set prefix=($esp)'/grub'
set root=(loop0)
configfile $prefix/grub.cfg
HEREDOC
