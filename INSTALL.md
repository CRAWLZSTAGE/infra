# Installation Instructions

Please make sure you have the prerequisite software on your KOMPUTER

## OSX

### HomeBrew
```sh
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
brew update
brew install docker docker-compose
brew install dnsmasq
```

### Docker Setup

Refer to [testing doc](TESTING.md#Local-Deployment)

### DNSMasq Setup

Courtesy https://medium.com/@narakuw/brew-install-dnsmasq-in-macos-sierra-26021c824be8

```sh
# Create config files
mkdir -pv $(brew --prefix)/etc/
cp /usr/local/opt/dnsmasq/dnsmasq.conf.example /usr/local/etc/dnsmasq.conf
echo 'address=/crawlz.me/$(docker-machine ip local-dev)' > $(brew --prefix)/etc/dnsmasq.conf
echo 'no-resolv' > $(brew --prefix)/etc/dnsmasq.conf
echo 'strict-order' > $(brew --prefix)/etc/dnsmasq.conf
echo 'server=8.8.8.8#5353' > $(brew --prefix)/etc/dnsmasq.conf
echo 'listen-address=127.0.0.1,192.168.x.x' > $(brew --prefix)/etc/dnsmasq.conf

# Load daemons
sudo launchctl load -w /Library/LaunchDaemons/homebrew.mxcl.dnsmasq.plist
sudo cp -v $(brew --prefix dnsmasq)/homebrew.mxcl.dnsmasq.plist /Library/LaunchDaemons

# Update local resolver
sudo mkdir -v /etc/resolver
sudo bash -c 'echo "nameserver 127.0.0.1" > /etc/resolver/crawlz.me'

# Reload dnsmasq service
sudo launchctl unload homebrew.mxcl.dnsmasq.plist && sudo launchctl load homebrew.mxcl.dnsmasq.plist
```

Update your DNS preferences in System_Preferences/Network/Advanced...


