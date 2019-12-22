sudo apt-add-repository ppa:bitcoin/bitcoin
sudo apt-get update
sudo apt-get install bitcoind
crontab -e

*/15 * * * * sudo echo 1 > /proc/sys/vm/drop_caches
*/15 * * * * sudo echo 2 > /proc/sys/vm/drop_caches
*/15 * * * * sudo echo 3 > /proc/sys/vm/drop_caches

@reboot bitcoind -daemon

bitcoind -daemon
tail -f ~/.bitcoin/debug.log