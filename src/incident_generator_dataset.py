import random
from datetime import datetime, timedelta
import pandas as pd

# --- Diversity pools ---
SERVICES = ["PaymentService", "AuthService", "OrderService", "SearchService", "InventoryService", "Gateway", "BillingService", "UserService"]
HOSTS = ["node-1", "node-2", "node-3", "node-4", "node-6", "vm-2", "vm-7", "vm-9"]
DBS = ["db-server-1", "db-server-2", "db-server-3"]

CPU_SYMPTOMS_A = [
    "{service} is timing out.",
    "Seeing timeouts on {service}.",
    "{service} requests are failing.",
    "Users reporting errors on {service}."
]
CPU_SYMPTOMS_B = [
    "CPU is at {cpu}% on {host}.",
    "High load on {host} (CPU {cpu}%).",
    "{host} looks overloaded (CPU {cpu}%)."
]
RESTART_LINES_A = ["Restarting deployment.", "Rolling restart now.", "Restarting the service."]
RESTART_LINES_B = ["Stable now.", "Errors stopped.", "Service looks healthy.", "Traffic is back to normal."]

PREVENT_CPU = [
    "Enable auto-scaling and add CPU alerts.",
    "Configure HPA and set CPU thresholds.",
    "Tune resource limits/requests and add alerts.",
    "Investigate load spike and add scaling policy.",
    "Add rate limiting and investigate traffic spikes.",
    "Add autoscaling plus dashboards for CPU and latency."
]

#--------------variability in DB connection incidents--------------
DB_SYMPTOMS_A = [
    "App cannot connect to DB.",
    "Database connection errors in the app.",
    "Seeing DB connection failures.",
    "Requests failing due to DB connectivity."
]
DB_SYMPTOMS_B = [
    "{db} not responding.",
    "Connection refused on {db}.",
    "{db} appears down/unreachable.",
    "DB host {db} is failing health checks."
]
DB_ACTIONS_A = [
    "Restarting database service.",
    "Restarting DB now.",
    "Attempting DB restart.",
    "Cycling the DB service."
]
DB_CONFIRM_B = [
    "Connection restored.",
    "DB is back online.",
    "App is connecting again.",
    "Errors cleared after restart."
]
DB_ROOT_CAUSE = [
    "Database service on {db} was unavailable (connection refused).",
    "Database host {db} stopped responding to connections.",
    "Temporary DB outage on {db} caused connection failures.",
    "DB service disruption on {db} led to application errors."
]
DB_RESOLUTION = [
    "Restarted {db_type} service to restore connectivity.",
    "Restarted the database service ({db_type}) and verified connections.",
    "Performed DB service restart ({db_type}) and confirmed recovery.",
    "Restarted {db_type} and monitored until stable."
]
DB_PREVENT = [
    "Add DB health checks and connection retry/backoff.",
    "Enable DB monitoring/alerts and implement client retries.",
    "Add failover strategy and improve DB uptime monitoring.",
    "Configure connection pooling with retries and alert on DB errors.",
    "Set up DB replication/failover and monitor connection errors.",
    "Add circuit breaker + retries in the application."
]

#--------------variability in disk full incidents--------------
DISK_SYMPTOMS_A = [
    "Disk full on {host}.",
    "Storage is at 100% on {host}.",
    "No space left on device on {host}.",
    "Disk usage critical on {host}."
]

DISK_SYMPTOMS_B = [
    "Likely logs grew too fast.",
    "Checking largest directories now.",
    "Investigating /var/log and temp files.",
    "Looking for big files and old archives."
]

DISK_ACTIONS_A = [
    "Clearing old logs.",
    "Rotating logs and cleaning up.",
    "Removing old temp files.",
    "Deleting old archives."
]

DISK_CONFIRM_B = [
    "Space freed; disk back to normal.",
    "Disk usage dropped; service recovering.",
    "Write operations are working again.",
    "System stable after cleanup."
]

DISK_ROOT_CAUSE = [
    "Disk exhaustion on {host} caused write failures for {service}.",
    "Uncontrolled log growth filled disk on {host}, impacting {service}.",
    "Temporary storage exhaustion on {host} led to write errors in {service}.",
    "Disk usage reached 100% on {host}, causing failures in {service}."
]

DISK_RESOLUTION = [
    "Cleared old logs and temporary files to free disk space.",
    "Removed large/old log files and verified disk recovery.",
    "Cleaned up logs and validated {service} resumed normal writes.",
    "Freed disk space by removing old data and confirmed stability."
]

DISK_PREVENT = [
    "Configure log rotation and disk usage alerts.",
    "Set up log retention limits and monitoring alerts.",
    "Implement automated cleanup and disk threshold alerting.",
    "Apply log rotation policies and review storage capacity planning.",
    "Add automated cleanup job and enforce retention limits.",
    "Alert earlier (e.g., 80% disk) and review capacity."
]

DISK_CLEANUP_COMMANDS = [
    "rm -rf /var/log/old_logs/*",
    "find /var/log -type f -name '*.log' -mtime +7 -delete",
    "journalctl --vacuum-time=7d",
    "du -sh /var/* | sort -h"
]

#--------------variability in network latency incidents--------------
NET_SYMPTOMS_A = [
    "API timing out.",
    "Requests are timing out intermittently.",
    "Seeing elevated latency and timeouts.",
    "Clients reporting slow responses."
]

NET_SYMPTOMS_B = [
    "Network latency spike detected.",
    "Packet loss observed on the link.",
    "Upstream dependency is slow.",
    "Gateway latency increased."
]

NET_ACTIONS_A = [
    "Monitoring traffic and error rates.",
    "Checking upstream health and metrics.",
    "Investigating recent network changes.",
    "Verifying routing/DNS status."
]

NET_CONFIRM_B = [
    "Latency normalized.",
    "Timeouts stopped.",
    "System looks stable now.",
    "Error rates back to normal."
]

NET_ROOT_CAUSE = [
    "Network latency spike (~{latency}ms) caused request timeouts in {service}.",
    "Transient network degradation (latency ~{latency}ms) impacted {service} availability.",
    "Increased network latency and/or packet loss caused timeouts for {service}.",
    "Upstream network instability led to timeouts observed in {service}."
]

NET_RESOLUTION = [
    "Monitored the system until network conditions stabilized.",
    "Validated network recovery and continued monitoring until stable.",
    "Observed stabilization after investigating network metrics and dependencies.",
    "Confirmed recovery once latency returned to normal levels."
]

NET_PREVENT = [
    "Add latency SLO alerts and investigate network bottlenecks.",
    "Set up packet loss monitoring and alert thresholds.",
    "Implement retry/backoff and alert on upstream latency spikes.",
    "Add end-to-end tracing and network performance alerts.",
    "Add upstream dependency SLO alerts and tracing.",
    "Implement client-side timeouts + exponential backoff."
]

#--------------variability in security failed login incidents--------------
SEC_IPS = [
    "192.168.1.25", "10.10.14.8", "172.16.3.99", "203.0.113.14", "198.51.100.22"
]
SEC_USERS = ["admin", "root", "svc_app", "svc_ci", "ops_user"]
SEC_SYSTEMS = ["SSH", "VPN", "WebLogin", "RDP"]

SEC_SYMPTOMS_A = [
    "Suspicious login attempts detected.",
    "Seeing repeated authentication failures.",
    "Alert: multiple failed logins in a short window.",
    "Potential brute-force activity detected."
]

SEC_SYMPTOMS_B = [
    "Source IP {ip} is triggering failures.",
    "Many failures targeting user {user}.",
    "Spike in failed logins on {system}.",
    "Geo anomaly flagged for IP {ip}."
]

SEC_ACTIONS_A = [
    "Blocking the IP now.",
    "Applying a temporary firewall block.",
    "Enabling rate limiting on auth.",
    "Locking the account temporarily."
]

SEC_CONFIRM_B = [
    "Failures dropped after the block.",
    "No more attempts observed.",
    "Alert cleared after mitigation.",
    "Traffic looks normal now."
]

SEC_ROOT_CAUSE = [
    "Brute-force login attempts from {ip} targeting {user} via {system}.",
    "Repeated failed authentication attempts from {ip} indicated a brute-force attempt.",
    "Suspicious login activity from {ip} triggered account lockouts for {user}.",
    "High-rate failed logins from {ip} caused security alerts on {system}."
]

SEC_RESOLUTION = [
    "Blocked {ip} at the firewall and locked {user} temporarily.",
    "Applied firewall rule to drop traffic from {ip} and monitored authentication logs.",
    "Temporarily blocked {ip}, forced password reset for {user}, and monitored alerts.",
    "Enabled rate limiting and blocked {ip} to stop repeated failures."
]

SEC_PREVENT = [
    "Enable MFA and add rate-limiting for authentication.",
    "Configure account lockout policies and MFA for privileged accounts.",
    "Add bot protection/rate limits and alert on abnormal login patterns.",
    "Require MFA, reduce exposed auth surface, and monitor failed login spikes.",
    "Restrict admin access by IP allowlist and enable MFA.",
    "Tune fail2ban thresholds and add SIEM alerting."
]

SEC_COMMANDS = [
    "iptables -A INPUT -s {ip} -j DROP",
    "ufw deny from {ip}",
    "fail2ban-client set sshd banip {ip}",
    "netsh advfirewall firewall add rule name=\"Block {ip}\" dir=in action=block remoteip={ip}"
]


# -----------------------------
# Helper functions
# -----------------------------
def rand_time(start_dt: datetime, max_minutes: int = 60) -> datetime:
    return start_dt + timedelta(minutes=random.randint(0, max_minutes),
                                seconds=random.randint(0, 59))


def fmt(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def plus(dt: datetime, seconds: int = 0, minutes: int = 0) -> datetime:
    return dt + timedelta(seconds=seconds, minutes=minutes)


# -----------------------------
# Template generators (5 types)
# Each returns a dict with columns
# -----------------------------
def incident_cpu_timeout(incident_id: str, base_time: datetime) -> dict:
    service = random.choice(SERVICES)
    host = random.choice(HOSTS)
    cpu = random.choice([90, 92, 95, 97, 99])

    t0 = base_time
    log_lines = [
    f"{fmt(t0)} ERROR {service} timeout on {host}",
    f"{fmt(plus(t0, seconds=5))} WARN CPU usage {cpu}% on {host}",
    f"{fmt(plus(t0, minutes=1))} INFO Restart initiated for {service}",
    f"{fmt(plus(t0, minutes=2))} INFO Service restored",
]

# Optional extra variability
    if random.random() < 0.5:
        log_lines.insert(2, f"{fmt(plus(t0, seconds=20))} WARN Queue depth high for {service}")
    if random.random() < 0.3:
        log_lines.append(f"{fmt(plus(t0, minutes=3))} INFO Health check passed for {service}")

    logs = "\n".join(log_lines)
    a1 = random.choice(CPU_SYMPTOMS_A).format(service=service)
    b1 = random.choice(CPU_SYMPTOMS_B).format(service=service, host=host, cpu=cpu)
    a2 = random.choice(RESTART_LINES_A)
    b2 = random.choice(RESTART_LINES_B)

    chat = "\n".join([
        f"Engineer A: {a1}",
        f"Engineer B: {b1}",
        f"Engineer A: {a2}",
        f"Engineer B: {b2}",
    ])

    command = f"kubectl rollout restart deployment {service}"

    return {
        "incident_id": incident_id,
        "incident_type": "cpu_timeout",
        "logs": logs,
        "chat_transcript": chat,
        "commands_executed": command,
        "root_cause": f"High CPU usage on {host} caused {service} timeouts.",
        "resolution": f"Restarted {service} deployment.",
        "preventive_action": random.choice(PREVENT_CPU)
    }


def incident_db_connection(incident_id: str, base_time: datetime) -> dict:
    service = random.choice(["PaymentService", "AuthService", "OrderService"])
    db = random.choice(["db-server-1", "db-server-2"])
    db_type = random.choice(["mysql", "postgresql"])

    t0 = base_time

    # --- Logs with optional variability ---
    log_lines = [
        f"{fmt(t0)} ERROR {service} failed to connect to database",
        f"{fmt(plus(t0, seconds=10))} WARN Connection refused on {db}",
        f"{fmt(plus(t0, minutes=1))} INFO Database service restarted",
        f"{fmt(plus(t0, minutes=2))} INFO Connection restored",
    ]

    # Optional extra lines (diversity)
    if random.random() < 0.5:
        log_lines.insert(2, f"{fmt(plus(t0, seconds=30))} WARN DB health check failed on {db}")
    if random.random() < 0.3:
        log_lines.append(f"{fmt(plus(t0, minutes=3))} INFO Application error rate returned to normal")

    logs = "\n".join(log_lines)

    # --- Chat diversity ---
    a1 = random.choice(DB_SYMPTOMS_A)
    b1 = random.choice(DB_SYMPTOMS_B).format(db=db)
    a2 = random.choice(DB_ACTIONS_A)
    b2 = random.choice(DB_CONFIRM_B)

    # Optional extra chat line
    extra_chat = []
    if random.random() < 0.4:
        extra_chat.append("Engineer A: Monitoring connections for 2 minutes.")

    chat_lines = [
        f"Engineer A: {a1}",
        f"Engineer B: {b1}",
        f"Engineer A: {a2}",
        f"Engineer B: {b2}",
        *extra_chat
    ]
    chat = "\n".join(chat_lines)

    # --- Command variability ---
    # Keep it safe: use common restart patterns
    command = random.choice([
        f"systemctl restart {db_type}",
        f"service {db_type} restart"
    ])

    # --- Output diversity ---
    root_cause = random.choice(DB_ROOT_CAUSE).format(db=db)
    resolution = random.choice(DB_RESOLUTION).format(db_type=db_type)
    preventive_action = random.choice(DB_PREVENT)

    return {
        "incident_id": incident_id,
        "incident_type": "db_connection_failure",
        "logs": logs,
        "chat_transcript": chat,
        "commands_executed": command,
        "root_cause": root_cause,
        "resolution": resolution,
        "preventive_action": preventive_action
    }


def incident_disk_full(incident_id: str, base_time: datetime) -> dict:
    service = random.choice(["LoggingService", "OrderService", "ImageProcessor", "ETLWorker"])
    host = random.choice(["node-4", "node-6", "vm-2", "vm-9"])

    t0 = base_time

    # --- Logs with optional variability ---
    log_lines = [
        f"{fmt(t0)} ERROR Disk space 100% on {host}",
        f"{fmt(plus(t0, seconds=20))} WARN Write failure in {service}",
    ]

    # Optional: add common disk-related indicators
    if random.random() < 0.5:
        log_lines.append(f"{fmt(plus(t0, seconds=35))} WARN No space left on device on {host}")
    if random.random() < 0.4:
        log_lines.append(f"{fmt(plus(t0, minutes=1))} INFO Running cleanup on {host}")

    # Always include cleanup + recovery
    log_lines.extend([
        f"{fmt(plus(t0, minutes=2))} INFO Old logs cleared",
        f"{fmt(plus(t0, minutes=3))} INFO Disk usage reduced to {random.choice([55, 60, 65, 70])}%",
    ])

    # Optional: add final health check
    if random.random() < 0.3:
        log_lines.append(f"{fmt(plus(t0, minutes=4))} INFO {service} health check passed")

    logs = "\n".join(log_lines)

    # --- Chat diversity ---
    a1 = random.choice(DISK_SYMPTOMS_A).format(host=host)
    b1 = random.choice(DISK_SYMPTOMS_B)
    a2 = random.choice(DISK_ACTIONS_A)
    b2 = random.choice(DISK_CONFIRM_B)

    chat_lines = [
        f"Engineer A: {a1}",
        f"Engineer B: {b1}",
        f"Engineer A: {a2}",
        f"Engineer B: {b2}",
    ]

    # Optional: extra line about verification
    if random.random() < 0.4:
        chat_lines.append("Engineer A: Verifying disk usage and service health.")

    chat = "\n".join(chat_lines)

    # --- Command variability ---
    # Sometimes use a single cleanup command, sometimes include a diagnostic command too
    if random.random() < 0.5:
        command = random.choice(DISK_CLEANUP_COMMANDS)
    else:
        command = " ; ".join(random.sample(DISK_CLEANUP_COMMANDS, k=2))

    # --- Output diversity ---
    root_cause = random.choice(DISK_ROOT_CAUSE).format(host=host, service=service)
    resolution = random.choice(DISK_RESOLUTION).format(service=service)
    preventive_action = random.choice(DISK_PREVENT)

    return {
        "incident_id": incident_id,
        "incident_type": "disk_full",
        "logs": logs,
        "chat_transcript": chat,
        "commands_executed": command,
        "root_cause": root_cause,
        "resolution": resolution,
        "preventive_action": preventive_action
    }


def incident_network_latency(incident_id: str, base_time: datetime) -> dict:
    service = random.choice(["APIService", "Gateway", "OrderService", "SearchService"])
    latency = random.choice([180, 250, 300, 450, 600, 900])

    # Optional: include packet loss sometimes
    packet_loss = random.choice([0.5, 1.0, 2.5, 5.0])

    t0 = base_time

    # --- Logs with optional variability ---
    log_lines = [
        f"{fmt(t0)} ERROR API timeout in {service}",
        f"{fmt(plus(t0, seconds=10))} WARN Network latency {latency}ms",
    ]

    # Optional extra indicators
    if random.random() < 0.4:
        log_lines.append(f"{fmt(plus(t0, seconds=20))} WARN Increased error rate detected for {service}")
    if random.random() < 0.35:
        log_lines.append(f"{fmt(plus(t0, seconds=30))} WARN Packet loss {packet_loss}% observed")
    if random.random() < 0.3:
        log_lines.append(f"{fmt(plus(t0, seconds=45))} INFO Checking upstream dependency health")

    # Recovery line(s)
    log_lines.append(f"{fmt(plus(t0, minutes=1))} INFO Network stabilized")

    # Optional: post-recovery verification
    if random.random() < 0.4:
        log_lines.append(f"{fmt(plus(t0, minutes=2))} INFO Latency back to normal for {service}")

    logs = "\n".join(log_lines)

    # --- Chat diversity ---
    a1 = random.choice(NET_SYMPTOMS_A)
    b1 = random.choice(NET_SYMPTOMS_B)
    a2 = random.choice(NET_ACTIONS_A)
    b2 = random.choice(NET_CONFIRM_B)

    chat_lines = [
        f"Engineer A: {a1}",
        f"Engineer B: {b1}",
        f"Engineer A: {a2}",
        f"Engineer B: {b2}",
    ]

    # Optional extra chat line (investigation detail)
    if random.random() < 0.35:
        chat_lines.append("Engineer A: No application deploys in the last 30 minutes.")

    chat = "\n".join(chat_lines)

    # --- Command variability ---
    # Often there is no direct command; sometimes run diagnostics
    command = random.choice([
        "",  # no command
        "ping -c 5 upstream-service",
        "traceroute upstream-service",
        "curl -I https://upstream-service/health"
    ]) if random.random() < 0.7 else ""

    # --- Output diversity ---
    root_cause = random.choice(NET_ROOT_CAUSE).format(service=service, latency=latency)
    resolution = random.choice(NET_RESOLUTION)
    preventive_action = random.choice(NET_PREVENT)

    return {
        "incident_id": incident_id,
        "incident_type": "network_latency_timeout",
        "logs": logs,
        "chat_transcript": chat,
        "commands_executed": command,
        "root_cause": root_cause,
        "resolution": resolution,
        "preventive_action": preventive_action
    }


def incident_failed_logins(incident_id: str, base_time: datetime) -> dict:
    ip = random.choice(SEC_IPS)
    user = random.choice(SEC_USERS)
    system = random.choice(SEC_SYSTEMS)

    t0 = base_time

    # --- Logs with variability ---
    # Vary attempt count + window
    attempts = random.choice([20, 35, 50, 80])
    window_m = random.choice([2, 5, 10])

    log_lines = [
        f"{fmt(t0)} WARN Multiple failed login attempts ({attempts} in {window_m}m) from {ip} on {system}",
    ]

    # Optional: account lock event
    if random.random() < 0.7:
        log_lines.append(f"{fmt(plus(t0, minutes=window_m))} ERROR Account locked for user {user}")

    # Optional: MFA / auth throttling event
    if random.random() < 0.35:
        log_lines.append(f"{fmt(plus(t0, minutes=window_m+1))} INFO Authentication throttling enabled for {system}")

    # Mitigation event
    log_lines.append(f"{fmt(plus(t0, minutes=window_m+2))} INFO Mitigation applied: IP blocked")

    # Optional: post-mitigation verification
    if random.random() < 0.4:
        log_lines.append(f"{fmt(plus(t0, minutes=window_m+5))} INFO Failed login rate returned to baseline")

    logs = "\n".join(log_lines)

    # --- Chat diversity ---
    a1 = random.choice(SEC_SYMPTOMS_A)
    b1 = random.choice(SEC_SYMPTOMS_B).format(ip=ip, user=user, system=system)
    a2 = random.choice(SEC_ACTIONS_A)
    b2 = random.choice(SEC_CONFIRM_B)

    chat_lines = [
        f"Engineer A: {a1}",
        f"Engineer B: {b1}",
        f"Engineer A: {a2}",
        f"Engineer B: {b2}",
    ]

    # Optional extra chat line
    if random.random() < 0.35:
        chat_lines.append(f"Engineer A: Auditing other users for similar attempts on {system}.")

    chat = "\n".join(chat_lines)

    # --- Command variability ---
    # Choose a mitigation command style (Linux/Windows/fail2ban)
    command_template = random.choice(SEC_COMMANDS)
    command = command_template.format(ip=ip)

    # --- Output diversity ---
    root_cause = random.choice(SEC_ROOT_CAUSE).format(ip=ip, user=user, system=system)
    resolution = random.choice(SEC_RESOLUTION).format(ip=ip, user=user)
    preventive_action = random.choice(SEC_PREVENT)

    return {
        "incident_id": incident_id,
        "incident_type": "security_failed_logins",
        "logs": logs,
        "chat_transcript": chat,
        "commands_executed": command,
        "root_cause": root_cause,
        "resolution": resolution,
        "preventive_action": preventive_action
    }


# -----------------------------
# Main dataset generator
# -----------------------------
TEMPLATES = [
    incident_cpu_timeout,
    incident_db_connection,
    incident_disk_full,
    incident_network_latency,
    incident_failed_logins,
]


def generate_dataset(n_samples: int = 50, seed: int = 42) -> pd.DataFrame:
    random.seed(seed)

    start_dt = datetime(2026, 2, 1, 9, 0, 0)
    rows = []

    for i in range(1, n_samples + 1):
        incident_id = f"INC_{i:04d}"
        base_time = rand_time(start_dt, max_minutes=600)  # within 10 hours
        template_fn = random.choice(TEMPLATES)
        rows.append(template_fn(incident_id, base_time))

    return pd.DataFrame(rows)

def generate_balanced_dataset(per_template: int = 40, seed: int = 42) -> pd.DataFrame:
    random.seed(seed)

    start_dt = datetime(2026, 2, 1, 9, 0, 0)
    rows = []
    i = 1

    for template_fn in TEMPLATES:
        for _ in range(per_template):
            incident_id = f"INC_{i:04d}"
            base_time = rand_time(start_dt, max_minutes=600)
            rows.append(template_fn(incident_id, base_time))
            i += 1

    # Shuffle so templates are mixed (not grouped)
    random.shuffle(rows)

    return pd.DataFrame(rows)


if __name__ == "__main__":
    df = generate_balanced_dataset(per_template=60, seed=7)  # 40*5 = 200
    output_path = "C:\\AIG_Sem2\\NLP\\Context-Aware-Incident-Report-Generation\\data\\raw\\incident_dataset.csv"
    df.to_csv(output_path, index=False, encoding="utf-8")
    print(f"Saved {len(df)} incidents to: {output_path}")
    print(df["incident_type"].value_counts())
