import subprocess
import os
from subprocess import Popen, PIPE

# create dev/null object, which will be used with subprocess to avoid broken pipe spam
FNULL = open(os.devnull, 'w')

# Convenience class containing utility methods for executing commands and converting data
class resource(object):
    def __init__(self):
        pass

    def calculate(self, command):
        # Output of communicate()[0] is bytes in Python 3
        args = subprocess.Popen([command], shell=True, stderr=FNULL, stdout=PIPE).communicate()[0]
        if isinstance(args, bytes):
            args = args.decode("utf-8")
        args = args.strip()
        if args == "0":
            args = 1
        if args == "":
            args = 1
        return args

    def calculate_gig(self, number):
        modified_number = number / 1000000
        return modified_number

    def calculate_kilo(self, number):
        modified_number = number / 1000
        return modified_number

# Class used for cpu stats
class cpu(object):
    def __init__(self):
        pass

    def load_threshold(self, load, cores):
        procs_over = load - cores
        if procs_over <= 0:
            procs_over = 1
        return procs_over

    def check_usage(self, idle, sys, user, io):
        usage = 100 - idle

        usage = str(usage)
        user = str(user)
        sys = str(sys)
        io = str(io)

        print("According to iostat data on average the CPU is at " + usage + "% utilization.")
        print("According to iostat data on average " + user + "% of the CPU usage is user.")
        print("According to iostat data on average " + sys + "% of the CPU usage is sys.")
        print("According to iostat data on average " + io + "% of the CPU usage is IO.\n")

    def check_user_cpu(self, user):
        user = str(user)
        print("The user that has consumed the most cpu based on top is " + user + ". Here is a snapshot of this user's processes: \n")
        ps_command = ["ps", "aux"]
        grep_command = ["grep", user]
        ps_process = subprocess.Popen(ps_command, stdout=subprocess.PIPE)
        grep_process = subprocess.Popen(grep_command, stdin=ps_process.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        ps_process.stdout.close()
        stdout, stderr = grep_process.communicate()
        output_str = stdout.decode('utf-8')
        error_str = stderr.decode('utf-8')
        print(output_str)


	
# Class used for memory stats
class memory(object):
    def __init__(self):
        pass

    def pid_usage(self, pid):
        pid = str(pid)
        cmd1 = Popen(["pmap -d " + pid], shell=True, stdout=PIPE)
        cmd2 = Popen(["tail -1"], shell=True, stdin=cmd1.stdout, stdout=PIPE)
        cmd3 = Popen([" awk '{print $4}'"], shell=True, stdin=cmd2.stdout, stdout=PIPE)

        usage = cmd3.communicate()[0]
        if isinstance(usage, bytes):
            usage = usage.decode("utf-8")
        usage = usage.strip()
        return usage

# Class used for iowait stat calculations
class io_wait(object):
    def __init__(self):
        pass

    def top_io_user_average(self, user1, user2, user3, user4, user5):

        user1 = str(user1)
        user2 = str(user2)
        user3 = str(user3)
        user4 = str(user4)
        user5 = str(user5)

        print("The system has run pidstat in batch mode 5 times. The following commands were writing the most to the disk during each iteration (excluding systemd and jbd2): \n")

        user_average = [user1, user2, user3, user4, user5]
        for user in user_average:
            print(user)

        print("\n")
        pass

# Create dictionary containing commands that will be executed on the system
commands = {
    "cpu_avg_idle": "iostat -c | head -4 | awk '{print $6}' | tail -1",
    "cpu_avg_io": "iostat -c | head -4 | awk '{print $4}' | tail -1",
    "cpu_avg_user": "iostat -c | head -4 | awk '{print $1}' | tail -1",
    "cpu_avg_sys": "iostat -c | head -4 | awk '{print $3}' | tail -1",
    "cpu_cores": "cat /proc/cpuinfo | grep processor | tail -1 | cut -d\: -f2",
    "one_load": "uptime | cut -d\: -f5 | awk '{print $1}' | cut -d\, -f1",
    "five_load": "uptime | cut -d\: -f5 | awk '{print $2}' | cut -d\, -f1",
    "fifteen_load": "uptime | cut -d\: -f5 | awk '{print $3}' | cut -d\, -f1",
    "top_cpu_user": "top -bn1 | egrep -v '(root|mysql)'| head -8 | awk '{print $2}'| tail -1 | sed 's/\+//g'",
    "top_cpu_procs": "ps aux | head -1;ps aux | sort -nrk3 | head -10 | egrep -v USER",
    "sorted_procs": "ps -eo user | sort | uniq -c| sort -nr | head",
    "top_mem_pid": "ps aux | sort -nrk4 | head -1 | awk '{print $2}'",
    "top_mem_procs": "ps aux | head -1; ps aux | sort -nrk4 | head -10",
    "total_mem": "grep -i memtotal /proc/meminfo | awk '{print $2}'",
    "free_mem": "grep -i memfree /proc/meminfo | awk '{print $2}'", 
    "total_swap": "grep -i swaptotal /proc/meminfo | awk '{print $2}'",
    "swap_free": "grep -i swapfree /proc/meminfo | awk '{print $2}'",
    "top_mem_user": "top -bn1 -o %MEM | egrep -v root| head -8 | awk '{print $2}'| tail -1 | sed 's/\+//g'",
    "top_io_user": "pidstat -d | egrep -v '(systemd|jbd2)'| sort -nrk6 | head -1 | awk '{print $9}'",
    "network_sar": "sar -n DEV |head -3; sar -n DEV | grep eth0 | tail -10",
    "tcpdump_top_domains": "tcpdump -i any -nn port 80 or port 443 -A -s0 -c5000 2>/dev/null | egrep 'Host: ' | sort | uniq -cd | sort -rn | head -20",
    "tcpdump_top_source_ips": "tcpdump -i any -nn -A -s0 -c5000 2> /dev/null| grep ' IP ' |awk '{print $3}' | sort | uniq -c |sort -rn | head -20",
    "netstat_tcp": "netstat -ant|wc -l",
    "netstat_udp": "netstat -anu|wc -l",
    "top_source": "netstat -tn|awk '{print $5}'|cut -d: -f1|sort -n|uniq -dc|sort -rn|head",
    "top_destination": "netstat -tn|awk '{print $4}'|cut -d: -f1|sort -n|uniq -dc|sort -rn|head",
    "netstat_con_types": "netstat -ant|awk '{print $NF}'|sort|uniq -c|sort -nr| head",
    "packets_received": "ifconfig | grep -A6 eth0 | grep 'RX packets' | awk '{print $3}'",
    "packets_transfered": "ifconfig | grep -A6 eth0 | grep 'TX packets' | awk '{print $3}'",
    "bytes_received": "ifconfig | grep -A6 eth0 | grep 'RX packets' | awk '{print $5}'",
    "bytes_transfered": "ifconfig | grep -A6 eth0 | grep 'TX packets' | awk '{print $5}'",
    "cpanel_check": "(ls /usr/local/cpanel/ >> /dev/null 2>&1 && echo yes) || echo no",
    "log_parse": " grep -c $(date +%d/%b/%Y) /usr/local/apache/domlogs/*/* | awk -F : '{print $2, $1}' | sort -nr | head | sed 's/ /\t/'",
}

# Set CPU variables
cpu_avg_idle = float(resource().calculate(commands['cpu_avg_idle']))
cpu_avg_io = float(resource().calculate(commands['cpu_avg_io']))
cpu_avg_user = float(resource().calculate(commands['cpu_avg_user']))
cpu_avg_sys = float(resource().calculate(commands['cpu_avg_sys']))
cpu_cores = int(resource().calculate(commands['cpu_cores']))
# Have to account for processor 0
cpu_cores = cpu_cores + 1
one_load = float(resource().calculate(commands['one_load']))
five_load = float(resource().calculate(commands['five_load']))
fifteen_load = float(resource().calculate(commands['fifteen_load']))
load_average = float(one_load + five_load + fifteen_load) / 3
procs_over = int(cpu().load_threshold(load_average, cpu_cores))
top_cpu_user = resource().calculate(commands['top_cpu_user'])

# Set Memory variables
top_mem_pid = str(resource().calculate(commands['top_mem_pid']))
pid_mem_usage = str(memory().pid_usage(top_mem_pid))
top_mem_user = str(resource().calculate(commands['top_mem_user']))
total_mem = int(resource().calculate(commands['total_mem']))
total_mem_gig = int(resource().calculate_gig(total_mem))
free_mem = int(resource().calculate(commands['free_mem']))  # kilobytes
free_mem_gig = int(resource().calculate_gig(free_mem))
total_swap = int(resource().calculate(commands['total_swap']))
swap_free = int(resource().calculate(commands['swap_free']))
swap_used = total_swap - swap_free

# Set IO variables
io_user1 = str(resource().calculate(commands['top_io_user']))
io_user2 = str(resource().calculate(commands['top_io_user']))
io_user3 = str(resource().calculate(commands['top_io_user']))
io_user4 = str(resource().calculate(commands['top_io_user']))
io_user5 = str(resource().calculate(commands['top_io_user']))

# Set network variables:
network_sar = str(resource().calculate(commands['network_sar']))
netstat_top_source = str(resource().calculate(commands['top_source']))
netstat_top_destination = str(resource().calculate(commands['top_destination']))
netstat_tcp = int(resource().calculate(commands['netstat_tcp']))
netstat_udp = int(resource().calculate(commands['netstat_udp']))
netstat_total = netstat_tcp + netstat_udp
netstat_con_types = str(resource().calculate(commands['netstat_con_types']))
packets_received = str(resource().calculate(commands['packets_received']))
packets_transfered = str(resource().calculate(commands['packets_transfered']))
bytes_received = str(resource().calculate(commands['bytes_received']))
bytes_transfered = str(resource().calculate(commands['bytes_transfered']))
cpanel = str(resource().calculate(commands['cpanel_check']))
logs = str(resource().calculate(commands['log_parse']))


# Server analyzing logic
# Issue counter, increment if any issue conditions are found
issue_check = 0

# Start with displaying system load, check if it is over recommended threshold
print("Checking sytem load...")
print("The aggregate system load is " + str(load_average) + "\n")
if procs_over > 1:
    print("There are " + str(cpu_cores) + " CPU cores on this system. There should only be 1 load per core, so over the course of 15 minutes the system load is " + str(procs_over) + " over where it should be. The current 1 minute load is " + str(one_load) + ".\n")
    issue_check = issue_check + 1

# CPU checks
if cpu_avg_idle > 30:
    print("Accoring to iostat data the CPU is over than 30% idle. Checking CPU usage...\n")
    cpu().check_usage(cpu_avg_idle, cpu_avg_sys, cpu_avg_user, cpu_avg_io)
    issue_check = issue_check + 1

    if cpu_avg_io > 5:
        print("Accoring to iostat data the system IO average is above 5% this could be causing perfomance issues.\n")
        io_wait().top_io_user_average(io_user1, io_user2, io_user3, io_user4, io_user5)
        print("\n")

    if cpu_avg_user > cpu_avg_sys:
        print("The CPU user usage is higher than the CPU system usage.\n")
        cpu().check_user_cpu(top_cpu_user)
        print("\nThat does not mean that this user is necessarily the problem. Here are the top 10 CPU consuming processes in the current process table:\n")
        print(resource().calculate(commands['top_cpu_procs']))
        print("\n")

    if cpu_avg_sys > cpu_avg_user:
        print("The CPU system usage is higher than the CPU user usage.\n")
        print("\nHere are the top 10 CPU consuming processes:")
        print(resource().calculate(commands['top_cpu_procs']))
        print("\n")

# Memory checks:
if free_mem_gig < 10:
    issue_check = issue_check + 1
    print("There is less than 10G of memory available on the system...")
    print("There is " + str(total_mem_gig) + "G of memory on the system.")
    print("There is " + str(free_mem) + "kB of free memory available.")
    print("There is " + str(swap_used) + "kB of swap in use.")
    print("The user using the most memory according the top data is " + str(top_mem_user) + ".")
    print("The pid consuming the most memory is " + str(top_mem_pid) + ". This pid's writable/private usage is " + str(pid_mem_usage) + " according to pmap data.")
    print("\n")
    print("Here is a sorted list of the top 10 memory consuming procs:")
    print(resource().calculate(commands['top_mem_procs']))
    print("\n")

# Network check
if netstat_total > 1500:
    issue_check = issue_check + 1
    print("There are over 1.5k connections in netstat, running network checks...")
    print("There are " + str(netstat_tcp) + " tcp connections in netstat")
    print("There are " + str(netstat_udp) + " udp connections in netstat")
    print("Here is alist of the sorted connection types in netstat: \n")
    print(netstat_con_types)
    print("\n")
    print("Here is a list of the top source ips in netstat: \n")
    print(netstat_top_source)
    print("\n")
    print("Here is a list of the top destintation ips in netstat: \n")
    print(netstat_top_destination)
    print("\n")
    print("Calculating ifconfig stats...")
    print("There are " + str(bytes_received) + " bytes received on the NIC")
    print("There are " + str(bytes_transfered) + " bytes transfered on the NIC")
    print("There are " + str(packets_received) + " packets received on the NIC")
    print("There are " + str(packets_transfered) + " packets transfered on the NIC")
    print("\n")
    print("Here is the tail end of  the sar network stats: \n")
    print(network_sar)
    print("\n")
    print("Parsing data from 2 tcpdumps, 5k packets a piece. this might take a few...")
    print("Here are the top request domains in the first packet capture: \n")
    print(resource().calculate(commands['tcpdump_top_domains']))
    print("\n")
    print("Here are the top source IPs in the second packet capture: \n")
    print(resource().calculate(commands['tcpdump_top_source_ips']))
    print("\n")
    if str(cpanel) == "yes":
        print("Looks like this a cpanel server, checking the top sites in the access logs: \n")
        print(str(logs))
    else:
        print("This is not a cpanel server, skipping log check.")

# Need to close the dev/null object that was opened earlier
FNULL.close()
