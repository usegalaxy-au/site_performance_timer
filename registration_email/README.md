# registration_performance_timer

The registration performance timer runs a large number of selenium jobs, simulating a specified number of users registering
on the system, and waiting for a verification email. Stats are generated for each run. Under the hood, it launches many
instances of the registration_email_perf_timer docker container in parallel, and logs the stats (stats are in the influxdb
wire protocol which can be posted directly to influx), along with a csv file that logs error output per run.

## Output

### standard output:

The standard output is the same as what's generated by the registration_email_perf_timer.
```
email_verification,server=https://dev.usegalaxy.org.au,email=usegalaxyaustresstest+u_0@gmail.com,status=success result=14.905893087387085 1680360373280370498
email_verification,server=https://dev.usegalaxy.org.au,email=usegalaxyaustresstest+u_1@gmail.com,status=success result=1.749422550201416 1680364987208320427
email_verification,server=https://dev.usegalaxy.org.au,email=usegalaxyaustresstest+u_2@gmail.com,status=success result=1.5955517292022705 1680365020334151834
```

### log output:

The log output in csv format can be used to look at per execution runtime and any error output.

```csv
```

## Usage

1. Generate the tests

   Before running the tests, a list of tests to be executed should be generated as follows:
   ```bash
   python3 generate_reg_email_perf_tests.py -s "https://dev.usegalaxy.org.au" --imap_password some_pass --num_users 10 > list_of_tests.txt
   ```

    The parameters define which server to target, a username pattern to use when registering, and the connection details of the imap account to check
    for receipt of the verification email.

    ```bash
    sudo docker run --rm -e GALAXY_SERVER=https://dev.usegalaxy.org.au -e GALAXY_EMAIL=usegalaxyaustresstest+u_0@gmail.com -e GALAXY_USERNAME=u_0 -e GALAXY_PASSWORD=9df24e1c-3d4f-46ff-8cb7-d8a39ab3d1f4 -e IMAP_SERVER=imap.gmail.com -e IMAP_USERNAME=usegalaxyaustresstest@gmail.com -e IMAP_PORT=993 -e IMAP_PASSWORD=some_pass usegalaxyau/registration_email_perf_timer:latest
    sudo docker run --rm -e GALAXY_SERVER=https://dev.usegalaxy.org.au -e GALAXY_EMAIL=usegalaxyaustresstest+u_1@gmail.com -e GALAXY_USERNAME=u_1 -e GALAXY_PASSWORD=9df24e1c-3d4f-46ff-8cb7-d8a39ab3d1f4 -e IMAP_SERVER=imap.gmail.com -e IMAP_USERNAME=usegalaxyaustresstest@gmail.com -e IMAP_PORT=993 -e IMAP_PASSWORD=some_pass usegalaxyau/registration_email_perf_timer:latest
    sudo docker run --rm -e GALAXY_SERVER=https://dev.usegalaxy.org.au -e GALAXY_EMAIL=usegalaxyaustresstest+u_2@gmail.com -e GALAXY_USERNAME=u_2 -e GALAXY_PASSWORD=9df24e1c-3d4f-46ff-8cb7-d8a39ab3d1f4 -e IMAP_SERVER=imap.gmail.com -e IMAP_USERNAME=usegalaxyaustresstest@gmail.com -e IMAP_PORT=993 -e IMAP_PASSWORD=some_pass usegalaxyau/registration_email_perf_timer:latest
    ```

2. Execute the tests

    To execute the tests generated above:
    ```bash
    cat list_of_tests.txt | parallel -S 4/115.146.85.212 -S 4/115.146.85.100 -j 1 --results test_results.csv > test_results.txt
    ```

    The above will use two execution nodes (115.146.85.212 and 115.146.85.100), each with 4 cores (the prefix in front of the ip),
    and pipe the influx stats into `test_results.txt` and output log into `test_results.csv`. The `-j` parameter specifies the number
    of users to simulate in parallel.

    The execution nodes must have docker installed and have ssh access enabled, but can otherwise be vanilla ubuntu nodes.
    It must also be possible to perform passwordless authentication against the execution nodes. Configure your
    `~/.ssh/config` file as follows to do so:
    ```
    Host 115.146.85.212
    User ubuntu
    IdentityFile /home/ubuntu/keys/cloudman_keypair_rc.pem

    Host 115.146.85.100
    User ubuntu
    IdentityFile /home/ubuntu/keys/cloudman_keypair_rc.pem
    ```

### Email inbox for registration emails

A gmail account has been pre-created for receiving the registration message generated by Galaxy. The credentials for the inbox
are stored in an Ansible vault. The vault can be decrypted using the same keys used for usegalaxy.au's infrastructure playbook.
Use the gmail account name as the IMAP_USERNAME and the app password as the IMAP_PASSWORD when running the tests.

### Extra commands

#### Updating the docker container
If the docker container for the registration_email_perf_timer is updated, use the following command to update it on all nodes:
```bash
parallel --nonall -S 4/115.146.85.212 -S 4/115.146.85.100 sudo docker pull usegalaxyau/registration_email_perf_timer:latest
```

#### Increasing shh connections
```bash
parallel --nonall -S 115.146.86.82 -S 115.146.84.23 -S 115.146.86.236 -S 115.146.86.71 -S 115.146.84.220 -S 115.146.84.115 'sudo grep -q "^MaxSessions" /etc/ssh/sshd_config && sudo sed "s/^MaxSessions.*/MaxSessions 50/" -i /etc/ssh/sshd_config || sudo sed "$ a\MaxSessions 50" -i /etc/ssh/sshd_config'
parallel --nonall -S 115.146.86.82 -S 115.146.84.23 -S 115.146.86.236 -S 115.146.86.71 -S 115.146.84.220 -S 115.146.84.115 'sudo grep -q "^MaxStartups" /etc/ssh/sshd_config && sudo sed "s/^MaxStartups.*/MaxStartups 100:30:1000/" -i /etc/ssh/sshd_config || sudo sed "$ a\MaxStartups 100:30:1000" -i /etc/ssh/sshd_config'
parallel --nonall -S 115.146.86.82 -S 115.146.84.23 -S 115.146.86.236 -S 115.146.86.71 -S 115.146.84.220 -S 115.146.84.115 sudo service ssh restart
```