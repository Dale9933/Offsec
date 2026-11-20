import dns.resolver
import random
import string
import sys
from concurrent.futures import ThreadPoolExecutor


resolver = dns.resolver.Resolver()
resolver.timeout = 2
resolver.lifetime = 4

record_types = ["A", "AAAA", "CNAME", "MX", "NS", "TXT"]


def check(subdomain):
    found = {}

    for record_type in record_types:
        try:
            answers = resolver.resolve(subdomain, record_type)
            found[record_type] = [r.to_text() for r in answers]

        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers, dns.resolver.LifetimeTimeout):
            pass

    return subdomain, found


def get_wildcard(domain):
    name = "".join(random.choices(string.ascii_lowercase, k=16)) + "." + domain

    try:
        answers = resolver.resolve(name, "A")
        return set(r.to_text() for r in answers)
    except Exception:
        return set()


def get_subdomains(domain, wordlist="subenum_wordlist.txt", threads=20):
    with open(wordlist) as file:
        words = set(line.strip() for line in file if line.strip())

    wildcard = get_wildcard(domain)
    if wildcard:
        print("wildcard gefunden: " + ", ".join(wildcard))

    targets = [word + "." + domain for word in words]
    subdomains = {}

    with ThreadPoolExecutor(threads) as pool:
        for subdomain, found in pool.map(check, targets):
            if not found:
                continue

            if wildcard and list(found.keys()) == ["A"] and set(found["A"]) == wildcard:
                continue

            subdomains[subdomain] = found
            print("[+] " + subdomain + " " + str(found))

    return subdomains


def save(subdomains, filename):
    with open(filename, "w") as file:
        for subdomain in subdomains:
            for record_type in subdomains[subdomain]:
                for value in subdomains[subdomain][record_type]:
                    file.write(subdomain + "," + record_type + "," + value + "\n")


if len(sys.argv) < 2:
    print("benutzung: python subenum.py domain [ausgabe.csv]")
    sys.exit()

result = get_subdomains(sys.argv[1])
print(str(len(result)) + " subdomains gefunden")

if len(sys.argv) > 2:
    save(result, sys.argv[2])
