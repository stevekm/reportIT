# Instructions for setting up the remote IonTorrent server for the pipeline

1. Log into the server with the default account provided by Thermo Fischer 

```bash
ssh iontorrent@126.72.3.98
```

2. If it does not already exist, create the ssh directory on the server, and log out of the remote server
```bash
mkdir -p ~/.ssh
exit
```

3. Make sure you've set up a public ssh key WITHOUT a passphrase, as per description [here](https://gist.github.com/stevekm/93de1539d8008d220c9a1c4d19110b3e)

4. Append the local system's public ssh key to the remote IonTorrent server's `authorized_keys` file
```bash
cat ~/.ssh/id_rsa.pub | ssh iontorrent@126.72.3.98 'cat >> .ssh/authorized_keys'
```
- your local system public key might be in a file such as `~/.ssh/id_dsa.pub` or `~/.ssh/id_rsa.pub`

If it worked, you should now be able to log into the server without entering a password:

```bash
ssh iontorrent@126.72.3.98
```

NOTE: Steps 3 & 4 must be repeated for each local system user who plans to use the pipeline. 
NOTE: The IonTorrent server account that is used for this process must match the one set in the 
