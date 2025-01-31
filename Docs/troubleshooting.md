# Trouble Shooting

**Please check the port of pressure regulator !!!!!**

- 1 is connected to the pump
- 2 is connected to the display
- 3 is connected to the exhaust air

## if get this error:

```plaintext
    C:\Users\pijuanyu>ssh pijuanyu@10.247.250.181
    @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    @    WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!     @
    @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    IT IS POSSIBLE THAT SOMEONE IS DOING SOMETHING NASTY!
    Someone could be eavesdropping on you right now (man-in-the-middle attack)!
    It is also possible that a host key has just been changed.
    The fingerprint for the ED25519 key sent by the remote host is
    SHA256:AG70F5dXTXLXOF5b2VTTpmoHVs8Ve3Xg84qNDWIqYBk.
    Please contact your system administrator.
    Add correct host key in C:\\Users\\pijuanyu/.ssh/known_hosts to get rid of this message.
    Offending ECDSA key in C:\\Users\\pijuanyu/.ssh/known_hosts:3
    Host key for 10.247.250.181 has changed and you have requested strict checking.
    Host key verification failed.
```

Type this on the windows PC:
```plaintext
    ssh-keygen -R 10.247.250.181
```
