sudo apt-add-repository ppa:bitcoin/bitcoin
sudo apt-get update
sudo apt-get install bitcoind
crontab -e
@reboot bitcoind -daemon
bitcoind -daemon
tail -f ~/.bitcoin/debug.log